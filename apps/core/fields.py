"""
Custom field types for core functionality
"""

from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet


class EncryptedCharField(models.CharField):
    """
    CharField that transparently encrypts/decrypts data using Fernet encryption.

    Uses FIELD_ENCRYPTION_KEY from settings for encryption.
    Data is encrypted at rest in the database and decrypted when retrieved.
    """

    def __init__(self, *args, **kwargs):
        # Ensure we have an encryption key
        if not hasattr(settings, "FIELD_ENCRYPTION_KEY"):
            raise ValueError("FIELD_ENCRYPTION_KEY must be set in settings for EncryptedCharField")
        super().__init__(*args, **kwargs)

    def get_cipher(self):
        """Get Fernet cipher instance"""
        key = settings.FIELD_ENCRYPTION_KEY
        if isinstance(key, str):
            key = key.encode()
        return Fernet(key)

    def from_db_value(self, value, expression, connection):
        """Decrypt value when loading from database"""
        if value is None:
            return value

        try:
            cipher = self.get_cipher()
            # Value is stored as bytes in DB
            if isinstance(value, str):
                value = value.encode()
            decrypted = cipher.decrypt(value)
            return decrypted.decode("utf-8")
        except Exception:
            # If decryption fails, return None
            return None

    def get_prep_value(self, value):
        """Encrypt value before saving to database"""
        if value is None:
            return value

        cipher = self.get_cipher()
        if isinstance(value, str):
            value = value.encode()
        encrypted = cipher.encrypt(value)
        return encrypted.decode("utf-8")
