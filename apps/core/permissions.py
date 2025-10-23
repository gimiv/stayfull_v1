"""
Custom permissions for organization-based access control
"""

from rest_framework import permissions


class IsOrganizationMemberOrReadOnly(permissions.BasePermission):
    """
    Permission class for organization-based access control.

    Rules:
    1. Superusers: Full access to everything
    2. Staff users: Can view/edit ONLY their organization's data
    3. Authenticated users: Read-only to public data (if any)
    4. Anonymous users: No access
    """

    def has_permission(self, request, view):
        """Check if user has permission to access this endpoint"""

        # Superusers have full access
        if request.user and request.user.is_superuser:
            return True

        # Staff users have access to their org
        if request.user and request.user.is_authenticated:
            if hasattr(request.user, "staff_positions") and request.user.staff_positions.exists():
                return True

        # Read-only for safe methods (if we want public API later)
        if request.method in permissions.SAFE_METHODS:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        """Check if user can access this specific object"""

        # Superusers can access everything
        if request.user and request.user.is_superuser:
            return True

        # Staff can only access their organization's data
        if request.user and hasattr(request.user, "staff_positions") and request.user.staff_positions.exists():
            staff = request.user.staff_positions.first()
            user_org = staff.organization

            # Direct organization FK
            if hasattr(obj, "organization"):
                return obj.organization == user_org

            # Indirect through hotel
            elif hasattr(obj, "hotel"):
                return obj.hotel.organization == user_org

        return False


class IsSameOrganization(permissions.BasePermission):
    """
    Strict permission: User MUST be from same organization.
    Use for sensitive operations.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if hasattr(request.user, "staff_positions") and request.user.staff_positions.exists():
            staff = request.user.staff_positions.first()
            user_org = staff.organization

            if hasattr(obj, "organization"):
                return obj.organization == user_org
            elif hasattr(obj, "hotel"):
                return obj.hotel.organization == user_org

        return False
