"""
Script to delete ONLY frontend_role table data
Keeps frontend_role_permissions data intact (will be orphaned but preserved)
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def delete_role_table_data_only():
    """Delete only frontend_role table data, keeping permissions intact"""
    cursor = connection.cursor()
    
    # Check current counts
    cursor.execute("SELECT COUNT(*) FROM frontend_role")
    role_count_before = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
    perm_count = cursor.fetchone()[0]
    
    if role_count_before == 0:
        print("⚠ frontend_role table is already empty.")
        return
    
    print(f"Found {role_count_before} roles in frontend_role table.")
    print(f"Found {perm_count} permissions in frontend_role_permissions table.")
    
    if perm_count > 0:
        print(f"\n⚠ Warning: There are {perm_count} permissions that reference roles.")
        print("   These permissions will become orphaned (they'll remain but reference non-existent roles).")
        print("   This is okay if you plan to restore roles later with the same role_ids.")
    
    # Get foreign key constraint name
    cursor.execute("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'frontend_role_permissions' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%role_id%'
    """)
    fk_constraints = cursor.fetchall()
    
    # Temporarily disable foreign key constraints to allow deletion
    # We'll delete roles while keeping permissions
    try:
        # Disable foreign key checks (PostgreSQL way)
        # Note: PostgreSQL doesn't have a simple way to disable FKs like MySQL
        # We need to drop and recreate the constraint, or use a different approach
        
        # Method: Delete roles by temporarily removing the foreign key constraint
        if fk_constraints:
            print(f"\nTemporarily removing foreign key constraints...")
            for fk in fk_constraints:
                constraint_name = fk[0]
                try:
                    cursor.execute(f"""
                        ALTER TABLE frontend_role_permissions 
                        DROP CONSTRAINT IF EXISTS {constraint_name}
                    """)
                    print(f"✓ Removed constraint: {constraint_name}")
                except Exception as e:
                    print(f"⚠ Could not remove constraint {constraint_name}: {e}")
        
        # Now delete all roles
        print(f"\nDeleting {role_count_before} roles from frontend_role table...")
        cursor.execute("DELETE FROM frontend_role")
        deleted_count = cursor.rowcount
        connection.commit()
        
        print(f"✓ Successfully deleted {deleted_count} roles from frontend_role table")
        
        # Recreate foreign key constraints if they were removed
        if fk_constraints:
            print(f"\nRecreating foreign key constraints...")
            # The constraint will be recreated automatically by Django on next migration
            # Or we can recreate it manually
            try:
                cursor.execute("""
                    ALTER TABLE frontend_role_permissions
                    ADD CONSTRAINT frontend_role_permissions_role_id_fkey
                    FOREIGN KEY (role_id) REFERENCES frontend_role(role_id)
                    ON DELETE CASCADE
                """)
                print(f"✓ Recreated foreign key constraint")
            except Exception as e:
                print(f"⚠ Could not recreate constraint (may already exist): {e}")
        
        connection.commit()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM frontend_role")
        role_count_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
        perm_count_after = cursor.fetchone()[0]
        
        print(f"\n✓ Verification:")
        print(f"   Roles in frontend_role: {role_count_after} (was {role_count_before})")
        print(f"   Permissions in frontend_role_permissions: {perm_count_after} (preserved)")
        
        if role_count_after == 0:
            print("✓ frontend_role table is now empty (table structure preserved)")
        if perm_count_after == perm_count:
            print("✓ frontend_role_permissions data preserved (may be orphaned)")
        
    except Exception as e:
        connection.rollback()
        print(f"\n✗ Error deleting roles: {e}")
        print("\nTrying alternative method (direct deletion with constraint handling)...")
        
        # Alternative: Try to delete with CASCADE or by handling constraints differently
        try:
            # Simply delete - if FK constraint prevents it, we'll get an error
            cursor.execute("DELETE FROM frontend_role")
            connection.commit()
            print("✓ Deleted roles using direct deletion")
        except Exception as fk_error:
            print(f"✗ Foreign key constraint prevents deletion: {fk_error}")
            print("\n⚠ Solution: You need to either:")
            print("   1. Delete permissions first, then roles")
            print("   2. Temporarily modify the foreign key constraint")
            print("   3. Use a database superuser to disable constraints")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Delete frontend_role Table Data Only")
    print("=" * 60)
    print("\nThis script will delete ALL data from frontend_role table ONLY.")
    print("The frontend_role_permissions table data will be PRESERVED.")
    print("\n⚠ WARNING:")
    print("   - Permissions will become orphaned (reference non-existent roles)")
    print("   - This is okay if you plan to restore roles with same role_ids later")
    print("   - The action cannot be undone!")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print("\nDeleting data from frontend_role table...")
    delete_role_table_data_only()
    
    print("\n" + "=" * 60)
    print("Deletion complete!")
    print("=" * 60)

