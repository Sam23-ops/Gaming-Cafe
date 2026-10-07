import json
from datetime import datetime, time, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Booking, BookingSeat, BookingItem, SeatHold, BookingSession
from .services import SeatInventoryManager, QRCodeService, BookingStateMachine
from apps.venue.models import Zone, Seat
from apps.pricing.models import GamingPackage, AddOn, Offer
from apps.pricing.services import PricingCalculator
from apps.core.utils import log_action

def booking_wizard_view(request):
    """
    Main Interactive 8-Step Booking Engine Flow:
    1. Date, Time & Duration
    2. Zone & Platform
    3. Interactive Seat Map (Available, Held, Occupied, Maintenance)
    4. Gaming Package or Custom Hourly + Add-ons
    5. Offers & Coupon Application
    6. Transparent Price Breakdown (Base + Addons - Discount + Tax)
    7. Customer Contact Info / Auth Checkpoint
    8. Payment / Finalize
    """
    # Initialize session key if guest
    if not request.session.session_key:
        request.session.create()

    zones = Zone.objects.filter(is_active=True).prefetch_related('platforms')
    packages = GamingPackage.objects.filter(is_active=True).prefetch_related('included_zones')
    addons = AddOn.objects.filter(is_active=True)
    offers = Offer.objects.filter(is_active=True)
    
    # Pre-selection query parameters (e.g. from Home or Game detail "Book Now" CTA)
    pre_zone_id = request.GET.get('zone')
    pre_package_id = request.GET.get('package')
    pre_game_id = request.GET.get('game')
    today_str = timezone.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        try:
            # Parse submission
            booking_date_str = request.POST.get('booking_date')
            start_time_str = request.POST.get('start_time')
            duration_hours = Decimal(request.POST.get('duration_hours', '1.0'))
            zone_id = request.POST.get('zone_id')
            package_id = request.POST.get('package_id') or None
            selected_seat_ids = request.POST.getlist('seat_ids') or [s.strip() for s in request.POST.get('seat_ids_json', '').split(',') if s.strip()]
            selected_addon_ids = request.POST.getlist('addon_ids')
            coupon_code = request.POST.get('coupon_code', '').strip().upper()
            
            # Customer details
            customer_name = request.POST.get('customer_name')
            customer_email = request.POST.get('customer_email')
            customer_phone = request.POST.get('customer_phone')

            if not request.user.is_authenticated and not (customer_name and customer_email and customer_phone):
                messages.error(request, "Please provide your contact name, email, and phone number to complete booking.")
                return redirect('bookings:wizard')

            if not selected_seat_ids:
                messages.error(request, "Please select at least one available seat on the arena map.")
                return redirect('bookings:wizard')

            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            start_parts = start_time_str.split(':')
            start_time = time(int(start_parts[0]), int(start_parts[1]))
            
            start_dt = datetime.combine(booking_date, start_time)
            end_dt = start_dt + timedelta(hours=float(duration_hours))
            end_time = end_dt.time()

            zone = Zone.objects.get(id=zone_id)
            package = GamingPackage.objects.filter(id=package_id).first() if package_id else None

            # 1. Authoritative Concurrency Check: Hold and Validate Seats
            held_ok, hold_result = SeatInventoryManager.hold_seats(
                seat_ids=selected_seat_ids,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key,
                booking_date=booking_date,
                start_time=start_time,
                duration_hours=duration_hours
            )

            if not held_ok:
                messages.error(request, f"Seat Conflict: {hold_result}")
                return redirect('bookings:wizard')

            # 2. Server-side authoritative price calculation
            pricing = PricingCalculator.calculate(
                zone=zone,
                package=package,
                duration_hours=duration_hours,
                seat_count=len(selected_seat_ids),
                addon_ids=selected_addon_ids,
                coupon_code=coupon_code,
                user=request.user if request.user.is_authenticated else None
            )

            # Determine User for booking
            booking_user = request.user if request.user.is_authenticated else None
            if not booking_user:
                # Fallback to guest user or first customer
                from apps.accounts.models import User
                booking_user = User.objects.filter(email=customer_email).first()
                if not booking_user:
                    booking_user = User.objects.create_user(
                        username=f"guest_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        email=customer_email,
                        phone=customer_phone,
                        first_name=customer_name.split()[0] if customer_name else 'Guest',
                        last_name=" ".join(customer_name.split()[1:]) if customer_name and len(customer_name.split()) > 1 else 'Gamer',
                        is_active=True
                    )

            # 3. Create Draft Booking
            booking = Booking.objects.create(
                user=booking_user,
                customer_name=customer_name or booking_user.get_full_name() or booking_user.username,
                customer_email=customer_email or booking_user.email,
                customer_phone=customer_phone or booking_user.phone,
                zone=zone,
                package=package,
                booking_date=booking_date,
                start_time=start_time,
                duration_hours=duration_hours,
                end_time=end_time,
                status='SEAT_HELD',
                base_amount=Decimal(str(pricing['base_amount'])),
                addons_amount=Decimal(str(pricing['addons_amount'])),
                discount_amount=Decimal(str(pricing['discount_amount'])),
                tax_amount=Decimal(str(pricing['tax_amount'])),
                total_amount=Decimal(str(pricing['grand_total'])),
                applied_offer=Offer.objects.filter(id=pricing['offer_id']).first() if pricing['offer_id'] else None,
                coupon_code_used=pricing['coupon_code'],
            )

            # Link seats
            for sid in selected_seat_ids:
                BookingSeat.objects.create(booking=booking, seat_id=sid)

            # Link addons
            for addon_id in selected_addon_ids:
                addon = AddOn.objects.filter(id=addon_id).first()
                if addon:
                    BookingItem.objects.create(
                        booking=booking,
                        addon=addon,
                        quantity=1,
                        unit_price=addon.price,
                        total_price=addon.price
                    )

            # Redirect to payment checkout simulator
            return redirect('payments:checkout', booking_reference=booking.booking_reference)

        except Exception as e:
            messages.error(request, f"Error processing booking request: {str(e)}")
            return redirect('bookings:wizard')

    context = {
        'zones': zones,
        'packages': packages,
        'addons': addons,
        'offers': offers,
        'today_str': today_str,
        'pre_zone_id': pre_zone_id,
        'pre_package_id': pre_package_id,
        'pre_game_id': pre_game_id,
    }
    return render(request, 'bookings/wizard.html', context)


