"""
Django REST Framework serializers for Guests app
Handles serialization/deserialization of Guest model with encryption support
"""

from rest_framework import serializers
from .models import Guest


class GuestSerializer(serializers.ModelSerializer):
    """Serializer for Guest model"""

    # Computed field
    full_name = serializers.CharField(read_only=True)

    # id_document_number is encrypted - the EncryptedCharField handles encryption/decryption
    # automatically, so serializer just treats it as a normal field

    class Meta:
        model = Guest
        fields = [
            'id', 'user', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'date_of_birth', 'nationality',
            'id_document_type', 'id_document_number',
            'address', 'preferences',
            'loyalty_tier', 'loyalty_points', 'vip_status', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'loyalty_points', 'created_at', 'updated_at']

    def validate_email(self, value):
        """Ensure email is unique across all guests"""
        # If updating an existing guest, exclude current instance from uniqueness check
        if self.instance:
            if Guest.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("Email already exists")
        else:  # Creating new guest
            if Guest.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists")
        return value
