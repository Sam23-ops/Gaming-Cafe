from django.db import models
from django.conf import settings

class Zone(models.Model):
    name = models.CharField(max_length=100) # e.g. "PC Arena", "Console Lounge", "VR Zone", "Racing Sim Rig"
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=150.00) # Base rate in INR
    icon = models.CharField(max_length=50, default='monitor') # lucide icon name
    theme_color = models.CharField(max_length=30, default='#FF3B4D')
    image = models.ImageField(upload_to='zones/', blank=True, null=True)
    display_order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} (₹{self.hourly_rate}/hr)"


class Platform(models.Model):
    PLATFORM_TYPES = [
        ('PC', 'PC Gaming Rig'),
        ('PS5', 'PlayStation 5 Pro'),
        ('XBOX', 'Xbox Series X'),
        ('VR', 'VR Pod (Quest 3 / PSVR2)'),
        ('SIM_RACING', 'Sim Racing Cockpit'),
    ]

    name = models.CharField(max_length=100)
    platform_type = models.CharField(max_length=30, choices=PLATFORM_TYPES, default='PC')
    specs = models.TextField(help_text="GPU, CPU, RAM, Display, Peripherals specs")
    icon = models.CharField(max_length=50, default='cpu')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='platforms')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_platform_type_display()})"


class Seat(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('HELD', 'Temporary Hold'),
        ('OCCUPIED', 'Occupied / In Session'),
        ('MAINTENANCE', 'Under Maintenance'),
    ]

    code = models.CharField(max_length=20, unique=True, help_text="e.g. PC-01, PS5-02, SIM-01")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='seats')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name='seats')
    
    # 2D Grid Layout coordinates for Interactive Arena Seat Map
    grid_row = models.PositiveIntegerField(default=1)
    grid_col = models.PositiveIntegerField(default=1)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    is_maintenance = models.BooleanField(default=False)
    maintenance_reason = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['zone', 'grid_row', 'grid_col', 'code']

    def __str__(self):
        return f"{self.code} - {self.zone.name} ({self.get_status_display()})"


class SeatMaintenanceLog(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='maintenance_logs')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    issue_description = models.TextField()
    resolution_notes = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Maintenance #{self.id} on {self.seat.code}: {'Resolved' if self.is_resolved else 'Pending'}"
