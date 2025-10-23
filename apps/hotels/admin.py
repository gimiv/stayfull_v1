"""
Django Admin configuration for Hotels app models
"""

from django.contrib import admin
from django import forms
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
import pytz
from .models import Hotel, RoomType, Room


class HotelAdminForm(forms.ModelForm):
    """Custom form for Hotel with timezone and currency dropdowns"""

    timezone = forms.ChoiceField(
        choices=[(tz, tz.replace('_', ' ')) for tz in pytz.common_timezones],
        help_text="Select the hotel's timezone"
    )

    currency = forms.ChoiceField(
        choices=[
            ('USD', 'USD - US Dollar'),
            ('EUR', 'EUR - Euro'),
            ('GBP', 'GBP - British Pound'),
            ('CAD', 'CAD - Canadian Dollar'),
            ('AUD', 'AUD - Australian Dollar'),
            ('JPY', 'JPY - Japanese Yen'),
            ('CNY', 'CNY - Chinese Yuan'),
            ('INR', 'INR - Indian Rupee'),
            ('MXN', 'MXN - Mexican Peso'),
            ('BRL', 'BRL - Brazilian Real'),
            ('CHF', 'CHF - Swiss Franc'),
            ('SGD', 'SGD - Singapore Dollar'),
            ('HKD', 'HKD - Hong Kong Dollar'),
            ('NZD', 'NZD - New Zealand Dollar'),
            ('SEK', 'SEK - Swedish Krona'),
            ('NOK', 'NOK - Norwegian Krone'),
            ('DKK', 'DKK - Danish Krone'),
            ('ZAR', 'ZAR - South African Rand'),
            ('AED', 'AED - UAE Dirham'),
            ('THB', 'THB - Thai Baht'),
        ],
        help_text="Select the hotel's currency"
    )

    class Meta:
        model = Hotel
        fields = '__all__'


@admin.register(Hotel)
class HotelAdmin(DynamicArrayMixin, admin.ModelAdmin):
    """Admin interface for Hotel model"""

    form = HotelAdminForm

    list_display = ["name", "slug", "type", "brand", "total_rooms", "is_active", "created_at"]
    list_filter = ["type", "is_active", "created_at", "updated_at"]
    search_fields = ["name", "slug", "brand"]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "brand", "type")}),
        ("Location & Contact", {"fields": ("address", "contact", "timezone")}),
        ("Internationalization", {"fields": ("currency", "languages")}),
        ("Operational Settings", {"fields": ("check_in_time", "check_out_time", "total_rooms")}),
        ("Status & Settings", {"fields": ("is_active", "settings")}),
        ("Metadata", {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    ordering = ["name"]


class RoomTypeAdminForm(forms.ModelForm):
    """Custom form for RoomType with size unit conversion"""

    SQFT_TO_SQM = 0.092903  # 1 sq ft = 0.092903 sq m

    size_unit = forms.ChoiceField(
        choices=[('sqm', 'Square Meters'), ('sqft', 'Square Feet')],
        initial='sqm',
        required=False,
        help_text="Select the unit for room size"
    )

    size_value = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        help_text="Enter room size in selected unit"
    )

    class Meta:
        model = RoomType
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing room type with size_sqm, show it in sq m
        if self.instance and self.instance.size_sqm:
            self.initial['size_value'] = self.instance.size_sqm
            self.initial['size_unit'] = 'sqm'

    def clean(self):
        cleaned_data = super().clean()
        size_value = cleaned_data.get('size_value')
        size_unit = cleaned_data.get('size_unit')

        # Convert to sq m if needed
        if size_value:
            if size_unit == 'sqft':
                cleaned_data['size_sqm'] = size_value * self.SQFT_TO_SQM
            else:
                cleaned_data['size_sqm'] = size_value

        return cleaned_data


@admin.register(RoomType)
class RoomTypeAdmin(DynamicArrayMixin, admin.ModelAdmin):
    """Admin interface for RoomType model"""

    form = RoomTypeAdminForm

    list_display = [
        "name",
        "code",
        "hotel",
        "base_price",
        "max_occupancy",
        "max_adults",
        "max_children",
        "is_active",
        "display_order",
    ]
    list_filter = ["hotel", "is_active", "created_at"]
    search_fields = ["name", "code", "hotel__name"]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("hotel", "name", "code", "description")}),
        ("Occupancy", {"fields": ("max_occupancy", "max_adults", "max_children")}),
        ("Pricing & Details", {"fields": ("base_price", "size_unit", "size_value")}),
        ("Configuration", {"fields": ("bed_configuration", "amenities", "images")}),
        ("Status & Ordering", {"fields": ("is_active", "display_order")}),
        ("Metadata", {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    ordering = ["hotel", "display_order", "name"]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin interface for Room model"""

    list_display = [
        "room_number",
        "hotel",
        "room_type",
        "floor",
        "status",
        "cleaning_status",
        "is_active",
    ]
    list_filter = ["hotel", "room_type", "status", "cleaning_status", "is_active", "created_at"]
    search_fields = ["room_number", "hotel__name", "room_type__name"]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("hotel", "room_type", "room_number", "floor")}),
        ("Status", {"fields": ("status", "cleaning_status", "is_active")}),
        ("Additional Information", {"fields": ("features", "notes")}),
        ("Metadata", {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    ordering = ["hotel", "room_number"]
