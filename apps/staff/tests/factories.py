"""
Factory classes for generating test data for Staff model
"""

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from faker import Faker
from datetime import date, timedelta

from apps.staff.models import Staff
from apps.hotels.tests.factories import HotelFactory

fake = Faker()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances"""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "defaultpass123")


class StaffFactory(DjangoModelFactory):
    """Factory for creating Staff test instances"""

    class Meta:
        model = Staff

    user = factory.SubFactory(UserFactory)
    hotel = factory.SubFactory(HotelFactory)
    organization = factory.LazyAttribute(lambda obj: obj.hotel.organization if obj.hotel else None)
    role = factory.Iterator(["manager", "receptionist", "housekeeping", "maintenance"])
    department = factory.LazyAttribute(
        lambda obj: {
            "manager": "Management",
            "receptionist": "Front Desk",
            "housekeeping": "Housekeeping",
            "maintenance": "Maintenance",
        }.get(obj.role, "General")
    )
    shift = factory.Iterator(["morning", "afternoon", "evening", "night"])
    is_active = True
    hired_at = factory.LazyFunction(
        lambda: date.today() - timedelta(days=fake.random_int(min=30, max=1825))
    )  # Hired 1 month to 5 years ago
    terminated_at = None

    # Note: permissions will be set automatically by the model's save() method
    # based on the role, so we don't need to set it here
