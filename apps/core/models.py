"""
Core models for Stayfull PMS.
"""

import uuid
from django.db import models


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
