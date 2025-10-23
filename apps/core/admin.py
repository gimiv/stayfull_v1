"""
Admin configuration for core app models
"""

from django.contrib import admin
from apps.core.models import Organization


class OrganizationFilteredAdmin(admin.ModelAdmin):
    """
    Base admin class that filters all querysets by user's organization.

    Filtering Rules:
    1. Superusers (is_superuser=True) see ALL data across ALL organizations
    2. Staff users see ONLY their organization's data
    3. Users without staff association see NOTHING

    All hotel-related admin classes MUST inherit from this.
    """

    def get_queryset(self, request):
        """Filter queryset by user's organization"""
        qs = super().get_queryset(request)

        # Rule 1: Superusers see everything (platform admins)
        if request.user.is_superuser:
            return qs

        # Rule 2: Hotel staff see only their organization's data
        if hasattr(request.user, "staff_positions") and request.user.staff_positions.exists():
            # Get the first staff position's organization
            staff = request.user.staff_positions.first()
            organization = staff.organization

            # Direct organization FK
            if hasattr(self.model, "organization"):
                return qs.filter(organization=organization)

            # Indirect through hotel (e.g., RoomType, Room, Reservation)
            elif hasattr(self.model, "hotel"):
                return qs.filter(hotel__organization=organization)

            # Fallback: no filtering possible
            else:
                return qs

        # Rule 3: No staff association = no access
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter foreign key dropdowns by user's organization"""

        # Skip filtering for superusers
        if request.user.is_superuser:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        # Filter if user has staff association
        if hasattr(request.user, "staff_positions") and request.user.staff_positions.exists():
            staff = request.user.staff_positions.first()
            organization = staff.organization

            # Filter Hotel dropdown
            if db_field.name == "hotel":
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    organization=organization
                )

            # Filter RoomType dropdown
            elif db_field.name == "room_type":
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    hotel__organization=organization
                )

            # Filter Guest dropdown
            elif db_field.name == "guest":
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    organization=organization
                )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_view_permission(self, request, obj=None):
        """Check if user can view this object"""
        if not obj:
            return super().has_view_permission(request, obj)

        # Superusers can view everything
        if request.user.is_superuser:
            return True

        # Check organization match
        if hasattr(request.user, "staff_positions") and request.user.staff_positions.exists():
            staff = request.user.staff_positions.first()
            user_org = staff.organization

            if hasattr(obj, "organization"):
                return obj.organization == user_org
            elif hasattr(obj, "hotel"):
                return obj.hotel.organization == user_org

        return False

    def has_change_permission(self, request, obj=None):
        """Check if user can edit this object"""
        return self.has_view_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Check if user can delete this object"""
        return self.has_view_permission(request, obj)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin interface for Organization model"""

    list_display = ["name", "slug", "type", "contact_email", "hotel_count", "is_active", "created_at"]
    list_filter = ["type", "is_active", "created_at"]
    search_fields = ["name", "slug", "contact_email"]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "type")}),
        ("Contact", {"fields": ("contact_email", "contact_phone")}),
        ("Status & Settings", {"fields": ("is_active", "settings")}),
        (
            "Metadata",
            {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def hotel_count(self, obj):
        """Display number of hotels in this organization"""
        return obj.hotels.count()

    hotel_count.short_description = "Hotels"

    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)

        # Non-superusers only see their own organization
        if not request.user.is_superuser:
            if hasattr(request.user, "staff_positions") and request.user.staff_positions.exists():
                staff = request.user.staff_positions.first()
                return qs.filter(id=staff.organization_id)
            return qs.none()

        return qs
