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


@pytest.mark.django_db
class TestRoomTypeModel:
    """Test suite for RoomType model"""

    def test_roomtype_creation_with_valid_data(self):
        """Test creating a room type with all required fields"""
        hotel = Hotel.objects.create(
            name="Test Hotel",
            slug="test-hotel",
            type="independent",
            address={"street_address": "123 St", "city": "NYC", "state": "NY", "postal_code": "10001", "country": "US"},
            contact={"phone": "+1-555-0001", "email": "test@hotel.com", "website": "https://test.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=100
        )

        room_type = RoomType.objects.create(
            hotel=hotel,
            name="Deluxe Suite",
            code="DLX",
            description="Spacious deluxe suite with city view",
            max_occupancy=4,
            max_adults=2,
            max_children=2,
            base_price=250.00,
            size_sqm=45.5,
            bed_configuration=[
                {"type": "king", "count": 1},
                {"type": "twin", "count": 2}
            ],
            amenities=["wifi", "tv", "mini_fridge", "safe"]
        )

        assert room_type.id is not None
        assert room_type.hotel == hotel
        assert room_type.name == "Deluxe Suite"
        assert room_type.code == "DLX"
        assert room_type.max_occupancy == 4
        assert room_type.is_active is True

    def test_roomtype_code_unique_per_hotel(self):
        """Test that room type code must be unique within a hotel"""
        hotel = Hotel.objects.create(
            name="Unique Code Hotel",
            slug="unique-code-hotel",
            type="boutique",
            address={"street_address": "456 Ave", "city": "NYC", "state": "NY", "postal_code": "10002", "country": "US"},
            contact={"phone": "+1-555-0002", "email": "unique@hotel.com", "website": "https://unique.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=50
        )

        RoomType.objects.create(
            hotel=hotel,
            name="Standard Room",
            code="STD",
            max_occupancy=2,
            max_adults=2,
            max_children=0,
            base_price=100.00,
            bed_configuration=[{"type": "queen", "count": 1}],
            amenities=["wifi"]
        )

        # Same code in same hotel should fail
        with pytest.raises(IntegrityError):
            RoomType.objects.create(
                hotel=hotel,
                name="Standard Plus",
                code="STD",  # Duplicate code in same hotel
                max_occupancy=2,
                max_adults=2,
                max_children=0,
                base_price=120.00,
                bed_configuration=[{"type": "queen", "count": 1}],
                amenities=["wifi", "tv"]
            )

    def test_roomtype_max_occupancy_equals_adults_plus_children(self):
        """Test that max_adults + max_children must equal max_occupancy"""
        hotel = Hotel.objects.create(
            name="Validation Hotel",
            slug="validation-hotel",
            type="chain",
            address={"street_address": "789 Blvd", "city": "NYC", "state": "NY", "postal_code": "10003", "country": "US"},
            contact={"phone": "+1-555-0003", "email": "valid@hotel.com", "website": "https://valid.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=75
        )

        with pytest.raises(ValidationError):
            room_type = RoomType(
                hotel=hotel,
                name="Invalid Occupancy",
                code="INV",
                max_occupancy=4,
                max_adults=2,
                max_children=1,  # 2 + 1 = 3, not 4!
                base_price=150.00,
                bed_configuration=[{"type": "king", "count": 1}],
                amenities=["wifi"]
            )
            room_type.full_clean()

    def test_roomtype_base_price_must_be_positive(self):
        """Test that base_price must be greater than 0"""
        hotel = Hotel.objects.create(
            name="Price Hotel",
            slug="price-hotel",
            type="independent",
            address={"street_address": "111 St", "city": "NYC", "state": "NY", "postal_code": "10111", "country": "US"},
            contact={"phone": "+1-555-0111", "email": "price@hotel.com", "website": "https://price.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=60
        )

        with pytest.raises(ValidationError):
            room_type = RoomType(
                hotel=hotel,
                name="Free Room",
                code="FREE",
                max_occupancy=2,
                max_adults=2,
                max_children=0,
                base_price=0.00,  # Invalid: must be > 0
                bed_configuration=[{"type": "twin", "count": 2}],
                amenities=["wifi"]
            )
            room_type.full_clean()

    def test_roomtype_requires_at_least_one_bed(self):
        """Test that at least one bed must be specified"""
        hotel = Hotel.objects.create(
            name="Bed Hotel",
            slug="bed-hotel",
            type="boutique",
            address={"street_address": "222 St", "city": "NYC", "state": "NY", "postal_code": "10222", "country": "US"},
            contact={"phone": "+1-555-0222", "email": "bed@hotel.com", "website": "https://bed.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=40
        )

        with pytest.raises(ValidationError):
            room_type = RoomType(
                hotel=hotel,
                name="No Bed Room",
                code="NBR",
                max_occupancy=2,
                max_adults=2,
                max_children=0,
                base_price=100.00,
                bed_configuration=[],  # Invalid: empty array
                amenities=["wifi"]
            )
            room_type.full_clean()

    def test_roomtype_string_representation(self):
        """Test RoomType __str__ method"""
        hotel = Hotel.objects.create(
            name="String Hotel",
            slug="string-hotel-rt",
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

        room_type = RoomType.objects.create(
            hotel=hotel,
            name="Presidential Suite",
            code="PRES",
            max_occupancy=6,
            max_adults=4,
            max_children=2,
            base_price=500.00,
            bed_configuration=[{"type": "king", "count": 2}],
            amenities=["wifi", "tv", "balcony"]
        )

        assert str(room_type) == "Presidential Suite (String Hotel)"


@pytest.mark.django_db
class TestRoomModel:
    """Test suite for Room model"""

    def test_room_creation_with_valid_data(self):
        """Test creating a room with all required fields"""
        hotel = Hotel.objects.create(
            name="Room Test Hotel",
            slug="room-test-hotel",
            type="independent",
            address={"street_address": "123 St", "city": "NYC", "state": "NY", "postal_code": "10001", "country": "US"},
            contact={"phone": "+1-555-0001", "email": "room@hotel.com", "website": "https://room.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=100
        )

        room_type = RoomType.objects.create(
            hotel=hotel,
            name="Standard Room",
            code="STD",
            max_occupancy=2,
            max_adults=2,
            max_children=0,
            base_price=100.00,
            bed_configuration=[{"type": "queen", "count": 1}],
            amenities=["wifi", "tv"]
        )

        room = Room.objects.create(
            hotel=hotel,
            room_type=room_type,
            room_number="101",
            floor=1,
            status="available",
            cleaning_status="clean"
        )

        assert room.id is not None
        assert room.hotel == hotel
        assert room.room_type == room_type
        assert room.room_number == "101"
        assert room.status == "available"
        assert room.is_active is True

    def test_room_number_unique_per_hotel(self):
        """Test that room_number must be unique within a hotel"""
        hotel = Hotel.objects.create(
            name="Unique Room Hotel",
            slug="unique-room-hotel",
            type="boutique",
            address={"street_address": "456 Ave", "city": "NYC", "state": "NY", "postal_code": "10002", "country": "US"},
            contact={"phone": "+1-555-0002", "email": "uniqueroom@hotel.com", "website": "https://uniqueroom.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=50
        )

        room_type = RoomType.objects.create(
            hotel=hotel,
            name="Deluxe",
            code="DLX",
            max_occupancy=3,
            max_adults=2,
            max_children=1,
            base_price=150.00,
            bed_configuration=[{"type": "king", "count": 1}],
            amenities=["wifi"]
        )

        Room.objects.create(
            hotel=hotel,
            room_type=room_type,
            room_number="201",
            floor=2,
            status="available",
            cleaning_status="clean"
        )

        # Same room number in same hotel should fail
        with pytest.raises(IntegrityError):
            Room.objects.create(
                hotel=hotel,
                room_type=room_type,
                room_number="201",  # Duplicate
                floor=2,
                status="available",
                cleaning_status="clean"
            )

    def test_room_status_validation(self):
        """Test that room status must be one of valid choices"""
        hotel = Hotel.objects.create(
            name="Status Hotel",
            slug="status-hotel",
            type="chain",
            address={"street_address": "789 Blvd", "city": "NYC", "state": "NY", "postal_code": "10003", "country": "US"},
            contact={"phone": "+1-555-0003", "email": "status@hotel.com", "website": "https://status.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=75
        )

        room_type = RoomType.objects.create(
            hotel=hotel,
            name="Suite",
            code="STE",
            max_occupancy=4,
            max_adults=3,
            max_children=1,
            base_price=200.00,
            bed_configuration=[{"type": "king", "count": 1}],
            amenities=["wifi", "tv"]
        )

        with pytest.raises(ValidationError):
            room = Room(
                hotel=hotel,
                room_type=room_type,
                room_number="301",
                floor=3,
                status="invalid_status",  # Invalid
                cleaning_status="clean"
            )
            room.full_clean()

    def test_room_string_representation(self):
        """Test Room __str__ method"""
        hotel = Hotel.objects.create(
            name="String Room Hotel",
            slug="string-room-hotel",
            type="independent",
            address={"street_address": "111 St", "city": "NYC", "state": "NY", "postal_code": "10111", "country": "US"},
            contact={"phone": "+1-555-0111", "email": "stringroom@hotel.com", "website": "https://stringroom.com"},
            timezone="America/New_York",
            currency="USD",
            languages=["en"],
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            total_rooms=60
        )

        room_type = RoomType.objects.create(
            hotel=hotel,
            name="Standard",
            code="STD",
            max_occupancy=2,
            max_adults=2,
            max_children=0,
            base_price=100.00,
            bed_configuration=[{"type": "queen", "count": 1}],
            amenities=["wifi"]
        )

        room = Room.objects.create(
            hotel=hotel,
            room_type=room_type,
            room_number="A-102",
            floor=1,
            status="available",
            cleaning_status="clean"
        )

        assert str(room) == "Room A-102 (String Room Hotel)"
