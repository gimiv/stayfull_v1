"""
Models for Guests app: Guest
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import date, timedelta

from apps.core.models import BaseModel
from apps.core.fields import EncryptedCharField


class Guest(BaseModel):
    """
    Represents a hotel guest.

    Business Rules:
    - Email must be unique within organization (not globally)
    - id_document_number must be encrypted at rest
    - Guest must be 18+ years old for primary guest on reservation
    - Loyalty points cannot be negative
    """

    ID_DOCUMENT_TYPE_CHOICES = [
        ("passport", "Passport"),
        ("drivers_license", "Driver's License"),
        ("national_id", "National ID"),
        ("other", "Other"),
    ]

    LOYALTY_TIER_CHOICES = [
        ("bronze", "Bronze"),
        ("silver", "Silver"),
        ("gold", "Gold"),
        ("platinum", "Platinum"),
    ]

    # Organization relationship (REQUIRED for multi-tenancy)
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.PROTECT,
        related_name="guests",
        null=True,  # Temporarily nullable for migration
        blank=True,
        help_text="Organization this guest belongs to",
    )

    # Optional link to User account
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="guest_profile",
        help_text="Linked user account (if registered)",
    )

    # Basic Information
    first_name = models.CharField(max_length=100, help_text="First name (1-100 characters)")
    last_name = models.CharField(max_length=100, help_text="Last name (1-100 characters)")
    email = models.EmailField(
        max_length=255, help_text="Email address (unique within organization)"
    )
    phone = models.CharField(
        max_length=20, help_text="Phone number with country code (e.g., +1-555-0123)"
    )

    # Personal Details
    date_of_birth = models.DateField(
        null=True, blank=True, help_text="Date of birth (must be 18+ for primary guest)"
    )
    nationality = models.CharField(
        max_length=2, null=True, blank=True, help_text="ISO 3166-1 alpha-2 country code"
    )

    # ID Document (Encrypted)
    id_document_type = models.CharField(
        max_length=20,
        choices=ID_DOCUMENT_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="Type of ID document",
    )
    id_document_number = EncryptedCharField(
        max_length=255,  # Encrypted data is longer than plaintext
        blank=True,
        null=True,
        help_text="ID document number (encrypted at rest)",
    )

    # Address & Preferences
    address = models.JSONField(
        null=True, blank=True, help_text="Home address (street, city, state, postal_code, country)"
    )
    preferences = models.JSONField(
        null=True, blank=True, help_text="Guest preferences (room floor, bed type, dietary, etc.)"
    )

    # Loyalty Program
    loyalty_tier = models.CharField(
        max_length=20,
        choices=LOYALTY_TIER_CHOICES,
        null=True,
        blank=True,
        help_text="Loyalty program tier",
    )
    loyalty_points = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Loyalty points balance (cannot be negative)",
    )

    # Status
    vip_status = models.BooleanField(default=False, help_text="VIP guest flag")

    # Staff Notes
    notes = models.TextField(
        max_length=2000,
        null=True,
        blank=True,
        help_text="Staff notes about guest (max 2000 characters)",
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "Guest"
        verbose_name_plural = "Guests"
        # Email unique within organization (not globally)
        unique_together = [["organization", "email"]]
        indexes = [
            models.Index(fields=["organization", "email"]),
            models.Index(fields=["organization", "loyalty_tier"]),
            models.Index(fields=["last_name", "first_name"]),
        ]

    @property
    def full_name(self):
        """Return guest's full name"""
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name

    def clean(self):
        """Validate model fields and business rules"""
        super().clean()

        # Validate age (must be 18+)
        if self.date_of_birth:
            today = date.today()
            age = (
                today.year
                - self.date_of_birth.year
                - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            )
            if age < 18:
                raise ValidationError(
                    {
                        "date_of_birth": "Guest must be at least 18 years old for primary guest on reservation."
                    }
                )

        # Validate loyalty points cannot be negative
        if self.loyalty_points is not None and self.loyalty_points < 0:
            raise ValidationError({"loyalty_points": "Loyalty points cannot be negative."})

        # Validate ID document type if number is provided
        if self.id_document_number and not self.id_document_type:
            raise ValidationError(
                {"id_document_type": "Document type is required when document number is provided."}
            )
