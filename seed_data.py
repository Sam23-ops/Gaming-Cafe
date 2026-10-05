"""
Gamer's Adda — Complete Seed (PS5 Only, Navi Mumbai)
3 physical stations: PS5-01 (₹60), SIM-01 (₹80), PS5-03 (₹60)
"""
import os, sys, django
from datetime import time, timedelta
from decimal import Decimal

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except: pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gammers_adda.settings')
django.setup()

from django.utils import timezone
from django.db import transaction as db_transaction
from apps.core.models import SystemSetting, Announcement, AuditLog
from apps.accounts.models import User, Role, Permission
from apps.venue.models import Zone, Platform, Seat
from apps.games.models import Genre, Game, GameScreenshot
from apps.pricing.models import GamingPackage, AddOn, Offer
from apps.bookings.models import Booking, BookingSeat, BookingSession
from apps.payments.models import Payment, Invoice
from apps.engagement.models import Review, GalleryCategory, GalleryItem, Event

def seed_all():
    print("[*] Gamer's Adda — Full Seed (PS5 Only)...")
    now = timezone.now()

    # ── 1. SYSTEM SETTINGS ────────────────────────────────────────────────────
    for key, val, desc in [
        ('site_name',     "Gamer's Adda",       "Brand"),
        ('tagline',       "PLAY • ENJOY • CONNECT", "Slogan"),
        ('contact_phone', "+91 8355923184",     "Phone"),
        ('contact_email', "sumitmaheshmarvalkar343@gmail.com", "Email"),
        ('venue_address', "Shankar Mahadev Apt, Sector 5, Kopar Khairane, Navi Mumbai, Maharashtra 400709", "Address"),
        ('opening_hours', "10:00 AM – 02:00 AM (Mon – Sun)", "Hours"),
        ('currency_symbol','₹',                  "Currency"),
        ('tax_percentage', "18",                  "GST"),
    ]:
        SystemSetting.objects.update_or_create(
            key=key, defaults={'value': val, 'description': desc, 'is_public': True})
    print("  [+] System settings — Navi Mumbai address saved.")

    # ── 2. ANNOUNCEMENT ───────────────────────────────────────────────────────
    Announcement.objects.update_or_create(
        title="🎮 Book 3 Hours on PS5 & Get 40 Minutes FREE + a Snack! Use code: MEGA3HR",
        defaults={
            'content':     "Limited-time mega combo offer at Gamer's Adda, Kopar Khairane!",
            'badge_text':  "HOT DEAL",
            'action_url':  "/pricing/offers/",
            'action_text': "Grab Offer",
            'is_active':   True,
        }
    )

    # ── 3. RBAC ───────────────────────────────────────────────────────────────
    perm_codes = ['booking.view','booking.create','booking.edit','booking.cancel',
                  'booking.refund','game.create','game.edit','game.delete',
                  'offer.create','offer.edit','offer.publish',
                  'review.approve','review.reject',
                  'gallery.upload','gallery.delete',
                  'payment.view','payment.refund',
                  'report.view','role.manage','audit.view',
                  'arena.manage','seat.maintenance']
    created_perms = {}
    for code in perm_codes:
        p, _ = Permission.objects.get_or_create(codename=code, defaults={'name': code, 'domain': 'General', 'description': code})
        created_perms[code] = p

    roles_cfg = {
        'CUSTOMER':    ['booking.view','booking.create','booking.edit','booking.cancel'],
        'STAFF':       ['booking.view','booking.create','arena.manage','seat.maintenance','payment.view'],
        'MANAGER':     perm_codes,
        'FINANCE':     ['payment.view','payment.refund','booking.refund','report.view','audit.view'],
        'CONTENT_MANAGER': ['game.create','game.edit','game.delete','offer.create','offer.edit',
                            'offer.publish','review.approve','review.reject','gallery.upload','gallery.delete'],
        'ADMIN':       perm_codes,
        'SUPER_ADMIN': perm_codes,
    }
    role_names = {
        'CUSTOMER':'Customer','STAFF':'Staff','MANAGER':'Manager',
        'FINANCE':'Finance','CONTENT_MANAGER':'Content Manager',
        'ADMIN':'Admin','SUPER_ADMIN':'Super Admin',
    }
    created_roles = {}
    for code, perms in roles_cfg.items():
        role, _ = Role.objects.get_or_create(code=code, defaults={'name': role_names[code], 'description': role_names[code]})
        role.permissions.set([created_perms[p] for p in perms if p in created_perms])
        created_roles[code] = role
    print("  [+] RBAC roles configured.")

    # ── 4. USERS ──────────────────────────────────────────────────────────────
    created_users = {}
    for uname, email, pwd, rcode, gamer in [
        ('admin',  'admin@gamersadda.com',  'admin123',   'SUPER_ADMIN', 'RootAdmin'),
        ('staff',  'staff@gamersadda.com',  'staff123',   'STAFF',       'StaffPro'),
        ('gamer1', 'viper@gmail.com',       'gamer123',   'CUSTOMER',    'ViperX'),
        ('gamer2', 'shadow@gmail.com',      'gamer123',   'CUSTOMER',    'ShadowNinja'),
        ('gamer3', 'neon@gmail.com',        'gamer123',   'CUSTOMER',    'NeonGhost'),
    ]:
        u = User.objects.filter(username=uname).first()
        if not u:
            u = User.objects.create_user(
                username=uname, email=email, password=pwd,
                gamer_tag=gamer, role=created_roles[rcode],
                loyalty_points=350,
                is_superuser=(rcode=='SUPER_ADMIN'),
                is_staff=(rcode in ['STAFF','MANAGER','ADMIN','SUPER_ADMIN'])
            )
        created_users[uname] = u
    print("  [+] Users created.")

    # ── 5. ZONES & PLATFORMS (PS5 ONLY) ───────────────────────────────────────
    # Delete any lingering PC/VR/Xbox zones
    Zone.objects.filter(slug__in=['pc-arena','vr-pod']).delete()

    console_zone, _ = Zone.objects.update_or_create(slug='console-lounge', defaults={
        'name':         'PS5 Console Lounge',
        'description':  'PlayStation 5 + 65" 4K Samsung TV + Premium Sofa. ₹60/hr.',
        'hourly_rate':  Decimal('60.00'),
        'icon':         'gamepad-2',
        'display_order': 1, 'is_active': True,
    })
    sim_zone, _ = Zone.objects.update_or_create(slug='sim-racing', defaults={
        'name':         'PS5 Sim Racing Station',
        'description':  'PS5 + Logitech G29 Steering Wheel + 4K TV + Racing Seat. ₹80/hr.',
        'hourly_rate':  Decimal('80.00'),
        'icon':         'gauge',
        'display_order': 2, 'is_active': True,
    })

    p_ps5, _ = Platform.objects.update_or_create(name='PlayStation 5 + 65" 4K TV', defaults={
        'platform_type': 'PS5',
        'specs':         'Sony PlayStation 5 Disc Edition | 65" Samsung Crystal 4K TV | DualSense Wireless Controller | Luxury Sofa',
        'icon': 'tv', 'zone': console_zone,
    })
    p_sim, _ = Platform.objects.update_or_create(name='PS5 + Steering Wheel Sim', defaults={
        'platform_type': 'SIM_RACING',
        'specs':         'Sony PlayStation 5 | Logitech G29 Driving Force Wheel + Pedals | 65" 4K TV | Racing Cockpit Seat',
        'icon': 'gauge', 'zone': sim_zone,
    })
    print("  [+] PS5 zones & platforms set.")

    # ── 6. SEATS — 4 STATIONS (3 PS5 + 1 SIM) ───────────────────────────────
    Seat.objects.exclude(code__in=['PS5-01','PS5-02','SIM-01','PS5-03']).delete()
    for code, z, p, r, c in [
        ('PS5-01', console_zone, p_ps5, 3, 3),   # Sofa 1 — bottom right
        ('PS5-02', console_zone, p_ps5, 2, 3),   # Sofa 2 — middle right  
        ('SIM-01', sim_zone,     p_sim, 2, 2),   # Sim Racing — middle center
        ('PS5-03', console_zone, p_ps5, 1, 2),   # Sofa 3* — top center
    ]:
        Seat.objects.update_or_create(code=code, defaults={
            'zone': z, 'platform': p,
            'grid_row': r, 'grid_col': c,
            'status': 'AVAILABLE', 'is_maintenance': False,
        })
    print("  [+] 4 stations: PS5-01 (₹60), PS5-02 (₹60), SIM-01 (₹80), PS5-03 (₹60).")

    # ── 7. GAMES — PS5 FOCUSED WITH POSTERS ──────────────────────────────────
    # Delete all old games and re-seed cleanly
    Game.objects.all().delete()
    Genre.objects.all().delete()

    sports_g, _ = Genre.objects.get_or_create(slug='sports',   defaults={'name': 'Sports',          'icon': 'trophy'})
    action_g, _ = Genre.objects.get_or_create(slug='action',   defaults={'name': 'Action / RPG',     'icon': 'sword'})
    racing_g, _ = Genre.objects.get_or_create(slug='racing',   defaults={'name': 'Racing / Sim',     'icon': 'gauge'})
    fight_g,  _ = Genre.objects.get_or_create(slug='fighting', defaults={'name': 'Fighting',         'icon': 'flame'})
    sandbox_g,_ = Genre.objects.get_or_create(slug='sandbox',  defaults={'name': 'Open World',       'icon': 'map'})

    games_data = [
        {
            'title':       'FC 26',
            'slug':        'fc-26',
            'genre':       sports_g,
            'tagline':     "EA Sports FC 26 — The World's Game on PS5",
            'description': 'The most realistic football experience on PlayStation 5. '
                           'Play on our massive 65" 4K TV with DualSense haptic triggers '
                           'that let you feel every tackle and powerful shot.',
            'cover_url':   'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?auto=format&fit=crop&w=600&q=80',
            'rating':      Decimal('4.8'),
            'player_mode': 'MULTIPLAYER',
            'developer':   'EA Sports',
            'is_featured': True,
            'is_new_release': True,
            'release_year': 2026,
            'max_players': 4,
            'platforms':   [p_ps5],
        },
        {
            'title':       'WWE 2K25',
            'slug':        'wwe-2k25',
            'genre':       sports_g,
            'tagline':     'Rule Beyond Limits — WWE 2K25 on PS5',
            'description': 'WWE 2K25 — Rule Beyond Limits. Bigger roster, bolder moments, '
                           'same passion on PlayStation 5. Immersive gameplay, expanded roster, '
                           'iconic superstars on our 65" 4K sofa setup. Play now at Gamer\'s Adda!',
            'cover_url':   '/static/images/posters/wwe2k25.jpg',
            'rating':      Decimal('4.7'),
            'player_mode': 'COOP',
            'developer':   '2K Games',
            'is_featured': True,
            'is_new_release': False,
            'release_year': 2025,
            'max_players': 4,
            'platforms':   [p_ps5],
        },
        {
            'title':       'WWE 2K26',
            'slug':        'wwe-2k26',
            'genre':       sports_g,
            'tagline':     'Bigger. Bolder. Together. — WWE 2K26',
            'description': 'WWE 2K26 — A New Era Begins. Acknowledge the game! '
                           'Enhanced gameplay, iconic superstars, expanded universe & next-gen '
                           'experience on PS5. Finish Your Story at Gamer\'s Adda, Kopar Khairane!',
            'cover_url':   '/static/images/posters/wwe2k26.jpg',
            'rating':      Decimal('4.9'),
            'player_mode': 'COOP',
            'developer':   '2K Games',
            'is_featured': True,
            'is_new_release': True,
            'release_year': 2026,
            'max_players': 4,
            'platforms':   [p_ps5],
        },
        {
            'title':       'GTA V',
            'slug':        'gta-v-ps5',
            'genre':       sandbox_g,
            'tagline':     'Los Santos Never Sleeps — GTA V on PS5',
            'description': 'Explore. Steal. Drive. Survive. Repeat. '
                           'Grand Theft Auto V PS5 Edition — Big City, Bigger Stories, Total Freedom. '
                           'Single Player & Online Mode, Open World Action. Play with your squad at Gamer\'s Adda!',
            'cover_url':   '/static/images/posters/gtav.jpg',
            'rating':      Decimal('4.9'),
            'player_mode': 'MULTIPLAYER',
            'developer':   'Rockstar Games',
            'is_featured': True,
            'is_new_release': False,
            'release_year': 2022,
            'max_players': 2,
            'platforms':   [p_ps5],
        },
        {
            'title':       'God of War: Ragnarök',
            'slug':        'god-of-war-ragnarok',
            'genre':       action_g,
            'tagline':     'Kratos & Atreus — Face Ragnarök on PS5',
            'description': 'The epic Norse mythology adventure on PlayStation 5. '
                           'Feel every axe throw and brutal combat with DualSense haptic '
                           'feedback. Stunning visuals at 60fps on our 65" 4K TV.',
            'cover_url':   'https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=600&q=80',
            'rating':      Decimal('5.0'),
            'player_mode': 'SINGLE',
            'developer':   'Santa Monica Studio',
            'is_featured': True,
            'is_new_release': False,
            'release_year': 2022,
            'max_players': 1,
            'platforms':   [p_ps5],
        },
        {
            'title':       'F1 25',
            'slug':        'f1-25',
            'genre':       racing_g,
            'tagline':     'All Drivers. All Tracks. One Passion. — F1 25',
            'description': 'F1 25 — Feel The Rush! Drive your story with Lando Norris, '
                           'Max Verstappen & Lewis Hamilton. Realistic handling, iconic tracks, '
                           'online multiplayer & next-gen graphics on our Sim Racing rig at ₹80/hr.',
            'cover_url':   '/static/images/posters/f125.jpg',
            'rating':      Decimal('4.8'),
            'player_mode': 'MULTIPLAYER',
            'developer':   'Codemasters / EA Sports',
            'is_featured': True,
            'is_new_release': True,
            'release_year': 2025,
            'max_players': 2,
            'platforms':   [p_sim],
        },
        {
            'title':       'Mortal Kombat 1',
            'slug':        'mortal-kombat-1',
            'genre':       fight_g,
            'tagline':     'A New Era Begins — Mortal Kombat 1 on PS5',
            'description': 'Play Has No Limits. Past Meets A New Beginning. '
                           'Mortal Kombat 1 — Epic Fighters, Stunning Realms, Next-Gen Experience. '
                           'A New Legacy begins at Gamer\'s Adda. Play Now!',
            'cover_url':   '/static/images/posters/mk1.jpg',
            'rating':      Decimal('4.7'),
            'player_mode': 'COOP',
            'developer':   'NetherRealm Studios',
            'is_featured': True,
            'is_new_release': False,
            'release_year': 2023,
            'max_players': 2,
            'platforms':   [p_ps5],
        },
        {
            'title':       'Mortal Kombat 11',
            'slug':        'mortal-kombat-11',
            'genre':       fight_g,
            'tagline':     "You're Next — Mortal Kombat 11 on PS5",
            'description': 'Fight For A Better Tomorrow. Mortal Kombat 11 — Kustomize, Kompete, Conquer. '
                           'Iconic Characters, Deep Kustomization, Cinematic Story Mode, Online Multiplayer. '
                           'Test Your Skills at Gamer\'s Adda, Kopar Khairane!',
            'cover_url':   '/static/images/posters/mk11.jpg',
            'rating':      Decimal('4.8'),
            'player_mode': 'COOP',
            'developer':   'NetherRealm Studios',
            'is_featured': True,
            'is_new_release': False,
            'release_year': 2021,
            'max_players': 2,
            'platforms':   [p_ps5],
        },
    ]

    for ginfo in games_data:
        plats = ginfo.pop('platforms')
        cover = ginfo.get('cover_url', '')
        game, _ = Game.objects.update_or_create(slug=ginfo['slug'], defaults=ginfo)
        game.platforms.set(plats)
        # Update poster screenshot
        GameScreenshot.objects.update_or_create(
            game=game,
            defaults={
                'image_url': cover,
                'caption': f"{game.title} — Available at Gamer's Adda, Kopar Khairane"
            }
        )
    print("  [+] 8 PS5 games seeded with YOUR custom poster images.")

    # ── 8. ADD-ONS / SNACKS — AS SPECIFIED ───────────────────────────────────
    AddOn.objects.all().delete()
    addons_data = [
        # Drinks
        ('Pepsi (300ml Can)',              'BEVERAGE', 'Ice cold Pepsi straight from the chiller', Decimal('20.00'), 'droplets'),
        ('Thums Up (300ml Can)',           'BEVERAGE', 'Bold & fizzy Thums Up from the fridge',    Decimal('20.00'), 'droplets'),
        ('Fanta Orange (300ml Can)',       'BEVERAGE', 'Refreshing Fanta orange, chilled',         Decimal('20.00'), 'droplets'),
        # Snacks
        ('Kurkure (Regular)',              'SNACK',    'Classic Kurkure masala puffs',             Decimal('20.00'), 'utensils'),
        ('Kurkure Masala Munch',           'SNACK',    'Extra spicy Masala Munch crunchies',       Decimal('20.00'), 'utensils'),
        ('Kurkure Green Chutney',          'SNACK',    'Tangy green chutney flavour Kurkure',      Decimal('20.00'), 'utensils'),
        ('Bingo Tedhe Medhe',              'SNACK',    'Twisted wheat snack — perfectly crunchy',  Decimal('20.00'), 'utensils'),
    ]
    for name, cat, desc, price, icon in addons_data:
        AddOn.objects.get_or_create(name=name, defaults={
            'category': cat, 'description': desc, 'price': price, 'icon': icon, 'is_active': True
        })
    print("  [+] Snacks & drinks seeded (Pepsi ₹20, Thums Up ₹20, Fanta ₹20, Kurkure ₹20, etc.)")

    # ── 9. PACKAGES ───────────────────────────────────────────────────────────
    GamingPackage.objects.all().delete()
    pkgs = [
        {
            'name': 'PS5 Quick Play (1 Hour)',
            'slug': 'ps5-1hr',
            'tagline': '1 Hour on PS5 + 10 Minutes FREE!',
            'description': 'Book 1 hour and get 10 extra minutes on the house. Perfect for a quick session with your favourite game.',
            'duration_hours': Decimal('1.0'),
            'price': Decimal('60.00'),
            'original_price': Decimal('70.00'),
            'badge_text': '+10 MIN FREE',
            'features_list': '1 Hour on PlayStation 5\n+10 Minutes Bonus FREE\n65" 4K Samsung TV\nDualSense Wireless Controller\nChoose any game from the library',
            'display_order': 1,
        },
        {
            'name': 'PS5 Duo Session (2 Hours)',
            'slug': 'ps5-2hr',
            'tagline': '2 Hours + 30 Minutes FREE!',
            'description': 'Perfect for you and a friend. 2 hours of uninterrupted PS5 gaming with 30 bonus minutes on us!',
            'duration_hours': Decimal('2.0'),
            'price': Decimal('120.00'),
            'original_price': Decimal('160.00'),
            'badge_text': '+30 MIN FREE',
            'features_list': '2 Hours on PlayStation 5\n+30 Minutes Bonus FREE\n65" 4K Samsung TV\nDualSense Controllers (x2)\nChoose any game from the library',
            'display_order': 2,
        },
        {
            'name': 'PS5 Mega Session (3 Hours)',
            'slug': 'ps5-3hr',
            'tagline': '3 Hours + 40 Minutes FREE + FREE Snack!',
            'description': 'The ultimate PS5 value pack! 3 full hours plus 40 bonus minutes AND a free snack from our chiller. This is the one to grab!',
            'duration_hours': Decimal('3.0'),
            'price': Decimal('180.00'),
            'original_price': Decimal('260.00'),
            'badge_text': 'BEST VALUE 🔥',
            'features_list': '3 Hours on PlayStation 5\n+40 Minutes Bonus FREE\n1 FREE Snack (any from our menu)\n65" 4K Samsung TV\nDualSense Controllers (up to 4)\nChoose any game from the library',
            'display_order': 3,
        },
        {
            'name': 'Sim Racing Turbo (1 Hour)',
            'slug': 'sim-1hr',
            'tagline': 'PS5 Sim Racing + Steering Wheel',
            'description': 'Race on our dedicated steering wheel station. F1 2024, Gran Turismo & more. Force-feedback for the most realistic experience.',
            'duration_hours': Decimal('1.0'),
            'price': Decimal('80.00'),
            'original_price': Decimal('80.00'),
            'badge_text': 'SIM RACING',
            'features_list': '1 Hour on Sim Racing Station\nLogitech G29 Wheel + Pedals\nPS5 + 4K TV\nF1 2024, GT7 & Racing Games',
            'display_order': 4,
        },
    ]
    for p in pkgs:
        GamingPackage.objects.update_or_create(slug=p['slug'], defaults=p)
    print("  [+] 4 packages seeded (with free minutes bonuses).")

    # ── 10. OFFERS — TIME-BONUS FOCUSED ───────────────────────────────────────
    Offer.objects.all().delete()
    offers_data = [
        {
            'title':       '🎁 1 Hour Booking — 10 Minutes FREE!',
            'slug':        'free-10min-1hr',
            'banner_tag':  '⏱ BONUS TIME',
            'description': 'Book ANY PS5 station for 1 hour and walk away with 10 extra minutes '
                           'absolutely FREE! More gaming for the same price — no strings attached. '
                           'Just show up, play, and enjoy your bonus round. Valid every day!',
            'offer_type':  'FLAT',
            'discount_value': Decimal('10.00'),
            'coupon_code': 'PLAY10FREE',
            'min_order_amount': Decimal('60.00'),
            'max_discount_cap': Decimal('10.00'),
            'valid_from':  now,
            'valid_until': now + timedelta(days=30),
            'is_active':   True,
        },
        {
            'title':       '👥 4 Players? Get 20 Minutes FREE!',
            'slug':        'squad-20min-free',
            'banner_tag':  '🎮 SQUAD OFFER',
            'description': 'Roll in as a squad of 4 and we\'ll throw in 20 extra minutes FREE '
                           'on your 1-hour session! Perfect for FIFA, WWE, or Tekken battles with '
                           'the full crew. No code needed — just mention it at the counter!',
            'offer_type':  'GROUP',
            'discount_value': Decimal('13.00'),  # ~20 mins worth of ₹60/hr = ₹20
            'coupon_code': 'SQUAD4FREE',
            'min_order_amount': Decimal('60.00'),
            'max_discount_cap': Decimal('20.00'),
            'valid_from':  now,
            'valid_until': now + timedelta(days=30),
            'is_active':   True,
        },
        {
            'title':       '⚡ Book 2 Hours → Get 30 Minutes FREE!',
            'slug':        'bonus-30min-2hr',
            'banner_tag':  '🔥 DOUBLE TIME',
            'description': 'Double your game time and we double your bonus! Book any 2-hour '
                           'PS5 session and receive a whopping 30 minutes FREE on top. '
                           'That\'s 2.5 hours of gaming at the price of 2. Apply code at checkout!',
            'offer_type':  'FLAT',
            'discount_value': Decimal('30.00'),
            'coupon_code': 'BONUS30MIN',
            'min_order_amount': Decimal('120.00'),
            'max_discount_cap': Decimal('30.00'),
            'valid_from':  now,
            'valid_until': now + timedelta(days=7),
            'is_active':   True,
        },
        {
            'title':       '🏆 Book 3 Hours → 40 Min FREE + FREE Snack!',
            'slug':        'mega-3hr-combo',
            'banner_tag':  '🔥 MEGA COMBO',
            'description': 'THE ultimate Gamer\'s Adda deal! Lock in 3 hours on any PS5 station '
                           'and we\'ll give you 40 minutes EXTRA free PLUS a FREE snack from '
                           'our fridge (Kurkure, Pepsi, Thums Up — your choice!). '
                           'Over ₹50 in savings. Only at Kopar Khairane!',
            'offer_type':  'FLAT',
            'discount_value': Decimal('50.00'),
            'coupon_code': 'MEGA3HR',
            'min_order_amount': Decimal('180.00'),
            'max_discount_cap': Decimal('60.00'),
            'valid_from':  now,
            'valid_until': now + timedelta(days=7),
            'is_active':   True,
        },
        {
            'title':       '🏎️ Sim Racing Special — ₹70/hr (Save ₹10)',
            'slug':        'sim-rush-deal',
            'banner_tag':  'SIM DEAL',
            'description': 'Feel the rush of real racing! Book our PS5 Sim Station with '
                           'Logitech G29 steering wheel and pedals at just ₹70/hr instead of ₹80. '
                           'Race F1, GT7 and more with true force-feedback!',
            'offer_type':  'FLAT',
            'discount_value': Decimal('10.00'),
            'coupon_code': 'SIMPRO',
            'min_order_amount': Decimal('70.00'),
            'max_discount_cap': Decimal('10.00'),
            'valid_from':  now,
            'valid_until': now + timedelta(days=14),
            'is_active':   True,
        },
    ]
    for o in offers_data:
        Offer.objects.update_or_create(slug=o['slug'], defaults=o)
    print("  [+] 5 time-bonus offers seeded (10min/1hr, 20min/4p, 30min/2hr, 40min+snack/3hr).")

    # ── 11. GALLERY ───────────────────────────────────────────────────────────
    GalleryCategory.objects.all().delete()
    gc_ps5,  _ = GalleryCategory.objects.get_or_create(slug='ps5',   defaults={'name': 'PS5 Lounge',        'icon': 'gamepad-2'})
    gc_sim,  _ = GalleryCategory.objects.get_or_create(slug='sim',   defaults={'name': 'Sim Racing Rig',    'icon': 'gauge'})
    gc_ev,   _ = GalleryCategory.objects.get_or_create(slug='events',defaults={'name': 'Game Nights',       'icon': 'trophy'})
    gc_cafe, _ = GalleryCategory.objects.get_or_create(slug='cafe',  defaults={'name': 'The Adda Vibe',     'icon': 'coffee'})

    GalleryItem.objects.all().delete()
    for title, cat, url, feat in [
        ("PS5 Sofa Suite — 65\" 4K Gaming",       gc_ps5,  'https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=800&q=80', True),
        ("Tekken 8 Sofa Battle — Kopar Khairane", gc_ps5,  'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?auto=format&fit=crop&w=800&q=80', True),
        ("Sim Racing — F1 Wheel + PS5",            gc_sim,  'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=800&q=80', True),
        ("WWE 2K25 Crown the Champion Night",      gc_ev,   'https://images.unsplash.com/photo-1547347298-4074fc3086f0?auto=format&fit=crop&w=800&q=80', True),
        ("Chill Gaming with Kurkure & Pepsi",       gc_cafe, 'https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?auto=format&fit=crop&w=800&q=80', False),
    ]:
        GalleryItem.objects.get_or_create(title=title, defaults={'category': cat, 'image_url': url, 'is_featured': feat})
    print("  [+] Gallery seeded.")

    # ── 12. REVIEWS ───────────────────────────────────────────────────────────
    Review = None
    try:
        from apps.engagement.models import Review
    except: pass
    if Review:
        for user, stars, title, comment, admin_r in [
            (created_users['gamer1'], 5,
             "Best PS5 Setup in Navi Mumbai!",
             "Came with 3 friends for WWE 2K25 — 4 of us on the sofa, staff gave us extra time! "
             "The 65\" 4K screen is insane. The Kurkure and Pepsi were a bonus. Highly recommended!",
             "Thank you ViperX! See you next weekend 🎮"),
            (created_users['gamer2'], 5,
             "Sim Racing is a Must-Try!",
             "Booked the steering wheel station for F1 2024 — force feedback felt so real! "
             "Staff set up everything quickly. Got ₹10 off with SIMPRO code. Loved it!",
             "Glad you had a blast ShadowNinja! Come race again anytime."),
            (created_users['gamer3'], 5,
             "MEGA3HR Offer is Unbeatable Value!",
             "Used the MEGA3HR code — got 3hrs, 40 min free AND a free Kurkure. Played God of War "
             "and GTA V back to back. This place has the best PS5 in Kopar Khairane!",
             "Thanks NeonGhost! That MEGA deal is our pride and joy 🏆"),
        ]:
            Review.objects.get_or_create(user=user, title=title, defaults={
                'rating': stars, 'hardware_rating': stars, 'atmosphere_rating': stars,
                'service_rating': stars, 'comment': comment, 'admin_response': admin_r,
                'is_verified_booking': True, 'status': 'APPROVED',
            })
    print("  [+] Reviews seeded.")

    # ── 13. DEMO LIVE SESSION ─────────────────────────────────────────────────
    today = now.date()
    seat_ps5_01 = Seat.objects.get(code='PS5-01')
    b1, _ = Booking.objects.get_or_create(
        booking_reference='GA-DEMO-PS501',
        defaults={
            'user':            created_users['gamer2'],
            'customer_name':   'Ananya Rao (ShadowNinja)',
            'customer_email':  created_users['gamer2'].email,
            'customer_phone':  '+919876500002',
            'zone':            console_zone,
            'booking_date':    today,
            'start_time':      time(15, 0),
            'end_time':        time(17, 0),
            'duration_hours':  Decimal('2.0'),
            'status':          'IN_SESSION',
            'base_amount':     Decimal('120.00'),
            'addons_amount':   Decimal('40.00'),
            'discount_amount': Decimal('0.00'),
            'tax_amount':      Decimal('28.80'),
            'total_amount':    Decimal('188.80'),
        }
    )
    BookingSeat.objects.get_or_create(booking=b1, seat=seat_ps5_01)
    pay1, _ = Payment.objects.get_or_create(booking=b1, defaults={
        'amount': b1.total_amount, 'payment_method': 'UPI',
        'status': 'SUCCESS', 'paid_at': now - timedelta(minutes=30),
    })
    Invoice.objects.get_or_create(booking=b1, defaults={
        'payment': pay1, 'subtotal': Decimal('160.00'),
        'discount_amount': Decimal('0.00'), 'tax_amount': Decimal('28.80'),
        'total_amount': b1.total_amount,
    })
    BookingSession.objects.get_or_create(booking=b1, seat=seat_ps5_01, defaults={
        'status':            'IN_PROGRESS',
        'actual_start_time': now - timedelta(minutes=30),
        'expected_end_time': now + timedelta(minutes=90),
        'checked_in_by':     created_users['staff'],
    })
    seat_ps5_01.status = 'OCCUPIED'
    seat_ps5_01.save()
    print("  [+] Demo live session on PS5-01 active.")

    # ── 14. AUDIT LOG ─────────────────────────────────────────────────────────
    AuditLog.objects.create(
        actor=created_users['admin'], actor_name='RootAdmin', actor_role='Super Admin',
        action_type='CREATE', entity_name='System', entity_id='1',
        description="Gamer's Adda — Full seed v3. PS5 only. Navi Mumbai. 8 games. 5 offers."
    )

    print("\n[SUCCESS] ✅ Seed Complete!")
    print("=" * 62)
    print("  Address   : Shankar Mahadev Apt, Sector 5, Kopar Khairane")
    print("  Stations  : PS5-01 (₹60/hr) | SIM-01 (₹80/hr) | PS5-03 (₹60/hr)")
    print("  Games     : FC26, WWE2K25, WWE2K26, GTA5, GoW, F1 2024, MK1, MK11")
    print("  Snacks    : Pepsi, Thums Up, Fanta, Kurkure, Masala Munch, etc.")
    print("  Offers    : +10min/1hr | +20min/4p | +30min/2hr | +40min+snack/3hr")
    print("  Payment   : Razorpay gateway (set RAZORPAY_KEY_ID in env)")
    print("  Admin     : admin/admin123 | Staff: staff/staff123")
    print("=" * 62)

if __name__ == '__main__':
    seed_all()
