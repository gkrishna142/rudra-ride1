#!/usr/bin/env python
"""
Test script to verify that string role_ids like "R001" can be saved.
Run this after the database migration is complete.

Usage: python manage.py shell < test_role_id_save.py
OR: python manage.py shell
    Then copy-paste the code below
"""
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(backend_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Change to backend directory
os.chdir(backend_dir)

# Setup Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
try:
    django.setup()
except django.core.exceptions.ImproperlyConfigured as e:
    # If there's a namespace issue, try a different approach
    print("Warning: Django setup issue detected. Trying alternative method...")
    # Remove any conflicting frontend paths
    import importlib
    if 'frontend' in sys.modules:
        del sys.modules['frontend']
    django.setup()

from frontend.models import User as FrontendUser
from django.db import connection

def check_column_type():
    """Check if role_id column is VARCHAR"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'frontend_user' AND column_name = 'role_id';
        """)
        result = cursor.fetchone()
        if result:
            column_name, data_type, max_length = result
            print(f"Column: {column_name}")
            print(f"Data Type: {data_type}")
            print(f"Max Length: {max_length}")
            
            if data_type == 'character varying' and max_length == 50:
                print("✅ Column type is correct (VARCHAR(50))")
                return True
            else:
                print(f"❌ Column type is {data_type}, expected 'character varying'")
                return False
        else:
            print("❌ Column not found")
            return False

def test_save_role_id():
    """Test saving a string role_id"""
    try:
        # Try to create a test user with role_id "R001"
        test_user = FrontendUser.objects.create(
            name="Test User",
            email=f"test_{os.urandom(4).hex()}@example.com",
            password="test123",
            role_id="R001",
            phone_number="1234567890"
        )
        print(f"✅ Successfully saved user with role_id='R001' (User ID: {test_user.id})")
        
        # Verify it was saved correctly
        saved_user = FrontendUser.objects.get(id=test_user.id)
        if saved_user.role_id == "R001":
            print("✅ Verified: role_id was saved correctly as 'R001'")
        else:
            print(f"❌ Error: role_id was saved as '{saved_user.role_id}' instead of 'R001'")
        
        # Clean up - delete test user
        test_user.delete()
        print("✅ Test user deleted")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if 'invalid input syntax for type integer' in error_msg.lower():
            print("❌ ERROR: Database column is still INTEGER type.")
            print("   Please run the migration: ALTER TABLE frontend_user ALTER COLUMN role_id TYPE VARCHAR(50)...")
        else:
            print(f"❌ ERROR: {error_msg}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing role_id Column Type and String Value Saving")
    print("=" * 60)
    print()
    
    print("Step 1: Checking column type...")
    column_ok = check_column_type()
    print()
    
    if column_ok:
        print("Step 2: Testing save with role_id='R001'...")
        save_ok = test_save_role_id()
        print()
        
        if save_ok:
            print("=" * 60)
            print("✅ SUCCESS: Everything is working correctly!")
            print("   You can now save role_id values like 'R001', 'R002', etc.")
            print("=" * 60)
        else:
            print("=" * 60)
            print("❌ FAILED: Could not save string role_id")
            print("=" * 60)
    else:
        print("=" * 60)
        print("❌ Column type is incorrect. Please run the database migration first.")
        print("   See: backend/frontend/migrations/QUICK_SQL_FOR_DBA.sql")
        print("=" * 60)

