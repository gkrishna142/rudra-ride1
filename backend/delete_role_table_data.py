"""
Script to delete all data from frontend_role table only
This will delete all roles but keep the table structure
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def delete_role_data():
    """Delete all data from frontend_role table only"""
    cursor = connection.cursor()
    
    # First, check current count
    cursor.execute("SELECT COUNT(*) FROM frontend_role")
    count_before = cursor.fetchone()[0]
    
    if count_before == 0:
        print("⚠ frontend_role table is already empty.")
        return
    
    print(f"Found {count_before} roles in frontend_role table.")
    
    # Check for foreign key constraints
    cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
    perm_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM frontend_user_roles")
    user_role_count = cursor.fetchone()[0]
    
    # Automatically handle foreign key constraints by deleting related data first
    # This is necessary to delete from frontend_role
    if perm_count > 0:
        print(f"\nDeleting {perm_count} related permissions (required for foreign key constraints)...")
        cursor.execute("DELETE FROM frontend_role_permissions")
        print(f"✓ Deleted {perm_count} permissions from frontend_role_permissions")
    
    if user_role_count > 0:
        print(f"Deleting {user_role_count} related user-role assignments (required for foreign key constraints)...")
        cursor.execute("DELETE FROM frontend_user_roles")
        print(f"✓ Deleted {user_role_count} user-role assignments from frontend_user_roles")
    
    # Now delete all roles from frontend_role table
    try:
        print(f"\nDeleting {count_before} roles from frontend_role table...")
        cursor.execute("DELETE FROM frontend_role")
        deleted_count = cursor.rowcount
        connection.commit()
        
        print(f"\n✓ Successfully deleted {deleted_count} roles from frontend_role table")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM frontend_role")
        count_after = cursor.fetchone()[0]
        print(f"✓ Verification: {count_after} roles remaining in frontend_role table")
        
        if count_after == 0:
            print("✓ frontend_role table is now empty (table structure preserved)")
        
    except Exception as e:
        connection.rollback()
        print(f"\n✗ Error deleting roles: {e}")
        raise

if __name__ == '__main__':
    print("=" * 60)
    print("Delete frontend_role Table Data Only")
    print("=" * 60)
    print("\nThis script will delete ALL data from the frontend_role table ONLY.")
    print("The table structure will remain intact.")
    print("\nNote: Related data in frontend_role_permissions and frontend_user_roles")
    print("      will be automatically deleted first due to foreign key constraints.")
    print("\n⚠ WARNING: This action cannot be undone!")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print("\nDeleting data from frontend_role table...")
    delete_role_data()
    
    print("\n" + "=" * 60)
    print("Deletion complete!")
    print("=" * 60)

