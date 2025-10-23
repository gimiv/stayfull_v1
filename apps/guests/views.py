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
    filterset_fields = ['account_status', 'nationality', 'language_preference']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['first_name', 'last_name', 'email', 'created_at', 'loyalty_points']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filter guests by active status by default.
        Support additional filtering via query params.
        """
        queryset = Guest.objects.all().order_by('-created_at')

        # Optional: Filter to only active guests by default
        # Can override with ?account_status=inactive
        status = self.request.query_params.get('account_status')
        if status is None and self.action == 'list':
            # Default to active guests for list view
            queryset = queryset.filter(account_status='active')

        return queryset
