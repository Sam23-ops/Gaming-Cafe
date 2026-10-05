from django.contrib import admin
from .models import Genre, Game, GameScreenshot

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

class GameScreenshotInline(admin.TabularInline):
    model = GameScreenshot
    extra = 1

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'genre', 'player_mode', 'rating', 'release_year', 'is_available', 'is_featured']
    list_filter = ['genre', 'player_mode', 'is_available', 'is_featured']
    list_editable = ['is_available', 'is_featured', 'rating']
    search_fields = ['title', 'developer', 'tagline']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['platforms']
    inlines = [GameScreenshotInline]

@admin.register(GameScreenshot)
class GameScreenshotAdmin(admin.ModelAdmin):
    list_display = ['game', 'caption']
    search_fields = ['game__title', 'caption']
