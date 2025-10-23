"""
Tests for hotel model factories
"""

import pytest
from apps.hotels.tests.factories import HotelFactory, RoomTypeFactory, RoomFactory


@pytest.mark.django_db
class TestFactories:
    """Test that all factories work correctly"""

    def test_hotel_factory_creates_valid_hotel(self):
        """Test HotelFactory creates a valid Hotel instance"""
        hotel = HotelFactory()

        assert hotel.pk is not None
        assert hotel.name is not None
        assert hotel.slug is not None
        assert hotel.type in ['independent', 'chain', 'boutique']
        assert hotel.total_rooms > 0
        assert isinstance(hotel.address, dict)
        assert isinstance(hotel.contact, dict)
        assert isinstance(hotel.languages, list)

    def test_roomtype_factory_creates_valid_roomtype(self):
        """Test RoomTypeFactory creates a valid RoomType instance"""
        room_type = RoomTypeFactory()

        assert room_type.pk is not None
        assert room_type.hotel is not None
        assert room_type.name is not None
        assert room_type.code is not None
        assert room_type.max_occupancy == room_type.max_adults + room_type.max_children
        assert room_type.base_price > 0
        assert isinstance(room_type.bed_configuration, list)
        assert isinstance(room_type.amenities, list)

    def test_room_factory_creates_valid_room(self):
        """Test RoomFactory creates a valid Room instance"""
        room = RoomFactory()

        assert room.pk is not None
        assert room.hotel is not None
        assert room.room_type is not None
        assert room.room_number is not None
        assert room.status in ['available', 'occupied', 'maintenance', 'blocked', 'out_of_order']
        assert room.cleaning_status in ['clean', 'dirty', 'in_progress', 'inspected']

    def test_room_factory_with_same_hotel(self):
        """Test creating multiple rooms for the same hotel"""
        hotel = HotelFactory()
        room_type = RoomTypeFactory(hotel=hotel)
        room1 = RoomFactory(hotel=hotel, room_type=room_type)
        room2 = RoomFactory(hotel=hotel, room_type=room_type)

        assert room1.hotel == room2.hotel == hotel
        assert room1.room_type == room2.room_type == room_type
        assert room1.room_number != room2.room_number  # Should have different room numbers

    def test_batch_creation(self):
        """Test creating multiple instances using batch"""
        hotels = HotelFactory.create_batch(3)
        assert len(hotels) == 3
        assert all(hotel.pk is not None for hotel in hotels)

        room_types = RoomTypeFactory.create_batch(5, hotel=hotels[0])
        assert len(room_types) == 5
        assert all(rt.hotel == hotels[0] for rt in room_types)
