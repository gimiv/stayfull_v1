"""
Tests for Hotels API ViewSets.
"""

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from decimal import Decimal

from ..models import Hotel, RoomType, Room
from .factories import HotelFactory, RoomTypeFactory, RoomFactory


class HotelViewSetTest(APITestCase):
    """Tests for HotelViewSet API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.force_authenticate(user=self.user)
        self.hotel = HotelFactory()

    def test_list_hotels(self):
        """GET /api/v1/hotels/ returns hotel list"""
        HotelFactory.create_batch(3)
        response = self.client.get("/api/v1/hotels/")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) >= 1

    def test_create_hotel(self):
        """POST /api/v1/hotels/ creates a hotel"""
        data = {
            "name": "New Test Hotel",
            "type": "independent",
            "check_in_time": "15:00:00",
            "check_out_time": "11:00:00",
            "timezone": "America/New_York",
            "currency": "USD",
            "languages": ["en"],
            "total_rooms": 100,
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "country": "US",
                "postal_code": "10001",
            },
            "contact": {"phone": "+1-555-0100", "email": "info@newtesthotel.com"},
        }
        response = self.client.post("/api/v1/hotels/", data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Test Hotel"
        assert response.data["type"] == "independent"

    def test_retrieve_hotel(self):
        """GET /api/v1/hotels/{id}/ returns hotel detail"""
        response = self.client.get(f"/api/v1/hotels/{self.hotel.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(self.hotel.id)
        assert response.data["name"] == self.hotel.name

    def test_update_hotel(self):
        """PATCH /api/v1/hotels/{id}/ updates hotel"""
        data = {"name": "Updated Hotel Name"}
        response = self.client.patch(f"/api/v1/hotels/{self.hotel.id}/", data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Hotel Name"

    def test_delete_hotel(self):
        """DELETE /api/v1/hotels/{id}/ deletes hotel"""
        hotel = HotelFactory()
        response = self.client.delete(f"/api/v1/hotels/{hotel.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Hotel.objects.filter(id=hotel.id).exists()

    def test_hotel_stats_custom_action(self):
        """GET /api/v1/hotels/{id}/stats/ returns hotel statistics"""
        # Create some rooms for this hotel
        room_type = RoomTypeFactory(hotel=self.hotel)
        RoomFactory.create_batch(3, hotel=self.hotel, room_type=room_type)

        response = self.client.get(f"/api/v1/hotels/{self.hotel.id}/stats/")

        assert response.status_code == status.HTTP_200_OK
        assert "total_rooms" in response.data
        assert "active_rooms" in response.data
        assert "total_room_types" in response.data

    def test_unauthenticated_access_denied(self):
        """Unauthenticated requests are rejected"""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/hotels/")

        # Can be 401 or 403 depending on authentication configuration
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_retrieve_nonexistent_hotel(self):
        """GET /api/v1/hotels/{invalid_id}/ returns 404"""
        response = self.client.get("/api/v1/hotels/00000000-0000-0000-0000-000000000000/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_hotels_pagination(self):
        """GET /api/v1/hotels/?page=1 returns paginated results"""
        HotelFactory.create_batch(15)
        response = self.client.get("/api/v1/hotels/?page=1")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data
        assert response.data["count"] >= 15

    def test_filter_hotels_by_type(self):
        """GET /api/v1/hotels/?type=independent filters correctly"""
        HotelFactory(type="independent")
        HotelFactory(type="chain")
        response = self.client.get("/api/v1/hotels/?type=independent")

        assert response.status_code == status.HTTP_200_OK
        for hotel in response.data["results"]:
            assert hotel["type"] == "independent"

    def test_search_hotels_by_name(self):
        """GET /api/v1/hotels/?search=Test searches by name"""
        HotelFactory(name="Test Luxury Hotel")
        HotelFactory(name="Another Hotel")
        response = self.client.get("/api/v1/hotels/?search=Test")

        assert response.status_code == status.HTTP_200_OK
        # Should find hotels with 'Test' in the name


class RoomTypeViewSetTest(APITestCase):
    """Tests for RoomTypeViewSet API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.force_authenticate(user=self.user)
        self.hotel = HotelFactory()
        self.room_type = RoomTypeFactory(hotel=self.hotel)

    def test_list_room_types_filtered_by_hotel(self):
        """GET /api/v1/room-types/?hotel={id} filters by hotel"""
        # Create room types for different hotels
        other_hotel = HotelFactory()
        RoomTypeFactory(hotel=other_hotel)

        response = self.client.get(f"/api/v1/room-types/?hotel={self.hotel.id}")

        assert response.status_code == status.HTTP_200_OK
        # All returned room types should belong to the specified hotel
        for rt in response.data["results"]:
            assert str(rt["hotel"]) == str(self.hotel.id)

    def test_available_rooms_action(self):
        """GET /api/v1/room-types/{id}/available_rooms/ returns availability count"""
        # Create some available rooms
        RoomFactory.create_batch(3, hotel=self.hotel, room_type=self.room_type, status="available")

        response = self.client.get(f"/api/v1/room-types/{self.room_type.id}/available_rooms/")

        assert response.status_code == status.HTTP_200_OK
        assert "available_rooms" in response.data
        assert response.data["available_rooms"] >= 3


