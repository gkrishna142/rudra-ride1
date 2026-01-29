"""
Script to delete data from BOTH frontend_role and frontend_role_permissions tables
Keeps table structures intact, only deletes data
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def delete_both_tables_data():
    """Delete data from both frontend_role_permissions and frontend_role tables"""
    cursor = connection.cursor()
    
    # Check current counts
    cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
    perm_count_before = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM frontend_role")
    role_count_before = cursor.fetchone()[0]
    
    print(f"Current data:")
    print(f"  frontend_role_permissions: {perm_count_before} records")
    print(f"  frontend_role: {role_count_before} records")
    
    if perm_count_before == 0 and role_count_before == 0:
        print("\n⚠ Both tables are already empty.")
        return
    
    try:
        # Step 1: Delete permissions first (to avoid foreign key constraint issues)
        if perm_count_before > 0:
            print(f"\nDeleting {perm_count_before} permissions from frontend_role_permissions...")
            cursor.execute("DELETE FROM frontend_role_permissions")
            deleted_perms = cursor.rowcount
            print(f"✓ Deleted {deleted_perms} permissions")
        
        # Step 2: Delete roles
        if role_count_before > 0:
            print(f"\nDeleting {role_count_before} roles from frontend_role...")
            cursor.execute("DELETE FROM frontend_role")
            deleted_roles = cursor.rowcount
            print(f"✓ Deleted {deleted_roles} roles")
        
        connection.commit()
        
        # Verify deletion
        cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
        perm_count_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM frontend_role")
        role_count_after = cursor.fetchone()[0]
        
        print(f"\n✓ Verification:")
        print(f"   frontend_role_permissions: {perm_count_after} records (was {perm_count_before})")
        print(f"   frontend_role: {role_count_after} records (was {role_count_before})")
        
        if perm_count_after == 0 and role_count_after == 0:
            print("\n✓ Both tables are now empty (table structures preserved)")
        
    except Exception as e:
        connection.rollback()
        print(f"\n✗ Error deleting data: {e}")
        
        # If foreign key constraint error, try dropping constraint first
        if "foreign key" in str(e).lower() or "constraint" in str(e).lower():
            print("\n⚠ Foreign key constraint detected. Trying alternative method...")
            try:
                # Try to find and drop the constraint
                cursor.execute("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'frontend_role_permissions' 
                    AND constraint_type = 'FOREIGN KEY'
                    AND constraint_name LIKE '%role_id%'
                    LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    constraint_name = result[0]
                    print(f"   Dropping constraint: {constraint_name}")
                    cursor.execute(f"""
                        ALTER TABLE frontend_role_permissions 
                        DROP CONSTRAINT IF EXISTS {constraint_name}
                    """)
                    
                    # Now delete data
                    if perm_count_before > 0:
                        cursor.execute("DELETE FROM frontend_role_permissions")
                    if role_count_before > 0:
                        cursor.execute("DELETE FROM frontend_role")
                    
                    connection.commit()
                    print("✓ Data deleted successfully after dropping constraint")
                else:
                    print("✗ Could not find constraint. Please run SQL manually in pgAdmin.")
                    print("\nSQL to run in pgAdmin:")
                    print("""
-- Drop constraint
ALTER TABLE frontend_role_permissions 
DROP CONSTRAINT IF EXISTS frontend_role_permis_role_id_6897cda1_fk_frontend_;

-- Delete data
DELETE FROM frontend_role_permissions;
DELETE FROM frontend_role;
                    """)
            except Exception as e2:
                print(f"✗ Alternative method also failed: {e2}")
                raise
        else:
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Delete Data from frontend_role and frontend_role_permissions")
    print("=" * 60)
    print("\nThis script will delete ALL data from:")
    print("  - frontend_role_permissions table")
    print("  - frontend_role table")
    print("\nTable structures will remain intact.")
    print("\n⚠ WARNING: This action cannot be undone!")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print("\nDeleting data from both tables...")
    delete_both_tables_data()
    
    print("\n" + "=" * 60)
    print("Deletion complete!")
    print("=" * 60)

