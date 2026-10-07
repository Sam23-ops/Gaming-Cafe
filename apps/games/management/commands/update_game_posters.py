"""
Management command to update game cover images with high-quality poster URLs

Usage:
    python manage.py update_game_posters
"""
from django.core.management.base import BaseCommand
from apps.games.models import Game
from apps.games.game_posters import GAME_POSTER_URLS


class Command(BaseCommand):
    help = 'Update game cover_url fields with high-quality poster URLs from CDN'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎮 Updating game poster URLs...'))
        
        updated_count = 0
        not_found = []
        
        for game in Game.objects.all():
            poster_url = GAME_POSTER_URLS.get(game.slug)
            
            if poster_url:
                if game.cover_url != poster_url:
                    game.cover_url = poster_url
                    game.save(update_fields=['cover_url'])
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Updated: {game.title} → {poster_url[:60]}...')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  ≈ Unchanged: {game.title}')
                    )
            else:
                not_found.append(game.title)
                self.stdout.write(
                    self.style.WARNING(f'  ✗ No poster found for: {game.title} (slug: {game.slug})')
                )
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS(f'✅ Successfully updated {updated_count} game posters!'))
        
        if not_found:
            self.stdout.write(self.style.WARNING(f'\n⚠️  {len(not_found)} games need poster URLs:'))
            for title in not_found[:10]:  # Show first 10
                self.stdout.write(self.style.WARNING(f'   • {title}'))
            if len(not_found) > 10:
                self.stdout.write(self.style.WARNING(f'   ... and {len(not_found) - 10} more'))
            self.stdout.write('\n💡 Add poster URLs to apps/games/game_posters.py')
        
        self.stdout.write('='*70 + '\n')
