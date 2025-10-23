"""
Factory classes for generating test data for Hotels app models.

Uses factory_boy and Faker for realistic test data generation.
"""

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from apps.hotels.models import Hotel, RoomType, Room

fake = Faker()


class HotelFactory(DjangoModelFactory):
    """Factory for creating Hotel test instances"""

    class Meta:
        model = Hotel

    name = factory.Sequence(lambda n: f"Test Hotel {n}")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    brand = factory.Faker('company')
    type = factory.Iterator(['independent', 'chain', 'boutique'])

    address = factory.LazyFunction(
        lambda: {
            'street': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'postal_code': fake.postcode(),
            'country': 'US'
        }
    )

    contact = factory.LazyFunction(
        lambda: {
            'phone': fake.phone_number(),
            'email': fake.company_email(),
            'website': fake.url()
        }
    )

    timezone = 'America/New_York'
    currency = 'USD'
    languages = ['en', 'es']

    check_in_time = '15:00'
    check_out_time = '11:00'

    total_rooms = factory.Faker('random_int', min=10, max=500)
    is_active = True
    settings = factory.LazyFunction(
        lambda: {
            'booking_rules': {
                'min_stay': 1,
                'max_stay': 30
            },
            'policies': {
                'pets_allowed': fake.boolean(),
                'smoking_allowed': False
            }
        }
    )


class RoomTypeFactory(DjangoModelFactory):
    """Factory for creating RoomType test instances"""

    class Meta:
        model = RoomType

    hotel = factory.SubFactory(HotelFactory)
    name = factory.Iterator(['Standard Room', 'Deluxe Room', 'Junior Suite', 'Executive Suite'])
    code = factory.Sequence(lambda n: f"RT{n:03d}")
    description = factory.Faker('text', max_nb_chars=200)

    max_occupancy = 4
    max_adults = 2
    max_children = 2

    base_price = factory.Faker('pydecimal', left_digits=3, right_digits=2, min_value=50, max_value=500)
    size_sqm = factory.Faker('pydecimal', left_digits=2, right_digits=2, min_value=20, max_value=80)

    bed_configuration = factory.LazyFunction(
        lambda: [
            {'type': 'queen', 'count': 1}
        ]
    )

    amenities = factory.LazyFunction(
        lambda: [
            'wifi', 'tv', 'mini_fridge', 'coffee_maker',
            'air_conditioning', 'safe', 'work_desk'
        ]
    )

    images = factory.LazyFunction(
        lambda: [
            {'url': fake.image_url(), 'caption': 'Room view'},
            {'url': fake.image_url(), 'caption': 'Bathroom'}
        ]
    )

    is_active = True
    display_order = factory.Sequence(lambda n: n)


class RoomFactory(DjangoModelFactory):
    """Factory for creating Room test instances"""

    class Meta:
        model = Room

    hotel = factory.SubFactory(HotelFactory)
    room_type = factory.SubFactory(RoomTypeFactory, hotel=factory.SelfAttribute('..hotel'))
    room_number = factory.Sequence(lambda n: f"{100 + n}")
    floor = factory.Faker('random_int', min=1, max=10)

    status = 'available'
    cleaning_status = 'clean'

    features = factory.LazyFunction(
        lambda: {
            'view': fake.random_element(['ocean', 'city', 'garden', 'pool']),
            'accessible': fake.boolean()
        }
    )

    notes = factory.Faker('text', max_nb_chars=100)
    is_active = True
