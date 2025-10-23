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
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.hotel = HotelFactory()

    def test_list_hotels(self):
        """GET /api/v1/hotels/ returns hotel list"""
        HotelFactory.create_batch(3)
        response = self.client.get('/api/v1/hotels/')

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1

    def test_create_hotel(self):
        """POST /api/v1/hotels/ creates a hotel"""
        data = {
            'name': 'New Test Hotel',
            'type': 'independent',
            'check_in_time': '15:00:00',
            'check_out_time': '11:00:00',
            'timezone': 'America/New_York',
            'currency': 'USD',
            'languages': ['en']
        }
        response = self.client.post('/api/v1/hotels/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Test Hotel'
        assert response.data['type'] == 'independent'

    def test_retrieve_hotel(self):
        """GET /api/v1/hotels/{id}/ returns hotel detail"""
        response = self.client.get(f'/api/v1/hotels/{self.hotel.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(self.hotel.id)
        assert response.data['name'] == self.hotel.name

    def test_update_hotel(self):
        """PATCH /api/v1/hotels/{id}/ updates hotel"""
        data = {'name': 'Updated Hotel Name'}
        response = self.client.patch(f'/api/v1/hotels/{self.hotel.id}/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Hotel Name'

    def test_delete_hotel(self):
        """DELETE /api/v1/hotels/{id}/ deletes hotel"""
        hotel = HotelFactory()
        response = self.client.delete(f'/api/v1/hotels/{hotel.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Hotel.objects.filter(id=hotel.id).exists()

    def test_hotel_stats_custom_action(self):
        """GET /api/v1/hotels/{id}/stats/ returns hotel statistics"""
        # Create some rooms for this hotel
        room_type = RoomTypeFactory(hotel=self.hotel)
        RoomFactory.create_batch(3, hotel=self.hotel, room_type=room_type)

        response = self.client.get(f'/api/v1/hotels/{self.hotel.id}/stats/')

        assert response.status_code == status.HTTP_200_OK
        assert 'total_rooms' in response.data
        assert 'active_rooms' in response.data
        assert 'total_room_types' in response.data

    def test_unauthenticated_access_denied(self):
        """Unauthenticated requests are rejected"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/hotels/')

        # Can be 401 or 403 depending on authentication configuration
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class RoomTypeViewSetTest(APITestCase):
    """Tests for RoomTypeViewSet API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.hotel = HotelFactory()
        self.room_type = RoomTypeFactory(hotel=self.hotel)

    def test_list_room_types_filtered_by_hotel(self):
        """GET /api/v1/room-types/?hotel={id} filters by hotel"""
        # Create room types for different hotels
        other_hotel = HotelFactory()
        RoomTypeFactory(hotel=other_hotel)

        response = self.client.get(f'/api/v1/room-types/?hotel={self.hotel.id}')

        assert response.status_code == status.HTTP_200_OK
        # All returned room types should belong to the specified hotel
        for rt in response.data['results']:
            assert rt['hotel'] == str(self.hotel.id)

    def test_available_rooms_action(self):
        """GET /api/v1/room-types/{id}/available_rooms/ returns availability count"""
        # Create some available rooms
        RoomFactory.create_batch(3, hotel=self.hotel, room_type=self.room_type, status='available')

        response = self.client.get(f'/api/v1/room-types/{self.room_type.id}/available_rooms/')

        assert response.status_code == status.HTTP_200_OK
        assert 'available_rooms' in response.data
        assert response.data['available_rooms'] >= 3


class RoomViewSetTest(APITestCase):
    """Tests for RoomViewSet API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.hotel = HotelFactory()
        self.room_type = RoomTypeFactory(hotel=self.hotel)
        self.room = RoomFactory(hotel=self.hotel, room_type=self.room_type, status='available')

    def test_list_rooms_filtered_by_status(self):
        """GET /api/v1/rooms/?status=available filters by status"""
        RoomFactory(hotel=self.hotel, room_type=self.room_type, status='occupied')

        response = self.client.get('/api/v1/rooms/?status=available')

        assert response.status_code == status.HTTP_200_OK
        # All returned rooms should have 'available' status
        for room in response.data['results']:
            assert room['status'] == 'available'

    def test_update_room_status_action(self):
        """POST /api/v1/rooms/{id}/update_status/ updates room status"""
        data = {'status': 'occupied'}
        response = self.client.post(f'/api/v1/rooms/{self.room.id}/update_status/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'occupied'

        # Verify in database
        self.room.refresh_from_db()
        assert self.room.status == 'occupied'

    def test_validation_errors(self):
        """Invalid data returns validation errors"""
        data = {
            'hotel': self.hotel.id,
            'room_type': self.room_type.id,
            'room_number': '',  # Invalid: empty room number
        }
        response = self.client.post('/api/v1/rooms/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'room_number' in response.data
