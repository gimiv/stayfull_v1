"""
Tests for Django Admin configuration
"""

import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from apps.hotels.models import Hotel, RoomType, Room
from apps.hotels.admin import HotelAdmin, RoomTypeAdmin, RoomAdmin


class TestAdminRegistration:
    """Test that all models are properly registered in Django Admin"""

    def test_hotel_is_registered(self):
        """Test Hotel model is registered in admin"""
        assert Hotel in admin.site._registry

    def test_roomtype_is_registered(self):
        """Test RoomType model is registered in admin"""
        assert RoomType in admin.site._registry

    def test_room_is_registered(self):
        """Test Room model is registered in admin"""
        assert Room in admin.site._registry


class TestAdminConfiguration:
    """Test admin class configurations"""

    def test_hotel_admin_configuration(self):
        """Test HotelAdmin has correct configuration"""
        assert HotelAdmin.list_display == [
            "name",
            "slug",
            "type",
            "brand",
            "total_rooms",
            "is_active",
            "created_at",
        ]
        assert HotelAdmin.list_filter == ["type", "is_active", "created_at", "updated_at"]
        assert HotelAdmin.search_fields == ["name", "slug", "brand"]
        assert HotelAdmin.readonly_fields == ["id", "created_at", "updated_at"]
        assert HotelAdmin.ordering == ["name"]
        assert len(HotelAdmin.fieldsets) == 6

    def test_roomtype_admin_configuration(self):
        """Test RoomTypeAdmin has correct configuration"""
        assert RoomTypeAdmin.list_display == [
            "name",
            "code",
            "hotel",
            "base_price",
            "max_occupancy",
            "max_adults",
            "max_children",
            "is_active",
            "display_order",
        ]
        assert RoomTypeAdmin.list_filter == ["hotel", "is_active", "created_at"]
        assert RoomTypeAdmin.search_fields == ["name", "code", "hotel__name"]
        assert RoomTypeAdmin.readonly_fields == ["id", "created_at", "updated_at"]
        assert RoomTypeAdmin.ordering == ["hotel", "display_order", "name"]
        assert len(RoomTypeAdmin.fieldsets) == 6

    def test_room_admin_configuration(self):
        """Test RoomAdmin has correct configuration"""
        assert RoomAdmin.list_display == [
            "room_number",
            "hotel",
            "room_type",
            "floor",
            "status",
            "cleaning_status",
            "is_active",
        ]
        assert RoomAdmin.list_filter == [
            "hotel",
            "room_type",
            "status",
            "cleaning_status",
            "is_active",
            "created_at",
        ]
        assert RoomAdmin.search_fields == ["room_number", "hotel__name", "room_type__name"]
        assert RoomAdmin.readonly_fields == ["id", "created_at", "updated_at"]
        assert RoomAdmin.ordering == ["hotel", "room_number"]
        assert len(RoomAdmin.fieldsets) == 4


@pytest.mark.django_db
class TestAdminFunctionality:
    """Test admin interface functionality"""

    def test_hotel_admin_str_representation(self):
        """Test Hotel admin shows proper string representation"""
        from apps.hotels.tests.factories import HotelFactory

        hotel = HotelFactory(name="Test Resort")
        assert str(hotel) == "Test Resort"

    def test_roomtype_admin_str_representation(self):
        """Test RoomType admin shows proper string representation"""
        from apps.hotels.tests.factories import HotelFactory, RoomTypeFactory

        hotel = HotelFactory(name="Test Resort")
        room_type = RoomTypeFactory(hotel=hotel, name="Deluxe Suite")
        assert str(room_type) == "Deluxe Suite (Test Resort)"

    def test_room_admin_str_representation(self):
        """Test Room admin shows proper string representation"""
        from apps.hotels.tests.factories import HotelFactory, RoomFactory

        hotel = HotelFactory(name="Test Resort")
        room = RoomFactory(hotel=hotel, room_number="101")
        assert str(room) == "Room 101 (Test Resort)"

    def test_admin_site_has_correct_models_count(self):
        """Test that we have registered the expected number of hotel models"""
        hotel_models = [
            model
            for model in admin.site._registry.keys()
            if model.__module__.startswith("apps.hotels")
        ]
        assert len(hotel_models) == 3  # Hotel, RoomType, Room
