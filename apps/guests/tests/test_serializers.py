"""
Test suite for Guest serializer
Tests encryption handling, email validation, and computed fields
"""

import pytest
from django.test import TestCase
from datetime import date, timedelta

from apps.guests.serializers import GuestSerializer
from apps.guests.tests.factories import GuestFactory
from apps.guests.models import Guest


class GuestSerializerTest(TestCase):
    """Test suite for GuestSerializer"""

    def setUp(self):
        self.guest = GuestFactory()

    def test_serialization(self):
        """Test model → JSON serialization"""
        serializer = GuestSerializer(self.guest)
        data = serializer.data

        assert data["first_name"] == self.guest.first_name
        assert data["last_name"] == self.guest.last_name
        assert data["email"] == self.guest.email
        assert data["full_name"] == self.guest.full_name
        assert "id" in data
        assert "created_at" in data

    def test_email_uniqueness_validated_on_create(self):
        """Test that email uniqueness is validated when creating new guest"""
        existing_guest = GuestFactory(email="unique@test.com")

        # Try to create another guest with same email
        data = {
            "first_name": "New",
            "last_name": "Guest",
            "email": "unique@test.com",  # Duplicate!
            "phone": "+1-555-9999",
        }
        serializer = GuestSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_email_uniqueness_validated_on_update(self):
        """Test that email uniqueness is validated when updating existing guest"""
        guest1 = GuestFactory(email="guest1@test.com")
        guest2 = GuestFactory(email="guest2@test.com")

        # Try to update guest1's email to guest2's email
        data = {
            "first_name": guest1.first_name,
            "last_name": guest1.last_name,
            "email": "guest2@test.com",  # Duplicate!
            "phone": guest1.phone,
        }
        serializer = GuestSerializer(instance=guest1, data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_encryption_works_transparently(self):
        """Test that encrypted id_document_number works transparently in serializer"""
        # Create guest with encrypted document number
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.encrypted@test.com",
            "phone": "+1-555-1111",
            "id_document_type": "passport",
            "id_document_number": "A12345678",  # Plaintext input
        }
        serializer = GuestSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        guest = serializer.save()

        # Verify: when we serialize back, we get the decrypted value
        read_serializer = GuestSerializer(guest)
        assert read_serializer.data["id_document_number"] == "A12345678"

        # Verify: value is encrypted in database
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id_document_number FROM guests_guest WHERE id = %s", [str(guest.id)]
            )
            raw_value = cursor.fetchone()[0]
            assert raw_value != "A12345678"  # Should be encrypted

    def test_full_name_computed_correctly(self):
        """Test that full_name property is included and computed correctly"""
        serializer = GuestSerializer(self.guest)
        data = serializer.data

        expected_full_name = f"{self.guest.first_name} {self.guest.last_name}"
        assert data["full_name"] == expected_full_name
        assert "full_name" in serializer.Meta.read_only_fields

    def test_deserialization_creates_valid_guest(self):
        """Test JSON → model deserialization"""
        eighteen_years_ago = date.today() - timedelta(days=365 * 18 + 10)

        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@test.com",
            "phone": "+1-555-2222",
            "date_of_birth": eighteen_years_ago.isoformat(),
            "nationality": "US",
            "address": {
                "street": "456 Test Ave",
                "city": "Test City",
                "state": "TS",
                "postal_code": "12345",
                "country": "US",
            },
            "preferences": {"room_floor": "high", "bed_type": "king"},
        }
        serializer = GuestSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        guest = serializer.save()

        assert guest.first_name == "Jane"
        assert guest.last_name == "Smith"
        assert guest.email == "jane.smith@test.com"
        assert guest.nationality == "US"