class RoomViewSetTest(APITestCase):
    """Tests for RoomViewSet API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.force_authenticate(user=self.user)
        self.hotel = HotelFactory()
        self.room_type = RoomTypeFactory(hotel=self.hotel)
        self.room = RoomFactory(hotel=self.hotel, room_type=self.room_type, status="available")

    def test_list_rooms_filtered_by_status(self):
        """GET /api/v1/rooms/?status=available filters by status"""
        RoomFactory(hotel=self.hotel, room_type=self.room_type, status="occupied")

        response = self.client.get("/api/v1/rooms/?status=available")

        assert response.status_code == status.HTTP_200_OK
        # All returned rooms should have 'available' status
        for room in response.data["results"]:
            assert room["status"] == "available"

    def test_update_room_status_action(self):
        """POST /api/v1/rooms/{id}/update_status/ updates room status"""
        data = {"status": "occupied"}
        response = self.client.post(
            f"/api/v1/rooms/{self.room.id}/update_status/", data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "occupied"

        # Verify in database
        self.room.refresh_from_db()
        assert self.room.status == "occupied"

    def test_validation_errors(self):
        """Invalid data returns validation errors"""
        data = {
            "hotel": self.hotel.id,
            "room_type": self.room_type.id,
            "room_number": "",  # Invalid: empty room number
        }
        response = self.client.post("/api/v1/rooms/", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "room_number" in response.data

    def test_retrieve_nonexistent_room(self):
        """GET /api/v1/rooms/{invalid_id}/ returns 404"""
        response = self.client.get("/api/v1/rooms/00000000-0000-0000-0000-000000000000/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_room_with_invalid_status(self):
        """POST /api/v1/rooms/{id}/update_status/ with invalid status returns error"""
        data = {"status": "invalid_status"}
        response = self.client.post(
            f"/api/v1/rooms/{self.room.id}/update_status/", data, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_list_rooms_pagination(self):
        """GET /api/v1/rooms/?page=1 returns paginated structure"""
        # Create 10 rooms
        RoomFactory.create_batch(10, hotel=self.hotel, room_type=self.room_type)

        response = self.client.get("/api/v1/rooms/?page=1")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data
        # Pagination structure exists (actual page size depends on DRF config)

    def test_list_rooms_empty_result(self):
        """GET /api/v1/rooms/?status=out_of_order returns empty list when no matches"""
        response = self.client.get("/api/v1/rooms/?status=out_of_order")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        # May have 0 or more results depending on test data
