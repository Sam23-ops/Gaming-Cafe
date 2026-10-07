"""
Quick fix to add missing database column
"""
import sqlite3
import os

# Connect to database
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add the missing column to bookings_booking table
    cursor.execute('''
        ALTER TABLE bookings_booking 
        ADD COLUMN session_started_notification_sent INTEGER DEFAULT 0
    ''')
    conn.commit()
    print("✅ Successfully added 'session_started_notification_sent' column to bookings_booking table!")
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e).lower():
        print("✓ Column already exists - no action needed")
    else:
        print(f"❌ Error: {e}")
finally:
    conn.close()

print("\n🎮 Database updated! You can now access the dashboard.")
print("🌐 Visit: http://127.0.0.1:8000/accounts/dashboard/")
