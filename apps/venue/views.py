from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Zone, Platform, Seat

def zones_list_view(request):
    """List of all gaming zones with specs and hourly rates."""
    zones = Zone.objects.filter(is_active=True).prefetch_related('platforms', 'seats')
    return render(request, 'venue/zones_list.html', {'zones': zones})


def zone_detail_view(request, slug):
    """Detailed view for a specific gaming zone."""
    zone = get_object_or_404(Zone, slug=slug, is_active=True)
    platforms = zone.platforms.filter(is_active=True)
    seats = zone.seats.all()
    return render(request, 'venue/zone_detail.html', {
        'zone': zone,
        'platforms': platforms,
        'seats': seats,
    })


def api_seat_layout(request):
    """
    JSON API returning all seats grouped by zone with coordinates and maintenance states.
    Used by interactive seat selector in booking wizard and Live Arena dashboard.
    """
    zone_id = request.GET.get('zone_id')
    seats_qs = Seat.objects.all().select_related('zone', 'platform')
    if zone_id:
        seats_qs = seats_qs.filter(zone_id=zone_id)
    
    seats_data = []
    for s in seats_qs:
        seats_data.append({
            'id': s.id,
            'code': s.code,
            'zone_id': s.zone_id,
            'zone_name': s.zone.name,
            'platform_name': s.platform.name,
            'platform_type': s.platform.platform_type,
            'specs': s.platform.specs,
            'grid_row': s.grid_row,
            'grid_col': s.grid_col,
            'status': 'MAINTENANCE' if s.is_maintenance else s.status,
            'is_maintenance': s.is_maintenance,
            'hourly_rate': float(s.zone.hourly_rate),
        })

    return JsonResponse({'seats': seats_data})
