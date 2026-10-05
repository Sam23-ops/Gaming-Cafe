from decimal import Decimal
from django.utils import timezone
from django.conf import settings
from .models import Offer, GamingPackage, AddOn, CouponUsage, PricingRule
from apps.venue.models import Zone, Seat

class PricingCalculator:
    """
    Authoritative server-side pricing, offer, add-on and tax calculation engine.
    """

    @classmethod
    def calculate(cls, zone=None, package=None, duration_hours=1.0, seat_count=1, addon_ids=None, coupon_code=None, user=None, booking_date=None, start_time=None):
        duration_hours = Decimal(str(duration_hours or 1.0))
        seat_count = int(seat_count or 1)
        tax_rate = Decimal(str(getattr(settings, 'DEFAULT_TAX_PERCENTAGE', 18.0))) / Decimal('100')

        # 1. Base / Package calculation
        if package:
            if isinstance(package, (int, str)):
                package = GamingPackage.objects.filter(id=package).first()
            base_amount = Decimal(str(package.price)) * Decimal(str(seat_count))
            package_name = package.name
        elif zone:
            if isinstance(zone, (int, str)):
                zone = Zone.objects.filter(id=zone).first()
            base_amount = Decimal(str(zone.hourly_rate)) * duration_hours * Decimal(str(seat_count))
            package_name = None
        else:
            base_amount = Decimal('150.00') * duration_hours * Decimal(str(seat_count))
            package_name = None

        # 2. Add-ons calculation
        addons_amount = Decimal('0.00')
        addons_list = []
        if addon_ids:
            addons = AddOn.objects.filter(id__in=addon_ids, is_active=True)
            for addon in addons:
                addons_amount += Decimal(str(addon.price))
                addons_list.append({
                    'id': addon.id,
                    'name': addon.name,
                    'price': float(addon.price),
                    'category': addon.category,
                })

        subtotal_before_discount = base_amount + addons_amount

        # 3. Dynamic Offer & Coupon Evaluation
        discount_amount = Decimal('0.00')
        offer_applied = None
        offer_error = None

        if coupon_code:
            coupon_code = coupon_code.strip().upper()
            offer = Offer.objects.filter(coupon_code__iexact=coupon_code, is_active=True).first()
            if not offer:
                offer_error = f"Invalid coupon code: '{coupon_code}'"
            elif not offer.is_currently_valid:
                offer_error = "This coupon code has expired or reached maximum usage limit."
            elif subtotal_before_discount < offer.min_order_amount:
                offer_error = f"Minimum order amount for this coupon is ₹{offer.min_order_amount}."
            elif user and user.is_authenticated and offer.max_uses_per_user:
                user_uses = CouponUsage.objects.filter(offer=offer, user=user).count()
                if user_uses >= offer.max_uses_per_user:
                    offer_error = f"You have already redeemed coupon '{coupon_code}'."
            elif zone and offer.applicable_zones.exists() and not offer.applicable_zones.filter(id=zone.id).exists():
                offer_error = f"Coupon '{coupon_code}' is not applicable to the selected zone."
            else:
                # Calculate discount
                offer_applied = offer
                if offer.offer_type == 'PERCENT' or offer.offer_type == 'STUDENT' or offer.offer_type == 'HAPPY_HOUR':
                    pct = Decimal(str(offer.discount_value)) / Decimal('100')
                    raw_discount = subtotal_before_discount * pct
                    if offer.max_discount_cap and raw_discount > offer.max_discount_cap:
                        discount_amount = Decimal(str(offer.max_discount_cap))
                    else:
                        discount_amount = raw_discount
                elif offer.offer_type == 'FLAT' or offer.offer_type == 'FIRST_BOOKING' or offer.offer_type == 'BIRTHDAY':
                    discount_amount = min(Decimal(str(offer.discount_value)), subtotal_before_discount)
                elif offer.offer_type == 'GROUP' and seat_count >= 3:
                    pct = Decimal(str(offer.discount_value)) / Decimal('100')
                    discount_amount = subtotal_before_discount * pct

        # 4. Tax Calculation (GST 18%)
        taxable_amount = max(Decimal('0.00'), subtotal_before_discount - discount_amount)
        tax_amount = (taxable_amount * tax_rate).quantize(Decimal('0.01'))
        grand_total = (taxable_amount + tax_amount).quantize(Decimal('0.01'))

        return {
            'base_amount': float(base_amount),
            'addons_amount': float(addons_amount),
            'addons_list': addons_list,
            'subtotal': float(subtotal_before_discount),
            'discount_amount': float(discount_amount),
            'taxable_amount': float(taxable_amount),
            'tax_amount': float(tax_amount),
            'grand_total': float(grand_total),
            'offer_id': offer_applied.id if offer_applied else None,
            'offer_title': offer_applied.title if offer_applied else None,
            'coupon_code': coupon_code if offer_applied else None,
            'offer_error': offer_error,
            'package_name': package_name,
        }
