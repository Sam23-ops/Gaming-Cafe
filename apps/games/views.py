from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Game, Genre
from apps.venue.models import Platform

def games_list_view(request):
    """
    Public Games Catalogue:
    - Search by keyword
    - Filter by Genre
    - Filter by Platform (PC, PS5, Xbox, VR, Racing)
    - Filter by Player Count / Mode
    - Sort by Popularity / Rating / New Releases
    """
    query = request.GET.get('q', '').strip()
    genre_slug = request.GET.get('genre', '')
    platform_type = request.GET.get('platform', '')
    player_mode = request.GET.get('mode', '')
    sort_by = request.GET.get('sort', 'featured')

    games = Game.objects.all().prefetch_related('platforms', 'genre')

    if query:
        games = games.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tagline__icontains=query) |
            Q(developer__icontains=query)
        )

    if genre_slug:
        games = games.filter(genre__slug=genre_slug)

    if platform_type:
        games = games.filter(platforms__platform_type=platform_type).distinct()

    if player_mode:
        games = games.filter(player_mode=player_mode)

    if sort_by == 'rating':
        games = games.order_by('-rating')
    elif sort_by == 'new':
        games = games.order_by('-release_year', '-created_at')
    elif sort_by == 'title':
        games = games.order_by('title')
    else: # featured
        games = games.order_by('-is_featured', '-rating')

    genres = Genre.objects.all()
    platforms = Platform.objects.values('platform_type', 'name').distinct()

    context = {
        'games': games,
        'genres': genres,
        'platforms': platforms,
        'search_query': query,
        'selected_genre': genre_slug,
        'selected_platform': platform_type,
        'selected_mode': player_mode,
        'selected_sort': sort_by,
        'total_count': games.count(),
    }
    return render(request, 'games/games_list.html', context)


def game_detail_view(request, slug):
    """Game detail page / modal with screenshots and direct booking CTA."""
    game = get_object_or_404(Game.objects.prefetch_related('screenshots', 'platforms', 'genre'), slug=slug)
    related_games = Game.objects.filter(genre=game.genre).exclude(id=game.id)[:4]
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'id': game.id,
            'title': game.title,
            'tagline': game.tagline,
            'description': game.description,
            'cover_image': game.display_image,
            'genre': game.genre.name if game.genre else '',
            'rating': str(game.rating),
            'developer': game.developer,
            'player_mode': game.get_player_mode_display(),
            'is_available': game.is_available,
            'system_requirements': game.system_requirements,
            'screenshots': [s.display_url for s in game.screenshots.all() if s.display_url],
            'platforms': [p.name for p in game.platforms.all()],
        })

    return render(request, 'games/game_detail.html', {
        'game': game,
        'related_games': related_games,
    })
