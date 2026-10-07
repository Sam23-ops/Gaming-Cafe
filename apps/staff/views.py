import json
from datetime import datetime, time, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.venue.models import Zone, Seat, SeatMaintenanceLog
from apps.bookings.models import Booking, BookingSeat, BookingSession
from apps.bookings.services import BookingStateMachine, SeatInventoryManager
from apps.pricing.models import GamingPackage, AddOn
from apps.pricing.services import PricingCalculator
from apps.payments.models import Payment, Transaction, Invoice
from apps.core.utils import log_action

STAFF_ROLES = ['STAFF', 'MANAGER', 'ADMIN', 'SUPER_ADMIN']

@role_required(STAFF_ROLES)
def staff_dashboard_view(request):
    """
    Operational front-desk overview:
    - Current Active Arena Players
    - Today's Arrivals queue
    - Today's Counter Revenue
    - Quick Access to QR Scanner, Live Arena & Walk-in Terminal
    """
    today = timezone.now().date()
    
    active_sessions = BookingSession.objects.filter(status='IN_PROGRESS').select_related('booking', 'seat__zone', 'seat__platform')
    todays_bookings = Booking.objects.filter(booking_date=today).order_by('start_time')
    
    total_seats = Seat.objects.count()
    occupied_count = active_sessions.count()
    occupancy_pct = int((occupied_count / total_seats * 100)) if total_seats > 0 else 0
    
    counter_revenue = sum([
        p.amount for p in Payment.objects.filter(created_at__date=today, status='SUCCESS')
    ])

    context = {
        'active_sessions': active_sessions,
        'todays_bookings': todays_bookings,
        'occupied_count': occupied_count,
        'total_seats': total_seats,
        'occupancy_pct': occupancy_pct,
        'counter_revenue': counter_revenue,
    }
    return render(request, 'staff/staff_dashboard.html', context)


@role_required(STAFF_ROLES)
def live_arena_view(request):
    """
    Live Arena Digital Seat Board:
    - Real-time visual matrix of all venue seats
    - Live countdown timers (color-shifting from Green to Amber to Red)
    - Player info & quick action toolbar: Check In, Extend (+30m, +1h), End Session, Maintenance
    """
    zones = Zone.objects.all().prefetch_related('seats__platform', 'seats__sessions')
    
    # Precompute active session for each seat
    active_sessions = BookingSession.objects.filter(status='IN_PROGRESS').select_related('booking__user', 'seat')
    session_by_seat_id = {s.seat_id: s for s in active_sessions}

    seats_data = []
    for zone in zones:
        for seat in zone.seats.all():
            session = session_by_seat_id.get(seat.id)
            seats_data.append({
                'seat': seat,
                'zone': zone,
                'session': session,
                'remaining_seconds': session.remaining_seconds if session else 0,
                'remaining_formatted': session.remaining_time_formatted if session else '',
                'customer_name': session.booking.customer_name if session else '',
                'gamer_tag': session.booking.user.gamer_tag if session and session.booking.user else (session.booking.customer_name if session else ''),
            })

    return render(request, 'staff/live_arena.html', {
        'zones': zones,
        'seats_data': seats_data,
    })


@role_required(STAFF_ROLES)
def qr_scanner_view(request):
    """
    Front-Desk QR Ticket Scanner & Validation Terminal.
    Supports camera scan simulation and manual reference search.
    """
    search_query = request.GET.get('q', '').strip()
    booking_match = None
    if search_query:
        booking_match = Booking.objects.filter(
            booking_reference__iexact=search_query
        ).first() or Booking.objects.filter(
            customer_phone=search_query
        ).first()

    return render(request, 'staff/qr_scanner.html', {
        'search_query': search_query,
        'booking_match': booking_match,
    })


