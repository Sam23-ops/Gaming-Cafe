import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)
    domain = models.CharField(max_length=50, default='General') # Booking, Games, Offers, Reviews, Payments, RBAC, etc.
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['domain', 'codename']

    def __str__(self):
        return f"{self.domain}: {self.codename} ({self.name})"


class Role(models.Model):
    CODE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('STAFF', 'Staff / Operator'),
        ('MANAGER', 'Manager'),
        ('CONTENT_MANAGER', 'Content Manager'),
        ('FINANCE', 'Finance'),
        ('ADMIN', 'Admin'),
        ('SUPER_ADMIN', 'Super Admin'),
    ]

    code = models.CharField(max_length=50, unique=True, choices=CODE_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')
    is_system_role = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def has_perm(self, codename):
        if self.code == 'SUPER_ADMIN':
            return True
        return self.permissions.filter(codename=codename).exists()


class User(AbstractUser):
    ROLE_CHOICES = Role.CODE_CHOICES

    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    gamer_tag = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Public gamer handle")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    avatar_color = models.CharField(max_length=20, default='#FF3B4D')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    
    # Customer Loyalty & Gamification
    loyalty_points = models.PositiveIntegerField(default=100)
    referral_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    
    date_of_birth = models.DateField(null=True, blank=True)
    favorite_platform = models.CharField(max_length=50, default='PC')
    favorite_genre = models.CharField(max_length=50, default='FPS')
    
    # Consents & Privacy
    marketing_consent = models.BooleanField(default=True)
    terms_accepted = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.gamer_tag and self.username:
            self.gamer_tag = self.username
        if not self.referral_code:
            self.referral_code = f"GA-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    @property
    def role_code(self):
        if self.is_superuser:
            return 'SUPER_ADMIN'
        return self.role.code if self.role else 'CUSTOMER'

    @property
    def is_staff_member(self):
        return self.is_superuser or (self.role and self.role.code in ['STAFF', 'MANAGER', 'ADMIN', 'SUPER_ADMIN', 'CONTENT_MANAGER', 'FINANCE'])

    @property
    def is_admin_member(self):
        return self.is_superuser or (self.role and self.role.code in ['ADMIN', 'SUPER_ADMIN', 'MANAGER'])

    def has_custom_perm(self, perm_codename):
        if self.is_superuser:
            return True
        if not self.role:
            return False
        return self.role.has_perm(perm_codename)

    def add_loyalty_points(self, points, reason='Booking Reward', booking=None):
        self.loyalty_points += points
        self.save(update_fields=['loyalty_points'])
        LoyaltyPointsLedger.objects.create(
            user=self,
            points_change=points,
            balance_after=self.loyalty_points,
            transaction_type='EARN',
            reason=reason,
            booking=booking
        )

    def deduct_loyalty_points(self, points, reason='Coupon / Discount Redemption', booking=None):
        if self.loyalty_points >= points:
            self.loyalty_points -= points
            self.save(update_fields=['loyalty_points'])
            LoyaltyPointsLedger.objects.create(
                user=self,
                points_change=-points,
                balance_after=self.loyalty_points,
                transaction_type='REDEEM',
                reason=reason,
                booking=booking
            )
            return True
        return False


class LoyaltyPointsLedger(models.Model):
    TYPE_CHOICES = [
        ('EARN', 'Earned Points'),
        ('REDEEM', 'Redeemed Points'),
        ('EXPIRE', 'Expired Points'),
        ('ADJUST', 'Admin Adjustment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points_ledger')
    points_change = models.IntegerField()
    balance_after = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    reason = models.CharField(max_length=255)
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='loyalty_transactions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.points_change:+d} pts ({self.reason})"
