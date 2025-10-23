"""
Tests for Staff API ViewSets.
"""

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User

from ..models import Staff
from .factories import StaffFactory
from apps.hotels.tests.factories import HotelFactory


class StaffViewSetTest(APITestCase):
    """Tests for StaffViewSet API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.force_authenticate(user=self.user)
        self.hotel = HotelFactory()
        self.staff_user = User.objects.create_user(username="staffuser", password="testpass123")
        self.staff = StaffFactory(hotel=self.hotel, user=self.staff_user, role="receptionist")

    def test_list_staff_filtered_by_hotel(self):
        """GET /api/v1/staff/?hotel={id} filters by hotel"""
        other_hotel = HotelFactory()
        other_staff_user = User.objects.create_user(username="otherstaff", password="testpass123")
        StaffFactory(hotel=other_hotel, user=other_staff_user)

        response = self.client.get(f"/api/v1/staff/?hotel={self.hotel.id}")

        assert response.status_code == status.HTTP_200_OK
        # All returned staff should belong to the specified hotel
        for staff in response.data["results"]:
            assert str(staff["hotel"]) == str(self.hotel.id)

    def test_create_staff(self):
        """POST /api/v1/staff/ creates a staff member"""
        new_user = User.objects.create_user(username="newstaff", password="testpass123")
        data = {
            "user": new_user.id,
            "hotel": str(self.hotel.id),
            "employee_id": "EMP-001",
            "role": "housekeeping",
            "department": "Housekeeping",
            "shift": "day",
            "hired_at": "2025-01-01",
        }
        response = self.client.post("/api/v1/staff/", data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["role"] == "housekeeping"
        # employee_id is returned, just verify creation succeeded

    def test_update_staff_permissions(self):
        """PATCH /api/v1/staff/{id}/ can update permissions"""
        custom_permissions = {"reservations": {"can_create": True, "can_view": True}}
        data = {"permissions": custom_permissions}
        response = self.client.patch(f"/api/v1/staff/{self.staff.id}/", data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "reservations" in response.data["permissions"]

    def test_filter_by_role(self):
        """GET /api/v1/staff/?role=manager filters by role"""
        manager_user = User.objects.create_user(username="manager", password="testpass123")
        StaffFactory(hotel=self.hotel, user=manager_user, role="manager")

        response = self.client.get("/api/v1/staff/?role=manager")

        assert response.status_code == status.HTTP_200_OK
        # All returned staff should have 'manager' role
        for staff in response.data["results"]:
            assert staff["role"] == "manager"

    def test_unauthenticated_access_denied(self):
        """Unauthenticated requests are rejected"""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/staff/")

        # Can be 401 or 403 depending on authentication configuration
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_retrieve_nonexistent_staff(self):
        """GET /api/v1/staff/{invalid_id}/ returns 404"""
        response = self.client.get("/api/v1/staff/00000000-0000-0000-0000-000000000000/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_staff_pagination(self):
        """GET /api/v1/staff/?page=1 returns paginated results"""
        # Create multiple staff members
        for i in range(15):
            user = User.objects.create_user(username=f"staff{i}", password="testpass123")
            StaffFactory(hotel=self.hotel, user=user)

        response = self.client.get("/api/v1/staff/?page=1")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data
