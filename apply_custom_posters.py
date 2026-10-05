"""
Run this script AFTER placing your poster images in static/images/posters/
with these exact filenames:
  mk11.jpg        → Mortal Kombat 11
  mk1.jpg         → Mortal Kombat 1
  wwe2k25.jpg     → WWE 2K25
  wwe2k26.jpg     → WWE 2K26
  gtav.jpg        → GTA V
  f125.jpg        → F1 25

Usage:  python apply_custom_posters.py
"""
import os, sys, shutil, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gammers_adda.settings')
django.setup()

from apps.games.models import Game

POSTER_MAP = {
    'mortal-kombat-11': 'mk11.jpg',
    'mortal-kombat-1':  'mk1.jpg',
    'wwe-2k25':         'wwe2k25.jpg',
    'wwe-2k26':         'wwe2k26.jpg',
    'gta-v-ps5':        'gtav.jpg',
    'f1-25':            'f125.jpg',
}

src_dir = os.path.join('static', 'images', 'posters')
dst_dir = os.path.join('media', 'games', 'covers')
os.makedirs(dst_dir, exist_ok=True)

for slug, filename in POSTER_MAP.items():
    src = os.path.join(src_dir, filename)
    if not os.path.exists(src):
        print(f"  [!] Missing: {src}  — place your poster here")
        continue
    dst = os.path.join(dst_dir, filename)
    shutil.copy2(src, dst)
    g = Game.objects.filter(slug=slug).first()
    if g:
        g.cover_image = f'games/covers/{filename}'
        g.save(update_fields=['cover_image'])
        print(f"  [+] {g.title} → {filename}")

print("\nDone. Reload the site to see your custom posters.")
