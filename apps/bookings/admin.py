from django.contrib import admin
from .models import Booking, BookingSeat, BookingItem, SeatHold, BookingSession

class BookingSeatInline(admin.TabularInline):
    model = BookingSeat
    extra = 0

class BookingItemInline(admin.TabularInline):
    model = BookingItem
    extra = 0

class BookingSessionInline(admin.TabularInline):
    model = BookingSession
    extra = 0

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'customer_name', 'zone', 'booking_date', 'start_time', 'duration_hours', 'total_amount', 'status']
    list_filter = ['status', 'zone', 'booking_date', 'is_walkin']
    search_fields = ['booking_reference', 'customer_name', 'customer_phone', 'customer_email']
    readonly_fields = ['booking_reference', 'qr_token', 'created_at', 'updated_at']
    inlines = [BookingSeatInline, BookingItemInline, BookingSessionInline]

@admin.register(SeatHold)
class SeatHoldAdmin(admin.ModelAdmin):
    list_display = ['seat', 'user', 'session_key', 'booking_date', 'start_time', 'end_time', 'held_until']
    list_filter = ['booking_date', 'held_until']
    search_fields = ['seat__code', 'session_key']

@admin.register(BookingSession)
class BookingSessionAdmin(admin.ModelAdmin):
    list_display = ['booking', 'status', 'scheduled_start_time', 'scheduled_end_time', 'extended_minutes']
    list_filter = ['status']
    search_fields = ['booking__booking_reference', 'seat__code']
