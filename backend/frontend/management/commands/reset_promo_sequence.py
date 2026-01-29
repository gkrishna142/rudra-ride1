"""
Django management command to reset PromoCode ID sequence
Usage: python manage.py reset_promo_sequence

This command resets the PostgreSQL sequence for frontend_promocode.id
to the maximum ID + 1, so new records get sequential IDs.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Max
from frontend.models import PromoCode


class Command(BaseCommand):
    help = 'Reset PromoCode ID sequence to continue from the highest existing ID'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                # Get the table name from the model
                table_name = PromoCode._meta.db_table
                self.stdout.write(f'Table name: {table_name}')
                
                # Get the maximum ID from the table using raw SQL
                cursor.execute(f"SELECT MAX(id) FROM {table_name};")
                result = cursor.fetchone()
                max_id = result[0] if result and result[0] is not None else None
                
                if max_id is None:
                    # Table is empty, reset to 1
                    next_id = 1
                    self.stdout.write('No promo codes found. Resetting sequence to start from 1.')
                else:
                    # Set sequence to max_id + 1
                    next_id = max_id + 1
                    self.stdout.write(f'Maximum ID found: {max_id}')
                
                # Try multiple methods to get the sequence name
                sequence_name = None
                
                # Method 1: Use pg_get_serial_sequence
                try:
                    cursor.execute(f"""
                        SELECT pg_get_serial_sequence('{table_name}', 'id');
                    """)
                    result = cursor.fetchone()
                    if result and result[0]:
                        sequence_name = result[0]
                except Exception as e:
                    self.stdout.write(f'Method 1 failed: {str(e)}')
                
                # Method 2: Try common sequence name patterns
                if not sequence_name:
                    possible_names = [
                        f'{table_name}_id_seq',
                        f'frontend_promocode_id_seq',
                    ]
                    for seq_name in possible_names:
                        try:
                            cursor.execute(f"SELECT 1 FROM pg_class WHERE relname = '{seq_name}';")
                            if cursor.fetchone():
                                sequence_name = seq_name
                                break
                        except:
                            continue
                
                # Method 3: Find sequence by searching
                if not sequence_name:
                    cursor.execute("""
                        SELECT sequencename 
                        FROM pg_sequences 
                        WHERE schemaname = 'public' 
                        AND sequencename LIKE '%promocode%id%seq%'
                        LIMIT 1;
                    """)
                    result = cursor.fetchone()
                    if result:
                        sequence_name = f"public.{result[0]}"
                
                if sequence_name:
                    # Remove schema prefix if present for setval
                    seq_for_setval = sequence_name.split('.')[-1] if '.' in sequence_name else sequence_name
                    
                    # Reset the sequence to the next ID
                    cursor.execute(f"""
                        SELECT setval('{seq_for_setval}', {next_id}, false);
                    """)
                    
                    # Verify it was set correctly
                    cursor.execute(f"SELECT currval('{seq_for_setval}');")
                    current_val = cursor.fetchone()[0]
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Successfully reset sequence "{sequence_name}" to {next_id}'
                        )
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  Current sequence value: {current_val}'
                        )
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  Next promo code will have ID: {next_id}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Could not find sequence for {table_name}.id')
                    )
                    self.stdout.write('Trying to find all sequences...')
                    cursor.execute("""
                        SELECT sequencename 
                        FROM pg_sequences 
                        WHERE schemaname = 'public' 
                        ORDER BY sequencename;
                    """)
                    sequences = cursor.fetchall()
                    if sequences:
                        self.stdout.write('Available sequences:')
                        for seq in sequences:
                            self.stdout.write(f'  - {seq[0]}')
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error resetting sequence: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())

