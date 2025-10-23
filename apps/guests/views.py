"""
API ViewSets for Guests app.

Provides REST API endpoints for Guest model.
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend

from .models import Guest
from .serializers import GuestSerializer


class GuestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing guests.

    Provides CRUD operations for guests with:
    - Filtering by account status
    - Search by email, name
    - Ordering by name, created date

    Important: Handles encrypted ID document fields transparently
    """

    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["loyalty_tier", "vip_status", "nationality"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering_fields = ["first_name", "last_name", "email", "created_at", "loyalty_points"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Return all guests ordered by creation date.
        Support filtering via query params.
        """
        return Guest.objects.all().order_by("-created_at")
