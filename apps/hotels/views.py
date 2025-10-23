"""
API ViewSets for Hotels app.

Provides REST API endpoints for Hotel, RoomType, and Room models.
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Hotel, RoomType, Room
from .serializers import HotelSerializer, RoomTypeSerializer, RoomSerializer


class HotelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing hotels.

    Provides CRUD operations for hotels with:
    - Filtering by type, active status
    - Search by name, slug
    - Ordering by name, created date
    """
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_active']
    search_fields = ['name', 'slug', 'brand']
    ordering_fields = ['name', 'created_at', 'total_rooms']
    ordering = ['name']

    def get_queryset(self):
        """
        Optimize queryset with select_related for performance.

        In future: Add multi-tenancy filtering based on user's hotel access.
        """
        return Hotel.objects.all().order_by('name')

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get hotel statistics.

        Returns:
        - Total rooms
        - Active rooms
        - Total room types
        - Occupancy summary
        """
        hotel = self.get_object()
        active_rooms_count = hotel.rooms.filter(is_active=True).count()
        return Response({
            'hotel_id': str(hotel.id),
            'hotel_name': hotel.name,
            'total_rooms': hotel.total_rooms,
            'active_rooms': active_rooms_count,
            'total_room_types': hotel.room_types.count(),
            'inactive_rooms': hotel.total_rooms - active_rooms_count,
        })


class RoomTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing room types.

    Provides CRUD operations for room types with:
    - Filtering by hotel, active status
    - Search by name, code
    - Ordering by name, base price
    """
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hotel', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'base_price', 'max_occupancy', 'created_at']
    ordering = ['hotel', 'name']

    def get_queryset(self):
        """
        Optimize queryset with select_related for hotel.
        """
        return RoomType.objects.select_related('hotel').order_by('hotel', 'name')

    @action(detail=True, methods=['get'])
    def available_rooms(self, request, pk=None):
        """
        Get count of available rooms for this room type.

        Returns rooms with status 'available' or 'clean'.
        """
        room_type = self.get_object()
        available_count = room_type.rooms.filter(
            status__in=['available', 'clean'],
            is_active=True
        ).count()

        return Response({
            'room_type_id': str(room_type.id),
            'room_type_name': room_type.name,
            'total_rooms': room_type.rooms.count(),
            'available_rooms': available_count,
        })


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing individual rooms.

    Provides CRUD operations for rooms with:
    - Filtering by hotel, room type, status, floor
    - Search by room number
    - Ordering by room number, floor
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hotel', 'room_type', 'status', 'cleaning_status', 'floor', 'is_active']
    search_fields = ['room_number']
    ordering_fields = ['room_number', 'floor', 'created_at']
    ordering = ['room_number']

    def get_queryset(self):
        """
        Optimize queryset with select_related for hotel and room_type.
        """
        return Room.objects.select_related('hotel', 'room_type').order_by('room_number')

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update room status.

        Accepts: {"status": "available|occupied|maintenance|out_of_order"}
        """
        room = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Room.STATUS_CHOICES):
            return Response(
                {'error': f'Invalid status. Must be one of: {", ".join(dict(Room.STATUS_CHOICES).keys())}'},
                status=400
            )

        room.status = new_status
        room.save()

        serializer = self.get_serializer(room)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_cleaning_status(self, request, pk=None):
        """
        Update room cleaning status.

        Accepts: {"cleaning_status": "clean|dirty|cleaning|inspecting"}
        """
        room = self.get_object()
        new_cleaning_status = request.data.get('cleaning_status')

        if new_cleaning_status not in dict(Room.CLEANING_STATUS_CHOICES):
            return Response(
                {'error': f'Invalid cleaning status. Must be one of: {", ".join(dict(Room.CLEANING_STATUS_CHOICES).keys())}'},
                status=400
            )

        room.cleaning_status = new_cleaning_status
        room.save()

        serializer = self.get_serializer(room)
        return Response(serializer.data)