@role_required(STAFF_ROLES)
def api_validate_checkin(request):
    """
    Validates QR code payload / token or booking reference and activates session.
    """
    if request.method == 'POST':
        token_or_ref = request.POST.get('qr_data', '').strip()
        
        # Extract token or reference
        ref = token_or_ref
        if 'REF:' in token_or_ref:
            # Parse QR code structured string
            parts = token_or_ref.split('|')
            for p in parts:
                if p.startswith('REF:'):
                    ref = p.replace('REF:', '').strip()

        booking = Booking.objects.filter(booking_reference__iexact=ref).first() or Booking.objects.filter(qr_token=ref).first()
        
        if not booking:
            return JsonResponse({'success': False, 'message': 'Invalid ticket: No matching booking found.'})

        if booking.status in ['CHECKED_IN', 'IN_SESSION']:
            return JsonResponse({'success': True, 'message': f'Booking {booking.booking_reference} is already checked in and active!'})

        if booking.status not in ['CONFIRMED', 'SEAT_HELD']:
            return JsonResponse({'success': False, 'message': f'Cannot check in. Booking status is {booking.get_status_display()}.'})

        # Execute check-in
        BookingStateMachine.check_in_booking(booking, request.user)

        return JsonResponse({
            'success': True,
            'message': f'✅ Valid Ticket! Checked in {booking.customer_name} on seat(s) {booking.seat_codes_display}.',
            'booking_ref': booking.booking_reference,
            'customer_name': booking.customer_name,
            'seats': booking.seat_codes_display,
            'duration': f"{booking.duration_hours} hours",
        })

    return JsonResponse({'error': 'POST required'}, status=400)


@role_required(STAFF_ROLES)
def walkin_booking_view(request):
    """
    Fast 30-Second Walk-in Booking Terminal for front desk staff:
    - Quick customer search / auto-creation
    - Zone and immediate available seat selection
    - Cash or Card on counter payment collection
    - Instant Check-in & Arena Session launch!
    """
    zones = Zone.objects.filter(is_active=True).prefetch_related('seats')
    packages = GamingPackage.objects.filter(is_active=True)

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', 'Walk-in Gamer')
        customer_phone = request.POST.get('customer_phone', '9999999999')
        customer_email = request.POST.get('customer_email', f"walkin_{datetime.now().strftime('%H%M%S')}@gamersadda.com")
        
        zone_id = request.POST.get('zone_id')
        seat_id = request.POST.get('seat_id')
        duration_hours = Decimal(request.POST.get('duration_hours', '1.0'))
        payment_method = request.POST.get('payment_method', 'CASH')
        package_id = request.POST.get('package_id') or None

        zone = Zone.objects.get(id=zone_id)
        seat = Seat.objects.get(id=seat_id)
        package = GamingPackage.objects.filter(id=package_id).first() if package_id else None

        # Check if seat is free
        now = timezone.now()
        start_time = now.time()
        end_time = (now + timedelta(hours=float(duration_hours))).time()

        if seat.is_maintenance or BookingSession.objects.filter(seat=seat, status='IN_PROGRESS').exists():
            messages.error(request, f"Seat {seat.code} is currently occupied or under maintenance.")
            return redirect('staff:walkin_booking')

        # Find or create customer
        customer_user = User.objects.filter(phone=customer_phone).first()
        if not customer_user:
            customer_user = User.objects.create_user(
                username=f"walkin_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                email=customer_email,
                phone=customer_phone,
                first_name=customer_name.split()[0],
                last_name=" ".join(customer_name.split()[1:]) if len(customer_name.split()) > 1 else 'Gamer',
                gamer_tag=customer_name
            )

        # Calculate Price
        pricing = PricingCalculator.calculate(
            zone=zone,
            package=package,
            duration_hours=duration_hours,
            seat_count=1,
            user=customer_user
        )

        # Create Booking
        booking = Booking.objects.create(
            user=customer_user,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            zone=zone,
            package=package,
            booking_date=now.date(),
            start_time=start_time,
            duration_hours=duration_hours,
            end_time=end_time,
            status='CONFIRMED',
            base_amount=Decimal(str(pricing['base_amount'])),
            tax_amount=Decimal(str(pricing['tax_amount'])),
            total_amount=Decimal(str(pricing['grand_total'])),
            is_walkin=True,
            created_by_staff=request.user
        )
        BookingSeat.objects.create(booking=booking, seat=seat)

        # Record payment
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_amount,
            payment_method=payment_method,
            status='SUCCESS',
            paid_at=now
        )
        Transaction.objects.create(
            payment=payment,
            transaction_id=f"WALK-{now.strftime('%H%M%S')}",
            transaction_type='PAYMENT',
            amount=payment.amount,
            status='SUCCESS'
        )

        # Start Session immediately
        BookingStateMachine.check_in_booking(booking, request.user)

        messages.success(request, f"⚡ Walk-in created! {customer_name} is active on seat {seat.code} for {duration_hours} hr(s). Total collected: ₹{booking.total_amount}")
        return redirect('staff:live_arena')

    return render(request, 'staff/walkin_booking.html', {
        'zones': zones,
        'packages': packages,
    })


