"""
Tests for Data Generator Service - Phase 6

Tests the conversion of onboarding session data into F-001 models.
"""

import pytest
from django.contrib.auth import get_user_model
from apps.core.models import Organization
from apps.staff.models import Staff
from apps.hotels.models import Hotel, RoomType, Room
from apps.ai_agent.models import NoraContext
from apps.ai_agent.services.data_generator import DataGenerator

User = get_user_model()


@pytest.mark.django_db
class TestDataGenerator:
    """Test hotel generation from onboarding data"""

    def test_generate_hotel_from_onboarding_basic(self):
        """Test basic hotel creation from onboarding data"""
        # Setup
        user = User.objects.create_user(
            username="testhotelowner",
            email="owner@testhotel.com",
            password="testpass123"
        )

        org = Organization.objects.create(
            name="Test Hotel Org",
            slug="test-hotel-org"
        )

        from django.utils import timezone

        staff = Staff.objects.create(
            user=user,
            organization=org,
            role="owner",
            department="Management",
            is_active=True,
            hired_at=timezone.now().date()
        )

        # Create onboarding context with sample data
        context = NoraContext.objects.create(
            user=user,
            organization=org,
            active_task='onboarding',
            task_state={
                'state': 'COMPLETE',
                'field_values': {
                    # Hotel basics
                    'hotel_name': 'Sunset Villa',
                    'address': '123 Beach Road',
                    'city': 'Miami',
                    'state': 'FL',
                    'zip_code': '33139',
                    'country': 'United States',
                    'phone': '+1-305-555-0100',
                    'email': 'info@sunsetvilla.com',
                    'website_url': 'https://sunsetvilla.com',
                    'check_in_time': '15:00:00',
                    'check_out_time': '11:00:00',
                    'timezone': 'America/New_York',
                    'currency': 'USD',
                    'hotel_description': 'Beautiful beachfront hotel in Miami',

                    # Room types
                    'num_room_types': 2,

                    # Room Type 1
                    'room_type_1_name': 'Ocean View King',
                    'room_type_1_description': 'Spacious room with ocean views',
                    'room_type_1_base_price': 199.00,
                    'room_type_1_base_occupancy': 2,
                    'room_type_1_max_occupancy': 3,
                    'room_type_1_beds': '1 King',
                    'room_type_1_size_sqft': 350,
                    'room_type_1_amenities': ['WiFi', 'TV', 'Mini Fridge', 'Ocean View'],
                    'room_type_1_quantity': 20,

                    # Room Type 2
                    'room_type_2_name': 'Deluxe Suite',
                    'room_type_2_description': 'Luxury suite with separate living area',
                    'room_type_2_base_price': 299.00,
                    'room_type_2_base_occupancy': 2,
                    'room_type_2_max_occupancy': 4,
                    'room_type_2_beds': '1 King + 1 Sofa Bed',
                    'room_type_2_size_sqft': 550,
                    'room_type_2_amenities': ['WiFi', 'TV', 'Kitchen', 'Balcony'],
                    'room_type_2_quantity': 10,

                    # Room numbering
                    'room_number_start': 101
                }
            }
        )

        # Execute
        generator = DataGenerator(user=user, organization=org)
        result = generator.generate_hotel_from_onboarding(context)

        # Debug: Print result if failed
        if not result['success']:
            print(f"\n❌ Generation failed: {result.get('error')}")
            print(f"Errors: {result.get('errors')}")

        # Assert - Success
        assert result['success'] is True, f"Failed: {result.get('error', 'Unknown error')}"
        assert result['hotel'] is not None
        assert len(result['errors']) == 0

        # Assert - Hotel created correctly
        hotel = result['hotel']
        assert hotel.name == 'Sunset Villa'
        assert hotel.slug == 'sunset-villa'
        assert hotel.organization == org
        assert hotel.address['city'] == 'Miami'
        assert hotel.address['state'] == 'FL'
        assert hotel.contact['phone'] == '+1-305-555-0100'
        assert hotel.contact['email'] == 'info@sunsetvilla.com'
        assert hotel.timezone == 'America/New_York'
        assert hotel.currency == 'USD'
        assert hotel.total_rooms == 30  # 20 + 10

        # Assert - Room types created
        room_types = result['room_types']
        assert len(room_types) == 2

        # Check first room type
        ocean_view = room_types[0]
        assert ocean_view.name == 'Ocean View King'
        assert ocean_view.base_price == 199.00
        assert ocean_view.max_occupancy == 3
        assert ocean_view.max_adults == 3
        assert ocean_view.bed_configuration['type'] == '1 King'
        assert 'WiFi' in ocean_view.amenities

        # Check second room type
        deluxe = room_types[1]
        assert deluxe.name == 'Deluxe Suite'
        assert deluxe.base_price == 299.00
        assert deluxe.max_occupancy == 4

        # Assert - Rooms created
        rooms = result['rooms']
        assert len(rooms) == 30  # 20 + 10

        # Check room numbering
        room_numbers = sorted([int(r.room_number) for r in rooms])
        assert room_numbers[0] == 101
        assert room_numbers[-1] == 130

        # Assert - Stats
        stats = result['stats']
        assert stats['total_rooms'] == 30
        assert stats['total_room_types'] == 2
        assert stats['hotel_slug'] == 'sunset-villa'

        # Assert - Context updated
        context.refresh_from_db()
        assert context.active_task == 'completed_onboarding'
        assert context.task_state['hotel_id'] == str(hotel.id)  # Stored as string

    def test_generate_hotel_slug_uniqueness(self):
        """Test that duplicate hotel names get unique slugs"""
        user = User.objects.create_user(username="owner1", email="owner1@test.com")
        org = Organization.objects.create(name="Org 1", slug="org-1")
        from django.utils import timezone as tz
        Staff.objects.create(
            user=user,
            organization=org,
            role="owner",
            department="Management",
            hired_at=tz.now().date()
        )

        # Create first hotel manually
        Hotel.objects.create(
            organization=org,
            name="Sunset Villa",
            slug="sunset-villa"
        )

        # Try to create another with same name via generator
        context = NoraContext.objects.create(
            user=user,
            organization=org,
            active_task='onboarding',
            task_state={
                'state': 'COMPLETE',
                'field_values': {
                    'hotel_name': 'Sunset Villa',  # Duplicate
                    'num_room_types': 1,
                    'room_type_1_name': 'Standard',
                    'room_type_1_base_price': 100.00,
                    'room_type_1_quantity': 5
                }
            }
        )

        generator = DataGenerator(user=user, organization=org)
        result = generator.generate_hotel_from_onboarding(context)

        assert result['success'] is True
        hotel = result['hotel']
        assert hotel.slug == 'sunset-villa-1'  # Auto-incremented

    def test_generate_hotel_missing_context_fail(self):
        """Test that generation fails if context is not in onboarding state"""
        user = User.objects.create_user(username="owner2", email="owner2@test.com")
        org = Organization.objects.create(name="Org 2", slug="org-2")

        context = NoraContext.objects.create(
            user=user,
            organization=org,
            active_task='idle',  # Not onboarding
            task_state={}
        )

        generator = DataGenerator(user=user, organization=org)
        result = generator.generate_hotel_from_onboarding(context)

        assert result['success'] is False
        assert 'not in onboarding state' in result['error']
