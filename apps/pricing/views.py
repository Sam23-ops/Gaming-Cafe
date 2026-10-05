import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import GamingPackage, Offer, AddOn
from .services import PricingCalculator
from apps.venue.models import Zone

def packages_view(request):
    """Browse gaming packages, hourly plans, and VIP combos."""
    packages = GamingPackage.objects.filter(is_active=True).prefetch_related('included_zones')
    addons = AddOn.objects.filter(is_active=True)
    return render(request, 'pricing/packages.html', {
        'packages': packages,
        'addons': addons,
    })


def offers_view(request):
    """Browse all promotional offers, happy hours, student discounts & promo codes."""
    offers = Offer.objects.filter(is_active=True).prefetch_related('applicable_zones')
    return render(request, 'pricing/offers.html', {'offers': offers})


@csrf_exempt
def api_calculate_price(request):
    """
    Live price preview API used by dynamic checkout and booking wizard.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        zone_id = data.get('zone_id')
        package_id = data.get('package_id')
        duration_hours = data.get('duration_hours', 1.0)
        seat_count = data.get('seat_count', 1)
        addon_ids = data.get('addon_ids', [])
        coupon_code = data.get('coupon_code', '')

        zone = Zone.objects.filter(id=zone_id).first() if zone_id else None
        package = GamingPackage.objects.filter(id=package_id).first() if package_id else None

        result = PricingCalculator.calculate(
            zone=zone,
            package=package,
            duration_hours=duration_hours,
            seat_count=seat_count,
            addon_ids=addon_ids,
            coupon_code=coupon_code,
            user=request.user if request.user.is_authenticated else None
        )
        return JsonResponse(result)
    
    return JsonResponse({'error': 'POST request required'}, status=400)
