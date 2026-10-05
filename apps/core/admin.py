from django.contrib import admin
from .models import AuditLog, SystemSetting, Announcement

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'actor_name', 'actor_role', 'action_type', 'entity_name', 'entity_id']
    list_filter = ['action_type', 'actor_role']
    search_fields = ['actor_name', 'description', 'entity_name']
    readonly_fields = ['created_at', 'actor', 'actor_name', 'actor_role', 'action_type',
                       'entity_name', 'entity_id', 'description', 'ip_address', 'metadata']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'is_public']
    search_fields = ['key', 'value']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'badge_text', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title']
    list_editable = ['is_active']
