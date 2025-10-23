"""
Django Admin configuration for Reservations app models
"""

from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Admin interface for Reservation model"""

    list_display = [
        "confirmation_number",
        "guest",
        "hotel",
        "check_in_date",
        "check_out_date",
        "nights",
        "status",
        "total_amount",
    ]
    list_filter = ["status", "source", "hotel", "check_in_date"]
    search_fields = ["confirmation_number", "guest__email", "guest__first_name", "guest__last_name"]
    readonly_fields = [
        "id",
        "confirmation_number",
        "nights",
        "total_room_charges",
        "total_amount",
        "booked_at",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            "Reservation Details",
            {"fields": ("confirmation_number", "hotel", "guest", "room_type", "room", "status")},
        ),
        ("Dates", {"fields": ("check_in_date", "check_out_date", "nights")}),
        ("Guests", {"fields": ("adults", "children")}),
        (
            "Financial",
            {
                "fields": (
                    "rate_per_night",
                    "total_room_charges",
                    "taxes",
                    "fees",
                    "extras",
                    "discounts",
                    "total_amount",
                    "deposit_paid",
                )
            },
        ),
        ("Source & Channel", {"fields": ("source", "channel")}),
        ("Notes & Requests", {"fields": ("special_requests", "notes"), "classes": ("collapse",)}),
        (
            "Timestamps",
            {
                "fields": (
                    "booked_at",
                    "checked_in_at",
                    "checked_out_at",
                    "cancelled_at",
                    "cancellation_reason",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Metadata", {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    ordering = ["-check_in_date", "-created_at"]

    def get_queryset(self, request):
        """Optimize queryset with select_related for performance"""
        queryset = super().get_queryset(request)
        return queryset.select_related("guest", "hotel", "room", "room_type")
