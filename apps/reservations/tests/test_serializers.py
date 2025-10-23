"""
Test suite for Reservation serializer
Tests nested data, date/occupancy validation, and computed fields
"""

import pytest
from django.test import TestCase
from datetime import date, timedelta
from decimal import Decimal

from apps.reservations.serializers import ReservationSerializer
from apps.reservations.tests.factories import ReservationFactory
from apps.guests.tests.factories import GuestFactory
from apps.hotels.tests.factories import HotelFactory, RoomTypeFactory, RoomFactory


class ReservationSerializerTest(TestCase):
    """Test suite for ReservationSerializer"""

    def setUp(self):
        self.hotel = HotelFactory()
        self.guest = GuestFactory()
        self.room_type = RoomTypeFactory(hotel=self.hotel, max_occupancy=4)
        self.room = RoomFactory(hotel=self.hotel, room_type=self.room_type)

        self.reservation = ReservationFactory(
            hotel=self.hotel,
            guest=self.guest,
            room=self.room,
            room_type=self.room_type,
            adults=2,
            children=1
        )

    def test_serialization_includes_nested_data(self):
        """Test that serialization includes all nested guest/hotel/room data"""
        serializer = ReservationSerializer(self.reservation)
        data = serializer.data

        # Verify nested fields are present
        assert data['guest_name'] == self.guest.full_name
        assert data['guest_email'] == self.guest.email
        assert data['hotel_name'] == self.hotel.name
        assert data['room_type_name'] == self.room_type.name
        assert data['room_number'] == self.room.room_number

        # Verify they're in the response
        assert 'guest_name' in data
        assert 'guest_email' in data
        assert 'hotel_name' in data
        assert 'room_type_name' in data
        assert 'room_number' in data

    def test_deserialization_validates_dates(self):
        """Test that check_out_date must be after check_in_date"""
        today = date.today()

        # Invalid: check_out before/equal to check_in
        data = {
            'hotel': str(self.hotel.id),
            'guest': str(self.guest.id),
            'room_type': str(self.room_type.id),
            'check_in_date': today.isoformat(),
            'check_out_date': today.isoformat(),  # Same day - invalid!
            'adults': 2,
            'status': 'confirmed',
            'source': 'direct',
            'rate_per_night': '150.00'
        }
        serializer = ReservationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'check_out_date' in serializer.errors

    def test_deserialization_validates_occupancy(self):
        """Test that total guests cannot exceed room_type max_occupancy"""
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # This room_type has max_occupancy=4
        # Try to book for 5 guests (exceeds limit)
        data = {
            'hotel': str(self.hotel.id),
            'guest': str(self.guest.id),
            'room_type': str(self.room_type.id),
            'check_in_date': today.isoformat(),
            'check_out_date': tomorrow.isoformat(),
            'adults': 3,
            'children': 2,  # 3 + 2 = 5 > max_occupancy(4)
            'status': 'confirmed',
            'source': 'direct',
            'rate_per_night': '150.00'
        }
        serializer = ReservationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'adults' in serializer.errors

    def test_read_only_fields_not_writable(self):
        """Test that read-only fields cannot be set via deserialization"""
        today = date.today()
        tomorrow = today + timedelta(days=1)

        data = {
            'hotel': str(self.hotel.id),
            'guest': str(self.guest.id),
            'room_type': str(self.room_type.id),
            'check_in_date': today.isoformat(),
            'check_out_date': tomorrow.isoformat(),
            'adults': 2,
            'status': 'confirmed',
            'source': 'direct',
            'rate_per_night': '150.00',
            # Try to set read-only fields
            'confirmation_number': 'HACKED123',
            'nights': 999,
            'total_amount': '999999.99'
        }
        serializer = ReservationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        reservation = serializer.save()

        # Read-only fields should NOT have the values we tried to set
        assert reservation.confirmation_number != 'HACKED123'
        assert reservation.nights != 999
        assert reservation.total_amount != Decimal('999999.99')

    def test_confirmation_number_auto_generated(self):
        """Test that confirmation_number is auto-generated on creation"""
        today = date.today()
        tomorrow = today + timedelta(days=1)

        data = {
            'hotel': str(self.hotel.id),
            'guest': str(self.guest.id),
            'room_type': str(self.room_type.id),
            'check_in_date': today.isoformat(),
            'check_out_date': tomorrow.isoformat(),
            'adults': 2,
            'status': 'confirmed',
            'source': 'direct',
            'rate_per_night': '150.00'
        }
        serializer = ReservationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        reservation = serializer.save()

        # Confirmation number should be auto-generated (not null/empty)
        assert reservation.confirmation_number is not None
        assert reservation.confirmation_number != ''
        assert len(reservation.confirmation_number) > 0

    def test_nights_auto_calculated(self):
        """Test that nights is auto-calculated from check-in/check-out dates"""
        today = date.today()
        three_days_later = today + timedelta(days=3)

        data = {
            'hotel': str(self.hotel.id),
            'guest': str(self.guest.id),
            'room_type': str(self.room_type.id),
            'check_in_date': today.isoformat(),
            'check_out_date': three_days_later.isoformat(),
            'adults': 2,
            'status': 'confirmed',
            'source': 'direct',
            'rate_per_night': '100.00'
        }
        serializer = ReservationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        reservation = serializer.save()

        # Should calculate nights = 3
        assert reservation.nights == 3

    def test_complex_reservation_creation(self):
        """Test creating a complex reservation with all optional fields"""
        today = date.today()
        checkout = today + timedelta(days=2)

        data = {
            'hotel': str(self.hotel.id),
            'guest': str(self.guest.id),
            'room': str(self.room.id),
            'room_type': str(self.room_type.id),
            'check_in_date': today.isoformat(),
            'check_out_date': checkout.isoformat(),
            'adults': 2,
            'children': 1,
            'status': 'confirmed',
            'source': 'ota',
            'channel': 'booking.com',
            'rate_per_night': '200.00',
            'taxes': '40.00',
            'fees': '20.00',
            'extras': '150.00',  # DecimalField, not JSON
            'discounts': '30.00',  # DecimalField, not JSON
            'deposit_paid': '100.00',
            'special_requests': 'Late check-in, high floor',
            'notes': 'VIP guest, anniversary celebration'
        }
        serializer = ReservationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        reservation = serializer.save()

        # Verify all fields were saved correctly
        assert reservation.adults == 2
        assert reservation.children == 1
        assert reservation.channel == 'booking.com'
        assert reservation.rate_per_night == Decimal('200.00')
        assert reservation.taxes == Decimal('40.00')
        assert reservation.fees == Decimal('20.00')
        assert reservation.extras == Decimal('150.00')
        assert reservation.discounts == Decimal('30.00')
        assert reservation.deposit_paid == Decimal('100.00')
        assert reservation.special_requests == 'Late check-in, high floor'
        assert reservation.notes == 'VIP guest, anniversary celebration'

        # Verify computed fields
        assert reservation.nights == 2
        assert reservation.confirmation_number is not None
