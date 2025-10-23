"""
API ViewSets for Staff app.

Provides REST API endpoints for Staff model.
"""

from rest_framework import viewsets, filters
from apps.core.permissions import IsOrganizationMemberOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import Staff
from .serializers import StaffSerializer


class StaffViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing staff members.

    Provides CRUD operations for staff with:
    - Filtering by hotel, role, active status
    - Search by user name, email, employee ID
    - Ordering by role, hired date
    - Multi-tenancy: Filter staff by hotel access
    """

    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsOrganizationMemberOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["hotel", "role", "is_active"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "employee_id"]
    ordering_fields = ["role", "hired_at", "created_at"]
    ordering = ["hotel", "role", "user__last_name"]

    def get_queryset(self):
        """Filter staff by user's organization and query params"""
        queryset = Staff.objects.select_related("user", "hotel", "organization")

        # CRITICAL: Organization-based multi-tenancy filtering
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, "staff_positions") and self.request.user.staff_positions.exists():
                staff = self.request.user.staff_positions.first()
                queryset = queryset.filter(organization=staff.organization)
            else:
                return queryset.none()

        # Additional query param filters
        hotel_id = self.request.query_params.get("hotel")
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)

        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.order_by("organization", "hotel", "role", "user__last_name")
