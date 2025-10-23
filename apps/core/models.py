"""
Core models for Stayfull PMS.
"""

import uuid
from django.db import models
from django.core.exceptions import ValidationError


class BaseModel(models.Model):
    """
    Abstract base model with UUID primary key and timestamps.

    All models in the Stayfull PMS inherit from this base model
    to ensure consistent ID generation and timestamp tracking.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, help_text="Unique identifier (UUID)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class Organization(BaseModel):
    """
    Represents a hotel owner/operator entity (tenant boundary).

    All hotels, guests, and staff belong to an organization.
    This is the primary isolation boundary in the system.

    Examples:
    - Independent hotel: "Downtown Inn"
    - Hotel chain: "Marriott International"
    - Hotel group: "Smith Hospitality Group"
    """

    TYPE_CHOICES = [
        ("independent", "Independent Hotel"),
        ("chain", "Hotel Chain/Group"),
        ("franchise", "Franchise Group"),
    ]

    # Basic Info
    name = models.CharField(
        max_length=200, help_text="Organization name (e.g., 'Smith Hotel Group')"
    )
    slug = models.SlugField(
        max_length=200, unique=True, help_text="URL-safe identifier (globally unique)"
    )

    # Type
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="independent",
        help_text="Organization type",
    )

    # Contact (for billing/support)
    contact_email = models.EmailField(
        help_text="Primary contact email for this organization"
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Primary contact phone",
    )

    # Status
    is_active = models.BooleanField(
        default=True, help_text="Organization active status"
    )

    # Settings
    settings = models.JSONField(
        blank=True,
        null=True,
        help_text="Organization-level settings and preferences",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Validate model fields"""
        super().clean()

        # Validate type
        valid_types = [choice[0] for choice in self.TYPE_CHOICES]
        if self.type not in valid_types:
            raise ValidationError(
                {"type": f'Type must be one of: {", ".join(valid_types)}'}
            )
