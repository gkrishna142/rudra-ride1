"""
Script to restore role_permissions table data
Modify the PERMISSIONS_DATA section below with your actual permission data
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
# PERMISSIONS DATA - Modify this with your actual data
# ============================================
PERMISSIONS_DATA = [
    # Example format:
    # {
    #     'role_id': 'R001',  # Must exist in frontend_role table
    #     'name': 'Super Admin',  # Role name (will be fetched from role if not provided)
    #     'page_path': '/',
    #     'permission_type': 'view',  # view, create, edit, delete
    #     'is_allowed': True
    # },
    # {
    #     'role_id': 'R001',
    #     'page_path': '/users',
    #     'permission_type': 'view',
    #     'is_allowed': True
    # },
    # {
    #     'role_id': 'R001',
    #     'page_path': '/users',
    #     'permission_type': 'create',
    #     'is_allowed': True
    # },
    # {
    #     'role_id': 'R001',
    #     'page_path': '/users',
    #     'permission_type': 'edit',
    #     'is_allowed': True
    # },
    # {
    #     'role_id': 'R001',
    #     'page_path': '/users',
    #     'permission_type': 'delete',
    #     'is_allowed': False
    # },
    # Add more permissions here...
]

def get_role_name(role_id):
    """Get role name from role_id"""
    cursor = connection.cursor()
    cursor.execute(
        "SELECT name FROM frontend_role WHERE role_id = %s",
        [role_id]
    )
    result = cursor.fetchone()
    return result[0] if result else None

def restore_permissions():
    """Restore role permissions"""
    if not PERMISSIONS_DATA:
        print("⚠ No permission data provided. Please modify PERMISSIONS_DATA in the script.")
        print("\nExample format:")
        print("PERMISSIONS_DATA = [")
        print("    {'role_id': 'R001', 'page_path': '/', 'permission_type': 'view', 'is_allowed': True},")
        print("    {'role_id': 'R001', 'page_path': '/users', 'permission_type': 'create', 'is_allowed': True},")
        print("    {'role_id': 'R001', 'page_path': '/users', 'permission_type': 'edit', 'is_allowed': True},")
        print("    {'role_id': 'R001', 'page_path': '/users', 'permission_type': 'delete', 'is_allowed': False},")
        print("]")
        print("\n⚠ IMPORTANT: Roles must exist in frontend_role table before restoring permissions!")
        print("   Use the API endpoint POST /api/auth/roles/ to create roles first.")
        return
    
    cursor = connection.cursor()
    created_count = 0
    skipped_count = 0
    error_count = 0
    now = timezone.now()
    
    # First, check which roles exist
    cursor.execute("SELECT role_id, name FROM frontend_role")
    existing_roles = {row[0]: row[1] for row in cursor.fetchall()}
    
    if not existing_roles:
        print("⚠ No roles found in frontend_role table.")
        print("Please create roles first before restoring permissions.")
        return
    
    print(f"Found {len(existing_roles)} existing roles: {', '.join(existing_roles.keys())}\n")
    
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
        
        # Get role name (use provided name or fetch from database)
        role_name = perm_data.get('name') or existing_roles[role_id]
        
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
            print(f"✓ Created: {role_id} | {page_path} | {permission_type} | {status}")
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
    """List all existing permissions for reference"""
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
    print("Role Permissions Restoration Script")
    print("=" * 60)
    
    # List existing permissions
    print("\nCurrent state:")
    list_existing_permissions()
    
    print("\nThis script will restore role permissions.")
    print("Please modify the PERMISSIONS_DATA section in the script")
    print("with your actual permission data before running.\n")
    
    response = input("Do you want to proceed with restoration? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print("\nRestoring permissions...")
    restore_permissions()
    
    # List permissions after restoration
    print("\nFinal state:")
    list_existing_permissions()

