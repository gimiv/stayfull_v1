"""
Django app configuration for Staff app
"""

from django.apps import AppConfig


class StaffConfig(AppConfig):
    """Configuration for Staff app"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.staff"
    verbose_name = "Staff Management"
