"""
API ViewSets for Reservations app.

Provides REST API endpoints for Reservation model with custom actions.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.permissions import IsOrganizationMemberOrReadOnly
from django.db import models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from .models import Reservation
from .serializers import ReservationSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reservations.

    Provides CRUD operations for reservations with:
    - Filtering by hotel, status, dates, guest
    - Search by confirmation number, guest name
    - Ordering by check-in date, created date
    - Custom actions: check_availability, check_in, check_out, cancel
    """

    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsOrganizationMemberOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["hotel", "status", "source", "guest", "room_type"]
    search_fields = ["confirmation_number", "guest__first_name", "guest__last_name", "guest__email"]
    ordering_fields = ["check_in_date", "check_out_date", "created_at", "total_amount"]
    ordering = ["-check_in_date"]

    def get_queryset(self):
        """Filter reservations by user's organization and query params"""
        queryset = Reservation.objects.select_related("hotel", "guest", "room", "room_type")

        # CRITICAL: Organization-based multi-tenancy filtering
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, "staff_positions") and self.request.user.staff_positions.exists():
                staff = self.request.user.staff_positions.first()
                queryset = queryset.filter(hotel__organization=staff.organization)
            else:
                return queryset.none()

        # Additional query param filters
        hotel_id = self.request.query_params.get("hotel")
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        check_in_from = self.request.query_params.get("check_in_from")
        check_in_to = self.request.query_params.get("check_in_to")
        if check_in_from:
            queryset = queryset.filter(check_in_date__gte=check_in_from)
        if check_in_to:
            queryset = queryset.filter(check_in_date__lte=check_in_to)

        guest_id = self.request.query_params.get("guest")
        if guest_id:
            queryset = queryset.filter(guest_id=guest_id)

        return queryset.order_by("-check_in_date")

    @action(detail=False, methods=["post"])
    def check_availability(self, request):
        """
        Check room availability for given dates.

        POST /api/v1/reservations/check_availability/

        Body:
        {
            "hotel_id": "uuid",
            "room_type_id": "uuid",
            "check_in_date": "2025-11-01",
            "check_out_date": "2025-11-05"
        }

        Returns:
        {
            "available": true,
            "count": 5,
            "rooms": [...]
        }
        """
        hotel_id = request.data.get("hotel_id")
        room_type_id = request.data.get("room_type_id")
        check_in = request.data.get("check_in_date")
        check_out = request.data.get("check_out_date")

        # Validate required fields
        if not all([hotel_id, room_type_id, check_in, check_out]):
            return Response(
                {"error": "hotel_id, room_type_id, check_in_date, and check_out_date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find overlapping reservations
        overlapping = Reservation.objects.filter(
            hotel_id=hotel_id,
            room_type_id=room_type_id,
            status__in=["confirmed", "checked_in"],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in,
        ).values_list("room_id", flat=True)

        # Find available rooms
        from apps.hotels.models import Room

        available_rooms = Room.objects.filter(
            hotel_id=hotel_id, room_type_id=room_type_id, status="available", is_active=True
        ).exclude(id__in=overlapping)

        from apps.hotels.serializers import RoomSerializer

        return Response(
            {
                "available": available_rooms.exists(),
                "count": available_rooms.count(),
                "rooms": RoomSerializer(available_rooms, many=True).data,
            }
        )

    @action(detail=True, methods=["post"])
    def check_in(self, request, pk=None):
        """
        Check in a reservation.

        POST /api/v1/reservations/{id}/check_in/

        Body (optional):
        {
            "room_id": "uuid"  # Assign specific room, or auto-assign
        }

        Returns: Updated reservation with status='checked_in'
        """
        reservation = self.get_object()

        if reservation.status != "confirmed":
            return Response(
                {"error": "Only confirmed reservations can be checked in"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Assign room if provided
        room_id = request.data.get("room_id")
        if room_id:
            from apps.hotels.models import Room

            try:
                room = Room.objects.get(id=room_id, room_type=reservation.room_type)
                reservation.room = room
            except Room.DoesNotExist:
                return Response(
                    {"error": "Invalid room for this room type"}, status=status.HTTP_400_BAD_REQUEST
                )

        # Update status
        reservation.status = "checked_in"
        reservation.checked_in_at = timezone.now()
        reservation.save()

        serializer = self.get_serializer(reservation)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def check_out(self, request, pk=None):
        """
        Check out a reservation.

        POST /api/v1/reservations/{id}/check_out/

        Returns: Updated reservation with status='checked_out'
        """
        reservation = self.get_object()

        if reservation.status != "checked_in":
            return Response(
                {"error": "Only checked-in reservations can be checked out"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update status
        reservation.status = "checked_out"
        reservation.checked_out_at = timezone.now()
        reservation.save()

        serializer = self.get_serializer(reservation)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        Cancel a reservation.

        POST /api/v1/reservations/{id}/cancel/

        Body:
        {
            "reason": "Guest requested cancellation"
        }

        Returns: Updated reservation with status='cancelled'
        """
        reservation = self.get_object()

        if reservation.status == "checked_out":
            return Response(
                {"error": "Cannot cancel checked-out reservation"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update status
        reservation.status = "cancelled"
        reservation.cancelled_at = timezone.now()
        reservation.cancellation_reason = request.data.get("reason", "")
        reservation.save()

        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
