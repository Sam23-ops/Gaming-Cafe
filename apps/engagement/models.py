from django.db import models
from django.conf import settings
from apps.bookings.models import Booking
from apps.games.models import Game

class Review(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Moderation'),
        ('APPROVED', 'Approved & Published'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    
    rating = models.PositiveSmallIntegerField(default=5) # 1 to 5
    hardware_rating = models.PositiveSmallIntegerField(default=5)
    atmosphere_rating = models.PositiveSmallIntegerField(default=5)
    service_rating = models.PositiveSmallIntegerField(default=5)
    
    title = models.CharField(max_length=150)
    comment = models.TextField()
    photo = models.ImageField(upload_to='reviews/photos/', blank=True, null=True)
    
    is_verified_booking = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPROVED') # Approved by default or configurable
    
    admin_response = models.TextField(blank=True)
    admin_responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ({self.rating}★) - {self.title}"


class GalleryCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='image')

    class Meta:
        verbose_name_plural = 'Gallery Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class GalleryItem(models.Model):
    title = models.CharField(max_length=150)
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='gallery/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    @property
    def display_url(self):
        if self.image:
            return self.image.url
        return self.image_url or 'https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80'


class Event(models.Model):
    EVENT_TYPES = [
        ('TOURNAMENT', 'Esports Tournament'),
        ('COMMUNITY_NIGHT', 'Community LAN Night'),
        ('LAUNCH_PARTY', 'New Game Launch Party'),
        ('WORKSHOP', 'Pro Coaching / Workshop'),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, default='TOURNAMENT')
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    
    banner_image = models.ImageField(upload_to='events/', blank=True, null=True)
    banner_url = models.URLField(max_length=500, blank=True)
    
    description = models.TextField()
    rules = models.TextField(blank=True)
    prize_pool = models.CharField(max_length=100, default='₹50,000 Cash Pool')
    entry_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    max_participants = models.PositiveIntegerField(default=32)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()}) - {self.start_time.strftime('%b %d')}"

    @property
    def display_banner(self):
        if self.banner_image:
            return self.banner_image.url
        return self.banner_url or 'https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=800&q=80'

    @property
    def is_full(self):
        return self.registrations.count() >= self.max_participants


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    gamer_tag = models.CharField(max_length=50)
    team_name = models.CharField(max_length=100, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.gamer_tag} registered for {self.event.title}"
