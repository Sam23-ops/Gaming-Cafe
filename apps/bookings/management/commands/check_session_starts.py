"""
Management command to check for bookings that should start now
and send session start notifications.

Run this every minute via cron/scheduler:
    python manage.py check_session_starts
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.bookings.models import Booking, BookingSession
from apps.core.email_utils import send_session_start_notification


class Command(BaseCommand):
    help = 'Check for sessions that should start now and send notifications'

    def handle(self, *args, **options):
        now = timezone.now()
        current_time = now.time()
        current_date = now.date()
        
        # Find all CONFIRMED bookings for today where start_time is within the next 2 minutes
        # This gives us a 2-minute window to catch sessions even if cron runs slightly late
        start_window_begin = (now - timedelta(minutes=1)).time()
        start_window_end = (now + timedelta(minutes=1)).time()
        
        bookings_to_start = Booking.objects.filter(
            status='CONFIRMED',
            booking_date=current_date,
            start_time__gte=start_window_begin,
            start_time__lte=start_window_end,
            session_started_notification_sent=False  # New field to track if notification sent
        )
        
        count = 0
        for booking in bookings_to_start:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Starting session: {booking.booking_reference} - {booking.customer_name} @ {booking.start_time}'
                )
            )
            
            # Create or get BookingSession instance
            session, session_created = BookingSession.objects.get_or_create(
                booking=booking,
                defaults={
                    'status': 'IN_PROGRESS',
                }
            )
            
            # Start the session if not already started
            if not session.actual_start_time:
                session.start_session()
            
            # Send session start notification
            send_session_start_notification(booking)
            
            # Mark notification as sent
            booking.session_started_notification_sent = True
            
            # Update status to IN_SESSION
            if booking.status == 'CONFIRMED':
                booking.status = 'IN_SESSION'
            
            booking.save(update_fields=['session_started_notification_sent', 'status'])
            count += 1
        
        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Successfully started {count} session(s) and sent notifications')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No sessions to start at this time')
            )
