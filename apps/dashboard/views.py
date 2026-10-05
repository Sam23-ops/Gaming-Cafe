import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.views.decorators.csrf import csrf_exempt

from apps.accounts.decorators import role_required, permission_required
from apps.accounts.models import User, Role, Permission
from apps.venue.models import Zone, Platform, Seat, SeatMaintenanceLog
from apps.games.models import Game, Genre
from apps.pricing.models import GamingPackage, Offer, AddOn, CouponUsage
from apps.bookings.models import Booking, BookingSeat, BookingSession
from apps.payments.models import Payment, Transaction, Refund
from apps.engagement.models import Review, GalleryItem, Event
from apps.core.models import AuditLog, SystemSetting, Announcement
from apps.core.utils import log_action

ADMIN_ROLES = ['MANAGER', 'ADMIN', 'SUPER_ADMIN', 'FINANCE', 'CONTENT_MANAGER']

@role_required(ADMIN_ROLES)
def admin_dashboard_view(request):
    """
    Executive Admin Dashboard & Business Intelligence KPIs:
    - Today's & Lifetime Revenue
    - Booking Funnel & Volume Trends
    - Zone & Platform Occupancy Distribution
    - Live Arena Health & Alerts
    - Recent Customer Activity Stream
    """
    today = timezone.now().date()
    start_of_week = today - timedelta(days=6)

    # Core KPIs
    todays_bookings = Booking.objects.filter(booking_date=today)
    todays_revenue = sum([p.amount for p in Payment.objects.filter(created_at__date=today, status='SUCCESS')])
    total_revenue = sum([p.amount for p in Payment.objects.filter(status='SUCCESS')])
    total_bookings_count = Booking.objects.count()
    
    total_seats = Seat.objects.count()
    active_sessions = BookingSession.objects.filter(status='IN_PROGRESS').count()
    maintenance_count = Seat.objects.filter(is_maintenance=True).count()
    available_seats = max(0, total_seats - active_sessions - maintenance_count)
    
    pending_reviews_count = Review.objects.filter(status='PENDING').count()
    
    # 7-Day Revenue Trend Data for Chart.js
    daily_labels = []
    daily_revenues = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        daily_labels.append(day.strftime('%a, %d %b'))
        day_rev = Payment.objects.filter(created_at__date=day, status='SUCCESS').aggregate(s=Sum('amount'))['s'] or 0
        daily_revenues.append(float(day_rev))

    # Zone distribution data
    zone_names = []
    zone_booking_counts = []
    for z in Zone.objects.all():
        zone_names.append(z.name)
        cnt = Booking.objects.filter(zone=z).count()
        zone_booking_counts.append(cnt)

    recent_activity = AuditLog.objects.all()[:8]
    recent_bookings = Booking.objects.all().order_by('-created_at')[:6]

    context = {
        'todays_revenue': todays_revenue,
        'total_revenue': total_revenue,
        'todays_bookings_count': todays_bookings.count(),
        'total_bookings_count': total_bookings_count,
        'total_seats': total_seats,
        'active_sessions': active_sessions,
        'available_seats': available_seats,
        'maintenance_count': maintenance_count,
        'pending_reviews_count': pending_reviews_count,
        'daily_labels_json': json.dumps(daily_labels),
        'daily_revenues_json': json.dumps(daily_revenues),
        'zone_names_json': json.dumps(zone_names),
        'zone_booking_counts_json': json.dumps(zone_booking_counts),
        'recent_activity': recent_activity,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@role_required(ADMIN_ROLES)
def bookings_list_view(request):
    """Admin Master Booking Management."""
    status_filter = request.GET.get('status', '')
    zone_filter = request.GET.get('zone', '')
    search_q = request.GET.get('q', '').strip()

    bookings = Booking.objects.all().select_related('user', 'zone', 'package').prefetch_related('seats__seat')

    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if zone_filter:
        bookings = bookings.filter(zone_id=zone_filter)
    if search_q:
        bookings = bookings.filter(
            Q(booking_reference__icontains=search_q) |
            Q(customer_name__icontains=search_q) |
            Q(customer_email__icontains=search_q) |
            Q(customer_phone__icontains=search_q)
        )

    zones = Zone.objects.all()
    return render(request, 'dashboard/bookings_list.html', {
        'bookings': bookings[:50],
        'zones': zones,
        'selected_status': status_filter,
        'selected_zone': zone_filter,
        'search_query': search_q,
    })


@role_required(ADMIN_ROLES)
def seats_management_view(request):
    """Admin seat layout, zone rates, and maintenance controller."""
    zones = Zone.objects.all().prefetch_related('seats__platform')
    platforms = Platform.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_seat':
            code = request.POST.get('code').strip().upper()
            zone_id = request.POST.get('zone_id')
            platform_id = request.POST.get('platform_id')
            row = int(request.POST.get('grid_row', 1))
            col = int(request.POST.get('grid_col', 1))

            Seat.objects.create(
                code=code,
                zone_id=zone_id,
                platform_id=platform_id,
                grid_row=row,
                grid_col=col
            )
            log_action(request.user, 'CREATE', 'Seat', code, f"Created new seat {code}")
            messages.success(request, f"Seat {code} created successfully!")
            return redirect('dashboard:seat_management')

    return render(request, 'dashboard/seat_management.html', {
        'zones': zones,
        'platforms': platforms,
    })


@role_required(['CONTENT_MANAGER', 'MANAGER', 'ADMIN', 'SUPER_ADMIN'])
def games_manage_view(request):
    """Admin Games CRUD and Playable Inventory manager."""
    games = Game.objects.all().prefetch_related('genre', 'platforms')
    genres = Genre.objects.all()
    platforms = Platform.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            title = request.POST.get('title')
            genre_id = request.POST.get('genre_id')
            tagline = request.POST.get('tagline', '')
            description = request.POST.get('description', '')
            cover_url = request.POST.get('cover_url', '')
            rating = request.POST.get('rating', '4.8')
            player_mode = request.POST.get('player_mode', 'MULTIPLAYER')
            is_featured = bool(request.POST.get('is_featured'))
            
            from django.utils.text import slugify
            slug = slugify(title)
            
            game = Game.objects.create(
                title=title,
                slug=slug,
                genre_id=genre_id,
                tagline=tagline,
                description=description,
                cover_url=cover_url,
                rating=Decimal(rating),
                player_mode=player_mode,
                is_featured=is_featured,
                is_available=True
            )
            platform_ids = request.POST.getlist('platform_ids')
            if platform_ids:
                game.platforms.set(platform_ids)

            log_action(request.user, 'CREATE', 'Game', game.id, f"Added game: {title}")
            messages.success(request, f"Game '{title}' added to catalog!")
            return redirect('dashboard:games_manage')

        elif action == 'toggle_availability':
            game_id = request.POST.get('game_id')
            game = get_object_or_404(Game, id=game_id)
            game.is_available = not game.is_available
            game.save()
            log_action(request.user, 'UPDATE', 'Game', game.id, f"Toggled availability of {game.title} to {game.is_available}")
            messages.info(request, f"Updated '{game.title}' availability to {'Online' if game.is_available else 'Maintenance'}.")
            return redirect('dashboard:games_manage')

    return render(request, 'dashboard/games_manage.html', {
        'games': games,
        'genres': genres,
        'platforms': platforms,
    })


@role_required(['MANAGER', 'ADMIN', 'SUPER_ADMIN', 'CONTENT_MANAGER'])
def offers_manage_view(request):
    """Dynamic Offers and Promotional Rule Engine Manager."""
    offers = Offer.objects.all().prefetch_related('applicable_zones')
    zones = Zone.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            title = request.POST.get('title')
            offer_type = request.POST.get('offer_type', 'PERCENT')
            discount_value = Decimal(request.POST.get('discount_value', '10'))
            max_discount_cap = Decimal(request.POST.get('max_discount_cap')) if request.POST.get('max_discount_cap') else None
            min_order_amount = Decimal(request.POST.get('min_order_amount', '0'))
            coupon_code = request.POST.get('coupon_code', '').strip().upper() or None
            description = request.POST.get('description', '')
            banner_tag = request.POST.get('banner_tag', 'OFFER')

            from django.utils.text import slugify
            slug = slugify(f"{title}-{timezone.now().strftime('%M%S')}")

            offer = Offer.objects.create(
                title=title,
                slug=slug,
                offer_type=offer_type,
                discount_value=discount_value,
                max_discount_cap=max_discount_cap,
                min_order_amount=min_order_amount,
                coupon_code=coupon_code,
                description=description,
                banner_tag=banner_tag,
                is_active=True
            )
            log_action(request.user, 'CREATE', 'Offer', offer.id, f"Created promotional offer: {title} ({coupon_code or 'Auto'})")
            messages.success(request, f"Offer '{title}' published successfully!")
            return redirect('dashboard:offers_manage')

        elif action == 'toggle_active':
            offer_id = request.POST.get('offer_id')
            offer = get_object_or_404(Offer, id=offer_id)
            offer.is_active = not offer.is_active
            offer.save()
            messages.info(request, f"Offer '{offer.title}' is now {'Active' if offer.is_active else 'Disabled'}.")
            return redirect('dashboard:offers_manage')

    return render(request, 'dashboard/offers_manage.html', {
        'offers': offers,
        'zones': zones,
    })


@role_required(['MANAGER', 'ADMIN', 'SUPER_ADMIN', 'CONTENT_MANAGER'])
def reviews_moderation_view(request):
    """Reviews Moderation & Official Admin Responses."""
    reviews = Review.objects.all().select_related('user', 'booking')

    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        action = request.POST.get('action') # APPROVE, REJECT, REPLY
        review = get_object_or_404(Review, id=review_id)

        if action == 'APPROVE':
            review.status = 'APPROVED'
            review.save()
            messages.success(request, f"Review #{review.id} approved and published.")
        elif action == 'REJECT':
            review.status = 'REJECTED'
            review.save()
            messages.warning(request, f"Review #{review.id} marked as rejected.")
        elif action == 'REPLY':
            reply_text = request.POST.get('admin_response')
            review.admin_response = reply_text
            review.admin_responded_at = timezone.now()
            review.save()
            messages.success(request, "Official reply posted to review.")

        log_action(request.user, 'UPDATE', 'Review', review.id, f"Moderated Review #{review.id} -> {action}")
        return redirect('dashboard:reviews_moderation')

    return render(request, 'dashboard/reviews_moderation.html', {'reviews': reviews})


@role_required(['FINANCE', 'MANAGER', 'ADMIN', 'SUPER_ADMIN'])
def payments_list_view(request):
    """Financial transactions, payment gateway verification, and refunds ledger."""
    payments = Payment.objects.all().select_related('booking', 'invoice').order_by('-created_at')
    refunds = Refund.objects.all().select_related('payment__booking').order_by('-created_at')

    total_collected = sum([p.amount for p in payments if p.status == 'SUCCESS'])
    total_refunded = sum([r.amount for r in refunds if r.status == 'COMPLETED'])

    return render(request, 'dashboard/payments_list.html', {
        'payments': payments[:50],
        'refunds': refunds[:20],
        'total_collected': total_collected,
        'total_refunded': total_refunded,
        'net_revenue': total_collected - total_refunded,
    })


@role_required(['SUPER_ADMIN'])
def rbac_matrix_view(request):
    """
    Granular RBAC Permission Matrix Editor:
    Interactive cross-table displaying all Roles vs all Domain Permissions.
    Super Admins can toggle individual granular permissions with 1-click.
    """
    roles = Role.objects.all().prefetch_related('permissions')
    permissions = Permission.objects.all().order_by('domain', 'name')
    
    # Group permissions by Domain (Booking, Games, Offers, Reviews, Payments, Governance, etc.)
    domains = {}
    for p in permissions:
        domains.setdefault(p.domain, []).append(p)

    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        perm_id = request.POST.get('perm_id')
        action = request.POST.get('action') # add or remove

        role = get_object_or_404(Role, id=role_id)
        perm = get_object_or_404(Permission, id=perm_id)

        if action == 'add':
            role.permissions.add(perm)
        else:
            role.permissions.remove(perm)

        log_action(
            request.user,
            'RBAC_CHANGE',
            'RolePermission',
            f"{role.code}:{perm.codename}",
            f"{'Granted' if action == 'add' else 'Revoked'} permission '{perm.codename}' for role '{role.name}'"
        )
        return JsonResponse({'success': True, 'action': action, 'role': role.name, 'perm': perm.codename})

    return render(request, 'dashboard/rbac_matrix.html', {
        'roles': roles,
        'domains': domains,
        'permissions': permissions,
    })


@role_required(['MANAGER', 'ADMIN', 'SUPER_ADMIN'])
def audit_logs_view(request):
    """Immutable Audit Log explorer for all operational, financial, and admin mutations."""
    action_type = request.GET.get('action', '')
    logs = AuditLog.objects.all()

    if action_type:
        logs = logs.filter(action_type=action_type)

    return render(request, 'dashboard/audit_logs.html', {
        'logs': logs[:100],
        'action_choices': AuditLog.ACTION_CHOICES,
        'selected_action': action_type,
    })


@role_required(['MANAGER', 'ADMIN', 'SUPER_ADMIN'])
def reports_view(request):
    """Comprehensive Business Intelligence Reports & Analytics."""
    today = timezone.now().date()
    
    # Peak hour analysis
    hour_distribution = Booking.objects.values('start_time').annotate(count=Count('id')).order_by('-count')[:8]
    
    # Popular Games ranking
    popular_games = Game.objects.annotate(event_count=Count('events')).order_by('-rating')[:6]
    
    # Top offers redeemed
    top_offers = Offer.objects.annotate(usage_count=Count('usages')).order_by('-usage_count')[:5]

    return render(request, 'dashboard/reports.html', {
        'hour_distribution': hour_distribution,
        'popular_games': popular_games,
        'top_offers': top_offers,
    })


@role_required(['ADMIN', 'SUPER_ADMIN'])
def settings_view(request):
    """Global venue settings, tax rates, hold timers, and cafe announcements."""
    settings_list = SystemSetting.objects.all()
    announcements = Announcement.objects.all().order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'save_settings':
            for setting in settings_list:
                val = request.POST.get(f"setting_{setting.key}")
                if val is not None:
                    setting.value = val
                    setting.save()
            log_action(request.user, 'UPDATE', 'SystemSetting', 'Global', "Updated venue system settings")
            messages.success(request, "System settings updated successfully!")
            return redirect('dashboard:settings')

        elif action == 'create_announcement':
            title = request.POST.get('title')
            content = request.POST.get('content')
            badge_text = request.POST.get('badge_text', 'NEW')
            action_url = request.POST.get('action_url', '')

            Announcement.objects.create(
                title=title,
                content=content,
                badge_text=badge_text,
                action_url=action_url,
                is_active=True
            )
            log_action(request.user, 'CREATE', 'Announcement', title, f"Posted venue announcement: {title}")
            messages.success(request, "Announcement published!")
            return redirect('dashboard:settings')

    return render(request, 'dashboard/settings.html', {
        'settings_list': settings_list,
        'announcements': announcements,
    })
