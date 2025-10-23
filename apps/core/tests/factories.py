"""
Test factories for core models
"""

import factory
from apps.core.models import Organization


class OrganizationFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Organization instances"""

    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: f"Test Organization {n}")
    slug = factory.Sequence(lambda n: f"test-org-{n}")
    type = "independent"
    contact_email = factory.Sequence(lambda n: f"contact{n}@testorg.com")
    contact_phone = "+1-555-0100"
    is_active = True
    settings = {}
