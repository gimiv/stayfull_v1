"""
Tests for Reservations API ViewSets.
"""

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from datetime import date, timedelta
from decimal import Decimal

from ..models import Reservation
from .factories import ReservationFactory
from apps.hotels.tests.factories import HotelFactory, RoomTypeFactory, RoomFactory
from apps.guests.tests.factories import GuestFactory


class ReservationViewSetTest(APITestCase):
    """Tests for ReservationViewSet API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)

        self.hotel = HotelFactory()
        self.room_type = RoomTypeFactory(hotel=self.hotel)
        self.room = RoomFactory(hotel=self.hotel, room_type=self.room_type, status='available')
        self.guest = GuestFactory()

    def test_list_reservations(self):
        """GET /api/v1/reservations/ returns reservation list"""
        ReservationFactory.create_batch(3, hotel=self.hotel, room_type=self.room_type)
        response = self.client.get('/api/v1/reservations/')

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1

    def test_create_reservation(self):
        """POST /api/v1/reservations/ creates a reservation"""
        check_in = date.today() + timedelta(days=7)
        check_out = check_in + timedelta(days=3)

        data = {
            'hotel': str(self.hotel.id),
            'guest': str(self.guest.id),
            'room_type': str(self.room_type.id),
            'check_in_date': str(check_in),
            'check_out_date': str(check_out),
            'adults': 2,
            'children': 0,
            'rate_per_night': '199.00',
            'source': 'direct',
        }
        response = self.client.post('/api/v1/reservations/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['adults'] == 2
        assert 'confirmation_number' in response.data

    def test_filter_by_hotel(self):
        """GET /api/v1/reservations/?hotel={id} filters by hotel"""
        other_hotel = HotelFactory()
        other_room_type = RoomTypeFactory(hotel=other_hotel)
        ReservationFactory(hotel=other_hotel, room_type=other_room_type)

        response = self.client.get(f'/api/v1/reservations/?hotel={self.hotel.id}')

        assert response.status_code == status.HTTP_200_OK
        # All returned reservations should belong to the specified hotel
        for reservation in response.data['results']:
            assert reservation['hotel'] == str(self.hotel.id)

    def test_filter_by_status(self):
        """GET /api/v1/reservations/?status=confirmed filters by status"""
        ReservationFactory(hotel=self.hotel, room_type=self.room_type, status='confirmed')
        ReservationFactory(hotel=self.hotel, room_type=self.room_type, status='cancelled')

        response = self.client.get('/api/v1/reservations/?status=confirmed')

        assert response.status_code == status.HTTP_200_OK
        # All returned reservations should have 'confirmed' status
        for reservation in response.data['results']:
            assert reservation['status'] == 'confirmed'

    def test_filter_by_date_range(self):
        """GET /api/v1/reservations/?check_in_from=...&check_in_to=... filters by dates"""
        today = date.today()
        next_week = today + timedelta(days=7)
        next_month = today + timedelta(days=30)

        # Create reservation with check-in next week
        ReservationFactory(
            hotel=self.hotel,
            room_type=self.room_type,
            check_in_date=next_week,
            check_out_date=next_week + timedelta(days=2)
        )

        response = self.client.get(
            f'/api/v1/reservations/?check_in_from={next_week}&check_in_to={next_month}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_check_availability(self):
        """POST /api/v1/reservations/check_availability/ returns available rooms"""
        check_in = date.today() + timedelta(days=7)
        check_out = check_in + timedelta(days=3)

        data = {
            'hotel_id': str(self.hotel.id),
            'room_type_id': str(self.room_type.id),
            'check_in_date': str(check_in),
            'check_out_date': str(check_out)
        }
        response = self.client.post('/api/v1/reservations/check_availability/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'available' in response.data
        assert 'count' in response.data
        assert 'rooms' in response.data

    def test_check_in_reservation(self):
        """POST /api/v1/reservations/{id}/check_in/ checks in a reservation"""
        reservation = ReservationFactory(
            hotel=self.hotel,
            room_type=self.room_type,
            status='confirmed'
        )
        data = {'room_id': str(self.room.id)}
        response = self.client.post(f'/api/v1/reservations/{reservation.id}/check_in/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'checked_in'
        assert response.data['room'] == str(self.room.id)
        assert 'checked_in_at' in response.data

    def test_check_out_reservation(self):
        """POST /api/v1/reservations/{id}/check_out/ checks out a reservation"""
        reservation = ReservationFactory(
            hotel=self.hotel,
            room=self.room,
            room_type=self.room_type,
            status='checked_in'
        )
        response = self.client.post(f'/api/v1/reservations/{reservation.id}/check_out/', format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'checked_out'
        assert 'checked_out_at' in response.data

    def test_cancel_reservation(self):
        """POST /api/v1/reservations/{id}/cancel/ cancels a reservation"""
        reservation = ReservationFactory(hotel=self.hotel, room_type=self.room_type, status='confirmed')
        data = {'reason': 'Guest changed plans'}
        response = self.client.post(f'/api/v1/reservations/{reservation.id}/cancel/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'cancelled'
        assert 'cancelled_at' in response.data

    def test_cannot_check_in_pending_reservation(self):
        """Cannot check in a reservation that is not confirmed"""
        reservation = ReservationFactory(
            hotel=self.hotel,
            room_type=self.room_type,
            status='pending'
        )
        data = {'room_id': str(self.room.id)}
        response = self.client.post(f'/api/v1/reservations/{reservation.id}/check_in/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_cannot_check_out_without_check_in(self):
        """Cannot check out a reservation that is not checked in"""
        reservation = ReservationFactory(
            hotel=self.hotel,
            room_type=self.room_type,
            status='confirmed'
        )
        response = self.client.post(f'/api/v1/reservations/{reservation.id}/check_out/', format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_cannot_cancel_checked_out_reservation(self):
        """Cannot cancel a reservation that is already checked out"""
        reservation = ReservationFactory(
            hotel=self.hotel,
            room_type=self.room_type,
            status='checked_out'
        )
        data = {'reason': 'Late cancellation'}
        response = self.client.post(f'/api/v1/reservations/{reservation.id}/cancel/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
