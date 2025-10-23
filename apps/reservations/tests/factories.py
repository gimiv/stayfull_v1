"""
Factory classes for generating test data for Reservation model
"""

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from datetime import date, timedelta
from decimal import Decimal
import random

from apps.reservations.models import Reservation
from apps.hotels.tests.factories import HotelFactory, RoomTypeFactory, RoomFactory
from apps.guests.tests.factories import GuestFactory

fake = Faker()


class ReservationFactory(DjangoModelFactory):
    """Factory for creating Reservation test instances"""

    class Meta:
        model = Reservation

    hotel = factory.SubFactory(HotelFactory)
    guest = factory.SubFactory(GuestFactory)
    room_type = factory.SubFactory(
        RoomTypeFactory,
        hotel=factory.SelfAttribute('..hotel')  # Same hotel as reservation
    )
    room = None  # Initially unassigned (will be assigned later)

    # Dates: Future check-in (1-30 days from now), 1-7 nights stay
    check_in_date = factory.LazyFunction(
        lambda: date.today() + timedelta(days=random.randint(1, 30))
    )
    check_out_date = factory.LazyAttribute(
        lambda obj: obj.check_in_date + timedelta(days=random.randint(1, 7))
    )

    # Guests
    adults = 2
    children = 0

    # Status and source
    status = 'confirmed'
    source = factory.Iterator(['direct', 'ota', 'gds', 'walkin', 'corporate'])
    channel = factory.LazyAttribute(
        lambda obj: {
            'ota': 'Booking.com',
            'gds': 'Amadeus',
            'corporate': 'Acme Corp'
        }.get(obj.source, '')
    )

    # Financial
    rate_per_night = Decimal('199.00')
    taxes = Decimal('25.00')
    fees = Decimal('10.00')
    extras = Decimal('0.00')
    discounts = Decimal('0.00')
    deposit_paid = Decimal('0.00')

    # Notes (auto-calculated fields will be set by model's save() method)
    special_requests = ''
    notes = ''

    # Note: nights, total_room_charges, and total_amount are auto-calculated
    # by the model's save() method, so we don't set them here
