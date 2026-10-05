import os
import sys
import traceback
import django
from django.core.management import call_command

def run():
    log_file = open('init_db.log', 'w', encoding='utf-8', buffering=1)
    # Duplicate stdout/stderr to both console and file
    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, obj):
            for f in self.files:
                try:
                    f.write(obj)
                    f.flush()
                except Exception:
                    pass
        def flush(self):
            for f in self.files:
                try:
                    f.flush()
                except Exception:
                    pass

    sys.stdout = Tee(sys.stdout, log_file)
    sys.stderr = Tee(sys.stderr, log_file)

    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gammers_adda.settings')
        django.setup()

        print("=== 1. MAKEMIGRATIONS ===")
        call_command('makemigrations', 'core', 'accounts', 'venue', 'games', 'pricing', 'bookings', 'payments', 'engagement')

        print("\n=== 2. MIGRATE ===")
        call_command('migrate')

        print("\n=== 3. SEED DATA ===")
        from seed_data import seed_all
        seed_all()

        print("\n=== 4. RUN TESTS ===")
        call_command('test', 'apps.bookings')

        print("\n=== ALL COMPLETED SUCCESSFULLY ===")
    except Exception as e:
        print(f"\n❌ ERROR OCCURRED: {e}")
        traceback.print_exc()
    finally:
        log_file.close()

if __name__ == '__main__':
    run()
