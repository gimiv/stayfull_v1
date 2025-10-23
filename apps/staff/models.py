"""
Staff model for managing hotel staff members and their permissions
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from apps.core.models import BaseModel
from apps.hotels.models import Hotel


class Staff(BaseModel):
    """
    Represents a hotel staff member with role-based permissions.

    Business Rules:
    - User + Hotel combination must be unique (one Staff entry per user per hotel)
    - User can have multiple Staff entries for different hotels
    - Default permissions are automatically set based on role when created
    - Permissions can be customized after creation
    """

    ROLE_CHOICES = [
        ("manager", "Manager"),
        ("receptionist", "Receptionist"),
        ("housekeeping", "Housekeeping"),
        ("maintenance", "Maintenance"),
    ]

    # Foreign Keys
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="staff_positions")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="staff")

    # Role & Department
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100)
    shift = models.CharField(max_length=50)

    # Permissions (JSON)
    permissions = models.JSONField(default=dict, blank=True)

    # Status
    is_active = models.BooleanField(default=True)

    # Employment Dates
    hired_at = models.DateField()
    terminated_at = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        unique_together = [["user", "hotel"]]
        ordering = ["hotel", "role", "user__last_name"]

    def set_default_permissions_for_role(self):
        """
        Set default permissions based on staff role.

        Permission Structure:
        {
            "reservations": {can_create, can_view, can_edit, can_delete, can_cancel},
            "guests": {can_create, can_view, can_edit, can_delete},
            "rooms": {can_create, can_view, can_edit_status, can_delete},
            "reports": {can_view_financial, can_view_operational},
            "settings": {can_edit_hotel, can_manage_staff}
        }
        """
        defaults = {
            "manager": {
                "reservations": {
                    "can_create": True,
                    "can_view": True,
                    "can_edit": True,
                    "can_delete": True,
                    "can_cancel": True,
                },
                "guests": {
                    "can_create": True,
                    "can_view": True,
                    "can_edit": True,
                    "can_delete": True,
                },
                "rooms": {
                    "can_create": True,
                    "can_view": True,
                    "can_edit_status": True,
                    "can_delete": True,
                },
                "reports": {"can_view_financial": True, "can_view_operational": True},
                "settings": {"can_edit_hotel": True, "can_manage_staff": True},
            },
            "receptionist": {
                "reservations": {
                    "can_create": True,
                    "can_view": True,
                    "can_edit": True,
                    "can_delete": False,
                    "can_cancel": True,
                },
                "guests": {
                    "can_create": True,
                    "can_view": True,
                    "can_edit": True,
                    "can_delete": False,
                },
                "rooms": {
                    "can_create": False,
                    "can_view": True,
                    "can_edit_status": True,
                    "can_delete": False,
                },
                "reports": {"can_view_financial": False, "can_view_operational": True},
                "settings": {"can_edit_hotel": False, "can_manage_staff": False},
            },
            "housekeeping": {
                "reservations": {
                    "can_create": False,
                    "can_view": True,
                    "can_edit": False,
                    "can_delete": False,
                    "can_cancel": False,
                },
                "guests": {
                    "can_create": False,
                    "can_view": True,
                    "can_edit": False,
                    "can_delete": False,
                },
                "rooms": {
                    "can_create": False,
                    "can_view": True,
                    "can_edit_status": True,
                    "can_delete": False,
                },
                "reports": {"can_view_financial": False, "can_view_operational": True},
                "settings": {"can_edit_hotel": False, "can_manage_staff": False},
            },
            "maintenance": {
                "reservations": {
                    "can_create": False,
                    "can_view": True,
                    "can_edit": False,
                    "can_delete": False,
                    "can_cancel": False,
                },
                "guests": {
                    "can_create": False,
                    "can_view": False,
                    "can_edit": False,
                    "can_delete": False,
                },
                "rooms": {
                    "can_create": False,
                    "can_view": True,
                    "can_edit_status": True,
                    "can_delete": False,
                },
                "reports": {"can_view_financial": False, "can_view_operational": True},
                "settings": {"can_edit_hotel": False, "can_manage_staff": False},
            },
        }
        self.permissions = defaults.get(self.role, {})

    def save(self, *args, **kwargs):
        """Override save to set default permissions if not already set"""
        if not self.permissions:
            self.set_default_permissions_for_role()
        super().save(*args, **kwargs)

    @property
    def is_manager(self):
        """Return True if staff member is a manager"""
        return self.role == "manager"

    def __str__(self):
        """Return string representation of staff member"""
        return f"{self.user.get_full_name()} - {self.hotel.name} ({self.role})"
