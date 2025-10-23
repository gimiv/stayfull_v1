"""
Multi-tenancy isolation tests - verify organization-based data filtering
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory

from apps.core.tests.factories import OrganizationFactory
from apps.hotels.tests.factories import HotelFactory, RoomTypeFactory, RoomFactory
from apps.guests.tests.factories import GuestFactory
from apps.staff.tests.factories import StaffFactory
from apps.reservations.tests.factories import ReservationFactory

from apps.hotels.views import HotelViewSet, RoomTypeViewSet, RoomViewSet
from apps.guests.views import GuestViewSet
from apps.reservations.views import ReservationViewSet
from apps.staff.views import StaffViewSet


@pytest.mark.django_db
class TestMultiTenancyIsolation:
    """Test suite for multi-tenancy data isolation"""

    def setup_method(self):
        """Set up test data for each test"""
        # Create two organizations
        self.org1 = OrganizationFactory(name="Organization 1", slug="org1")
        self.org2 = OrganizationFactory(name="Organization 2", slug="org2")

        # Create hotels for each organization
        self.hotel1 = HotelFactory(organization=self.org1, name="Hotel 1")
        self.hotel2 = HotelFactory(organization=self.org2, name="Hotel 2")

        # Create staff users for each organization
        self.user1 = User.objects.create_user(username="staff1", password="pass123")
        self.staff1 = StaffFactory(user=self.user1, organization=self.org1, hotel=self.hotel1)

        self.user2 = User.objects.create_user(username="staff2", password="pass123")
        self.staff2 = StaffFactory(user=self.user2, organization=self.org2, hotel=self.hotel2)

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username="admin", password="admin123", email="admin@test.com"
        )

        # Request factory (use DRF's APIRequestFactory for query_params support)
        self.factory = APIRequestFactory()

    def test_hotel_viewset_filters_by_organization(self):
        """Test that HotelViewSet only returns hotels from user's organization"""
        # Create request as staff1
        request = self.factory.get("/api/hotels/")
        request.user = self.user1

        # Get queryset
        viewset = HotelViewSet()
        viewset.request = request
        qs = viewset.get_queryset()

        # Should only see org1's hotel
        assert qs.count() == 1
        assert self.hotel1 in qs
        assert self.hotel2 not in qs

    def test_hotel_viewset_superuser_sees_all(self):
        """Test that superuser sees all hotels"""
        request = self.factory.get("/api/hotels/")
        request.user = self.superuser

        viewset = HotelViewSet()
        viewset.request = request
        qs = viewset.get_queryset()

        # Should see both hotels
        assert qs.count() >= 2
        assert self.hotel1 in qs
        assert self.hotel2 in qs

    def test_guest_viewset_filters_by_organization(self):
        """Test that GuestViewSet only returns guests from user's organization"""
        # Create guests for each org
        guest1 = GuestFactory(organization=self.org1)
        guest2 = GuestFactory(organization=self.org2)

        # Create request as staff1
        request = self.factory.get("/api/guests/")
        request.user = self.user1

        viewset = GuestViewSet()
        viewset.request = request
        qs = viewset.get_queryset()

        # Should only see org1's guest
        assert guest1 in qs
        assert guest2 not in qs

    def test_room_type_viewset_filters_by_organization(self):
        """Test that RoomTypeViewSet only returns room types from user's organization"""
        # Create room types for each org
        rt1 = RoomTypeFactory(hotel=self.hotel1)
        rt2 = RoomTypeFactory(hotel=self.hotel2)

        # Create request as staff1
        request = self.factory.get("/api/room-types/")
        request.user = self.user1

        viewset = RoomTypeViewSet()
        viewset.request = request
        qs = viewset.get_queryset()

        # Should only see org1's room type
        assert rt1 in qs
        assert rt2 not in qs

    def test_room_viewset_filters_by_organization(self):
        """Test that RoomViewSet only returns rooms from user's organization"""
        # Create rooms for each org
        room1 = RoomFactory(hotel=self.hotel1)
        room2 = RoomFactory(hotel=self.hotel2)

        # Create request as staff1
        request = self.factory.get("/api/rooms/")
        request.user = self.user1

        viewset = RoomViewSet()
        viewset.request = request
        qs = viewset.get_queryset()

        # Should only see org1's room
        assert room1 in qs
        assert room2 not in qs

    def test_reservation_viewset_filters_by_organization(self):
        """Test that ReservationViewSet only returns reservations from user's organization"""
        # Create reservations for each org
        res1 = ReservationFactory(hotel=self.hotel1)
        res2 = ReservationFactory(hotel=self.hotel2)

        # Create request as staff1
        request = self.factory.get("/api/reservations/")
        request.user = self.user1

        viewset = ReservationViewSet()
        viewset.request = request
        qs = viewset.get_queryset()

        # Should only see org1's reservation
        assert res1 in qs
        assert res2 not in qs

    def test_staff_viewset_filters_by_organization(self):
        """Test that StaffViewSet only returns staff from user's organization"""
        # Create request as staff1
        request = self.factory.get("/api/staff/")
        request.user = self.user1

        viewset = StaffViewSet()
        viewset.request = request
        qs = viewset.get_queryset()

        # Should only see org1's staff
        assert self.staff1 in qs
        assert self.staff2 not in qs

    def test_guest_email_unique_within_organization(self):
        """Test that same email can exist in different organizations"""
        # Create guest with same email in different orgs
        email = "john@example.com"
        guest1 = GuestFactory(organization=self.org1, email=email)
        guest2 = GuestFactory(organization=self.org2, email=email)

        # Both should exist
        assert guest1.email == email
        assert guest2.email == email
        assert guest1.organization != guest2.organization

    def test_cross_organization_data_leak_prevention(self):
        """Test that user cannot access data from other organizations"""
        # Create data in org2
        hotel2 = self.hotel2
        guest2 = GuestFactory(organization=self.org2)
        room2 = RoomFactory(hotel=hotel2)

        # Try to access as org1 staff
        request = self.factory.get("/api/hotels/")
        request.user = self.user1

        # Hotel viewset
        hotel_viewset = HotelViewSet()
        hotel_viewset.request = request
        hotels = hotel_viewset.get_queryset()
        assert hotel2 not in hotels

        # Guest viewset
        guest_viewset = GuestViewSet()
        guest_viewset.request = request
        guests = guest_viewset.get_queryset()
        assert guest2 not in guests

        # Room viewset
        room_viewset = RoomViewSet()
        room_viewset.request = request
        rooms = room_viewset.get_queryset()
        assert room2 not in rooms

    def test_user_without_staff_association_sees_nothing(self):
        """Test that users without staff association cannot see any data"""
        # Create user without staff association
        orphan_user = User.objects.create_user(username="orphan", password="pass123")

        request = self.factory.get("/api/hotels/")
        request.user = orphan_user

        viewset = HotelViewSet()
        viewset.request = request
        qs = viewset.get_queryset()

        # Should see nothing
        assert qs.count() == 0
