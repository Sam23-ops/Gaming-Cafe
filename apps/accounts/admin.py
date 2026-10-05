from django.contrib import admin
from .models import Permission, Role, User, LoyaltyPointsLedger

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['codename', 'name', 'domain']
    list_filter = ['domain']
    search_fields = ['codename', 'name']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_system_role']
    filter_horizontal = ['permissions']
    list_filter = ['is_system_role']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'gamer_tag', 'role', 'loyalty_points', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'gamer_tag', 'phone']
    fieldsets = (
        ('Identity', {'fields': ('username', 'email', 'first_name', 'last_name', 'password')}),
        ('Gamer Profile', {'fields': ('gamer_tag', 'avatar', 'avatar_color', 'phone', 'date_of_birth', 'favorite_platform', 'favorite_genre')}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Loyalty & Referral', {'fields': ('loyalty_points', 'referral_code', 'referred_by')}),
        ('Consent', {'fields': ('marketing_consent', 'terms_accepted')}),
    )

@admin.register(LoyaltyPointsLedger)
class LoyaltyPointsLedgerAdmin(admin.ModelAdmin):
    list_display = ['user', 'points_change', 'balance_after', 'transaction_type', 'reason', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['user__username', 'reason']
    readonly_fields = ['created_at']
