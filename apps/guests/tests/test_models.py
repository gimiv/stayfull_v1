"""
Tests for Guest model
"""

import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError


@pytest.mark.django_db
class TestGuestModel:
    """Test suite for Guest model"""

    def test_guest_creation_with_valid_data(self):
        """Test creating a Guest with all valid required fields"""
        from apps.guests.models import Guest

        guest = Guest.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1-555-0123",
            date_of_birth=date(1990, 1, 1),
            nationality="US",
            loyalty_points=100,
            vip_status=False
        )

        assert guest.pk is not None
        assert guest.first_name == "John"
        assert guest.last_name == "Doe"
        assert guest.email == "john.doe@example.com"
        assert guest.loyalty_points == 100
        assert guest.vip_status is False

    def test_guest_email_must_be_unique(self):
        """Test that email must be unique across all guests"""
        from apps.guests.models import Guest

        Guest.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1-555-0123",
        )

        # Attempt to create another guest with same email
        with pytest.raises(IntegrityError):
            Guest.objects.create(
                first_name="Jane",
                last_name="Smith",
                email="john@example.com",  # Duplicate email
                phone="+1-555-0124",
            )

    def test_guest_id_document_number_is_encrypted(self):
        """Test that id_document_number is encrypted at rest"""
        from apps.guests.models import Guest

        guest = Guest.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.encrypted@example.com",
            phone="+1-555-0123",
            id_document_type="passport",
            id_document_number="A12345678"
        )

        # Retrieve from database
        guest_from_db = Guest.objects.get(pk=guest.pk)

        # The field should transparently decrypt
        assert guest_from_db.id_document_number == "A12345678"

        # Check that the raw database value is encrypted (not plaintext)
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id_document_number FROM guests_guest WHERE id = %s",
                [str(guest.pk)]
            )
            raw_value = cursor.fetchone()[0]
            # Encrypted value should NOT match plaintext
            assert raw_value != "A12345678"
            # Encrypted value should have content (not None)
            assert raw_value is not None

    def test_guest_age_validation_minimum_18_years(self):
        """Test that guest must be at least 18 years old"""
        from apps.guests.models import Guest

        # Create guest who is 17 years old (underage)
        seventeen_years_ago = date.today() - timedelta(days=365 * 17)

        guest = Guest(
            first_name="Minor",
            last_name="Guest",
            email="minor@example.com",
            phone="+1-555-0123",
            date_of_birth=seventeen_years_ago
        )

        with pytest.raises(ValidationError) as exc_info:
            guest.full_clean()

        assert 'date_of_birth' in exc_info.value.message_dict
        assert 'must be at least 18 years old' in str(exc_info.value)

    def test_guest_loyalty_points_cannot_be_negative(self):
        """Test that loyalty_points cannot be negative"""
        from apps.guests.models import Guest

        guest = Guest(
            first_name="John",
            last_name="Doe",
            email="john.negative@example.com",
            phone="+1-555-0123",
            loyalty_points=-10  # Negative points
        )

        with pytest.raises(ValidationError) as exc_info:
            guest.full_clean()

        assert 'loyalty_points' in exc_info.value.message_dict

    def test_guest_full_name_property(self):
        """Test the full_name property combines first and last name"""
        from apps.guests.models import Guest

        guest = Guest.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.fullname@example.com",
            phone="+1-555-0123",
        )

        assert guest.full_name == "John Doe"

    def test_guest_string_representation(self):
        """Test Guest __str__ method returns full name"""
        from apps.guests.models import Guest

        guest = Guest.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane.str@example.com",
            phone="+1-555-0123",
        )

        assert str(guest) == "Jane Smith"

    def test_guest_defaults(self):
        """Test Guest model default values"""
        from apps.guests.models import Guest

        guest = Guest.objects.create(
            first_name="Default",
            last_name="Test",
            email="default@example.com",
            phone="+1-555-0123",
        )

        assert guest.loyalty_points == 0  # Default
        assert guest.vip_status is False  # Default
        assert guest.created_at is not None
        assert guest.updated_at is not None

    def test_guest_id_document_types(self):
        """Test valid ID document types"""
        from apps.guests.models import Guest

        valid_types = ['passport', 'drivers_license', 'national_id', 'other']

        for doc_type in valid_types:
            guest = Guest.objects.create(
                first_name="Test",
                last_name=f"DocType{doc_type}",
                email=f"test.{doc_type}@example.com",
                phone="+1-555-0123",
                id_document_type=doc_type,
                id_document_number=f"DOC{doc_type}123"
            )
            assert guest.id_document_type == doc_type

    def test_guest_loyalty_tier_values(self):
        """Test valid loyalty tier values"""
        from apps.guests.models import Guest

        valid_tiers = ['bronze', 'silver', 'gold', 'platinum']

        for tier in valid_tiers:
            guest = Guest.objects.create(
                first_name="Test",
                last_name=f"Tier{tier}",
                email=f"test.{tier}@example.com",
                phone="+1-555-0123",
                loyalty_tier=tier
            )
            assert guest.loyalty_tier == tier

    def test_guest_with_preferences_json(self):
        """Test Guest with preferences JSON field"""
        from apps.guests.models import Guest

        preferences = {
            'room_floor': 'high',
            'bed_type': 'king',
            'pillow': 'firm',
            'dietary': ['vegetarian'],
            'accessibility': ['wheelchair_accessible']
        }

        guest = Guest.objects.create(
            first_name="Preference",
            last_name="Test",
            email="preferences@example.com",
            phone="+1-555-0123",
            preferences=preferences
        )

        assert guest.preferences == preferences
        assert guest.preferences['room_floor'] == 'high'
        assert 'vegetarian' in guest.preferences['dietary']
