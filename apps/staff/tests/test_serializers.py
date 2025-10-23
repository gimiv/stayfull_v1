"""
Test suite for Staff serializer
Tests nested user/hotel data, permissions, and computed fields
"""

import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date

from apps.staff.serializers import StaffSerializer
from apps.staff.tests.factories import StaffFactory, UserFactory
from apps.hotels.tests.factories import HotelFactory


class StaffSerializerTest(TestCase):
    """Test suite for StaffSerializer"""

    def setUp(self):
        self.user = UserFactory()
        self.hotel = HotelFactory()
        self.staff = StaffFactory(user=self.user, hotel=self.hotel, role='manager')

    def test_serialization_includes_nested_user_hotel_data(self):
        """Test that serialization includes nested user and hotel information"""
        serializer = StaffSerializer(self.staff)
        data = serializer.data

        assert data['user_email'] == self.user.email
        assert data['user_name'] == self.user.get_full_name()
        assert data['hotel_name'] == self.hotel.name
        assert 'user_email' in data
        assert 'user_name' in data
        assert 'hotel_name' in data

    def test_permissions_auto_populated_for_role(self):
        """Test that default permissions are set based on role"""
        # Create a new staff member
        user2 = UserFactory()
        data = {
            'user': user2.id,
            'hotel': str(self.hotel.id),
            'role': 'receptionist',
            'department': 'Front Desk',
            'shift': 'morning',
            'hired_at': date.today().isoformat()
        }
        serializer = StaffSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        staff = serializer.save()

        # Permissions should be auto-populated by model's save() method
        assert staff.permissions is not None
        assert 'reservations' in staff.permissions
        assert staff.permissions['reservations']['can_create'] is True
        # Receptionist should not have delete permission
        assert staff.permissions['reservations']['can_delete'] is False

    def test_is_manager_property_works(self):
        """Test that is_manager property is correctly exposed"""
        # Manager
        manager = StaffFactory(role='manager')
        serializer = StaffSerializer(manager)
        assert serializer.data['is_manager'] is True

        # Non-manager
        receptionist = StaffFactory(role='receptionist')
        serializer = StaffSerializer(receptionist)
        assert serializer.data['is_manager'] is False

    def test_deserialization_creates_valid_staff(self):
        """Test JSON → model deserialization"""
        user2 = UserFactory()
        data = {
            'user': user2.id,
            'hotel': str(self.hotel.id),
            'role': 'housekeeping',
            'department': 'Housekeeping',
            'shift': 'morning',
            'is_active': True,
            'hired_at': date.today().isoformat()
        }
        serializer = StaffSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        staff = serializer.save()

        assert staff.user == user2
        assert staff.hotel == self.hotel
        assert staff.role == 'housekeeping'
        assert staff.is_active is True
