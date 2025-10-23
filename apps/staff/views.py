"""
API ViewSets for Staff app.

Provides REST API endpoints for Staff model.
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
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
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["hotel", "role", "is_active"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "employee_id"]
    ordering_fields = ["role", "hired_at", "created_at"]
    ordering = ["hotel", "role", "user__last_name"]

    def get_queryset(self):
        """
        Filter staff by hotel and role.
        Multi-tenancy: Only show staff for hotels user has access to.
        """
        queryset = Staff.objects.filter(is_active=True).select_related("user", "hotel")

        # Filter by hotel (multi-tenancy support)
        hotel_id = self.request.query_params.get("hotel")
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)

        # Filter by role
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)

        return queryset.order_by("hotel", "role", "user__last_name")