def api_check_availability(request):
    """
    Returns real-time seat availability for the given zone, date, time & duration.
    """
    zone_id = request.GET.get('zone_id')
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    duration = request.GET.get('duration', 1.0)

    if not (zone_id and date_str and time_str):
        return JsonResponse({'error': 'Missing required parameters'}, status=400)

    session_key = request.session.session_key or ''
    user_id = request.user.id if request.user.is_authenticated else None

    seats = SeatInventoryManager.get_zone_availability(
        zone_id=zone_id,
        booking_date=date_str,
        start_time_str=time_str,
        duration_hours=duration,
        session_key=session_key,
        user_id=user_id
    )

    return JsonResponse({'seats': seats})


def booking_confirmation_view(request, booking_reference):
    """
    Strong Booking Confirmation Screen:
    - Booking ID & Status
    - Digital QR Ticket
    - Date, Time, Duration & Allocated Seats
    - Price Breakdown Receipt
    - Add to Google / Apple Calendar link
    - Directions to Arena
    """
    booking = get_object_or_404(
        Booking.objects.prefetch_related('seats__seat', 'items__addon', 'sessions'),
        booking_reference=booking_reference
    )
    qr_code_base64 = QRCodeService.generate_qr_base64(booking)

    return render(request, 'bookings/confirmation.html', {
        'booking': booking,
        'qr_code_base64': qr_code_base64,
    })


def booking_ticket_view(request, booking_reference):
    """Clean digital boarding pass ticket with QR code for smartphone presentation at front desk."""
    booking = get_object_or_404(
        Booking.objects.prefetch_related('seats__seat', 'items__addon'),
        booking_reference=booking_reference
    )
    qr_code_base64 = QRCodeService.generate_qr_base64(booking)

    return render(request, 'bookings/ticket.html', {
        'booking': booking,
        'qr_code_base64': qr_code_base64,
    })


@login_required
def my_bookings_view(request):
    """Customer portal: List of upcoming, completed, and cancelled bookings."""
    user = request.user
    upcoming = Booking.objects.filter(
        user=user,
        status__in=['CONFIRMED', 'SEAT_HELD', 'CHECKED_IN', 'IN_SESSION']
    ).order_by('booking_date', 'start_time')
    
    past = Booking.objects.filter(
        user=user,
        status__in=['COMPLETED', 'CANCELLED', 'REFUNDED', 'NO_SHOW', 'PAYMENT_FAILED']
    ).order_by('-booking_date', '-start_time')

    return render(request, 'bookings/my_bookings.html', {
        'upcoming_bookings': upcoming,
        'past_bookings': past,
    })


@login_required
def booking_detail_view(request, booking_reference):
    """Full details of a specific booking with actions (reschedule, cancel, invoice)."""
    booking = get_object_or_404(
        Booking.objects.prefetch_related('seats__seat', 'items__addon', 'sessions'),
        booking_reference=booking_reference
    )
    
    # Ensure only owner or staff can view
    if booking.user != request.user and not request.user.is_staff_member:
        messages.error(request, "Access denied.")
        return redirect('accounts:dashboard')

    qr_code_base64 = QRCodeService.generate_qr_base64(booking)

    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
        'qr_code_base64': qr_code_base64,
    })


