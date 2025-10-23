"""
Django Admin configuration for Staff app models
"""

from django.contrib import admin
from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    """Admin interface for Staff model"""

    list_display = [
        "get_staff_name",
        "user",
        "hotel",
        "role",
        "department",
        "is_active",
        "hired_at",
    ]
    list_filter = ["role", "hotel", "is_active", "department"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "hotel__name"]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        ("Staff Member", {"fields": ("user", "hotel")}),
        ("Role & Department", {"fields": ("role", "department", "shift")}),
        (
            "Permissions",
            {
                "fields": ("permissions",),
                "description": "Default permissions are set automatically based on role. You can customize them here.",
            },
        ),
        ("Employment Status", {"fields": ("is_active", "hired_at", "terminated_at")}),
        ("Metadata", {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    ordering = ["hotel", "role", "user__last_name"]

    def get_staff_name(self, obj):
        """Display staff member's full name"""
        return obj.user.get_full_name() or obj.user.username

    get_staff_name.short_description = "Staff Name"
    get_staff_name.admin_order_field = "user__last_name"
