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
        ("independent", "Independent"),
        ("chain", "Chain"),
        ("boutique", "Boutique"),
    ]

    # Basic Info
    name = models.CharField(max_length=200, help_text="Hotel name (3-200 characters)")
    slug = models.SlugField(
        max_length=200, unique=True, help_text="URL-safe identifier (globally unique)"
    )
    brand = models.CharField(
        max_length=100, blank=True, null=True, help_text="Brand name (if part of a chain)"
    )
    type = models.CharField(max_length=20, choices=HOTEL_TYPE_CHOICES, help_text="Hotel type")

    # Location & Contact
    address = models.JSONField(
        help_text="Physical address (street, city, state, postal_code, country)"
    )
    contact = models.JSONField(help_text="Contact information (phone, email, website)")
    timezone = models.CharField(max_length=50, help_text="IANA timezone (e.g., 'America/New_York')")

    # Internationalization
    currency = models.CharField(max_length=3, help_text="ISO 4217 currency code (e.g., 'USD')")
    languages = models.JSONField(
        help_text="Supported languages as ISO 639-1 codes (e.g., ['en', 'es'])"
    )

    # Operational Settings
    check_in_time = models.TimeField(help_text="Default check-in time (e.g., '15:00')")
    check_out_time = models.TimeField(help_text="Default check-out time (e.g., '11:00')")
    total_rooms = models.IntegerField(
        validators=[MinValueValidator(1)], help_text="Total number of rooms in the hotel"
    )

    # Status & Settings
    is_active = models.BooleanField(default=True, help_text="Hotel active status")
    settings = models.JSONField(
        blank=True, null=True, help_text="Additional hotel settings (booking rules, policies, etc.)"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Hotel"
        verbose_name_plural = "Hotels"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
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
            raise ValidationError({"total_rooms": "Total rooms must be greater than 0."})

        # Validate at least one language
        if not self.languages or len(self.languages) == 0:
            raise ValidationError({"languages": "At least one language must be specified."})

        # Validate check_out_time is before check_in_time (earlier in the day)
        if self.check_out_time and self.check_in_time:
            if self.check_out_time >= self.check_in_time:
                raise ValidationError(
                    {
                        "check_out_time": "Check-out time must be earlier in the day than check-in time (e.g., 11:00 < 15:00)."
                    }
                )

        # Validate type is in choices
        valid_types = [choice[0] for choice in self.HOTEL_TYPE_CHOICES]
        if self.type and self.type not in valid_types:
            raise ValidationError({"type": f'Hotel type must be one of: {", ".join(valid_types)}.'})


class RoomType(BaseModel):
    """
    Defines categories of rooms (e.g., Standard, Deluxe, Suite).

    Business Rules:
    - Code must be unique within a hotel
    - max_adults <= max_occupancy (individual limit)
    - max_children <= max_occupancy (individual limit)
    - Flexible occupancy: allows combinations (e.g., 2 adults + 1 child or 1 adult + 2 children)
    - Actual booking validation (total guests <= max_occupancy) happens at reservation time
    - At least one bed must be specified
    """

    # Relationships
    hotel = models.ForeignKey(
        Hotel, on_delete=models.CASCADE, related_name="room_types", help_text="Parent hotel"
    )

    # Basic Info
    name = models.CharField(max_length=100, help_text="Room type name (e.g., 'Deluxe Suite')")
    code = models.CharField(max_length=20, help_text="Short code (e.g., 'DLX', 'STD')")
    description = models.TextField(
        max_length=2000, blank=True, null=True, help_text="Detailed description"
    )

    # Occupancy
    max_occupancy = models.IntegerField(
        validators=[MinValueValidator(1)], help_text="Maximum total guests"
    )
    max_adults = models.IntegerField(validators=[MinValueValidator(1)], help_text="Maximum adults")
    max_children = models.IntegerField(
        validators=[MinValueValidator(0)], help_text="Maximum children"
    )

    # Pricing & Details
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Base nightly rate",
    )
    size_sqm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0.01)],
        help_text="Room size in square meters",
    )

    # Configuration
    bed_configuration = models.JSONField(
        help_text="Bed types and counts (e.g., [{'type': 'king', 'count': 1}])"
    )
    amenities = models.JSONField(help_text="Room amenities (e.g., ['wifi', 'tv', 'mini_fridge'])")
    images = models.JSONField(blank=True, null=True, help_text="Room photos with URLs")

    # Status
    is_active = models.BooleanField(default=True, help_text="Available for booking")
    display_order = models.IntegerField(default=0, help_text="Sort order in listings")

    class Meta:
        ordering = ["hotel", "display_order", "name"]
        verbose_name = "Room Type"
        verbose_name_plural = "Room Types"
        unique_together = [["hotel", "code"]]
        indexes = [
            models.Index(fields=["hotel", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.hotel.name})"

    def clean(self):
        """Validate model fields and business rules."""
        super().clean()

        # Validate occupancy limits (flexible combinations allowed)
        # Example: max_occupancy=3, max_adults=2, max_children=2 is VALID
        # because it allows: 2+1, 1+2, 2+0, 0+2 (all ≤ 3 people)
        # The actual booking validation (2+2=4 rejected) happens at reservation time
        if self.max_adults is not None and self.max_occupancy is not None:
            if self.max_adults > self.max_occupancy:
                raise ValidationError(
                    {
                        "max_adults": f"Max adults ({self.max_adults}) cannot exceed max occupancy ({self.max_occupancy})."
                    }
                )

        if self.max_children is not None and self.max_occupancy is not None:
            if self.max_children > self.max_occupancy:
                raise ValidationError(
                    {
                        "max_children": f"Max children ({self.max_children}) cannot exceed max occupancy ({self.max_occupancy})."
                    }
                )

        # Validate base_price > 0
        if self.base_price is not None and self.base_price <= 0:
            raise ValidationError({"base_price": "Base price must be greater than 0."})

        # Validate at least one bed
        if not self.bed_configuration or len(self.bed_configuration) == 0:
            raise ValidationError({"bed_configuration": "At least one bed must be specified."})


class Room(BaseModel):
    """
    Represents individual room units.

    Business Rules:
    - room_number must be unique within a hotel
    - Cannot be assigned if status != 'available'
    - cleaning_status must be 'clean' or 'inspected' before check-in
    """

    STATUS_CHOICES = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("maintenance", "Maintenance"),
        ("blocked", "Blocked"),
        ("out_of_order", "Out of Order"),
    ]

    CLEANING_STATUS_CHOICES = [
        ("clean", "Clean"),
        ("dirty", "Dirty"),
        ("in_progress", "In Progress"),
        ("inspected", "Inspected"),
    ]

    # Relationships
    hotel = models.ForeignKey(
        Hotel, on_delete=models.CASCADE, related_name="rooms", help_text="Parent hotel"
    )
    room_type = models.ForeignKey(
        RoomType, on_delete=models.PROTECT, related_name="rooms", help_text="Room type/category"
    )

    # Identification
    room_number = models.CharField(
        max_length=20, help_text="Room identifier (e.g., '101', 'A-205')"
    )
    floor = models.IntegerField(
        blank=True, null=True, help_text="Floor number (can be negative for basement)"
    )

    # Status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="available", help_text="Operational status"
    )
    cleaning_status = models.CharField(
        max_length=20,
        choices=CLEANING_STATUS_CHOICES,
        default="clean",
        help_text="Housekeeping status",
    )

    # Additional Info
    features = models.JSONField(blank=True, null=True, help_text="Room-specific features")
    notes = models.TextField(max_length=1000, blank=True, null=True, help_text="Internal notes")
    is_active = models.BooleanField(default=True, help_text="Available for assignment")

    class Meta:
        ordering = ["hotel", "room_number"]
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        unique_together = [["hotel", "room_number"]]
        indexes = [
            models.Index(fields=["hotel", "status"]),
            models.Index(fields=["room_type"]),
        ]

    def __str__(self):
        return f"Room {self.room_number} ({self.hotel.name})"

    def clean(self):
        """Validate model fields and business rules."""
        super().clean()

        # Validate status is in choices
        valid_statuses = [choice[0] for choice in self.STATUS_CHOICES]
        if self.status and self.status not in valid_statuses:
            raise ValidationError(
                {"status": f'Status must be one of: {", ".join(valid_statuses)}.'}
            )

        # Validate cleaning_status is in choices
        valid_cleaning_statuses = [choice[0] for choice in self.CLEANING_STATUS_CHOICES]
        if self.cleaning_status and self.cleaning_status not in valid_cleaning_statuses:
            raise ValidationError(
                {
                    "cleaning_status": f'Cleaning status must be one of: {", ".join(valid_cleaning_statuses)}.'
                }
            )
