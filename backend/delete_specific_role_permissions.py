#!/usr/bin/env python
"""
Script to delete specific 4 rows from frontend_role_permissions table
Rows to delete:
- page_path='view', permission_type='view', role_id='R001'
- page_path='view', permission_type='create', role_id='R001'
- page_path='view', permission_type='edit', role_id='R001'
- page_path='view', permission_type='delete', role_id='R001'
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def delete_specific_rows():
    """Delete the 4 specific rows from frontend_role_permissions"""
    
    with connection.cursor() as cursor:
        # First, check how many rows match our criteria
        cursor.execute("""
            SELECT COUNT(*) 
            FROM frontend_role_permissions 
            WHERE page_path = 'view' 
            AND role_id = 'R001'
            AND permission_type IN ('view', 'create', 'edit', 'delete')
        """)
        
        count_before = cursor.fetchone()[0]
        print(f"Found {count_before} rows matching the criteria")
        
        if count_before == 0:
            print("No rows found to delete.")
            return
        
        # Show what will be deleted
        cursor.execute("""
            SELECT page_path, permission_type, role_id, is_allowed 
            FROM frontend_role_permissions 
            WHERE page_path = 'view' 
            AND role_id = 'R001'
            AND permission_type IN ('view', 'create', 'edit', 'delete')
            ORDER BY permission_type
        """)
        
        rows_to_delete = cursor.fetchall()
        print("\nRows to be deleted:")
        print("-" * 80)
        for row in rows_to_delete:
            print(f"  page_path: {row[0]}, permission_type: {row[1]}, role_id: {row[2]}, is_allowed: {row[3]}")
        print("-" * 80)
        
        # Confirm deletion
        response = input(f"\nAre you sure you want to delete these {count_before} row(s)? (yes/no): ")
        
        if response.lower() != 'yes':
            print("Deletion cancelled.")
            return
        
        # Delete the rows
        cursor.execute("""
            DELETE FROM frontend_role_permissions 
            WHERE page_path = 'view' 
            AND role_id = 'R001'
            AND permission_type IN ('view', 'create', 'edit', 'delete')
        """)
        
        deleted_count = cursor.rowcount
        print(f"\n✓ Successfully deleted {deleted_count} row(s)")
        
        # Verify deletion
        cursor.execute("""
            SELECT COUNT(*) 
            FROM frontend_role_permissions 
            WHERE page_path = 'view' 
            AND role_id = 'R001'
            AND permission_type IN ('view', 'create', 'edit', 'delete')
        """)
        
        count_after = cursor.fetchone()[0]
        
        if count_after == 0:
            print("✓ Verification: All target rows have been deleted successfully")
        else:
            print(f"⚠ Warning: {count_after} matching row(s) still exist")

if __name__ == "__main__":
    print("Delete Specific Role Permissions")
    print("=" * 80)
    print("This script will delete exactly 4 rows from frontend_role_permissions:")
    print("  - page_path='view', permission_type='view', role_id='R001'")
    print("  - page_path='view', permission_type='create', role_id='R001'")
    print("  - page_path='view', permission_type='edit', role_id='R001'")
    print("  - page_path='view', permission_type='delete', role_id='R001'")
    print("=" * 80)
    
    try:
        delete_specific_rows()
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

