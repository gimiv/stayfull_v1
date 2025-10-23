"""
Reservation model for managing hotel bookings

This is the most complex model in F-001 with:
- 30+ fields
- Auto-calculated fields (nights, totals)
- Complex business rules (overlapping validation, auto-calculations)
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import timedelta
import random
import string

from apps.core.models import BaseModel
from apps.hotels.models import Hotel, Room, RoomType
from apps.guests.models import Guest


class Reservation(BaseModel):
    """
    Represents a hotel reservation/booking.

    Business Rules:
    - check_out_date must be after check_in_date
    - Total guests (adults + children) cannot exceed room_type.max_occupancy
    - No overlapping reservations for the same room (if room assigned)
    - Confirmation number is unique and auto-generated
    - nights, total_room_charges, and total_amount are auto-calculated
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("checked_in", "Checked In"),
        ("checked_out", "Checked Out"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
    ]

    SOURCE_CHOICES = [
        ("direct", "Direct Booking"),
        ("ota", "Online Travel Agency"),
        ("gds", "Global Distribution System"),
        ("walkin", "Walk-in"),
        ("corporate", "Corporate"),
        ("voice", "Voice Call"),
        ("chatbot", "Chatbot"),
    ]

    # ===== FOREIGN KEYS =====
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="reservations")
    guest = models.ForeignKey(
        Guest,
        on_delete=models.PROTECT,  # Protect guest deletion if reservations exist
        related_name="reservations",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,  # If room deleted, set to NULL but keep reservation
        null=True,
        blank=True,
        related_name="reservations",
    )
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,  # Protect room type deletion if reservations exist
        related_name="reservations",
    )

    # ===== CONFIRMATION & STATUS =====
    confirmation_number = models.CharField(
        max_length=20, unique=True, blank=True, help_text="Auto-generated unique confirmation code"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # ===== DATES =====
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    nights = models.IntegerField(
        default=0,
        validators=[MinValueValidator(1)],
        help_text="Auto-calculated from check-in/check-out dates",
    )

    # ===== GUESTS =====
    adults = models.IntegerField(
        validators=[MinValueValidator(1)], help_text="Number of adult guests"
    )
    children = models.IntegerField(
        default=0, validators=[MinValueValidator(0)], help_text="Number of children"
    )

    # ===== FINANCIAL FIELDS (Decimal for currency) =====
    rate_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Nightly rate for this reservation",
    )
    total_room_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Auto-calculated: rate_per_night × nights",
    )
    taxes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    extras = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Additional charges (room service, minibar, etc.)",
    )
    discounts = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Auto-calculated: room_charges + taxes + fees + extras - discounts",
    )
    deposit_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    # ===== SOURCE & CHANNEL =====
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="direct")
    channel = models.CharField(
        max_length=100,
        blank=True,
        help_text="Specific channel/partner (e.g., Booking.com, Expedia)",
    )

    # ===== NOTES =====
    special_requests = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Guest special requests (early check-in, late checkout, etc.)",
    )
    notes = models.TextField(
        max_length=2000, blank=True, help_text="Internal notes about this reservation"
    )

    # ===== TIMESTAMPS =====
    booked_at = models.DateTimeField(auto_now_add=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(max_length=500, blank=True)

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
        ordering = ["-check_in_date", "-created_at"]
        indexes = [
            models.Index(fields=["confirmation_number"]),
            models.Index(fields=["check_in_date", "check_out_date"]),
            models.Index(fields=["status"]),
        ]

    def generate_confirmation_number(self):
        """
        Generate a unique 10-character alphanumeric confirmation code.
        Format: XXXX-XXXX-XX (all uppercase letters and digits)
        """
        while True:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not Reservation.objects.filter(confirmation_number=code).exists():
                return code

    def clean(self):
        """
        Validate model fields and business rules.
        Called from save() method.
        """
        super().clean()

        # Validate: check_out_date must be after check_in_date
        if self.check_out_date <= self.check_in_date:
            raise ValidationError({"check_out_date": "Check-out must be after check-in date."})

        # Validate: Total guests cannot exceed room_type max_occupancy
        total_guests = self.adults + self.children
        if total_guests > self.room_type.max_occupancy:
            raise ValidationError(
                {
                    "adults": f"Total guests ({total_guests}) exceeds max occupancy ({self.room_type.max_occupancy})."
                }
            )

        # Validate: No overlapping reservations for the same room
        if self.room_id:  # Only check if room is assigned
            overlapping = Reservation.objects.filter(
                room=self.room, status__in=["confirmed", "checked_in"]  # Only active reservations
            ).filter(
                check_in_date__lt=self.check_out_date,  # Starts before this ends
                check_out_date__gt=self.check_in_date,  # Ends after this starts
            )

            # Exclude self when updating existing reservation
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError({"room": "Room has overlapping reservation for these dates."})

    def save(self, *args, **kwargs):
        """
        Override save to auto-generate confirmation number and calculate fields.
        """
        # Generate confirmation number if not set
        if not self.confirmation_number:
            self.confirmation_number = self.generate_confirmation_number()

        # Auto-calculate nights
        self.nights = (self.check_out_date - self.check_in_date).days

        # Auto-calculate total_room_charges
        self.total_room_charges = self.rate_per_night * Decimal(str(self.nights))

        # Auto-calculate total_amount
        self.total_amount = (
            self.total_room_charges + self.taxes + self.fees + self.extras - self.discounts
        )

        # Call clean() for validations
        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        """Return string representation of reservation"""
        return f"{self.confirmation_number} - {self.guest.full_name} ({self.check_in_date} to {self.check_out_date})"
