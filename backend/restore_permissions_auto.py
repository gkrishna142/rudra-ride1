"""
Script to restore ONLY frontend_role_permissions table data
Automatically creates minimal roles if they don't exist (required for foreign keys)
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

# Sample permissions data
SAMPLE_PERMISSIONS = [
    # R001 - Super Admin
    {'role_id': 'R001', 'page_path': '/', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R001', 'page_path': '/dashboard', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R001', 'page_path': '/users', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R001', 'page_path': '/users', 'permission_type': 'create', 'is_allowed': True},
    {'role_id': 'R001', 'page_path': '/users', 'permission_type': 'edit', 'is_allowed': True},
    {'role_id': 'R001', 'page_path': '/users', 'permission_type': 'delete', 'is_allowed': True},
    {'role_id': 'R001', 'page_path': '/roles', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R001', 'page_path': '/roles', 'permission_type': 'create', 'is_allowed': True},
    {'role_id': 'R001', 'page_path': '/roles', 'permission_type': 'edit', 'is_allowed': True},
    {'role_id': 'R001', 'page_path': '/roles', 'permission_type': 'delete', 'is_allowed': True},
    
    # R002 - Admin
    {'role_id': 'R002', 'page_path': '/', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R002', 'page_path': '/dashboard', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R002', 'page_path': '/users', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R002', 'page_path': '/users', 'permission_type': 'create', 'is_allowed': True},
    {'role_id': 'R002', 'page_path': '/users', 'permission_type': 'edit', 'is_allowed': True},
    {'role_id': 'R002', 'page_path': '/users', 'permission_type': 'delete', 'is_allowed': False},
    {'role_id': 'R002', 'page_path': '/roles', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R002', 'page_path': '/roles', 'permission_type': 'create', 'is_allowed': False},
    {'role_id': 'R002', 'page_path': '/roles', 'permission_type': 'edit', 'is_allowed': False},
    {'role_id': 'R002', 'page_path': '/roles', 'permission_type': 'delete', 'is_allowed': False},
    
    # R003 - Manager
    {'role_id': 'R003', 'page_path': '/', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R003', 'page_path': '/dashboard', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R003', 'page_path': '/users', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R003', 'page_path': '/users', 'permission_type': 'create', 'is_allowed': False},
    {'role_id': 'R003', 'page_path': '/users', 'permission_type': 'edit', 'is_allowed': True},
    {'role_id': 'R003', 'page_path': '/users', 'permission_type': 'delete', 'is_allowed': False},
    {'role_id': 'R003', 'page_path': '/roles', 'permission_type': 'view', 'is_allowed': False},
    
    # R004 - User
    {'role_id': 'R004', 'page_path': '/', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R004', 'page_path': '/dashboard', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R004', 'page_path': '/users', 'permission_type': 'view', 'is_allowed': False},
]

# Role names for auto-creation
ROLE_NAMES = {
    'R001': 'Super Admin',
    'R002': 'Admin',
    'R003': 'Manager',
    'R004': 'User',
}

def ensure_roles_exist():
    """Create roles if they don't exist (required for foreign key constraints)"""
    cursor = connection.cursor()
    now = timezone.now()
    created_count = 0
    
    # Get existing roles
    cursor.execute("SELECT role_id FROM frontend_role")
    existing_role_ids = {row[0] for row in cursor.fetchall()}
    
    # Get unique role_ids from permissions
    required_role_ids = set(perm['role_id'] for perm in SAMPLE_PERMISSIONS)
    
    # Create missing roles
    for role_id in required_role_ids:
        if role_id not in existing_role_ids:
            role_name = ROLE_NAMES.get(role_id, f'Role {role_id}')
            cursor.execute("""
                INSERT INTO frontend_role (role_id, name, description, default_page, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [role_id, role_name, f'Auto-created role for {role_name}', '/', True, now, now])
            created_count += 1
            print(f"✓ Auto-created role: {role_id} - {role_name}")
    
    if created_count > 0:
        connection.commit()
        print(f"\n✓ Created {created_count} roles (required for foreign key constraints)\n")
    
    return created_count

def restore_permissions():
    """Restore permissions to frontend_role_permissions table"""
    cursor = connection.cursor()
    
    # Ensure roles exist first
    ensure_roles_exist()
    
    # Get existing roles
    cursor.execute("SELECT role_id, name FROM frontend_role")
    existing_roles = {row[0]: row[1] for row in cursor.fetchall()}
    
    now = timezone.now()
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for perm_data in SAMPLE_PERMISSIONS:
        role_id = perm_data['role_id']
        page_path = perm_data['page_path']
        permission_type = perm_data['permission_type']
        is_allowed = perm_data.get('is_allowed', True)
        
        # Get role name
        role_name = existing_roles.get(role_id)
        if not role_name:
            error_count += 1
            continue
        
        # Check if permission already exists
        cursor.execute("""
            SELECT COUNT(*) FROM frontend_role_permissions 
            WHERE role_id = %s AND page_path = %s AND permission_type = %s
        """, [role_id, page_path, permission_type])
        exists = cursor.fetchone()[0] > 0
        
        if exists:
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
            print(f"✗ Error: {role_id} | {page_path} | {permission_type}: {e}")
            error_count += 1
    
    connection.commit()
    
    print("\n" + "=" * 60)
    print(f"Restoration Summary:")
    print(f"  ✓ Created: {created_count} permissions")
    print(f"  ⊘ Skipped (already exist): {skipped_count} permissions")
    print(f"  ✗ Errors: {error_count} permissions")
    print("=" * 60)
    
    # Verify final count
    cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
    final_count = cursor.fetchone()[0]
    print(f"\n✓ Total permissions in frontend_role_permissions table: {final_count}")

if __name__ == '__main__':
    print("=" * 60)
    print("Restore frontend_role_permissions Table Data Only")
    print("=" * 60)
    print("\nThis script will restore permissions to frontend_role_permissions table.")
    print("It will automatically create minimal roles if needed (for foreign key constraints).")
    print("\n⚠ This will create data in your database!")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print("\nRestoring permissions...")
    restore_permissions()
    
    print("\n" + "=" * 60)
    print("Restoration complete!")
    print("=" * 60)

