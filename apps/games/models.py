from django.db import models
from apps.venue.models import Platform

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, default='gamepad-2')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Game(models.Model):
    PLAYER_MODES = [
        ('SINGLE', 'Single Player'),
        ('COOP', 'Co-op 2-4 Players'),
        ('MULTIPLAYER', 'Massive Multiplayer / Esports'),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='games/covers/', blank=True, null=True)
    cover_url = models.URLField(max_length=500, blank=True, help_text="Fallback external image URL")
    
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name='games')
    platforms = models.ManyToManyField(Platform, related_name='games', blank=True)
    
    player_mode = models.CharField(max_length=30, choices=PLAYER_MODES, default='MULTIPLAYER')
    max_players = models.PositiveIntegerField(default=1)
    
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.8) # e.g. 4.9
    release_year = models.PositiveIntegerField(default=2024)
    developer = models.CharField(max_length=100, blank=True)
    
    is_available = models.BooleanField(default=True, help_text="False if game is undergoing update/patch")
    is_featured = models.BooleanField(default=False)
    is_new_release = models.BooleanField(default=False)
    
    system_requirements = models.TextField(blank=True, default="Optimized for 240FPS Ultra on Gammers Adda RTX 4090 rigs.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'title']

    def __str__(self):
        return self.title

    @property
    def display_image(self):
        if self.cover_image:
            return self.cover_image.url
        if self.cover_url:
            return self.cover_url
        return 'https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=600&q=80'


class GameScreenshot(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='screenshots')
    image = models.ImageField(upload_to='games/screenshots/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True)
    caption = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"Screenshot for {self.game.title}"

    @property
    def display_url(self):
        if self.image:
            return self.image.url
        return self.image_url or ''
