"""
Django REST Framework serializers for Hotels app
Handles serialization/deserialization of Hotel, RoomType, and Room models
"""

from rest_framework import serializers
from .models import Hotel, RoomType, Room


class HotelSerializer(serializers.ModelSerializer):
    """Serializer for Hotel model"""

    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'slug', 'type', 'brand',
            'address', 'contact', 'timezone', 'currency', 'languages',
            'check_in_time', 'check_out_time', 'total_rooms',
            'settings', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate hotel data including check-in/check-out times.
        Check-out time must be before check-in time (assumes next day checkout).
        """
        check_in_time = data.get('check_in_time')
        check_out_time = data.get('check_out_time')

        if check_in_time and check_out_time and check_out_time >= check_in_time:
            raise serializers.ValidationError({
                'check_out_time': "Check-out time must be before check-in time (checkout is next day)"
            })
        return data


class RoomTypeSerializer(serializers.ModelSerializer):
    """Serializer for RoomType model"""

    # Nested hotel name (read-only for display)
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)

    class Meta:
        model = RoomType
        fields = [
            'id', 'hotel', 'hotel_name', 'code', 'name', 'description',
            'max_occupancy', 'max_adults', 'max_children',
            'bed_configuration', 'size_sqm',
            'base_price', 'amenities', 'images', 'is_active', 'display_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'hotel_name']

    def validate(self, data):
        """Validate that max_adults + max_children equals max_occupancy"""
        max_adults = data.get('max_adults')
        max_children = data.get('max_children')
        max_occupancy = data.get('max_occupancy')

        # Only validate if all three fields are provided
        if max_adults is not None and max_children is not None and max_occupancy is not None:
            if (max_adults + max_children) != max_occupancy:
                raise serializers.ValidationError(
                    "max_adults + max_children must equal max_occupancy"
                )
        return data


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room model"""

    # Nested read-only fields for display
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'hotel', 'hotel_name', 'room_type', 'room_type_name',
            'room_number', 'floor', 'status', 'cleaning_status',
            'features', 'notes', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'hotel_name', 'room_type_name']
