from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Review, GalleryCategory, GalleryItem, Event, EventRegistration
from apps.bookings.models import Booking

def reviews_list_view(request):
    """Public reviews page with rating distribution and submission modal."""
    reviews = Review.objects.filter(status='APPROVED').select_related('user', 'booking')
    
    total_reviews = reviews.count()
    if total_reviews > 0:
        avg_rating = sum([r.rating for r in reviews]) / total_reviews
        rating_5 = reviews.filter(rating=5).count()
        rating_4 = reviews.filter(rating=4).count()
        rating_3 = reviews.filter(rating=3).count()
        rating_2 = reviews.filter(rating=2).count()
        rating_1 = reviews.filter(rating=1).count()
    else:
        avg_rating = 5.0
        rating_5 = rating_4 = rating_3 = rating_2 = rating_1 = 0

    return render(request, 'engagement/reviews.html', {
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'rating_5': rating_5,
        'rating_4': rating_4,
        'rating_3': rating_3,
        'rating_2': rating_2,
        'rating_1': rating_1,
    })


@login_required
def submit_review_view(request):
    """Customer submits feedback linked to a completed booking."""
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        rating = int(request.POST.get('rating', 5))
        hardware_rating = int(request.POST.get('hardware_rating', 5))
        atmosphere_rating = int(request.POST.get('atmosphere_rating', 5))
        service_rating = int(request.POST.get('service_rating', 5))
        title = request.POST.get('title')
        comment = request.POST.get('comment')
        photo = request.FILES.get('photo')

        booking = Booking.objects.filter(id=booking_id, user=request.user).first() if booking_id else None

        Review.objects.create(
            user=request.user,
            booking=booking,
            rating=rating,
            hardware_rating=hardware_rating,
            atmosphere_rating=atmosphere_rating,
            service_rating=service_rating,
            title=title,
            comment=comment,
            photo=photo,
            is_verified_booking=bool(booking),
            status='APPROVED' # Auto-publish or PENDING
        )

        messages.success(request, "🎮 Thank you for your review! Your feedback helps us improve the arena experience.")
        return redirect('engagement:reviews')

    # Get user's completed bookings that haven't been reviewed yet
    user_bookings = Booking.objects.filter(user=request.user, status__in=['COMPLETED', 'CONFIRMED'])
    return render(request, 'engagement/submit_review.html', {'user_bookings': user_bookings})


def gallery_view(request):
    """Responsive gallery showcase with category filtering and lightbox."""
    category_slug = request.GET.get('category')
    categories = GalleryCategory.objects.all()
    
    items = GalleryItem.objects.all()
    if category_slug:
        items = items.filter(category__slug=category_slug)

    return render(request, 'engagement/gallery.html', {
        'items': items,
        'categories': categories,
        'selected_category': category_slug,
    })


def events_list_view(request):
    """Upcoming esports tournaments and gaming events."""
    now = timezone.now()
    upcoming = Event.objects.filter(is_active=True, start_time__gte=now).order_by('start_time')
    past = Event.objects.filter(is_active=True, start_time__lt=now).order_by('-start_time')[:6]

    return render(request, 'engagement/events.html', {
        'upcoming_events': upcoming,
        'past_events': past,
    })


def event_detail_view(request, slug):
    """Tournament / Event details, brackets, prize pool, and registration CTA."""
    event = get_object_or_404(Event.objects.prefetch_related('registrations__user'), slug=slug)
    
    is_registered = False
    if request.user.is_authenticated:
        is_registered = event.registrations.filter(user=request.user).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        if not is_registered and not event.is_full:
            gamer_tag = request.POST.get('gamer_tag', request.user.gamer_tag or request.user.username)
            team_name = request.POST.get('team_name', '')
            EventRegistration.objects.create(
                event=event,
                user=request.user,
                gamer_tag=gamer_tag,
                team_name=team_name
            )
            messages.success(request, f"🎯 You are successfully registered for {event.title}!")
            return redirect('engagement:event_detail', slug=event.slug)

    return render(request, 'engagement/event_detail.html', {
        'event': event,
        'is_registered': is_registered,
    })
