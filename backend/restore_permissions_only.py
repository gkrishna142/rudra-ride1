"""
Script to restore ONLY frontend_role_permissions table data
Note: Roles must exist in frontend_role table first (due to foreign key constraints)
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from django.utils import timezone

# ============================================
# PERMISSIONS DATA - Add your permission data here
# ============================================
PERMISSIONS_DATA = [
    # Example format:
    # {
    #     'role_id': 'R001',  # Must exist in frontend_role table
    #     'page_path': '/',
    #     'permission_type': 'view',  # view, create, edit, delete
    #     'is_allowed': True
    # },
    # Add your permissions here...
]

def restore_permissions_only():
    """Restore only frontend_role_permissions table data"""
    cursor = connection.cursor()
    
    # Check if roles exist
    cursor.execute("SELECT COUNT(*) FROM frontend_role")
    role_count = cursor.fetchone()[0]
    
    if role_count == 0:
        print("⚠ ERROR: No roles found in frontend_role table!")
        print("   Permissions require roles to exist first (foreign key constraint).")
        print("\n   Please create roles first using one of these methods:")
        print("   1. Run: python create_sample_role_data.py (creates sample roles)")
        print("   2. Use API: POST /api/auth/roles/")
        print("   3. Use API: POST /api/auth/role-with-permissions/")
        return
    
    # Get existing roles
    cursor.execute("SELECT role_id, name FROM frontend_role")
    existing_roles = {row[0]: row[1] for row in cursor.fetchall()}
    print(f"✓ Found {len(existing_roles)} existing roles: {', '.join(existing_roles.keys())}\n")
    
    if not PERMISSIONS_DATA:
        print("⚠ No permission data provided. Please modify PERMISSIONS_DATA in the script.")
        print("\nExample format:")
        print("PERMISSIONS_DATA = [")
        print("    {'role_id': 'R001', 'page_path': '/', 'permission_type': 'view', 'is_allowed': True},")
        print("    {'role_id': 'R001', 'page_path': '/users', 'permission_type': 'create', 'is_allowed': True},")
        print("]")
        return
    
    now = timezone.now()
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for perm_data in PERMISSIONS_DATA:
        role_id = perm_data.get('role_id')
        page_path = perm_data.get('page_path')
        permission_type = perm_data.get('permission_type')
        is_allowed = perm_data.get('is_allowed', True)
        
        # Validate required fields
        if not role_id or not page_path or not permission_type:
            print(f"⚠ Skipping invalid permission (missing required fields): {perm_data}")
            error_count += 1
            continue
        
        # Check if role exists
        if role_id not in existing_roles:
            print(f"⚠ Role {role_id} does not exist. Skipping permission...")
            error_count += 1
            continue
        
        # Get role name
        role_name = existing_roles[role_id]
        
        # Check if permission already exists
        cursor.execute("""
            SELECT COUNT(*) FROM frontend_role_permissions 
            WHERE role_id = %s AND page_path = %s AND permission_type = %s
        """, [role_id, page_path, permission_type])
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            print(f"⊘ Permission already exists: {role_id} | {page_path} | {permission_type} (skipping)")
            skipped_count += 1
            continue
        
        # Insert permission using raw SQL
        try:
            cursor.execute("""
                INSERT INTO frontend_role_permissions 
                (role_id, name, page_path, permission_type, is_allowed, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (role_id, page_path, permission_type) DO NOTHING
            """, [role_id, role_name, page_path, permission_type, is_allowed, now, now])
            
            created_count += 1
            status = "allowed" if is_allowed else "denied"
            print(f"✓ Created: {role_id} | {page_path:30} | {permission_type:10} | {status}")
        except Exception as e:
            print(f"✗ Error creating permission {role_id} | {page_path} | {permission_type}: {e}")
            error_count += 1
    
    connection.commit()
    
    print("\n" + "=" * 60)
    print(f"Restoration Summary:")
    print(f"  ✓ Created: {created_count} permissions")
    print(f"  ⊘ Skipped (already exist): {skipped_count} permissions")
    print(f"  ✗ Errors: {error_count} permissions")
    print("=" * 60)

def list_existing_permissions():
    """List all existing permissions"""
    cursor = connection.cursor()
    cursor.execute("""
        SELECT role_id, name, page_path, permission_type, is_allowed
        FROM frontend_role_permissions
        ORDER BY role_id, page_path, permission_type
    """)
    permissions = cursor.fetchall()
    
    if not permissions:
        print("No existing permissions found.")
        return
    
    print(f"\nExisting permissions ({len(permissions)} total):")
    print("-" * 80)
    for perm in permissions:
        role_id, name, page_path, perm_type, is_allowed = perm
        status = "allowed" if is_allowed else "denied"
        print(f"  {role_id} | {page_path:30} | {perm_type:10} | {status}")
    print("-" * 80)

if __name__ == '__main__':
    print("=" * 60)
    print("Restore frontend_role_permissions Table Data Only")
    print("=" * 60)
    
    # Check current state
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
    current_count = cursor.fetchone()[0]
    print(f"\nCurrent permissions in database: {current_count}")
    
    # List existing permissions
    if current_count > 0:
        list_existing_permissions()
    
    print("\nThis script will restore permissions to frontend_role_permissions table.")
    print("⚠ IMPORTANT: Roles must exist in frontend_role table first!")
    print("Please modify the PERMISSIONS_DATA section in the script with your data.\n")
    
    response = input("Do you want to proceed with restoration? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print("\nRestoring permissions...")
    restore_permissions_only()
    
    # List permissions after restoration
    print("\nFinal state:")
    list_existing_permissions()

