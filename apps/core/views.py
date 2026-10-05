from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from apps.games.models import Game
from apps.pricing.models import GamingPackage, Offer
from apps.venue.models import Zone, Seat
from apps.engagement.models import Review, GalleryItem, Event
from apps.bookings.models import BookingSession

def home_view(request):
    """
    Public Home Page:
    - Hero with Live availability indicator widget
    - Featured offers & discounts
    - Top featured games & new releases
    - Popular gaming packages
    - Arena photo gallery preview
    - Verified customer reviews & rating stats
    - Upcoming tournaments & events
    """
    now = timezone.now()
    featured_games = Game.objects.filter(is_available=True, is_featured=True)[:6]
    packages = GamingPackage.objects.filter(is_active=True).order_by('display_order', 'price')[:4]
    offers = Offer.objects.filter(is_active=True).order_by('-discount_value')[:3]
    gallery_preview = GalleryItem.objects.filter(is_featured=True)[:6]
    reviews = Review.objects.filter(status='APPROVED').order_by('-created_at')[:4]
    upcoming_events = Event.objects.filter(is_active=True, start_time__gte=now).order_by('start_time')[:3]
    
    # Calculate live arena stats
    total_seats = Seat.objects.count()
    maintenance_seats = Seat.objects.filter(is_maintenance=True).count()
    active_sessions_count = BookingSession.objects.filter(status='IN_PROGRESS').count()
    available_now = max(0, total_seats - maintenance_seats - active_sessions_count)
    zones = Zone.objects.all().prefetch_related('seats')

    context = {
        'featured_games': featured_games,
        'packages': packages,
        'offers': offers,
        'gallery_preview': gallery_preview,
        'reviews': reviews,
        'upcoming_events': upcoming_events,
        'total_seats': total_seats,
        'available_seats': available_now,
        'occupied_seats': active_sessions_count,
        'maintenance_seats': maintenance_seats,
        'zones': zones,
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    """About Gammers Adda, our gaming infrastructure, specs and cafe experience."""
    zones = Zone.objects.all().prefetch_related('platforms', 'seats')
    return render(request, 'core/about.html', {'zones': zones})


def contact_view(request):
    """Venue location, directions, contact form, and direct contact details."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        return render(request, 'core/contact.html', {
            'success_message': f'Thank you {name}! Your message has been received. Our team will get back to you shortly.'
        })
    return render(request, 'core/contact.html')


def faqs_view(request):
    """Frequently Asked Questions."""
    return render(request, 'core/faqs.html')


def rules_view(request):
    """Arena rules, code of conduct, fair play and cancellation policies."""
    return render(request, 'core/rules.html')


def live_availability_api(request):
    """
    JSON endpoint for live availability counter on the home page and widgets.
    """
    total_seats = Seat.objects.count()
    maintenance_seats = Seat.objects.filter(is_maintenance=True).count()
    active_sessions = BookingSession.objects.filter(status='IN_PROGRESS').count()
    available_seats = max(0, total_seats - maintenance_seats - active_sessions)
    
    zone_stats = []
    for zone in Zone.objects.all():
        zone_total = zone.seats.count()
        zone_maint = zone.seats.filter(is_maintenance=True).count()
        zone_occ = BookingSession.objects.filter(status='IN_PROGRESS', seat__zone=zone).count()
        zone_avail = max(0, zone_total - zone_maint - zone_occ)
        zone_stats.append({
            'id': zone.id,
            'name': zone.name,
            'total': zone_total,
            'available': zone_avail,
            'occupied': zone_occ,
            'icon': zone.icon,
        })

    return JsonResponse({
        'total_seats': total_seats,
        'available_seats': available_seats,
        'occupied_seats': active_sessions,
        'maintenance_seats': maintenance_seats,
        'zones': zone_stats,
        'timestamp': timezone.now().isoformat(),
    })


def error_404_view(request, exception=None):
    """Custom 404 Page."""
    return render(request, 'core/404.html', status=404)


def error_500_view(request):
    """Custom 500 Page."""
    return render(request, 'core/500.html', status=500)


def error_403_view(request, exception=None):
    """Custom 403 Access Denied Page."""
    return render(request, 'core/403.html', status=403)
