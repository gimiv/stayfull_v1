"""
Django REST Framework serializers for Reservations app
Handles complex reservation serialization with nested guest/hotel/room data
"""

from rest_framework import serializers
from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for Reservation model"""

    # Nested read-only fields for rich responses
    guest_name = serializers.CharField(source="guest.full_name", read_only=True)
    guest_email = serializers.EmailField(source="guest.email", read_only=True)
    hotel_name = serializers.CharField(source="hotel.name", read_only=True)
    room_type_name = serializers.CharField(source="room_type.name", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True, allow_null=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "confirmation_number",
            "hotel",
            "hotel_name",
            "guest",
            "guest_name",
            "guest_email",
            "room",
            "room_number",
            "room_type",
            "room_type_name",
            "check_in_date",
            "check_out_date",
            "nights",
            "adults",
            "children",
            "status",
            "source",
            "channel",
            "rate_per_night",
            "total_room_charges",
            "taxes",
            "fees",
            "extras",
            "discounts",
            "total_amount",
            "deposit_paid",
            "special_requests",
            "notes",
            "booked_at",
            "checked_in_at",
            "checked_out_at",
            "cancelled_at",
            "cancellation_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "confirmation_number",
            "nights",
            "total_room_charges",
            "total_amount",
            "guest_name",
            "guest_email",
            "hotel_name",
            "room_type_name",
            "room_number",
            "booked_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        """
        Run model validations at the serializer level.
        Validates dates and occupancy constraints.
        """
        # Check dates
        check_in = data.get("check_in_date")
        check_out = data.get("check_out_date")
        if check_out and check_in and check_out <= check_in:
            raise serializers.ValidationError(
                {"check_out_date": "Check-out must be after check-in date"}
            )

        # Check occupancy
        adults = data.get("adults", 0)
        children = data.get("children", 0)
        room_type = data.get("room_type")
        if room_type and (adults + children) > room_type.max_occupancy:
            raise serializers.ValidationError(
                {
                    "adults": f"Total guests ({adults + children}) exceeds max occupancy ({room_type.max_occupancy})"
                }
            )

        return data
