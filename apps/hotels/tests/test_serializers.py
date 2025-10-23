"""
Test suite for Hotel app serializers
Following TDD: Write tests first, then implement serializers
"""

import pytest
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from decimal import Decimal

from apps.hotels.serializers import HotelSerializer, RoomTypeSerializer, RoomSerializer
from apps.hotels.tests.factories import HotelFactory, RoomTypeFactory, RoomFactory


class HotelSerializerTest(TestCase):
    """Test suite for HotelSerializer"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.hotel = HotelFactory()

    def test_serialization(self):
        """Test model → JSON serialization"""
        serializer = HotelSerializer(self.hotel)
        data = serializer.data

        assert data["name"] == self.hotel.name
        assert data["slug"] == self.hotel.slug
        assert data["type"] == self.hotel.type
        assert "id" in data
        assert "created_at" in data

    def test_deserialization(self):
        """Test JSON → model deserialization"""
        data = {
            "name": "Test Hotel Serializer",
            "type": "independent",
            "address": {"street": "123 Test St", "city": "Test City", "country": "US"},
            "contact": {"phone": "+1-555-0100", "email": "test@hotel.com"},
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "total_rooms": 50,
            "timezone": "America/New_York",
            "currency": "USD",
            "languages": ["en", "es"],
        }
        serializer = HotelSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        hotel = serializer.save()
        assert hotel.name == "Test Hotel Serializer"
        assert hotel.type == "independent"

    def test_validation_check_out_must_be_before_check_in(self):
        """Test validation: check_out_time must be before check_in_time (next day)"""
        data = {
            "name": "Invalid Hotel",
            "type": "independent",
            "address": {},
            "contact": {},
            "check_in_time": "11:00",
            "check_out_time": "15:00",  # After check-in - invalid!
            "total_rooms": 10,
            "timezone": "UTC",
            "currency": "USD",
            "languages": ["en"],
        }
        serializer = HotelSerializer(data=data)
        assert not serializer.is_valid()
        assert "check_out_time" in serializer.errors


class RoomTypeSerializerTest(TestCase):
    """Test suite for RoomTypeSerializer"""

    def setUp(self):
        self.hotel = HotelFactory()
        self.room_type = RoomTypeFactory(hotel=self.hotel)

    def test_serialization_includes_nested_hotel_name(self):
        """Test that serialization includes nested hotel_name"""
        serializer = RoomTypeSerializer(self.room_type)
        data = serializer.data

        # UUID is serialized as UUID object, convert both to string for comparison
        assert str(data["hotel"]) == str(self.room_type.hotel.id)
        assert data["hotel_name"] == self.hotel.name
        assert data["name"] == self.room_type.name
        assert "hotel_name" in data

    def test_validation_enforces_occupancy_rule(self):
        """Test validation: max_adults + max_children must equal max_occupancy"""
        data = {
            "hotel": str(self.hotel.id),
            "code": "TEST",
            "name": "Test Room Type",
            "max_occupancy": 4,
            "max_adults": 2,
            "max_children": 3,  # 2 + 3 = 5, not 4!
            "base_price": Decimal("100.00"),
            "bed_configuration": [{"type": "queen", "count": 1}],
            "amenities": ["wifi", "tv"],
        }
        serializer = RoomTypeSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors or "max_occupancy" in str(serializer.errors)

    def test_can_create_room_type_via_serializer(self):
        """Test that RoomType can be created via serializer"""
        data = {
            "hotel": str(self.hotel.id),
            "code": "DELUXE",
            "name": "Deluxe Room",
            "description": "A luxurious room",
            "max_occupancy": 4,
            "max_adults": 2,
            "max_children": 2,
            "base_price": Decimal("250.00"),
            "size_sqm": 35,
            "bed_configuration": [{"type": "king", "count": 1}],
            "amenities": ["wifi", "tv", "mini_fridge"],
        }
        serializer = RoomTypeSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        room_type = serializer.save()
        assert room_type.name == "Deluxe Room"
        assert room_type.max_occupancy == 4

    def test_read_only_fields_not_writable(self):
        """Test that read-only fields cannot be written"""
        data = {
            "hotel": str(self.hotel.id),
            "hotel_name": "Should Be Ignored",  # Read-only!
            "code": "TEST2",
            "name": "Test",
            "max_occupancy": 2,
            "max_adults": 2,
            "max_children": 0,
            "base_price": Decimal("100.00"),
            "bed_configuration": [{"type": "twin", "count": 2}],
            "amenities": ["wifi"],
        }
        serializer = RoomTypeSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        room_type = serializer.save()
        # hotel_name should be from actual hotel, not from data
        assert room_type.hotel.name != "Should Be Ignored"


class RoomSerializerTest(TestCase):
    """Test suite for RoomSerializer"""

    def setUp(self):
        self.hotel = HotelFactory()
        self.room_type = RoomTypeFactory(hotel=self.hotel)
        self.room = RoomFactory(hotel=self.hotel, room_type=self.room_type)

    def test_serialization_includes_nested_data(self):
        """Test that serialization includes nested hotel_name and room_type_name"""
        serializer = RoomSerializer(self.room)
        data = serializer.data

        assert data["hotel_name"] == self.hotel.name
        assert data["room_type_name"] == self.room_type.name
        assert data["room_number"] == self.room.room_number
        assert data["status"] == self.room.status

    def test_status_enum_validated(self):
        """Test that status field validates against allowed choices"""
        data = {
            "hotel": str(self.hotel.id),
            "room_type": str(self.room_type.id),
            "room_number": "999",
            "floor": 9,
            "status": "invalid_status",  # Not in choices!
        }
        serializer = RoomSerializer(data=data)
        assert not serializer.is_valid()
        assert "status" in serializer.errors

    def test_can_create_room_via_serializer(self):
        """Test that Room can be created via serializer"""
        data = {
            "hotel": str(self.hotel.id),
            "room_type": str(self.room_type.id),
            "room_number": "101",
            "floor": 1,
            "status": "available",
            "cleaning_status": "clean",
        }
        serializer = RoomSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        room = serializer.save()
        assert room.room_number == "101"
        assert room.status == "available"
