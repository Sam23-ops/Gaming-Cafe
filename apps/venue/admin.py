from django.contrib import admin
from .models import Zone, Platform, Seat, SeatMaintenanceLog

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'hourly_rate', 'icon', 'display_order', 'is_active']
    list_editable = ['hourly_rate', 'display_order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform_type', 'zone', 'is_active']
    list_filter = ['platform_type', 'zone', 'is_active']
    search_fields = ['name', 'specs']

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['code', 'zone', 'platform', 'grid_row', 'grid_col', 'status', 'is_maintenance']
    list_filter = ['zone', 'platform', 'status', 'is_maintenance']
    list_editable = ['status', 'is_maintenance']
    search_fields = ['code']

@admin.register(SeatMaintenanceLog)
class SeatMaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ['seat', 'reported_by', 'is_resolved', 'created_at', 'resolved_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['seat__code', 'issue_description']
