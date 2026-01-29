"""
Script to delete specific role permissions from the database
Usage: python delete_role_permissions.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from frontend.models import RolePermission
from django.db import connection
import sys

def delete_role_permissions_by_ids_and_type(start_id, end_id, permission_type=None):
    """Delete role permissions with IDs from start_id to end_id (inclusive), optionally filtered by permission_type"""
    try:
        with connection.cursor() as cursor:
            # Check if id column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='frontend_role_permissions' AND column_name='id'
            """)
            has_id_column = cursor.fetchone() is not None
            
            if not has_id_column:
                print("⚠️  Warning: The 'id' column doesn't exist in the database.")
                print("The database uses a composite primary key (role_id, page_path, permission_type).")
                print("\nYou can delete using the DELETE API endpoints instead:")
                print("  - Single permission: DELETE /api/auth/role-permissions/<role_id>/<page_path>/<permission_type>/")
                print("  - All permissions for a role: DELETE /api/auth/role-permissions/<role_id>/")
                return
            
            # Build query to find rows
            query = """
                SELECT id, role_id, page_path, permission_type, is_allowed
                FROM frontend_role_permissions
                WHERE id BETWEEN %s AND %s
            """
            params = [start_id, end_id]
            
            if permission_type:
                query += " AND permission_type = %s"
                params.append(permission_type)
            
            query += " ORDER BY id"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if not rows:
                filter_msg = f" with permission_type='{permission_type}'" if permission_type else ""
                print(f"No rows found with IDs between {start_id} and {end_id}{filter_msg}")
                return
            
            filter_msg = f" and permission_type='{permission_type}'" if permission_type else ""
            print(f"\nFound {len(rows)} rows to delete (IDs {start_id} to {end_id}{filter_msg}):")
            print("-" * 80)
            for row in rows:
                print(f"ID: {row[0]}, Role: {row[1]}, Page: {row[2]}, Permission: {row[3]}, Allowed: {row[4]}")
            print("-" * 80)
            
            # Confirm deletion
            confirm = input(f"\nAre you sure you want to delete these {len(rows)} rows? (yes/no): ")
            if confirm.lower() != 'yes':
                print("Deletion cancelled.")
                return
            
            # Build delete query
            delete_query = """
                DELETE FROM frontend_role_permissions
                WHERE id BETWEEN %s AND %s
            """
            delete_params = [start_id, end_id]
            
            if permission_type:
                delete_query += " AND permission_type = %s"
                delete_params.append(permission_type)
            
            cursor.execute(delete_query, delete_params)
            
            rows_deleted = cursor.rowcount
            filter_msg = f" with permission_type='{permission_type}'" if permission_type else ""
            print(f"\n✅ Successfully deleted {rows_deleted} rows (IDs {start_id} to {end_id}{filter_msg})")
            
    except Exception as e:
        print(f"\n❌ Error deleting rows: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    print("=" * 80)
    print("Delete Role Permissions Script")
    print("=" * 80)
    print("This script will delete rows from frontend_role_permissions table")
    print("with IDs from 46 to 49 and permission_type='view'")
    print("=" * 80)
    
    delete_role_permissions_by_ids_and_type(46, 49, permission_type='view')

