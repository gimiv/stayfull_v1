"""
API ViewSets for Guests app.

Provides REST API endpoints for Guest model.
"""

from rest_framework import viewsets, filters
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend

from .models import Guest
from .serializers import GuestSerializer
from apps.core.permissions import IsOrganizationMemberOrReadOnly


class GuestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing guests.

    Provides CRUD operations for guests with:
    - Filtering by account status
    - Search by email, name
    - Ordering by name, created date
    - Multi-tenancy: Only shows guests from user's organization

    Important: Handles encrypted ID document fields transparently
    """

    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [IsOrganizationMemberOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["loyalty_tier", "vip_status", "nationality"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering_fields = ["first_name", "last_name", "email", "created_at", "loyalty_points"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Filter guests by user's organization"""
        qs = super().get_queryset()

        # Superusers see all
        if self.request.user.is_superuser:
            return qs

        # Staff see only their organization's guests
        if hasattr(self.request.user, "staff_positions") and self.request.user.staff_positions.exists():
            staff = self.request.user.staff_positions.first()
            return qs.filter(organization=staff.organization)

        # Others see nothing
        return qs.none()

    def perform_create(self, serializer):
        """Auto-assign organization when creating guest"""
        if hasattr(self.request.user, "staff_positions") and self.request.user.staff_positions.exists():
            staff = self.request.user.staff_positions.first()
            serializer.save(organization=staff.organization)
        else:
            serializer.save()
