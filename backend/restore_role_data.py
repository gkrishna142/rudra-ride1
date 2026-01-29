"""
Script to restore role data
Run this script and provide the role details when prompted, or modify the DATA section below
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from frontend.models import Role, RolePermission, UserRole
from django.db import connection
from types import SimpleNamespace

# ============================================
# DATA SECTION - Modify this with your role data
# ============================================
ROLES_DATA = [
    # Example format:
    # {
    #     'role_id': 'R001',
    #     'name': 'Super Admin',
    #     'description': 'Full system access',
    #     'default_page': '/dashboard',
    #     'is_active': True,
    #     'permissions': [
    #         {'page_path': '/', 'permission_type': 'view', 'is_allowed': True},
    #         {'page_path': '/users', 'permission_type': 'view', 'is_allowed': True},
    #         {'page_path': '/users', 'permission_type': 'create', 'is_allowed': True},
    #         {'page_path': '/users', 'permission_type': 'edit', 'is_allowed': True},
    #         {'page_path': '/users', 'permission_type': 'delete', 'is_allowed': True},
    #     ]
    # },
    # Add more roles here...
]

USER_ROLES_DATA = [
    # Example format:
    # {
    #     'user_id': 1,  # Replace with actual user ID
    #     'role_id': 'R001',
    #     'is_active': True
    # },
    # Add more user-role assignments here...
]

def restore_roles():
    """Restore roles and their permissions"""
    if not ROLES_DATA:
        print("No role data provided. Please modify ROLES_DATA in the script.")
        return
    
    cursor = connection.cursor()
    created_count = 0
    permission_count = 0
    
    for role_data in ROLES_DATA:
        role_id = role_data['role_id']
        name = role_data['name']
        description = role_data.get('description', '')
        default_page = role_data.get('default_page', '/')
        is_active = role_data.get('is_active', True)
        permissions = role_data.get('permissions', [])
        
        # Check if role already exists
        cursor.execute(
            "SELECT COUNT(*) FROM frontend_role WHERE role_id = %s",
            [role_id]
        )
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            print(f"Role {role_id} ({name}) already exists. Skipping...")
            continue
        
        # Create role using raw SQL
        cursor.execute("""
            INSERT INTO frontend_role (role_id, name, description, default_page, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """, [role_id, name, description, default_page, is_active])
        
        created_count += 1
        print(f"✓ Created role: {role_id} - {name}")
        
        # Create permissions using raw SQL
        for perm in permissions:
            page_path = perm['page_path']
            permission_type = perm['permission_type']
            is_allowed = perm.get('is_allowed', True)
            
            # Use INSERT ... ON CONFLICT DO NOTHING to avoid duplicates
            cursor.execute("""
                INSERT INTO frontend_role_permissions 
                (role_id, page_path, permission_type, is_allowed, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (role_id, page_path, permission_type) DO NOTHING
            """, [role_id, page_path, permission_type, is_allowed])
            
            permission_count += 1
        
        print(f"  → Created {len(permissions)} permissions for {role_id}")
    
    connection.commit()
    print(f"\n✓ Restored {created_count} roles and {permission_count} permissions")

def restore_user_roles():
    """Restore user-role assignments"""
    if not USER_ROLES_DATA:
        print("No user-role data provided. Skipping user-role assignments...")
        return
    
    cursor = connection.cursor()
    created_count = 0
    
    for user_role_data in USER_ROLES_DATA:
        user_id = user_role_data['user_id']
        role_id = user_role_data['role_id']
        is_active = user_role_data.get('is_active', True)
        
        # Check if user exists
        cursor.execute(
            "SELECT COUNT(*) FROM frontend_user WHERE id = %s",
            [user_id]
        )
        user_exists = cursor.fetchone()[0] > 0
        
        if not user_exists:
            print(f"⚠ User ID {user_id} does not exist. Skipping user-role assignment...")
            continue
        
        # Check if role exists
        cursor.execute(
            "SELECT COUNT(*) FROM frontend_role WHERE role_id = %s",
            [role_id]
        )
        role_exists = cursor.fetchone()[0] > 0
        
        if not role_exists:
            print(f"⚠ Role {role_id} does not exist. Skipping user-role assignment...")
            continue
        
        # Check if assignment already exists
        cursor.execute("""
            SELECT COUNT(*) FROM frontend_user_roles 
            WHERE user_id = %s AND role_id = %s
        """, [user_id, role_id])
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            print(f"User-role assignment (user_id={user_id}, role_id={role_id}) already exists. Skipping...")
            continue
        
        # Create user-role assignment
        cursor.execute("""
            INSERT INTO frontend_user_roles (user_id, role_id, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
        """, [user_id, role_id, is_active])
        
        created_count += 1
        print(f"✓ Created user-role assignment: user_id={user_id}, role_id={role_id}")
    
    connection.commit()
    print(f"\n✓ Restored {created_count} user-role assignments")

if __name__ == '__main__':
    print("=" * 60)
    print("Role Data Restoration Script")
    print("=" * 60)
    print("\nThis script will restore roles, permissions, and user-role assignments.")
    print("Please modify the ROLES_DATA and USER_ROLES_DATA sections in the script")
    print("with your actual data before running.\n")
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print("\nRestoring roles and permissions...")
    restore_roles()
    
    print("\nRestoring user-role assignments...")
    restore_user_roles()
    
    print("\n" + "=" * 60)
    print("Restoration complete!")
    print("=" * 60)

