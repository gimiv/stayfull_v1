"""
Factory classes for generating test data for Guest model
"""

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from datetime import date, timedelta

from apps.guests.models import Guest

fake = Faker()


class GuestFactory(DjangoModelFactory):
    """Factory for creating Guest test instances"""

    class Meta:
        model = Guest

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence(lambda n: f'guest{n}@example.com')
    phone = factory.Faker('phone_number')

    # Date of birth: 25-65 years old (all adults)
    date_of_birth = factory.LazyFunction(
        lambda: date.today() - timedelta(days=365 * fake.random_int(min=25, max=65))
    )
    nationality = 'US'

    # ID Document
    id_document_type = factory.Iterator(['passport', 'drivers_license', 'national_id'])
    id_document_number = factory.Sequence(lambda n: f'DOC{n:08d}')

    # Address
    address = factory.LazyFunction(
        lambda: {
            'street': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'postal_code': fake.postcode(),
            'country': 'US'
        }
    )

    # Preferences
    preferences = factory.LazyFunction(
        lambda: {
            'room_floor': fake.random_element(['high', 'low', 'no_preference']),
            'bed_type': fake.random_element(['king', 'queen', 'twin']),
            'pillow': fake.random_element(['firm', 'soft']),
            'dietary': []
        }
    )

    # Loyalty
    loyalty_tier = factory.Iterator(['bronze', 'silver', 'gold', 'platinum'])
    loyalty_points = factory.Faker('random_int', min=0, max=10000)
    vip_status = factory.Faker('boolean', chance_of_getting_true=20)

    notes = factory.Faker('text', max_nb_chars=200)
