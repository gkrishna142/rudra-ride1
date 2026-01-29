"""
Script to restore frontend_role_permissions table data with sample permissions
This assumes you have roles R001, R002, R003, R004 in frontend_role table
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

# Sample permissions data (matches the sample roles: R001, R002, R003, R004)
SAMPLE_PERMISSIONS = [
    # R001 - Super Admin (Full access)
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
    
    # R002 - Admin (Most permissions, no delete on users, no modify on roles)
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
    
    # R003 - Manager (Limited permissions)
    {'role_id': 'R003', 'page_path': '/', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R003', 'page_path': '/dashboard', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R003', 'page_path': '/users', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R003', 'page_path': '/users', 'permission_type': 'create', 'is_allowed': False},
    {'role_id': 'R003', 'page_path': '/users', 'permission_type': 'edit', 'is_allowed': True},
    {'role_id': 'R003', 'page_path': '/users', 'permission_type': 'delete', 'is_allowed': False},
    {'role_id': 'R003', 'page_path': '/roles', 'permission_type': 'view', 'is_allowed': False},
    
    # R004 - User (View only)
    {'role_id': 'R004', 'page_path': '/', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R004', 'page_path': '/dashboard', 'permission_type': 'view', 'is_allowed': True},
    {'role_id': 'R004', 'page_path': '/users', 'permission_type': 'view', 'is_allowed': False},
]

def restore_permissions():
    """Restore permissions to frontend_role_permissions table"""
    cursor = connection.cursor()
    
    # Check if roles exist
    cursor.execute("SELECT role_id, name FROM frontend_role")
    existing_roles = {row[0]: row[1] for row in cursor.fetchall()}
    
    if not existing_roles:
        print("⚠ ERROR: No roles found in frontend_role table!")
        print("   Permissions require roles to exist first (foreign key constraint).")
        print("\n   Please create roles first:")
        print("   Run: python create_sample_role_data.py")
        return
    
    print(f"✓ Found {len(existing_roles)} existing roles: {', '.join(existing_roles.keys())}\n")
    
    # Check which roles from sample data exist
    required_roles = set(perm['role_id'] for perm in SAMPLE_PERMISSIONS)
    missing_roles = required_roles - set(existing_roles.keys())
    
    if missing_roles:
        print(f"⚠ Warning: Sample permissions require these roles that don't exist: {', '.join(missing_roles)}")
        print("   Permissions for missing roles will be skipped.\n")
    
    now = timezone.now()
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for perm_data in SAMPLE_PERMISSIONS:
        role_id = perm_data['role_id']
        page_path = perm_data['page_path']
        permission_type = perm_data['permission_type']
        is_allowed = perm_data.get('is_allowed', True)
        
        # Check if role exists
        if role_id not in existing_roles:
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
    print(f"  ✗ Errors/Skipped: {error_count} permissions")
    print("=" * 60)
    
    # Verify final count
    cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
    final_count = cursor.fetchone()[0]
    print(f"\n✓ Total permissions in database: {final_count}")

if __name__ == '__main__':
    print("=" * 60)
    print("Restore frontend_role_permissions Table Data")
    print("=" * 60)
    print("\nThis script will restore sample permissions to frontend_role_permissions table.")
    print("It requires roles R001, R002, R003, R004 to exist in frontend_role table.")
    print("\n⚠ This will create permissions in your database!")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print("\nRestoring permissions...")
    restore_permissions()
    
    print("\n" + "=" * 60)
    print("Restoration complete!")
    print("=" * 60)

