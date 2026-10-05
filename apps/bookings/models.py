import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from apps.venue.models import Zone, Platform, Seat
from apps.pricing.models import GamingPackage, AddOn, Offer

class Booking(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft / In Creation'),
        ('SEAT_HELD', 'Seat Held (Pending Payment)'),
        ('PAYMENT_PENDING', 'Payment Processing'),
        ('CONFIRMED', 'Confirmed & Booked'),
        ('CHECKED_IN', 'Checked In at Venue'),
        ('IN_SESSION', 'Active In Session'),
        ('COMPLETED', 'Completed Session'),
        ('EXPIRED', 'Seat Hold Expired'),
        ('PAYMENT_FAILED', 'Payment Failed'),
        ('CANCELLED', 'Cancelled by Customer'),
        ('REFUND_PENDING', 'Refund Processing'),
        ('REFUNDED', 'Refund Completed'),
        ('NO_SHOW', 'No Show'),
    ]

    booking_reference = models.CharField(max_length=30, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    
    # Guest/Walk-in details if customer doesn't have an online profile
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, related_name='bookings')
    package = models.ForeignKey(GamingPackage, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    booking_date = models.DateField()
    start_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    end_time = models.TimeField()
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')
    
    # Financial breakdown
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    addons_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    applied_offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    coupon_code_used = models.CharField(max_length=50, blank=True, null=True)
    
    is_walkin = models.BooleanField(default=False)
    created_by_staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_bookings')
    
    # QR verification token
    qr_token = models.CharField(max_length=64, unique=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booking_date', '-start_time', '-created_at']

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = f"GA-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:5].upper()}"
        if not self.qr_token:
            self.qr_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_reference} ({self.customer_name}) - {self.booking_date} {self.start_time} [{self.get_status_display()}]"

    @property
    def seat_codes_display(self):
        return ", ".join([bs.seat.code for bs in self.seats.all()])

    @property
    def can_cancel(self):
        """Allow cancellation if status is CONFIRMED and session starts in the future."""
        if self.status != 'CONFIRMED':
            return False
        booking_start = datetime.combine(self.booking_date, self.start_time)
        # 1 hour minimum notice
        return booking_start > datetime.now() + timedelta(hours=1)

    @property
    def can_reschedule(self):
        if self.status != 'CONFIRMED':
            return False
        booking_start = datetime.combine(self.booking_date, self.start_time)
        return booking_start > datetime.now() + timedelta(hours=1)


class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='seats')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='booking_seats')

    class Meta:
        unique_together = ('booking', 'seat')

    def __str__(self):
        return f"{self.booking.booking_reference} -> {self.seat.code}"


class BookingItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    addon = models.ForeignKey(AddOn, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.addon.name} for {self.booking.booking_reference}"


class SeatHold(models.Model):
    """
    Authoritative server-side temporary seat lock (10 minutes) during checkout.
    Guarantees no race condition or double booking.
    """
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='active_holds')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=64, blank=True)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    held_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['booking_date', 'start_time', 'end_time']),
            models.Index(fields=['held_until']),
        ]

    def is_expired(self):
        return timezone.now() > self.held_until

    def __str__(self):
        return f"Hold on {self.seat.code} for {self.booking_date} {self.start_time}-{self.end_time} until {self.held_until.strftime('%H:%M:%S')}"


class BookingSession(models.Model):
    """
    Operational Live Session tracking at the gaming venue.
    Enables live countdown timers, extensions, and check-in / check-out.
    """
    SESSION_STATUS = [
        ('SCHEDULED', 'Scheduled / Waiting Check-in'),
        ('IN_PROGRESS', 'Active In Progress'),
        ('EXTENDED', 'Session Extended'),
        ('COMPLETED', 'Session Completed'),
        ('TERMINATED', 'Manually Ended by Staff'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='sessions')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='sessions')
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='SCHEDULED')
    
    actual_start_time = models.DateTimeField(null=True, blank=True)
    expected_end_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    
    checked_in_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='checked_in_sessions')
    extended_minutes = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Session #{self.id} on {self.seat.code} [{self.get_status_display()}]"

    @property
    def remaining_seconds(self):
        if self.status != 'IN_PROGRESS' or not self.expected_end_time:
            return 0
        diff = (self.expected_end_time - timezone.now()).total_seconds()
        return max(0, int(diff))

    @property
    def remaining_time_formatted(self):
        seconds = self.remaining_seconds
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            return f"{hours:02d}h {mins:02d}m"
        return f"{mins:02d}m {secs:02d}s"
