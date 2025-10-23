"""
Models for Hotels app: Hotel, RoomType, Room
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel


class Hotel(BaseModel):
    """
    Represents a hotel property in the system.

    Business Rules:
    - Slug must be globally unique
    - Check-out time must be before check-in time (e.g., 11am checkout, 3pm checkin)
    - At least one language must be specified
    - Total rooms must be > 0
    """

    HOTEL_TYPE_CHOICES = [
        ('independent', 'Independent'),
        ('chain', 'Chain'),
        ('boutique', 'Boutique'),
    ]

    # Basic Info
    name = models.CharField(
        max_length=200,
        help_text="Hotel name (3-200 characters)"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL-safe identifier (globally unique)"
    )
    brand = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Brand name (if part of a chain)"
    )
    type = models.CharField(
        max_length=20,
        choices=HOTEL_TYPE_CHOICES,
        help_text="Hotel type"
    )

    # Location & Contact
    address = models.JSONField(
        help_text="Physical address (street, city, state, postal_code, country)"
    )
    contact = models.JSONField(
        help_text="Contact information (phone, email, website)"
    )
    timezone = models.CharField(
        max_length=50,
        help_text="IANA timezone (e.g., 'America/New_York')"
    )

    # Internationalization
    currency = models.CharField(
        max_length=3,
        help_text="ISO 4217 currency code (e.g., 'USD')"
    )
    languages = models.JSONField(
        help_text="Supported languages as ISO 639-1 codes (e.g., ['en', 'es'])"
    )

    # Operational Settings
    check_in_time = models.TimeField(
        help_text="Default check-in time (e.g., '15:00')"
    )
    check_out_time = models.TimeField(
        help_text="Default check-out time (e.g., '11:00')"
    )
    total_rooms = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total number of rooms in the hotel"
    )

    # Status & Settings
    is_active = models.BooleanField(
        default=True,
        help_text="Hotel active status"
    )
    settings = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional hotel settings (booking rules, policies, etc.)"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Hotel'
        verbose_name_plural = 'Hotels'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """
        Validate model fields and business rules.
        """
        super().clean()

        # Validate total_rooms > 0
        if self.total_rooms is not None and self.total_rooms <= 0:
            raise ValidationError({
                'total_rooms': 'Total rooms must be greater than 0.'
            })

        # Validate at least one language
        if not self.languages or len(self.languages) == 0:
            raise ValidationError({
                'languages': 'At least one language must be specified.'
            })

        # Validate check_out_time is before check_in_time (earlier in the day)
        if self.check_out_time and self.check_in_time:
            if self.check_out_time >= self.check_in_time:
                raise ValidationError({
                    'check_out_time': 'Check-out time must be earlier in the day than check-in time (e.g., 11:00 < 15:00).'
                })

        # Validate type is in choices
        valid_types = [choice[0] for choice in self.HOTEL_TYPE_CHOICES]
        if self.type and self.type not in valid_types:
            raise ValidationError({
                'type': f'Hotel type must be one of: {", ".join(valid_types)}.'
            })


class RoomType(BaseModel):
    """
    Defines categories of rooms (e.g., Standard, Deluxe, Suite).

    Business Rules:
    - Code must be unique within a hotel
    - max_adults + max_children must equal max_occupancy
    - At least one bed must be specified
    """
    # Will implement in next step
    pass


class Room(BaseModel):
    """
    Represents individual room units.

    Business Rules:
    - room_number must be unique within a hotel
    - Cannot be assigned if status != 'available'
    - cleaning_status must be 'clean' or 'inspected' before check-in
    """
    # Will implement in next step
    pass
