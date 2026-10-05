from django.contrib import admin
from .models import Review, GalleryCategory, GalleryItem, Event, EventRegistration

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'rating', 'status', 'is_verified_booking', 'created_at']
    list_filter = ['status', 'rating', 'is_verified_booking']
    list_editable = ['status']
    search_fields = ['title', 'comment', 'user__username']

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_featured', 'created_at']
    list_filter = ['category', 'is_featured']
    list_editable = ['is_featured']
    search_fields = ['title', 'caption']

class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'game', 'prize_pool', 'entry_fee', 'start_time', 'is_active']
    list_filter = ['event_type', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [EventRegistrationInline]

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'gamer_tag', 'team_name', 'registered_at']
    list_filter = ['event', 'registered_at']
    search_fields = ['gamer_tag', 'team_name', 'user__username']
