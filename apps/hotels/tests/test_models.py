"""
Tests for Hotel, RoomType, and Room models.
Following TDD approach - write tests first, then implement models.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import time
from apps.hotels.models import Hotel, RoomType, Room


@pytest.mark.django_db
class TestHotelModel:
    """Test suite for Hotel model"""

    def test_hotel_creation_with_valid_data(self):
        """Test creating a hotel with all required fields"""
        hotel = Hotel.objects.create(
            name="Grand Plaza Hotel",
            slug="grand-plaza-hotel",
            type="independent",
            address={
                "street_address": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "US"
            },
            contact={
                "phone": "+1-555-0123",
                "email": "info@grandplaza.com",
                "website": "https://grandplaza.com"
            },
            timezone="America/New_York",
            currency="USD",
            languages=["en", "es"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=100
        )

        assert hotel.id is not None
        assert hotel.name == "Grand Plaza Hotel"
        assert hotel.slug == "grand-plaza-hotel"
        assert hotel.type == "independent"
        assert hotel.is_active is True  # Default value
        assert hotel.created_at is not None
        assert hotel.updated_at is not None

    def test_hotel_slug_must_be_unique(self):
        """Test that hotel slug must be globally unique"""
        Hotel.objects.create(
            name="Hotel One",
            slug="unique-slug",
            type="independent",
            address={"street_address": "123 St", "city": "NYC", "state": "NY", "postal_code": "10001", "country": "US"},
            contact={"phone": "+1-555-0001", "email": "one@hotel.com", "website": "https://one.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=50
        )

        # Attempt to create another hotel with same slug
        with pytest.raises(IntegrityError):
            Hotel.objects.create(
                name="Hotel Two",
                slug="unique-slug",  # Duplicate slug
                type="boutique",
                address={"street_address": "456 Ave", "city": "NYC", "state": "NY", "postal_code": "10002", "country": "US"},
                contact={"phone": "+1-555-0002", "email": "two@hotel.com", "website": "https://two.com"},
                timezone="America/New_York",
                currency="USD",
                languages=["en"],
                check_in_time=time(15, 0),
                check_out_time=time(11, 0),
                total_rooms=75
            )

    def test_hotel_check_out_time_before_check_in_time(self):
        """Test that checkout time is earlier in the day than check-in (11am < 3pm)"""
        hotel = Hotel.objects.create(
            name="Time Test Hotel",
            slug="time-test-hotel",
            type="independent",
            address={"street_address": "789 Blvd", "city": "NYC", "state": "NY", "postal_code": "10003", "country": "US"},
            contact={"phone": "+1-555-0003", "email": "time@hotel.com", "website": "https://time.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),  # 3:00 PM
            check_out_time=time(11, 0),  # 11:00 AM
            total_rooms=60
        )

        # This should be valid: checkout (11:00) is before checkin (15:00)
        assert hotel.check_out_time.hour < hotel.check_in_time.hour

    def test_hotel_total_rooms_must_be_positive(self):
        """Test that total_rooms must be greater than 0"""
        with pytest.raises(ValidationError):
            hotel = Hotel(
                name="Zero Rooms Hotel",
                slug="zero-rooms",
                type="independent",
                address={"street_address": "000 St", "city": "NYC", "state": "NY", "postal_code": "10000", "country": "US"},
                contact={"phone": "+1-555-0000", "email": "zero@hotel.com", "website": "https://zero.com"},
                timezone="America/New_York",
                currency="USD",
                languages=["en"],
                check_in_time=time(15, 0),
                check_out_time=time(11, 0),
                total_rooms=0  # Invalid: must be > 0
            )
            hotel.full_clean()

    def test_hotel_requires_at_least_one_language(self):
        """Test that at least one language must be specified"""
        with pytest.raises(ValidationError):
            hotel = Hotel(
                name="No Language Hotel",
                slug="no-language",
                type="independent",
                address={"street_address": "111 St", "city": "NYC", "state": "NY", "postal_code": "10111", "country": "US"},
                contact={"phone": "+1-555-0111", "email": "lang@hotel.com", "website": "https://lang.com"},
                timezone="America/New_York",
                currency="USD",
                languages=[],  # Invalid: empty array
                check_in_time=time(15, 0),
                check_out_time=time(11, 0),
                total_rooms=100
            )
            hotel.full_clean()

    def test_hotel_type_validation(self):
        """Test that hotel type must be one of the valid choices"""
        with pytest.raises(ValidationError):
            hotel = Hotel(
                name="Invalid Type Hotel",
                slug="invalid-type",
                type="resort",  # Invalid: not in choices
                address={"street_address": "222 St", "city": "NYC", "state": "NY", "postal_code": "10222", "country": "US"},
                contact={"phone": "+1-555-0222", "email": "type@hotel.com", "website": "https://type.com"},
                timezone="America/New_York",
                currency="USD",
                languages=["en"],
                check_in_time=time(15, 0),
                check_out_time=time(11, 0),
                total_rooms=100
            )
            hotel.full_clean()

    def test_hotel_string_representation(self):
        """Test Hotel __str__ method"""
        hotel = Hotel.objects.create(
            name="String Test Hotel",
            slug="string-test",
            type="chain",
            address={"street_address": "333 St", "city": "NYC", "state": "NY", "postal_code": "10333", "country": "US"},
            contact={"phone": "+1-555-0333", "email": "string@hotel.com", "website": "https://string.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=100
        )

        assert str(hotel) == "String Test Hotel"

    def test_hotel_with_brand_name(self):
        """Test hotel can have optional brand name for chains"""
        hotel = Hotel.objects.create(
            name="Marriott Downtown",
            slug="marriott-downtown",
            brand="Marriott",  # Optional brand field
            type="chain",
            address={"street_address": "444 St", "city": "NYC", "state": "NY", "postal_code": "10444", "country": "US"},
            contact={"phone": "+1-555-0444", "email": "brand@hotel.com", "website": "https://brand.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en", "es", "fr"],
            check_in_time=time(16, 0),
            check_out_time=time(12, 0),
            total_rooms=200
        )

        assert hotel.brand == "Marriott"
        assert len(hotel.languages) == 3

    def test_hotel_with_settings(self):
        """Test hotel can store additional settings in JSON"""
        settings = {
            "booking_lead_time_days": 365,
            "min_stay_nights": 1,
            "max_stay_nights": 30,
            "cancellation_policy": "flexible"
        }

        hotel = Hotel.objects.create(
            name="Settings Hotel",
            slug="settings-hotel",
            type="boutique",
            address={"street_address": "555 St", "city": "NYC", "state": "NY", "postal_code": "10555", "country": "US"},
            contact={"phone": "+1-555-0555", "email": "settings@hotel.com", "website": "https://settings.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=50,
            settings=settings
        )

        assert hotel.settings["booking_lead_time_days"] == 365
        assert hotel.settings["cancellation_policy"] == "flexible"
