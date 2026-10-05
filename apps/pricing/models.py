from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.venue.models import Zone
from apps.games.models import Game

class PricingRule(models.Model):
    name = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='pricing_rules')
    base_hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    peak_hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    peak_start_hour = models.PositiveIntegerField(default=18, help_text="24-hr format (e.g. 18 = 6 PM)")
    peak_end_hour = models.PositiveIntegerField(default=23, help_text="24-hr format (e.g. 23 = 11 PM)")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.zone.name} (Base: ₹{self.base_hourly_rate})"


class GamingPackage(models.Model):
    name = models.CharField(max_length=100) # e.g. "3-Hour Gamer Rush", "All-Night Overkill (10PM - 6AM)", "Day Pass"
    slug = models.SlugField(max_length=100, unique=True)
    tagline = models.CharField(max_length=150, blank=True)
    description = models.TextField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=3.0)
    price = models.DecimalField(max_digits=8, decimal_places=2) # Package bundled price in INR
    original_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    included_zones = models.ManyToManyField(Zone, related_name='packages', blank=True)
    features_list = models.TextField(help_text="Line-separated list of perks (e.g. 1 Energy Drink included)")
    badge_text = models.CharField(max_length=50, blank=True, default='POPULAR')
    
    display_order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'price']

    def __str__(self):
        return f"{self.name} ({self.duration_hours} hrs - ₹{self.price})"

    @property
    def perks(self):
        return [f.strip() for f in self.features_list.split('\n') if f.strip()]

    @property
    def savings_amount(self):
        if self.original_price and self.original_price > self.price:
            return self.original_price - self.price
        return 0


class AddOn(models.Model):
    CATEGORY_CHOICES = [
        ('BEVERAGE', 'Drinks & Energy Beverages'),
        ('SNACK', 'Gaming Snacks & Meals'),
        ('HARDWARE', 'Pro Peripherals & VR Gear'),
        ('EXTRA', 'Extra Time / Coaching'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='BEVERAGE')
    description = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    icon = models.CharField(max_length=50, default='coffee')
    image = models.ImageField(upload_to='addons/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (+₹{self.price})"


class Offer(models.Model):
    OFFER_TYPES = [
        ('PERCENT', 'Percentage Discount (%)'),
        ('FLAT', 'Flat Amount Discount (₹)'),
        ('HAPPY_HOUR', 'Happy Hour Special'),
        ('WEEKDAY', 'Weekday Deal'),
        ('WEEKEND', 'Weekend Overdrive'),
        ('STUDENT', 'Student Verification Discount'),
        ('BIRTHDAY', 'Birthday Freebie / Discount'),
        ('FIRST_BOOKING', 'First Time Gamer Offer'),
        ('GROUP', 'Group Booking Discount (3+ seats)'),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    banner_tag = models.CharField(max_length=50, default='SAVE BIG')
    description = models.TextField()
    offer_type = models.CharField(max_length=30, choices=OFFER_TYPES, default='PERCENT')
    
    # Discount Values
    discount_value = models.DecimalField(max_digits=8, decimal_places=2, help_text="Percentage (e.g. 20) or Flat INR (e.g. 100)")
    max_discount_cap = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Maximum discount in INR")
    min_order_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Coupon code if code is required to activate
    coupon_code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    
    # Eligibility & constraints
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    max_total_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Leave blank for unlimited")
    max_uses_per_user = models.PositiveIntegerField(default=1)
    current_uses_count = models.PositiveIntegerField(default=0)
    
    applicable_zones = models.ManyToManyField(Zone, blank=True, related_name='offers')
    applicable_games = models.ManyToManyField(Game, blank=True, related_name='offers')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_offer_type_display()} - {self.discount_value})"

    @property
    def is_currently_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_total_uses and self.current_uses_count >= self.max_total_uses:
            return False
        return True

    @property
    def remaining_seconds(self):
        """Seconds until valid_until. Returns None if no expiry, 0 if expired."""
        if not self.valid_until:
            return None
        diff = (self.valid_until - timezone.now()).total_seconds()
        return max(0, int(diff))

    @property
    def is_expiring_soon(self):
        """True when < 1 hour remains."""
        secs = self.remaining_seconds
        return secs is not None and secs < 3600

    @property
    def is_fresh(self):
        """True if created within last 24 hours."""
        if not self.created_at:
            return False
        return (timezone.now() - self.created_at).total_seconds() < 86400

    @property
    def expires_display(self):
        """Human-readable expiry label."""
        secs = self.remaining_seconds
        if secs is None:
            return None
        if secs == 0:
            return "Expired"
        hrs, remainder = divmod(secs, 3600)
        mins, s = divmod(remainder, 60)
        if hrs >= 24:
            days = hrs // 24
            return f"{days}d {hrs % 24}h"
        return f"{hrs:02d}h {mins:02d}m {s:02d}s"


class CouponUsage(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupon_usages')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='coupon_usages')
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} used {self.offer.title} for ₹{self.discount_amount}"
