"""
Diagnostic script to check PromoCode sequence status
Run: python check_promo_sequence.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from frontend.models import PromoCode

def check_sequence():
    """Check the current state of the PromoCode ID sequence"""
    print("=" * 60)
    print("PromoCode Sequence Diagnostic")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # Get table name
        table_name = PromoCode._meta.db_table
        print(f"\n1. Table name: {table_name}")
        
        # Get max ID
        cursor.execute(f"SELECT MAX(id) FROM {table_name};")
        max_id = cursor.fetchone()[0]
        print(f"2. Maximum ID in table: {max_id if max_id else 'None (table is empty)'}")
        
        # Get sequence name
        cursor.execute(f"SELECT pg_get_serial_sequence('{table_name}', 'id');")
        seq_result = cursor.fetchone()
        sequence_name = seq_result[0] if seq_result and seq_result[0] else None
        print(f"3. Sequence name: {sequence_name if sequence_name else 'NOT FOUND'}")
        
        if sequence_name:
            # Get current sequence value
            try:
                # Remove schema prefix if present
                seq_for_currval = sequence_name.split('.')[-1] if '.' in sequence_name else sequence_name
                cursor.execute(f"SELECT currval('{seq_for_currval}');")
                current_seq = cursor.fetchone()[0]
                print(f"4. Current sequence value: {current_seq}")
                
                # Calculate what next ID will be
                cursor.execute(f"SELECT nextval('{seq_for_currval}');")
                next_id = cursor.fetchone()[0]
                # Reset it back
                cursor.execute(f"SELECT setval('{seq_for_currval}', {next_id - 1}, false);")
                print(f"5. Next ID that will be used: {next_id}")
                
                # Show the difference
                if max_id:
                    diff = next_id - max_id
                    print(f"6. Difference: {diff} (should be 1)")
                    if diff > 1:
                        print(f"   ⚠️  WARNING: Sequence is {diff - 1} ahead of max ID!")
                        print(f"   💡 Run: python manage.py reset_promo_sequence")
                else:
                    print(f"6. Table is empty, sequence should be at 1")
                    if next_id != 1:
                        print(f"   ⚠️  WARNING: Sequence is at {next_id}, should be at 1")
                        print(f"   💡 Run: python manage.py reset_promo_sequence")
            except Exception as e:
                print(f"4. Error getting sequence value: {str(e)}")
        else:
            print("\n⚠️  ERROR: Could not find sequence!")
            print("   This might mean:")
            print("   - The table doesn't use auto-increment")
            print("   - The sequence was deleted")
            print("   - Table name is different")
            
            # Try to find any related sequences
            cursor.execute("""
                SELECT sequencename 
                FROM pg_sequences 
                WHERE schemaname = 'public' 
                AND sequencename LIKE '%promo%'
                ORDER BY sequencename;
            """)
            sequences = cursor.fetchall()
            if sequences:
                print("\n   Found these related sequences:")
                for seq in sequences:
                    print(f"     - {seq[0]}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        check_sequence()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

