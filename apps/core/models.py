from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('CHECKIN', 'Check In'),
        ('CHECKOUT', 'Check Out'),
        ('PAYMENT', 'Payment Success'),
        ('REFUND', 'Refund Processed'),
        ('HOLD_SEAT', 'Seat Held'),
        ('MAINTENANCE', 'Maintenance Status Changed'),
        ('RBAC_CHANGE', 'Permissions / Role Modified'),
    ]

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    actor_name = models.CharField(max_length=150, default='System')
    actor_role = models.CharField(max_length=50, default='Anonymous')
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES)
    entity_name = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action_type']),
            models.Index(fields=['entity_name']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.actor_name} ({self.actor_role}) - {self.action_type} on {self.entity_name} #{self.entity_id}"


class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=255, blank=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.key}: {self.value[:30]}"

    @classmethod
    def get_val(cls, key, default=''):
        obj = cls.objects.filter(key=key).first()
        return obj.value if obj else default


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    badge_text = models.CharField(max_length=50, default='HOT')
    action_url = models.CharField(max_length=255, blank=True)
    action_text = models.CharField(max_length=50, blank=True, default='Learn More')
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
