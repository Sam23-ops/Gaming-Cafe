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
    
    # Session notification tracking
    session_started_notification_sent = models.BooleanField(default=False)
    
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
    Real-time Session Timer for live gaming sessions.
    Tracks elapsed/remaining time, auto-starts based on booking time,
    provides detailed session controls for admin/staff.
    """
    SESSION_STATUS = [
        ('SCHEDULED', 'Scheduled / Waiting to Start'),
        ('IN_PROGRESS', 'Active In Progress'),
        ('EXTENDED', 'Session Extended'),
        ('PAUSED', 'Temporarily Paused'),
        ('COMPLETED', 'Session Completed'),
        ('TERMINATED', 'Manually Ended by Staff'),
        ('EXPIRED', 'Time Expired'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='active_session', primary_key=True)
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='SCHEDULED')
    
    # Auto-calculated start time based on booking
    scheduled_start_time = models.DateTimeField()
    scheduled_end_time = models.DateTimeField()
    
    # Actual times (when session really starts/ends)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    
    # Extension tracking
    extended_minutes = models.PositiveIntegerField(default=0)
    extension_count = models.PositiveIntegerField(default=0)
    
    # Pause tracking
    total_paused_seconds = models.PositiveIntegerField(default=0)
    paused_at = models.DateTimeField(null=True, blank=True)
    
    # Staff actions
    started_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='started_sessions')
    terminated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='terminated_sessions')
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_start_time']

    def __str__(self):
        return f"Session: {self.booking.booking_reference} [{self.get_status_display()}]"

    def save(self, *args, **kwargs):
        # Auto-calculate scheduled times from booking
        if not self.scheduled_start_time:
            booking_datetime = timezone.make_aware(
                timezone.datetime.combine(self.booking.booking_date, self.booking.start_time)
            )
            self.scheduled_start_time = booking_datetime
            self.scheduled_end_time = booking_datetime + timedelta(hours=float(self.booking.duration_hours))
        super().save(*args, **kwargs)

    # ── Core Timer Properties ─────────────────────────────────────────────────

    @property
    def current_end_time(self):
        """End time including extensions"""
        if not self.scheduled_end_time:
            return None
        return self.scheduled_end_time + timedelta(minutes=self.extended_minutes)

    @property
    def elapsed_seconds(self):
        """Total elapsed time in seconds (excluding paused time)"""
        if not self.actual_start_time:
            return 0
        
        if self.status == 'PAUSED' and self.paused_at:
            elapsed = (self.paused_at - self.actual_start_time).total_seconds()
        elif self.actual_end_time:
            elapsed = (self.actual_end_time - self.actual_start_time).total_seconds()
        else:
            elapsed = (timezone.now() - self.actual_start_time).total_seconds()
        
        return max(0, int(elapsed - self.total_paused_seconds))

    @property
    def remaining_seconds(self):
        """Remaining time in seconds"""
        if self.status not in ['IN_PROGRESS', 'EXTENDED', 'PAUSED']:
            return 0
        
        if not self.current_end_time:
            return 0
        
        if self.status == 'PAUSED':
            # When paused, remaining time is frozen
            if self.paused_at:
                diff = (self.current_end_time - self.paused_at).total_seconds()
            else:
                diff = 0
        else:
            diff = (self.current_end_time - timezone.now()).total_seconds()
        
        return max(0, int(diff))

    @property
    def total_duration_seconds(self):
        """Total booked duration in seconds (including extensions)"""
        base_seconds = float(self.booking.duration_hours) * 3600
        extension_seconds = self.extended_minutes * 60
        return int(base_seconds + extension_seconds)

    @property
    def progress_percentage(self):
        """Session completion percentage (0-100)"""
        if self.total_duration_seconds == 0:
            return 0
        elapsed = self.elapsed_seconds
        total = self.total_duration_seconds
        return min(100, int((elapsed / total) * 100))

    # ── Formatted Display Properties ──────────────────────────────────────────

    @property
    def elapsed_time_display(self):
        """Format: 1h 23m or 45m 12s"""
        seconds = self.elapsed_seconds
        hours, remainder = divmod(seconds, 3600)
        mins, secs = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {mins:02d}m"
        return f"{mins}m {secs:02d}s"

    @property
    def remaining_time_display(self):
        """Format: 1h 23m or 45m 12s"""
        seconds = self.remaining_seconds
        hours, remainder = divmod(seconds, 3600)
        mins, secs = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {mins:02d}m"
        return f"{mins}m {secs:02d}s"

    @property
    def scheduled_start_display(self):
        """Format: 02:30 PM"""
        return self.scheduled_start_time.strftime('%I:%M %p')

    @property
    def scheduled_end_display(self):
        """Format: 04:30 PM"""
        return self.current_end_time.strftime('%I:%M %p') if self.current_end_time else 'N/A'

    @property
    def is_expiring_soon(self):
        """True if less than 10 minutes remaining"""
        return 0 < self.remaining_seconds < 600

    @property
    def is_expired(self):
        """True if time has run out"""
        return self.remaining_seconds == 0 and self.status == 'IN_PROGRESS'

    # ── Timer Control Methods ─────────────────────────────────────────────────

    def start_session(self, user=None):
        """Start the session timer"""
        if self.status in ['IN_PROGRESS', 'COMPLETED', 'TERMINATED']:
            return False
        
        self.actual_start_time = timezone.now()
        self.status = 'IN_PROGRESS'
        self.started_by = user
        self.save()
        return True

    def pause_session(self):
        """Pause the session timer"""
        if self.status != 'IN_PROGRESS':
            return False
        
        self.paused_at = timezone.now()
        self.status = 'PAUSED'
        self.save()
        return True

    def resume_session(self):
        """Resume a paused session"""
        if self.status != 'PAUSED' or not self.paused_at:
            return False
        
        # Add paused duration to total
        paused_duration = (timezone.now() - self.paused_at).total_seconds()
        self.total_paused_seconds += int(paused_duration)
        
        self.paused_at = None
        self.status = 'IN_PROGRESS'
        self.save()
        return True

    def extend_session(self, minutes, user=None):
        """Extend the session by X minutes"""
        if self.status not in ['IN_PROGRESS', 'EXTENDED', 'PAUSED']:
            return False
        
        self.extended_minutes += minutes
        self.extension_count += 1
        if self.status == 'IN_PROGRESS':
            self.status = 'EXTENDED'
        self.save()
        return True

    def complete_session(self):
        """Mark session as completed"""
        if self.status in ['COMPLETED', 'TERMINATED']:
            return False
        
        self.actual_end_time = timezone.now()
        self.status = 'COMPLETED'
        self.save()
        
        # Update booking status
        self.booking.status = 'COMPLETED'
        self.booking.save()
        return True

    def terminate_session(self, user=None, reason=''):
        """Manually end session before time expires"""
        if self.status in ['COMPLETED', 'TERMINATED']:
            return False
        
        self.actual_end_time = timezone.now()
        self.status = 'TERMINATED'
        self.terminated_by = user
        if reason:
            self.notes += f"\n[TERMINATED] {reason}"
        self.save()
        
        # Update booking status
        self.booking.status = 'COMPLETED'
        self.booking.save()
        return True
