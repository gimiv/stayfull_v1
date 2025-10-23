"""
Django Admin configuration for Guests app models
"""

from django.contrib import admin
from .models import Guest


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    """Admin interface for Guest model"""

    list_display = [
        "full_name",
        "email",
        "phone",
        "nationality",
        "loyalty_tier",
        "loyalty_points",
        "vip_status",
        "created_at",
    ]
    list_filter = ["loyalty_tier", "vip_status", "nationality", "created_at"]
    search_fields = ["first_name", "last_name", "email", "phone"]
    readonly_fields = ["id", "created_at", "updated_at", "full_name"]

    fieldsets = (
        ("Basic Information", {"fields": ("first_name", "last_name", "email", "phone")}),
        ("Personal Details", {"fields": ("date_of_birth", "nationality", "address")}),
        (
            "ID Document (Encrypted)",
            {"fields": ("id_document_type", "id_document_number"), "classes": ("collapse",)},
        ),
        ("Preferences", {"fields": ("preferences",)}),
        ("Loyalty Program", {"fields": ("loyalty_tier", "loyalty_points", "vip_status")}),
        ("Account", {"fields": ("user",)}),
        ("Notes", {"fields": ("notes",), "classes": ("collapse",)}),
        (
            "Metadata",
            {"fields": ("id", "full_name", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    ordering = ["last_name", "first_name"]
