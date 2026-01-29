"""
Script to create sample role and permission data for testing
This will create some example roles and permissions to demonstrate the system
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

# Sample data to create
SAMPLE_ROLES = [
    {
        'role_id': 'R001',
        'name': 'Super Admin',
        'description': 'Full system access with all permissions',
        'default_page': '/dashboard',
        'is_active': True,
        'permissions': [
            {'page_path': '/', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/dashboard', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'create', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'edit', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'delete', 'is_allowed': True},
            {'page_path': '/roles', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/roles', 'permission_type': 'create', 'is_allowed': True},
            {'page_path': '/roles', 'permission_type': 'edit', 'is_allowed': True},
            {'page_path': '/roles', 'permission_type': 'delete', 'is_allowed': True},
        ]
    },
    {
        'role_id': 'R002',
        'name': 'Admin',
        'description': 'Administrative access with most permissions',
        'default_page': '/dashboard',
        'is_active': True,
        'permissions': [
            {'page_path': '/', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/dashboard', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'create', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'edit', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'delete', 'is_allowed': False},
            {'page_path': '/roles', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/roles', 'permission_type': 'create', 'is_allowed': False},
            {'page_path': '/roles', 'permission_type': 'edit', 'is_allowed': False},
            {'page_path': '/roles', 'permission_type': 'delete', 'is_allowed': False},
        ]
    },
    {
        'role_id': 'R003',
        'name': 'Manager',
        'description': 'Manager level access with limited permissions',
        'default_page': '/dashboard',
        'is_active': True,
        'permissions': [
            {'page_path': '/', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/dashboard', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'create', 'is_allowed': False},
            {'page_path': '/users', 'permission_type': 'edit', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'delete', 'is_allowed': False},
            {'page_path': '/roles', 'permission_type': 'view', 'is_allowed': False},
        ]
    },
    {
        'role_id': 'R004',
        'name': 'User',
        'description': 'Basic user with view-only access',
        'default_page': '/dashboard',
        'is_active': True,
        'permissions': [
            {'page_path': '/', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/dashboard', 'permission_type': 'view', 'is_allowed': True},
            {'page_path': '/users', 'permission_type': 'view', 'is_allowed': False},
        ]
    },
]

def create_sample_data():
    """Create sample roles and permissions"""
    cursor = connection.cursor()
    now = timezone.now()
    roles_created = 0
    permissions_created = 0
    
    for role_data in SAMPLE_ROLES:
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
            print(f"⊘ Role {role_id} ({name}) already exists. Skipping...")
            # Still create permissions if they don't exist
            for perm in permissions:
                page_path = perm['page_path']
                permission_type = perm['permission_type']
                is_allowed = perm.get('is_allowed', True)
                
                cursor.execute("""
                    SELECT COUNT(*) FROM frontend_role_permissions 
                    WHERE role_id = %s AND page_path = %s AND permission_type = %s
                """, [role_id, page_path, permission_type])
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO frontend_role_permissions 
                        (role_id, name, page_path, permission_type, is_allowed, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (role_id, page_path, permission_type) DO NOTHING
                    """, [role_id, name, page_path, permission_type, is_allowed, now, now])
                    permissions_created += 1
            continue
        
        # Create role
        cursor.execute("""
            INSERT INTO frontend_role (role_id, name, description, default_page, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [role_id, name, description, default_page, is_active, now, now])
        
        roles_created += 1
        print(f"✓ Created role: {role_id} - {name}")
        
        # Create permissions
        for perm in permissions:
            page_path = perm['page_path']
            permission_type = perm['permission_type']
            is_allowed = perm.get('is_allowed', True)
            
            cursor.execute("""
                INSERT INTO frontend_role_permissions 
                (role_id, name, page_path, permission_type, is_allowed, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (role_id, page_path, permission_type) DO NOTHING
            """, [role_id, name, page_path, permission_type, is_allowed, now, now])
            
            permissions_created += 1
        
        print(f"  → Created {len(permissions)} permissions for {role_id}")
    
    connection.commit()
    
    print("\n" + "=" * 60)
    print(f"Sample Data Creation Summary:")
    print(f"  ✓ Roles created: {roles_created}")
    print(f"  ✓ Permissions created: {permissions_created}")
    print("=" * 60)

def verify_data():
    """Verify the created data"""
    cursor = connection.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM frontend_role")
    role_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
    perm_count = cursor.fetchone()[0]
    
    print(f"\nDatabase Status:")
    print(f"  Roles: {role_count}")
    print(f"  Permissions: {perm_count}")
    
    if role_count > 0:
        print("\nRoles in database:")
        cursor.execute("SELECT role_id, name, is_active FROM frontend_role ORDER BY role_id")
        for row in cursor.fetchall():
            status = "Active" if row[2] else "Inactive"
            print(f"  {row[0]} - {row[1]} ({status})")
    
    if perm_count > 0:
        print(f"\nSample permissions (showing first 10):")
        cursor.execute("""
            SELECT role_id, page_path, permission_type, is_allowed 
            FROM frontend_role_permissions 
            ORDER BY role_id, page_path, permission_type 
            LIMIT 10
        """)
        for row in cursor.fetchall():
            status = "allowed" if row[3] else "denied"
            print(f"  {row[0]} | {row[1]:30} | {row[2]:10} | {status}")

if __name__ == '__main__':
    print("=" * 60)
    print("Sample Role & Permission Data Creation Script")
    print("=" * 60)
    print("\nThis script will create sample roles and permissions for testing.")
    print("It will create:")
    print("  - 4 sample roles (Super Admin, Admin, Manager, User)")
    print("  - Multiple permissions for each role")
    print("\n⚠ This will create data in your database!")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print("\nCreating sample data...")
    create_sample_data()
    
    verify_data()
    
    print("\n" + "=" * 60)
    print("Sample data creation complete!")
    print("=" * 60)

