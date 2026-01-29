"""Verify zone management tables were created successfully"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('frontend_zone', 'zone_driver', 'zone_ride')
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print("=" * 70)
    print("ZONE MANAGEMENT TABLES VERIFICATION")
    print("=" * 70)
    print("\nTables created:")
    for table in ['frontend_zone', 'zone_driver', 'zone_ride']:
        if table in tables:
            print(f"  ✓ {table}")
        else:
            print(f"  ✗ {table} - MISSING")
    
    print("\n" + "=" * 70)
    if len(tables) == 3:
        print("✓ ALL TABLES CREATED SUCCESSFULLY!")
        print("\nTable names:")
        print("  - frontend_zone (zones table)")
        print("  - zone_driver (drivers table)")
        print("  - zone_ride (rides table)")
    else:
        print(f"⚠ Only {len(tables)}/3 tables found")
    print("=" * 70)

