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
from datetime import time as datetime_time
import re
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

    def _parse_time(self, time_str: str) -> datetime_time:
        """
        Parse time string from various formats to datetime.time object.

        Supports:
        - "3 PM", "11 AM"
        - "15:00", "11:00"
        - "15:00:00"
        """
        if not time_str:
            return datetime_time(15, 0)  # Default 3 PM

        time_str = time_str.strip()

        # Handle "3 PM" / "11 AM" format
        match = re.match(r'(\d{1,2})\s*(AM|PM)', time_str, re.IGNORECASE)
        if match:
            hour = int(match.group(1))
            period = match.group(2).upper()

            if period == 'PM' and hour != 12:
                hour += 12
            elif period == 'AM' and hour == 12:
                hour = 0

            return datetime_time(hour, 0)

        # Handle "15:00" or "15:00:00" format
        try:
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            return datetime_time(hour, minute)
        except (ValueError, IndexError):
            logger.warning(f"Could not parse time '{time_str}', using default")
            return datetime_time(15, 0)

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

        # Data is stored directly in task_state (not under 'field_values')
        # Support both formats for backward compatibility
        if 'field_values' in task_state:
            field_values = task_state['field_values']
        else:
            field_values = task_state

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

        # Extract hotel data (use actual onboarding field names)
        hotel_name = field_values.get('hotel_name', 'Unnamed Hotel')

        # Create slug from name (ensure uniqueness)
        base_slug = slugify(hotel_name)
        slug = base_slug
        counter = 1
        while Hotel.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Address (JSONField) - map from onboarding field names
        address = {
            'street': field_values.get('street_address', field_values.get('full_address', '')),
            'city': field_values.get('city', ''),
            'state': field_values.get('state', ''),
            'postal_code': field_values.get('postal_code', field_values.get('zip_code', '')),
            'country': field_values.get('country', 'United States')
        }

        # Contact (JSONField) - map from onboarding field names
        contact = {
            'phone': field_values.get('phone', ''),
            'email': field_values.get('contact_email', field_values.get('email', '')),
            'website': field_values.get('website', field_values.get('website_url', ''))
        }

        # Policies - parse times from natural language ("3 PM") to time objects
        check_in_time_str = field_values.get('checkin_time', field_values.get('check_in_time', '3 PM'))
        check_out_time_str = field_values.get('checkout_time', field_values.get('check_out_time', '11 AM'))

        check_in_time = self._parse_time(check_in_time_str)
        check_out_time = self._parse_time(check_out_time_str)

        # Timezone (inferred during onboarding)
        timezone_str = field_values.get('timezone', 'America/New_York')

        # Languages (required field)
        languages = field_values.get('languages', ['en'])

        # Hotel type
        hotel_type = field_values.get('hotel_type', 'independent')

        # Total rooms (calculate from room_types list OR old format)
        total_rooms_count = 0
        room_types = field_values.get('room_types', [])

        if room_types and isinstance(room_types, list):
            # New format: room_types is a list of dicts
            # We'll estimate rooms as 10 per type (will get real count from room creation)
            total_rooms_count = len(room_types) * 10
        else:
            # Old format: room_type_1_quantity, room_type_2_quantity, etc.
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
            timezone=timezone_str,
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

        Supports two formats:
        1. NEW FORMAT (list): room_types: [{type: "Standard Queen", price: 150}, ...]
        2. OLD FORMAT (numbered): room_type_1_name, room_type_1_price, etc.
        """
        from django.utils.text import slugify

        room_types = []
        room_types_data = field_values.get('room_types', [])

        # NEW FORMAT: room_types is a list of dicts
        if room_types_data and isinstance(room_types_data, list):
            for idx, room_data in enumerate(room_types_data, 1):
                # Simple format from conversation: {type: "Standard Queen", price: 150}
                name = room_data.get('type', room_data.get('name', f'Room Type {idx}'))
                base_price = float(room_data.get('price', room_data.get('base_price', 100.00)))

                # Use defaults for fields not collected in basic onboarding
                description = f'{name} at {hotel.name}'
                max_occupancy = room_data.get('occupancy', room_data.get('max_occupancy', 2))

                # Code (short code like 'STD', 'DLX', 'SUI')
                code = name[:3].upper() if len(name) >= 3 else name.upper()
                counter = 1
                while RoomType.objects.filter(hotel=hotel, code=code).exists():
                    code = f"{name[:3].upper()}{counter}"
                    counter += 1

                # Bed configuration - infer from name
                bed_type = "1 Queen"  # Default
                if 'king' in name.lower():
                    bed_type = "1 King"
                elif 'suite' in name.lower():
                    bed_type = "1 King"

                bed_configuration = {
                    'type': bed_type,
                    'description': bed_type
                }

                # Create RoomType
                room_type = RoomType.objects.create(
                    hotel=hotel,
                    name=name,
                    code=code,
                    description=description,
                    base_price=base_price,
                    max_occupancy=max_occupancy,
                    max_adults=max_occupancy,
                    max_children=0,  # Default
                    bed_configuration=bed_configuration,
                    size_sqm=None,  # Will be added in detailed onboarding
                    amenities=room_data.get('amenities', [])
                )

                room_types.append(room_type)
                logger.info(f"Created room type: {room_type.name} (${base_price}/night)")

        # OLD FORMAT: room_type_1_name, room_type_2_name, etc.
        else:
            num_types = int(field_values.get('num_room_types', 1))

            for i in range(1, num_types + 1):
                name = field_values.get(f'room_type_{i}_name', f'Room Type {i}')
                description = field_values.get(f'room_type_{i}_description', f'{name} at {hotel.name}')
                base_price = float(field_values.get(f'room_type_{i}_base_price', 100.00))
                max_occupancy = int(field_values.get(f'room_type_{i}_max_occupancy', 2))
                bed_type = field_values.get(f'room_type_{i}_beds', '1 Queen')

                code = name[:3].upper() if len(name) >= 3 else name.upper()
                counter = 1
                while RoomType.objects.filter(hotel=hotel, code=code).exists():
                    code = f"{name[:3].upper()}{counter}"
                    counter += 1

                bed_configuration = {
                    'type': bed_type,
                    'description': bed_type
                }

                amenities = field_values.get(f'room_type_{i}_amenities', [])
                if isinstance(amenities, str):
                    amenities = [a.strip() for a in amenities.split(',')]

                room_type = RoomType.objects.create(
                    hotel=hotel,
                    name=name,
                    code=code,
                    description=description,
                    base_price=base_price,
                    max_occupancy=max_occupancy,
                    max_adults=max_occupancy,
                    max_children=0,
                    bed_configuration=bed_configuration,
                    size_sqm=None,
                    amenities=amenities
                )

                room_types.append(room_type)
                logger.info(f"Created room type: {room_type.name} (${base_price}/night)")

        return room_types

    def _create_rooms(self, hotel: Hotel, room_types: list, field_values: dict) -> list:
        """
        Bulk create Room records and auto-number them.

        Supports two formats:
        1. NEW FORMAT (array): room_types = [{"type": "...", "quantity": 10}, ...]
        2. OLD FORMAT (numbered): room_type_N_quantity = 10

        Creates rooms like: 101, 102, 103, ..., 120 for first type,
                            121, 122, ..., 135 for second type, etc.
        """
        room_number_start = int(field_values.get('room_number_start', 101))
        current_number = room_number_start

        rooms_to_create = []

        # Check format
        room_types_array = field_values.get('room_types', [])
        if room_types_array and isinstance(room_types_array, list):
            # NEW FORMAT: array of room type objects
            for idx, (room_type, room_data) in enumerate(zip(room_types, room_types_array)):
                # Get quantity from room_data (default 10 if not specified)
                quantity = int(room_data.get('quantity', 10))

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

                logger.info(f"Created {quantity} rooms for {room_type.name}")
        else:
            # OLD FORMAT: room_type_1_quantity, room_type_2_quantity, etc.
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
