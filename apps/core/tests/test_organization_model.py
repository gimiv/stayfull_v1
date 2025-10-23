"""
Tests for Organization model
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.core.models import Organization
from apps.core.tests.factories import OrganizationFactory


@pytest.mark.django_db
class TestOrganizationModel:
    """Test suite for Organization model"""

    def test_create_organization(self):
        """Test creating an organization with valid data"""
        org = OrganizationFactory()
        assert org.id is not None
        assert org.name is not None
        assert org.slug is not None
        assert org.type in ["independent", "chain", "franchise"]
        assert org.is_active is True

    def test_organization_str_representation(self):
        """Test organization string representation"""
        org = OrganizationFactory(name="Test Hotel Group")
        assert str(org) == "Test Hotel Group"

    def test_organization_slug_unique(self):
        """Test that slug must be unique"""
        OrganizationFactory(slug="test-org")
        with pytest.raises(IntegrityError):
            OrganizationFactory(slug="test-org")

    def test_organization_type_choices(self):
        """Test that type must be one of the allowed choices"""
        # Valid types
        org1 = OrganizationFactory(type="independent")
        org2 = OrganizationFactory(type="chain")
        org3 = OrganizationFactory(type="franchise")

        assert org1.type == "independent"
        assert org2.type == "chain"
        assert org3.type == "franchise"

    def test_organization_type_validation(self):
        """Test that invalid type raises ValidationError"""
        org = OrganizationFactory.build(type="invalid_type")
        with pytest.raises(ValidationError) as exc_info:
            org.clean()
        assert "type" in exc_info.value.message_dict

    def test_organization_contact_email_required(self):
        """Test that contact_email is required"""
        with pytest.raises((ValidationError, IntegrityError)):
            org = Organization(
                name="Test Org",
                slug="test-org",
                type="independent",
                contact_email="",  # Empty email
            )
            org.full_clean()

    def test_organization_contact_phone_optional(self):
        """Test that contact_phone is optional"""
        org = OrganizationFactory(contact_phone=None)
        assert org.contact_phone is None

    def test_organization_settings_optional(self):
        """Test that settings field is optional"""
        org = OrganizationFactory(settings=None)
        assert org.settings is None

    def test_organization_settings_json(self):
        """Test that settings can store JSON data"""
        settings_data = {
            "billing": {"plan": "premium", "seats": 10},
            "preferences": {"timezone": "UTC", "currency": "USD"},
        }
        org = OrganizationFactory(settings=settings_data)
        assert org.settings == settings_data

    def test_organization_is_active_default(self):
        """Test that is_active defaults to True"""
        org = OrganizationFactory()
        assert org.is_active is True

    def test_organization_can_be_inactive(self):
        """Test that organization can be set to inactive"""
        org = OrganizationFactory(is_active=False)
        assert org.is_active is False

    def test_organization_created_at_auto_set(self):
        """Test that created_at is automatically set"""
        org = OrganizationFactory()
        assert org.created_at is not None

    def test_organization_updated_at_auto_set(self):
        """Test that updated_at is automatically set"""
        org = OrganizationFactory()
        assert org.updated_at is not None

    def test_organization_hotels_relationship(self):
        """Test that organization can have hotels"""
        from apps.hotels.tests.factories import HotelFactory

        org = OrganizationFactory()
        hotel1 = HotelFactory(organization=org)
        hotel2 = HotelFactory(organization=org)

        assert org.hotels.count() == 2
        assert hotel1 in org.hotels.all()
        assert hotel2 in org.hotels.all()

    def test_organization_guests_relationship(self):
        """Test that organization can have guests"""
        from apps.guests.tests.factories import GuestFactory

        org = OrganizationFactory()
        guest1 = GuestFactory(organization=org)
        guest2 = GuestFactory(organization=org)

        assert org.guests.count() == 2
        assert guest1 in org.guests.all()
        assert guest2 in org.guests.all()

    def test_organization_staff_relationship(self):
        """Test that organization can have staff"""
        from apps.staff.tests.factories import StaffFactory

        org = OrganizationFactory()
        staff1 = StaffFactory(organization=org, hotel=None)
        staff2 = StaffFactory(organization=org, hotel=None)

        assert org.staff.count() == 2
        assert staff1 in org.staff.all()
        assert staff2 in org.staff.all()

    def test_organization_ordering(self):
        """Test that organizations are ordered by name"""
        org1 = OrganizationFactory(name="Zeta Hotels")
        org2 = OrganizationFactory(name="Alpha Hotels")
        org3 = OrganizationFactory(name="Beta Hotels")

        orgs = Organization.objects.all()
        assert list(orgs) == [org2, org3, org1]  # Alpha, Beta, Zeta

    def test_organization_indexes(self):
        """Test that proper indexes exist"""
        # This is more of a schema test - checking index fields are correct
        indexes = [index.fields for index in Organization._meta.indexes]
        assert ["slug"] in indexes
        assert ["is_active"] in indexes
