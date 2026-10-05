from django.contrib import admin
from .models import PricingRule, GamingPackage, AddOn, Offer, CouponUsage

@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'zone', 'base_hourly_rate', 'peak_hourly_rate', 'is_active']
    list_filter = ['zone', 'is_active']

@admin.register(GamingPackage)
class GamingPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_hours', 'price', 'original_price', 'badge_text', 'display_order', 'is_active']
    list_editable = ['price', 'display_order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['included_zones']
    search_fields = ['name', 'tagline']

@admin.register(AddOn)
class AddOnAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'icon', 'is_active']
    list_filter = ['category', 'is_active']
    list_editable = ['price', 'is_active']
    search_fields = ['name']

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'offer_type', 'discount_value', 'coupon_code', 'is_active', 'current_uses_count']
    list_filter = ['offer_type', 'is_active']
    list_editable = ['is_active']
    search_fields = ['title', 'coupon_code']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['offer', 'user', 'booking', 'discount_amount', 'used_at']
    list_filter = ['offer', 'used_at']
    search_fields = ['user__username', 'offer__title', 'booking__booking_reference']
    readonly_fields = ['used_at']