@role_required(STAFF_ROLES)
def extend_session_view(request, session_id):
    """Extend an active gaming session by 30 mins or 1 hour."""
    session = get_object_or_404(BookingSession, id=session_id, status='IN_PROGRESS')
    
    if request.method == 'POST':
        extra_minutes = int(request.POST.get('minutes', 30))
        collected_amount = Decimal(request.POST.get('collected_amount', '50.00'))

        session.expected_end_time += timedelta(minutes=extra_minutes)
        session.extended_minutes += extra_minutes
        session.status = 'EXTENDED'
        session.save()

        # Update parent booking total and duration
        session.booking.duration_hours += Decimal(str(extra_minutes / 60))
        session.booking.total_amount += collected_amount
        session.booking.save()

        log_action(
            request.user,
            'UPDATE',
            'BookingSession',
            session.id,
            f"Extended session on {session.seat.code} by {extra_minutes} mins. Collected ₹{collected_amount}"
        )
        messages.success(request, f"Session on {session.seat.code} extended by {extra_minutes} minutes.")

    return redirect('staff:live_arena')


@role_required(STAFF_ROLES)
def end_session_view(request, session_id):
    """Manually complete or terminate an active session and release the seat."""
    session = get_object_or_404(BookingSession, id=session_id)
    
    session.status = 'COMPLETED'
    session.actual_end_time = timezone.now()
    session.save()

    session.seat.status = 'AVAILABLE'
    session.seat.save()

    session.booking.status = 'COMPLETED'
    session.booking.save()

    log_action(
        request.user,
        'CHECKOUT',
        'BookingSession',
        session.id,
        f"Ended session on {session.seat.code} for {session.booking.customer_name}"
    )
    messages.info(request, f"Session ended on {session.seat.code}. Seat is now available.")
    return redirect('staff:live_arena')


@role_required(STAFF_ROLES)
def toggle_seat_maintenance_view(request, seat_id):
    """Put a seat under maintenance or release it back to available."""
    seat = get_object_or_404(Seat, id=seat_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Hardware check / Maintenance')
        seat.is_maintenance = not seat.is_maintenance
        seat.maintenance_reason = reason if seat.is_maintenance else ''
        seat.status = 'MAINTENANCE' if seat.is_maintenance else 'AVAILABLE'
        seat.save()

        SeatMaintenanceLog.objects.create(
            seat=seat,
            reported_by=request.user,
            issue_description=reason,
            is_resolved=not seat.is_maintenance,
            resolved_at=timezone.now() if not seat.is_maintenance else None
        )

        log_action(
            request.user,
            'MAINTENANCE',
            'Seat',
            seat.id,
            f"Seat {seat.code} maintenance toggled to {'ON (' + reason + ')' if seat.is_maintenance else 'OFF (Resolved)'}"
        )
        status_str = "marked as Under Maintenance" if seat.is_maintenance else "restored to Available"
        messages.info(request, f"Seat {seat.code} is now {status_str}.")

    return redirect('staff:live_arena')


@role_required(STAFF_ROLES)
def session_monitor_view(request):
    """
    Premium real-time session monitor dashboard for staff/admin.
    Shows all active sessions with detailed timer info and advanced controls:
    - Extend, pause, resume, terminate sessions
    - Customer info, payment status, offers
    - Elapsed/remaining time with live updates
    """
    return render(request, 'staff/session_monitor.html', {
        'page_title': 'Live Session Monitor',
    })
