"""
Real-time Session Timer API Views
Provides live timer data and session control endpoints
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Booking, BookingSession


@require_http_methods(["GET"])
def session_timer_data(request, booking_reference):
    """
    Get real-time timer data for a specific booking session
    
    Returns JSON with:
    - elapsed_seconds, remaining_seconds, total_duration_seconds
    - elapsed_display, remaining_display
    - progress_percentage
    - status, is_expiring_soon, is_expired
    - customer_name, screen_number, zone
    - scheduled_start, scheduled_end, actual_start
    """
    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    
    # Check if user has permission to view this booking
    if not request.user.is_staff and booking.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        session = booking.active_session
    except BookingSession.DoesNotExist:
        return JsonResponse({
            'error': 'No active session found',
            'booking_status': booking.status,
        }, status=404)
    
    # Get screen numbers
    screen_numbers = ', '.join([bs.seat.code for bs in booking.seats.all()])
    
    # Get offer info
    offer_info = None
    if booking.applied_offer:
        offer = booking.applied_offer
        offer_info = {
            'name': offer.title,
            'discount': f'₹{booking.discount_amount}',
        }
    
    data = {
        # Timer data
        'elapsed_seconds': session.elapsed_seconds,
        'remaining_seconds': session.remaining_seconds,
        'total_duration_seconds': session.total_duration_seconds,
        'elapsed_display': session.elapsed_time_display,
        'remaining_display': session.remaining_time_display,
        'progress_percentage': session.progress_percentage,
        
        # Status
        'status': session.status,
        'status_display': session.get_status_display(),
        'is_expiring_soon': session.is_expiring_soon,
        'is_expired': session.is_expired,
        
        # Booking info
        'booking_reference': booking.booking_reference,
        'customer_name': booking.customer_name,
        'customer_phone': booking.customer_phone,
        'screen_number': screen_numbers,
        'zone': booking.zone.name if booking.zone else 'N/A',
        
        # Times
        'scheduled_start': session.scheduled_start_display,
        'scheduled_end': session.scheduled_end_display,
        'actual_start': session.actual_start_time.strftime('%I:%M %p') if session.actual_start_time else None,
        'actual_end': session.actual_end_time.strftime('%I:%M %p') if session.actual_end_time else None,
        
        # Payment & Offers
        'total_amount': float(booking.total_amount),
        'payment_status': 'PAID' if booking.status == 'CONFIRMED' else 'PENDING',
        'offer_applied': offer_info,
        
        # Extensions
        'extended_minutes': session.extended_minutes,
        'extension_count': session.extension_count,
        
        # Server time
        'server_time': timezone.now().isoformat(),
    }
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def active_sessions_list(request):
    """
    Get list of all active sessions (for admin/staff dashboard)
    Staff only
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Staff access required'}, status=403)
    
    sessions = BookingSession.objects.filter(
        status__in=['IN_PROGRESS', 'EXTENDED', 'PAUSED', 'SCHEDULED']
    ).select_related('booking', 'booking__zone', 'booking__user').prefetch_related('booking__seats__seat')
    
    sessions_data = []
    for session in sessions:
        booking = session.booking
        screen_numbers = ', '.join([bs.seat.code for bs in booking.seats.all()])
        
        sessions_data.append({
            'booking_reference': booking.booking_reference,
            'customer_name': booking.customer_name,
            'screen_number': screen_numbers,
            'zone': booking.zone.name if booking.zone else 'N/A',
            'status': session.status,
            'status_display': session.get_status_display(),
            'elapsed_display': session.elapsed_time_display,
            'remaining_display': session.remaining_time_display,
            'progress_percentage': session.progress_percentage,
            'is_expiring_soon': session.is_expiring_soon,
            'scheduled_start': session.scheduled_start_display,
            'scheduled_end': session.scheduled_end_display,
        })
    
    return JsonResponse({
        'sessions': sessions_data,
        'count': len(sessions_data),
        'server_time': timezone.now().isoformat(),
    })


@require_http_methods(["POST"])
@login_required
def extend_session(request, booking_reference):
    """
    Extend a session by X minutes (staff only)
    POST body: {"minutes": 30}
    """
    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    
    try:
        session = booking.active_session
    except BookingSession.DoesNotExist:
        return JsonResponse({'error': 'No active session found'}, status=404)
    
    import json
    data = json.loads(request.body)
    minutes = int(data.get('minutes', 0))
    
    if minutes <= 0:
        return JsonResponse({'error': 'Invalid minutes value'}, status=400)
    
    if session.extend_session(minutes, request.user):
        return JsonResponse({
            'success': True,
            'message': f'Session extended by {minutes} minutes',
            'new_end_time': session.scheduled_end_display,
            'remaining_seconds': session.remaining_seconds,
        })
    
    return JsonResponse({'error': 'Could not extend session'}, status=400)


@require_http_methods(["POST"])
@login_required
def terminate_session(request, booking_reference):
    """
    Manually end a session (staff only)
    POST body: {"reason": "Customer requested early exit"}
    """
    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    
    try:
        session = booking.active_session
    except BookingSession.DoesNotExist:
        return JsonResponse({'error': 'No active session found'}, status=404)
    
    import json
    data = json.loads(request.body)
    reason = data.get('reason', 'Manually terminated by staff')
    
    if session.terminate_session(request.user, reason):
        return JsonResponse({
            'success': True,
            'message': 'Session terminated successfully',
            'actual_end': session.actual_end_time.strftime('%I:%M %p'),
        })
    
    return JsonResponse({'error': 'Could not terminate session'}, status=400)


@require_http_methods(["POST"])
@login_required
def pause_session(request, booking_reference):
    """Pause a session (staff only)"""
    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    
    try:
        session = booking.active_session
    except BookingSession.DoesNotExist:
        return JsonResponse({'error': 'No active session found'}, status=404)
    
    if session.pause_session():
        return JsonResponse({
            'success': True,
            'message': 'Session paused',
            'status': session.status,
        })
    
    return JsonResponse({'error': 'Could not pause session'}, status=400)


@require_http_methods(["POST"])
@login_required
def resume_session(request, booking_reference):
    """Resume a paused session (staff only)"""
    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    
    try:
        session = booking.active_session
    except BookingSession.DoesNotExist:
        return JsonResponse({'error': 'No active session found'}, status=404)
    
    if session.resume_session():
        return JsonResponse({
            'success': True,
            'message': 'Session resumed',
            'status': session.status,
        })
    
    return JsonResponse({'error': 'Could not resume session'}, status=400)
