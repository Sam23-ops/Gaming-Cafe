from datetime import datetime, date, time, timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from apps.accounts.models import User, Role, Permission
from apps.venue.models import Zone, Platform, Seat
from apps.bookings.models import Booking, BookingSeat, SeatHold, BookingSession
from apps.bookings.services import SeatInventoryManager, BookingStateMachine
from apps.pricing.models import GamingPackage, Offer
from apps.pricing.services import PricingCalculator

class SeatConcurrencyAndInventoryTests(TestCase):
    def setUp(self):
        self.zone = Zone.objects.create(name='PC Arena', slug='pc-arena', hourly_rate=Decimal('150.00'))
        self.platform = Platform.objects.create(name='RTX 4090 Rig', platform_type='PC', zone=self.zone)
        self.seat = Seat.objects.create(code='PC-01', zone=self.zone, platform=self.platform, grid_row=1, grid_col=1)
        
        self.user1 = User.objects.create_user(username='player1', email='p1@test.com', password='password123')
        self.user2 = User.objects.create_user(username='player2', email='p2@test.com', password='password123')

    def test_seat_availability_and_double_booking_prevention(self):
        """Verify that two users cannot book the same seat for overlapping time slots."""
        booking_date = date(2026, 9, 10)
        start_time = time(14, 0)
        end_time = time(16, 0)

        # 1. Initially seat is available
        self.assertTrue(SeatInventoryManager.is_seat_available(
            self.seat.id, booking_date, start_time, end_time
        ))

        # 2. User 1 books the seat
        booking1 = Booking.objects.create(
            user=self.user1,
            customer_name='Player One',
            customer_email='p1@test.com',
            customer_phone='1234567890',
            zone=self.zone,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            duration_hours=Decimal('2.0'),
            status='CONFIRMED',
            total_amount=Decimal('300.00')
        )
        BookingSeat.objects.create(booking=booking1, seat=self.seat)

        # 3. User 2 tries to check availability for overlapping time (15:00 - 17:00)
        overlap_start = time(15, 0)
        overlap_end = time(17, 0)
        self.assertFalse(SeatInventoryManager.is_seat_available(
            self.seat.id, booking_date, overlap_start, overlap_end
        ))

        # 4. User 2 checks non-overlapping slot (16:00 - 18:00) -> Should be Available!
        non_overlap_start = time(16, 0)
        non_overlap_end = time(18, 0)
        self.assertTrue(SeatInventoryManager.is_seat_available(
            self.seat.id, booking_date, non_overlap_start, non_overlap_end
        ))

    def test_temporary_seat_hold_and_auto_expiry(self):
        """Test that active holds block other users but release upon expiration."""
        booking_date = date(2026, 9, 10)
        start_time = time(18, 0)
        end_time = time(20, 0)

        # User 1 holds seat for 10 minutes
        held_ok, holds = SeatInventoryManager.hold_seats(
            seat_ids=[self.seat.id],
            user=self.user1,
            session_key='session_user_1',
            booking_date=booking_date,
            start_time='18:00',
            duration_hours=2.0,
            hold_minutes=10
        )
        self.assertTrue(held_ok)

        # User 2 checks -> Seat should NOT be available
        self.assertFalse(SeatInventoryManager.is_seat_available(
            self.seat.id, booking_date, start_time, end_time, current_session_key='session_user_2'
        ))

        # Simulate expiration
        SeatHold.objects.filter(seat=self.seat).update(held_until=timezone.now() - timedelta(minutes=1))

        # User 2 checks again -> Hold expired, seat is available!
        self.assertTrue(SeatInventoryManager.is_seat_available(
            self.seat.id, booking_date, start_time, end_time, current_session_key='session_user_2'
        ))


class PricingAndOfferCalculationTests(TestCase):
    def setUp(self):
        self.zone = Zone.objects.create(name='PC Arena', slug='pc-arena', hourly_rate=Decimal('150.00'))
        self.offer_pct = Offer.objects.create(
            title='20% Student Offer',
            slug='student-20',
            offer_type='PERCENT',
            discount_value=Decimal('20.00'),
            coupon_code='STUDENT20',
            min_order_amount=Decimal('100.00'),
            is_active=True
        )

    def test_pricing_and_coupon_discount(self):
        """Verify server-side price calculation with discounts and GST."""
        # 2 hours on PC Arena = ₹300 base
        # 20% discount = ₹60 discount -> Taxable: ₹240 -> GST 18% = ₹43.20 -> Total: ₹283.20
        result = PricingCalculator.calculate(
            zone=self.zone,
            duration_hours=2.0,
            seat_count=1,
            coupon_code='STUDENT20'
        )

        self.assertEqual(result['base_amount'], 300.00)
        self.assertEqual(result['discount_amount'], 60.00)
        self.assertEqual(result['taxable_amount'], 240.00)
        self.assertEqual(result['tax_amount'], 43.20)
        self.assertEqual(result['grand_total'], 283.20)
        self.assertEqual(result['coupon_code'], 'STUDENT20')
