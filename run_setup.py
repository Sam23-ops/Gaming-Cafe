import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gammers_adda.settings')
django.setup()

from django.core.management import call_command

print(">>> STEP 1: RUNNING SYSTEM CHECK...", flush=True)
call_command('check')
print(">>> SYSTEM CHECK PASSED!", flush=True)

print(">>> STEP 2: RUNNING MAKEMIGRATIONS...", flush=True)
call_command('makemigrations', interactive=False)
print(">>> MAKEMIGRATIONS FINISHED!", flush=True)

print(">>> STEP 3: RUNNING MIGRATE...", flush=True)
call_command('migrate', interactive=False)
print(">>> MIGRATE FINISHED!", flush=True)

print(">>> STEP 4: SEEDING DATABASE...", flush=True)
from seed_data import seed_all
seed_all()
print(">>> SEEDING COMPLETED!", flush=True)

print(">>> ALL DATABASE INITIALIZATION COMPLETE!", flush=True)