@login_required
def reschedule_booking_view(request, booking_reference):
    """Reschedule an upcoming confirmed booking to a new date/time slot."""
    booking = get_object_or_404(Booking, booking_reference=booking_reference, user=request.user)

    if not booking.can_reschedule:
        messages.error(request, "This booking cannot be rescheduled (must be at least 1 hour prior to session).")
        return redirect('bookings:booking_detail', booking_reference=booking.booking_reference)

    if request.method == 'POST':
        new_date_str = request.POST.get('new_date')
        new_time_str = request.POST.get('new_time')

        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        parts = new_time_str.split(':')
        new_start = time(int(parts[0]), int(parts[1]))
        
        start_dt = datetime.combine(new_date, new_start)
        end_dt = start_dt + timedelta(hours=float(booking.duration_hours))
        new_end = end_dt.time()

        # Check seat availability for the same seats
        for bs in booking.seats.all():
            if not SeatInventoryManager.is_seat_available(
                seat_id=bs.seat_id,
                booking_date=new_date,
                start_time=new_start,
                end_time=new_end,
                exclude_booking_id=booking.id
            ):
                messages.error(request, f"Seat {bs.seat.code} is unavailable on {new_date} at {new_time_str}. Please choose another time.")
                return render(request, 'bookings/reschedule.html', {'booking': booking})

        # Update booking
        old_date = booking.booking_date
        old_time = booking.start_time
        booking.booking_date = new_date
        booking.start_time = new_start
        booking.end_time = new_end
        booking.save()

        log_action(
            request.user,
            'UPDATE',
            'Booking',
            booking.id,
            f"Rescheduled booking {booking.booking_reference} from {old_date} {old_time} to {new_date} {new_start}"
        )
        messages.success(request, "Your booking has been successfully rescheduled!")
        return redirect('bookings:booking_detail', booking_reference=booking.booking_reference)

    return render(request, 'bookings/reschedule.html', {'booking': booking})


@login_required
def cancel_booking_view(request, booking_reference):
    """Customer self-service cancellation with refund rule evaluation."""
    booking = get_object_or_404(Booking, booking_reference=booking_reference, user=request.user)

    if not booking.can_cancel:
        messages.error(request, "This booking cannot be cancelled (must be at least 1 hour prior to session).")
        return redirect('bookings:booking_detail', booking_reference=booking.booking_reference)

    if request.method == 'POST':
        cancellation_reason = request.POST.get('reason', 'Cancelled by customer')
        booking.status = 'CANCELLED'
        booking.notes = f"Cancelled on {timezone.now().strftime('%Y-%m-%d %H:%M')}. Reason: {cancellation_reason}"
        booking.save()

        # Create refund record if paid
        if hasattr(booking, 'payment') and booking.payment.status == 'SUCCESS':
            from apps.payments.models import Refund
            Refund.objects.create(
                payment=booking.payment,
                amount=booking.total_amount,
                reason=cancellation_reason,
                status='COMPLETED'
            )
            booking.status = 'REFUNDED'
            booking.save()

        # Release any active holds
        SeatHold.objects.filter(seat__booking_seats__booking=booking).delete()

        log_action(
            request.user,
            'UPDATE',
            'Booking',
            booking.id,
            f"Booking {booking.booking_reference} cancelled. Refund issued: ₹{booking.total_amount}"
        )
        messages.success(request, f"Booking {booking.booking_reference} cancelled successfully. ₹{booking.total_amount} refund has been processed.")
        return redirect('bookings:my_bookings')

    return render(request, 'bookings/cancel_refund.html', {'booking': booking})


@login_required
def my_session_timer_view(request, booking_reference):
    """
    Customer-facing real-time session timer dashboard.
    Shows elapsed/remaining time, session status, and booking details.
    """
    booking = get_object_or_404(
        Booking.objects.prefetch_related('seats__seat'),
        booking_reference=booking_reference
    )
    
    # Ensure only booking owner can view their timer
    if booking.user != request.user and not request.user.is_staff:
        messages.error(request, "Access denied. You can only view your own sessions.")
        return redirect('accounts:dashboard')
    
    # Check if session exists
    try:
        session = booking.active_session
    except BookingSession.DoesNotExist:
        messages.warning(request, "No active session found for this booking.")
        return redirect('bookings:booking_detail', booking_reference=booking_reference)
    
    # Only show timer for active sessions
    if session.status not in ['IN_PROGRESS', 'EXTENDED', 'PAUSED']:
        messages.info(request, f"Session status: {session.get_status_display()}")
        return redirect('bookings:booking_detail', booking_reference=booking_reference)
    
    return render(request, 'bookings/my_session_timer.html', {
        'booking': booking,
        'session': session,
    })
