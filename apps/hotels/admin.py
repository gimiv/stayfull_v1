"""
Django Admin configuration for Hotels app models
"""

from django.contrib import admin
from .models import Hotel, RoomType, Room


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    """Admin interface for Hotel model"""

    list_display = ['name', 'slug', 'type', 'brand', 'total_rooms', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'created_at', 'updated_at']
    search_fields = ['name', 'slug', 'brand']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'brand', 'type')
        }),
        ('Location & Contact', {
            'fields': ('address', 'contact', 'timezone')
        }),
        ('Internationalization', {
            'fields': ('currency', 'languages')
        }),
        ('Operational Settings', {
            'fields': ('check_in_time', 'check_out_time', 'total_rooms')
        }),
        ('Status & Settings', {
            'fields': ('is_active', 'settings')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ['name']


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    """Admin interface for RoomType model"""

    list_display = ['name', 'code', 'hotel', 'base_price', 'max_occupancy',
                    'max_adults', 'max_children', 'is_active', 'display_order']
    list_filter = ['hotel', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'hotel__name']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('hotel', 'name', 'code', 'description')
        }),
        ('Occupancy', {
            'fields': ('max_occupancy', 'max_adults', 'max_children')
        }),
        ('Pricing & Details', {
            'fields': ('base_price', 'size_sqm')
        }),
        ('Configuration', {
            'fields': ('bed_configuration', 'amenities', 'images')
        }),
        ('Status & Ordering', {
            'fields': ('is_active', 'display_order')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ['hotel', 'display_order', 'name']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin interface for Room model"""

    list_display = ['room_number', 'hotel', 'room_type', 'floor', 'status',
                    'cleaning_status', 'is_active']
    list_filter = ['hotel', 'room_type', 'status', 'cleaning_status', 'is_active', 'created_at']
    search_fields = ['room_number', 'hotel__name', 'room_type__name']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('hotel', 'room_type', 'room_number', 'floor')
        }),
        ('Status', {
            'fields': ('status', 'cleaning_status', 'is_active')
        }),
        ('Additional Information', {
            'fields': ('features', 'notes')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ['hotel', 'room_number']
