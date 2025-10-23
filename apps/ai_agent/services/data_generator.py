"""
Data Generator Service - Phase 6: Integration & Polish

Converts onboarding session data into operational F-001 models:
- Organization (already exists, linked to user)
- Hotel
- RoomType(s)
- Room(s) - bulk created and auto-numbered

This is the final step in onboarding: session → production-ready hotel.
"""

from django.db import transaction
from django.utils import timezone
from apps.core.models import Organization
from apps.hotels.models import Hotel, RoomType, Room
from apps.ai_agent.models import NoraContext
import logging

logger = logging.getLogger(__name__)


class DataGenerator:
    """
    Generate operational hotel records from onboarding session data.

    This service is the bridge between Nora's onboarding conversation
    and the actual F-001 PMS models. It takes the structured data
    collected during onboarding and creates all necessary database records.
    """

    def __init__(self, user, organization: Organization):
        self.user = user
        self.organization = organization

    def generate_hotel_from_onboarding(self, context: NoraContext) -> dict:
        """
        Create complete hotel setup from NoraContext task_state.

        Returns:
            {
                "success": True/False,
                "hotel": Hotel instance,
                "room_types": [RoomType instances],
                "rooms": [Room instances],
                "stats": {
                    "total_rooms": 45,
                    "total_room_types": 3
                },
                "errors": []
            }
        """
        if context.active_task != 'onboarding':
            return {
                "success": False,
                "error": "Context is not in onboarding state",
                "hotel": None
            }

        task_state = context.task_state
        field_values = task_state.get('field_values', {})

        errors = []
        hotel = None
        room_types = []
        rooms = []

        try:
            with transaction.atomic():
                # 1. Create Hotel
                hotel = self._create_hotel(field_values)

                if not hotel:
                    errors.append("Failed to create hotel")
                    return {"success": False, "errors": errors}

                # 2. Create RoomTypes
                room_types = self._create_room_types(hotel, field_values)

                if not room_types:
                    errors.append("Failed to create room types")
                    return {"success": False, "errors": errors, "hotel": hotel}

                # 3. Create Rooms (bulk)
                rooms = self._create_rooms(hotel, room_types, field_values)

                # 4. Mark onboarding complete
                context.active_task = 'completed_onboarding'
                context.task_state['onboarding_completed_at'] = timezone.now().isoformat()
                context.task_state['hotel_id'] = str(hotel.id)  # UUID to string for JSON
                context.save()

                logger.info(
                    f"Successfully generated hotel '{hotel.name}' with "
                    f"{len(room_types)} room types and {len(rooms)} rooms"
                )

                return {
                    "success": True,
                    "hotel": hotel,
                    "room_types": room_types,
                    "rooms": rooms,
                    "stats": {
                        "total_rooms": len(rooms),
                        "total_room_types": len(room_types),
                        "hotel_id": hotel.id,
                        "hotel_slug": hotel.slug
                    },
                    "errors": []
                }

        except Exception as e:
            logger.error(f"Error generating hotel: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "errors": [str(e)],
                "hotel": hotel,
                "room_types": room_types,
                "rooms": rooms
            }

    def _create_hotel(self, field_values: dict) -> Hotel:
        """
        Create Hotel record from onboarding data.

        Maps onboarding fields to Hotel model fields:
        - hotel_name → name
        - address, city, state, zip, country → address fields
        - phone, email → contact fields
        - check_in_time, check_out_time → policy fields
        - website_url → website
        """
        from django.utils.text import slugify

        # Extract hotel data
        hotel_name = field_values.get('hotel_name', 'Unnamed Hotel')

        # Create slug from name (ensure uniqueness)
        base_slug = slugify(hotel_name)
        slug = base_slug
        counter = 1
        while Hotel.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Address (JSONField)
        address = {
            'street': field_values.get('address', ''),
            'city': field_values.get('city', ''),
            'state': field_values.get('state', ''),
            'postal_code': field_values.get('zip_code', ''),
            'country': field_values.get('country', 'United States')
        }

        # Contact (JSONField)
        contact = {
            'phone': field_values.get('phone', ''),
            'email': field_values.get('email', ''),
            'website': field_values.get('website_url', '')
        }

        # Policies
        check_in_time = field_values.get('check_in_time', '15:00:00')
        check_out_time = field_values.get('check_out_time', '11:00:00')

        # Timezone (inferred during onboarding)
        timezone = field_values.get('timezone', 'America/New_York')

        # Languages (required field)
        languages = field_values.get('languages', ['en'])

        # Hotel type
        hotel_type = field_values.get('hotel_type', 'independent')

        # Total rooms (will calculate from room types)
        total_rooms_count = 0
        num_types = int(field_values.get('num_room_types', 1))
        for i in range(1, num_types + 1):
            qty = int(field_values.get(f'room_type_{i}_quantity', 0))
            total_rooms_count += qty

        # Create Hotel
        hotel = Hotel.objects.create(
            organization=self.organization,
            name=hotel_name,
            slug=slug,
            type=hotel_type,
            address=address,
            contact=contact,
            timezone=timezone,
            currency=field_values.get('currency', 'USD'),
            languages=languages,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            total_rooms=max(total_rooms_count, 1)  # At least 1
        )

        logger.info(f"Created hotel: {hotel.name} (slug: {hotel.slug})")
        return hotel

    def _create_room_types(self, hotel: Hotel, field_values: dict) -> list:
        """
        Create RoomType records for the hotel.

        Onboarding collects:
        - num_room_types: How many types (e.g., 3)
        - For each type:
          - room_type_N_name: "Ocean View King"
          - room_type_N_description: AI-enhanced description
          - room_type_N_base_price: 199.00
          - room_type_N_base_occupancy: 2
          - room_type_N_max_occupancy: 4
          - room_type_N_beds: "1 King"
          - room_type_N_size_sqft: 350
          - room_type_N_amenities: ["WiFi", "TV", "Mini Fridge"]
        """
        from django.utils.text import slugify

        num_types = int(field_values.get('num_room_types', 1))
        room_types = []

        for i in range(1, num_types + 1):
            # Extract data for this room type
            name = field_values.get(f'room_type_{i}_name', f'Room Type {i}')
            description = field_values.get(
                f'room_type_{i}_description',
                f'{name} at {hotel.name}'
            )
            base_price = float(field_values.get(f'room_type_{i}_base_price', 100.00))
            base_occupancy = int(field_values.get(f'room_type_{i}_base_occupancy', 2))
            max_occupancy = int(field_values.get(f'room_type_{i}_max_occupancy', 2))

            # Bed configuration (string like "1 King" or "2 Queens")
            bed_type = field_values.get(f'room_type_{i}_beds', '1 Queen')

            # Size (optional)
            size_sqft = field_values.get(f'room_type_{i}_size_sqft')
            if size_sqft:
                size_sqft = int(size_sqft)

            # Amenities (list - JSONField)
            amenities = field_values.get(f'room_type_{i}_amenities', [])
            if isinstance(amenities, str):
                # If string, convert to list
                amenities = [a.strip() for a in amenities.split(',')]

            # Code (short code like 'DLX', 'STD')
            code = name[:3].upper() if len(name) >= 3 else name.upper()
            counter = 1
            while RoomType.objects.filter(hotel=hotel, code=code).exists():
                code = f"{name[:3].upper()}{counter}"
                counter += 1

            # Bed configuration (JSONField)
            bed_configuration = {
                'type': bed_type,
                'description': bed_type  # e.g., "1 King"
            }

            # Create RoomType
            room_type = RoomType.objects.create(
                hotel=hotel,
                name=name,
                code=code,
                description=description,
                base_price=base_price,
                max_occupancy=max_occupancy,
                max_adults=max_occupancy,  # Simplified
                max_children=0,  # Default
                bed_configuration=bed_configuration,
                size_sqm=size_sqft * 0.092903 if size_sqft else None,  # Convert sqft to sqm
                amenities=amenities
            )

            room_types.append(room_type)
            logger.info(f"Created room type: {room_type.name} (${base_price}/night)")

        return room_types

    def _create_rooms(self, hotel: Hotel, room_types: list, field_values: dict) -> list:
        """
        Bulk create Room records and auto-number them.

        Onboarding collects:
        - room_type_N_quantity: How many of this type (e.g., 20)
        - room_number_start: Optional starting number (default: 101)

        Creates rooms like: 101, 102, 103, ..., 120 for first type,
                            121, 122, ..., 135 for second type, etc.
        """
        room_number_start = int(field_values.get('room_number_start', 101))
        current_number = room_number_start

        rooms_to_create = []

        for room_type in room_types:
            # Get quantity for this type
            # Find the index (room_type_1, room_type_2, etc.)
            type_index = None
            for i in range(1, 100):  # Max 100 types
                if field_values.get(f'room_type_{i}_name') == room_type.name:
                    type_index = i
                    break

            if type_index is None:
                logger.warning(f"Could not find quantity for room type {room_type.name}")
                continue

            quantity = int(field_values.get(f'room_type_{type_index}_quantity', 10))

            # Create rooms for this type
            for _ in range(quantity):
                rooms_to_create.append(
                    Room(
                        hotel=hotel,
                        room_type=room_type,
                        room_number=str(current_number),
                        floor=self._get_floor_from_number(current_number),
                        status='available',
                        cleaning_status='clean'
                    )
                )
                current_number += 1

        # Bulk create (performance optimization)
        rooms = Room.objects.bulk_create(rooms_to_create)
        logger.info(f"Bulk created {len(rooms)} rooms (numbers {room_number_start} to {current_number - 1})")

        return rooms

    def _get_floor_from_number(self, room_number: int) -> int:
        """
        Infer floor from room number.
        Examples:
        - 101-199 → Floor 1
        - 201-299 → Floor 2
        - 1-99 → Floor 0 (ground)
        """
        if room_number < 100:
            return 0
        return room_number // 100
