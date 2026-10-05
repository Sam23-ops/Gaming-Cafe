import io
import base64
import qrcode
from datetime import datetime, time, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from .models import Booking, BookingSeat, BookingItem, SeatHold, BookingSession
from apps.venue.models import Seat
from apps.core.utils import log_action

class SeatInventoryManager:
    """
    Authoritative server-side seat inventory engine.
    Validates overlap, manages hold lifecycles, and enforces concurrency safety.
    """

    @classmethod
    def clean_expired_holds(cls):
        """Purge holds that exceeded the 10-minute hold window."""
        SeatHold.objects.filter(held_until__lt=timezone.now()).delete()

    @classmethod
    def is_seat_available(cls, seat_id, booking_date, start_time, end_time, current_session_key='', current_user_id=None, exclude_booking_id=None):
        cls.clean_expired_holds()
        
        seat = Seat.objects.filter(id=seat_id).first()
        if not seat or seat.is_maintenance:
            return False

        # 1. Check existing confirmed or active bookings
        conflicting_bookings = Booking.objects.filter(
            booking_date=booking_date,
            seats__seat_id=seat_id,
            status__in=['CONFIRMED', 'CHECKED_IN', 'IN_SESSION']
        )
        if exclude_booking_id:
            conflicting_bookings = conflicting_bookings.exclude(id=exclude_booking_id)

        for b in conflicting_bookings:
            # Overlap condition: startA < endB AND endA > startB
            if start_time < b.end_time and end_time > b.start_time:
                return False

        # 2. Check active temporary holds by OTHER users
        holds = SeatHold.objects.filter(
            seat_id=seat_id,
            booking_date=booking_date,
            held_until__gte=timezone.now()
        )
        if current_user_id:
            holds = holds.exclude(user_id=current_user_id)
        elif current_session_key:
            holds = holds.exclude(session_key=current_session_key)

        for h in holds:
            if start_time < h.end_time and end_time > h.start_time:
                return False

        return True

    @classmethod
    def get_zone_availability(cls, zone_id, booking_date, start_time_str, duration_hours, session_key='', user_id=None):
        cls.clean_expired_holds()

        # Parse times
        if isinstance(booking_date, str):
            booking_date = datetime.strptime(booking_date, '%Y-%m-%d').date()
        
        if isinstance(start_time_str, str):
            parts = start_time_str.split(':')
            start_time = time(int(parts[0]), int(parts[1]))
        else:
            start_time = start_time_str

        duration = float(duration_hours or 1.0)
        start_dt = datetime.combine(booking_date, start_time)
        end_dt = start_dt + timedelta(hours=duration)
        end_time = end_dt.time()

        seats = Seat.objects.filter(zone_id=zone_id).select_related('platform')
        results = []

        for s in seats:
            if s.is_maintenance:
                status = 'MAINTENANCE'
            else:
                avail = cls.is_seat_available(
                    seat_id=s.id,
                    booking_date=booking_date,
                    start_time=start_time,
                    end_time=end_time,
                    current_session_key=session_key,
                    current_user_id=user_id
                )
                status = 'AVAILABLE' if avail else 'OCCUPIED'

            results.append({
                'id': s.id,
                'code': s.code,
                'platform': s.platform.name,
                'specs': s.platform.specs,
                'grid_row': s.grid_row,
                'grid_col': s.grid_col,
                'status': status,
            })

        return results

    @classmethod
    @transaction.atomic
    def hold_seats(cls, seat_ids, user, session_key, booking_date, start_time, duration_hours, hold_minutes=10):
        cls.clean_expired_holds()

        if isinstance(booking_date, str):
            booking_date = datetime.strptime(booking_date, '%Y-%m-%d').date()

        if isinstance(start_time, str):
            parts = start_time.split(':')
            start_time = time(int(parts[0]), int(parts[1]))

        start_dt = datetime.combine(booking_date, start_time)
        end_dt = start_dt + timedelta(hours=float(duration_hours))
        end_time = end_dt.time()
        held_until = timezone.now() + timedelta(minutes=hold_minutes)

        # Clear existing holds by this user/session
        if user and user.is_authenticated:
            SeatHold.objects.filter(user=user).delete()
        elif session_key:
            SeatHold.objects.filter(session_key=session_key).delete()

        # Validate all requested seats are free
        for sid in seat_ids:
            if not cls.is_seat_available(sid, booking_date, start_time, end_time, session_key, user.id if user and user.is_authenticated else None):
                return False, f"Seat #{sid} is no longer available for the selected time."

        # Create new holds
        created_holds = []
        for sid in seat_ids:
            h = SeatHold.objects.create(
                seat_id=sid,
                user=user if user and user.is_authenticated else None,
                session_key=session_key or '',
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                held_until=held_until
            )
            created_holds.append(h)

        return True, created_holds


class QRCodeService:
    """Generates verification QR codes for booking confirmation and check-in tickets."""

    @classmethod
    def generate_qr_base64(cls, booking):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=8,
            border=2,
        )
        
        # QR payload contains verified ticket verification data
        qr_data = f"GAMMERS_ADDA|REF:{booking.booking_reference}|DATE:{booking.booking_date}|TIME:{booking.start_time}|SEATS:{booking.seat_codes_display}|TOKEN:{booking.qr_token}"
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#07080C", back_color="#FFFFFF")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{encoded}"


class BookingStateMachine:
    """
    Manages booking status transitions and operational session lifecycle.
    """

    @classmethod
    @transaction.atomic
    def confirm_booking(cls, booking, payment=None):
        booking.status = 'CONFIRMED'
        booking.save(update_fields=['status', 'updated_at'])

        # Delete any active holds for these seats
        SeatHold.objects.filter(seat__booking_seats__booking=booking).delete()

        # Award loyalty reward points to customer (10 points per ₹100 spent)
        if booking.user and booking.user.is_authenticated:
            earned_points = int(booking.total_amount // Decimal('10'))
            if earned_points > 0:
                booking.user.add_loyalty_points(
                    points=earned_points,
                    reason=f"XP Earned for Booking #{booking.booking_reference}",
                    booking=booking
                )

        log_action(
            booking.user,
            'CREATE',
            'Booking',
            booking.id,
            f"Booking {booking.booking_reference} confirmed for ₹{booking.total_amount}"
        )
        return booking

    @classmethod
    @transaction.atomic
    def check_in_booking(cls, booking, staff_user=None):
        """Staff checks in the customer, starts live venue sessions and countdown timers."""
        booking.status = 'CHECKED_IN'
        booking.save(update_fields=['status', 'updated_at'])

        now = timezone.now()
        expected_end = now + timedelta(hours=float(booking.duration_hours))

        # Create live arena sessions for each booked seat
        for bs in booking.seats.all():
            BookingSession.objects.create(
                booking=booking,
                seat=bs.seat,
                status='IN_PROGRESS',
                actual_start_time=now,
                expected_end_time=expected_end,
                checked_in_by=staff_user
            )
            # Update seat status
            bs.seat.status = 'OCCUPIED'
            bs.seat.save(update_fields=['status'])

        log_action(
            staff_user,
            'CHECKIN',
            'Booking',
            booking.id,
            f"Customer checked in for booking {booking.booking_reference} (Seats: {booking.seat_codes_display})"
        )
        return True
