"""
Django REST Framework serializers for Staff app
Handles serialization/deserialization of Staff model with nested user/hotel data
"""

from rest_framework import serializers
from .models import Staff


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for Staff model"""

    # Nested user info (read-only)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    hotel_name = serializers.CharField(source="hotel.name", read_only=True)

    # Computed field
    is_manager = serializers.BooleanField(read_only=True)

    class Meta:
        model = Staff
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "hotel",
            "hotel_name",
            "role",
            "department",
            "shift",
            "permissions",
            "is_active",
            "is_manager",
            "hired_at",
            "terminated_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user_email",
            "user_name",
            "hotel_name",
            "is_manager",
            "created_at",
            "updated_at",
        ]
