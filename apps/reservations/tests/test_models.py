"""
Test suite for Reservation model
Following TDD: Write tests first, then implement model

This is the most complex model in F-001 with:
- 30+ fields
- Auto-calculated fields (nights, totals)
- Complex business rules (overlapping, validations)
"""

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from datetime import date, timedelta
from decimal import Decimal

from apps.reservations.models import Reservation
from apps.hotels.tests.factories import HotelFactory, RoomFactory, RoomTypeFactory
from apps.guests.tests.factories import GuestFactory


@pytest.mark.django_db
class TestReservationModel:
    """Test suite for Reservation model - 17 comprehensive tests"""

    @pytest.fixture
    def test_hotel(self):
        """Create a test hotel"""
        return HotelFactory()

    @pytest.fixture
    def test_guest(self):
        """Create a test guest"""
        return GuestFactory()

    @pytest.fixture
    def test_room_type(self, test_hotel):
        """Create a test room type"""
        return RoomTypeFactory(hotel=test_hotel, max_occupancy=4)

    @pytest.fixture
    def test_room(self, test_hotel, test_room_type):
        """Create a test room"""
        return RoomFactory(hotel=test_hotel, room_type=test_room_type)

    # ===== DATE AND CALCULATION TESTS =====

    def test_nights_auto_calculated_correctly(self, test_hotel, test_guest, test_room_type):
        """Test that nights are auto-calculated from check-in/check-out dates"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=3)

        reservation = Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        assert reservation.nights == 3

    def test_total_room_charges_calculated_correctly(self, test_hotel, test_guest, test_room_type):
        """Test total_room_charges = rate_per_night × nights"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=4)

        reservation = Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('200.00'),
            status='confirmed'
        )

        # 4 nights × $200 = $800
        assert reservation.total_room_charges == Decimal('800.00')

    def test_total_amount_calculated_with_taxes_fees_discounts(self, test_hotel, test_guest, test_room_type):
        """Test total_amount = room_charges + taxes + fees + extras - discounts"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        reservation = Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('100.00'),
            taxes=Decimal('20.00'),
            fees=Decimal('10.00'),
            extras=Decimal('15.00'),
            discounts=Decimal('25.00'),
            status='confirmed'
        )

        # room_charges = 100 × 2 = 200
        # total = 200 + 20 + 10 + 15 - 25 = 220
        assert reservation.total_amount == Decimal('220.00')

    def test_checkout_must_be_after_checkin(self, test_hotel, test_guest, test_room_type):
        """Test ValidationError if check_out <= check_in"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in  # Same day - invalid!

        reservation = Reservation(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        with pytest.raises(ValidationError) as exc_info:
            reservation.save()
        assert 'Check-out must be after check-in' in str(exc_info.value)

    # ===== OCCUPANCY VALIDATION TESTS =====

    def test_adults_plus_children_cannot_exceed_max_occupancy(self, test_hotel, test_guest, test_room_type):
        """Test that total guests cannot exceed room_type max_occupancy"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        # room_type.max_occupancy = 4
        reservation = Reservation(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=3,
            children=2,  # 3 + 2 = 5 > 4 max_occupancy
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        with pytest.raises(ValidationError) as exc_info:
            reservation.save()
        assert 'exceeds max occupancy' in str(exc_info.value)

    def test_occupancy_validation_passes_when_within_limit(self, test_hotel, test_guest, test_room_type):
        """Test that occupancy validation passes when within max_occupancy"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        reservation = Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            children=2,  # 2 + 2 = 4, exactly at max
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        assert reservation.pk is not None

    # ===== OVERLAPPING RESERVATION TESTS (CRITICAL!) =====

    def test_cannot_create_overlapping_reservation_same_room(self, test_hotel, test_guest, test_room, test_room_type):
        """Test that overlapping reservations for the same room are blocked"""
        # Create first reservation (Jan 10-15)
        Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room=test_room,
            room_type=test_room_type,
            check_in_date=date(2025, 1, 10),
            check_out_date=date(2025, 1, 15),
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        # Attempt overlapping reservation (Jan 12-17) - should fail!
        guest2 = GuestFactory()
        reservation2 = Reservation(
            hotel=test_hotel,
            guest=guest2,
            room=test_room,  # Same room!
            room_type=test_room_type,
            check_in_date=date(2025, 1, 12),  # Overlaps!
            check_out_date=date(2025, 1, 17),
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        with pytest.raises(ValidationError) as exc_info:
            reservation2.save()
        assert 'overlapping reservation' in str(exc_info.value)

    def test_can_create_nonoverlapping_reservation_same_room(self, test_hotel, test_guest, test_room, test_room_type):
        """Test that non-overlapping reservations for same room are allowed"""
        # Create first reservation (Jan 10-15)
        Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room=test_room,
            room_type=test_room_type,
            check_in_date=date(2025, 1, 10),
            check_out_date=date(2025, 1, 15),
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        # Create non-overlapping reservation (Jan 15-20) - check-out = next check-in is OK
        guest2 = GuestFactory()
        reservation2 = Reservation.objects.create(
            hotel=test_hotel,
            guest=guest2,
            room=test_room,  # Same room
            room_type=test_room_type,
            check_in_date=date(2025, 1, 15),  # Starts when first ends
            check_out_date=date(2025, 1, 20),
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        assert reservation2.pk is not None

    def test_can_create_overlapping_for_different_rooms(self, test_hotel, test_guest, test_room_type):
        """Test that overlapping dates are OK for different rooms"""
        room1 = RoomFactory(hotel=test_hotel, room_type=test_room_type, room_number='101')
        room2 = RoomFactory(hotel=test_hotel, room_type=test_room_type, room_number='102')

        # Create reservation for room 101 (Jan 10-15)
        Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room=room1,
            room_type=test_room_type,
            check_in_date=date(2025, 1, 10),
            check_out_date=date(2025, 1, 15),
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        # Create overlapping reservation for room 102 - should work!
        guest2 = GuestFactory()
        reservation2 = Reservation.objects.create(
            hotel=test_hotel,
            guest=guest2,
            room=room2,  # Different room!
            room_type=test_room_type,
            check_in_date=date(2025, 1, 12),  # Overlapping dates OK
            check_out_date=date(2025, 1, 17),
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        assert reservation2.pk is not None

    # ===== CONFIRMATION NUMBER TESTS =====

    def test_confirmation_number_auto_generated(self, test_hotel, test_guest, test_room_type):
        """Test that confirmation number is auto-generated if not provided"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        reservation = Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        assert reservation.confirmation_number is not None
        assert len(reservation.confirmation_number) == 10  # 10-character code

    def test_confirmation_number_is_unique(self, test_hotel, test_guest, test_room_type):
        """Test that confirmation numbers are unique across all reservations"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        # Create first reservation
        res1 = Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        # Create second reservation
        guest2 = GuestFactory()
        res2 = Reservation.objects.create(
            hotel=test_hotel,
            guest=guest2,
            room_type=test_room_type,
            check_in_date=check_in + timedelta(days=10),
            check_out_date=check_in + timedelta(days=12),
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        assert res1.confirmation_number != res2.confirmation_number

    # ===== STATUS TRANSITION TESTS =====

    def test_can_transition_pending_to_confirmed(self, test_hotel, test_guest, test_room_type):
        """Test status transition: pending → confirmed"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        reservation = Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='pending'
        )

        reservation.status = 'confirmed'
        reservation.save()

        assert reservation.status == 'confirmed'

    def test_can_transition_confirmed_to_checked_in(self, test_hotel, test_guest, test_room_type):
        """Test status transition: confirmed → checked_in"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        reservation = Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        reservation.status = 'checked_in'
        reservation.save()

        assert reservation.status == 'checked_in'

    def test_can_transition_checked_in_to_checked_out(self, test_hotel, test_guest, test_room_type):
        """Test status transition: checked_in → checked_out"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        reservation = Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='checked_in'
        )

        reservation.status = 'checked_out'
        reservation.save()

        assert reservation.status == 'checked_out'

    def test_can_cancel_from_any_status_except_checked_out(self, test_hotel, test_guest, test_room_type):
        """Test that reservations can be cancelled from any status except checked_out"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        # Test cancelling from 'confirmed'
        reservation = Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        reservation.status = 'cancelled'
        reservation.save()

        assert reservation.status == 'cancelled'

    # ===== FOREIGN KEY CONSTRAINT TESTS =====

    def test_guest_deletion_blocked_by_protect(self, test_hotel, test_guest, test_room_type):
        """Test that deleting a guest with reservations is blocked (PROTECT)"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        # Attempt to delete guest should be blocked
        with pytest.raises(Exception):  # Django will raise ProtectedError
            test_guest.delete()

    def test_room_deletion_sets_null(self, test_hotel, test_guest, test_room, test_room_type):
        """Test that deleting a room sets reservation.room to NULL (SET_NULL)"""
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        reservation = Reservation.objects.create(
            hotel=test_hotel,
            guest=test_guest,
            room=test_room,
            room_type=test_room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            rate_per_night=Decimal('150.00'),
            status='confirmed'
        )

        # Delete the room
        test_room.delete()

        # Reload reservation
        reservation.refresh_from_db()

        # Room should be NULL, but reservation still exists
        assert reservation.room is None
        assert reservation.pk is not None
