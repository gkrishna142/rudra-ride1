"""
Django management command to alter role_id column from INTEGER to VARCHAR(50).

This command attempts to run the database migration programmatically.
If you don't have ALTER TABLE privileges, it will provide clear instructions.

Usage:
    python manage.py alter_role_id_column
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError


class Command(BaseCommand):
    help = 'Alter role_id column from INTEGER to VARCHAR(50) to support string role IDs like "R001"'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Only check the current column type without making changes',
        )

    def handle(self, *args, **options):
        check_only = options['check_only']
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Role ID Column Migration Tool'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        
        # Step 1: Check current column type
        self.stdout.write('Step 1: Checking current column type...')
        current_type = self.check_column_type()
        
        if current_type:
            column_name, data_type, max_length = current_type
            self.stdout.write(f'  Column: {column_name}')
            self.stdout.write(f'  Current Type: {data_type}')
            if max_length:
                self.stdout.write(f'  Max Length: {max_length}')
            self.stdout.write('')
            
            # Check if already migrated
            if data_type == 'character varying' and max_length == 50:
                self.stdout.write(self.style.SUCCESS('✅ Column is already VARCHAR(50)!'))
                self.stdout.write(self.style.SUCCESS('   No migration needed. You can save string role_ids like "R001".'))
                return
            
            if check_only:
                self.stdout.write(self.style.WARNING('⚠️  Column is still INTEGER. Migration needed.'))
                self.stdout.write('   Run without --check-only to attempt migration.')
                return
            
            # Step 2: Attempt migration
            self.stdout.write('Step 2: Attempting to alter column type...')
            success = self.alter_column_type()
            
            if success:
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('✅ SUCCESS: Column type changed to VARCHAR(50)!'))
                self.stdout.write(self.style.SUCCESS('   You can now save role_id values like "R001", "R002", etc.'))
                self.stdout.write('')
                self.stdout.write('Step 3: Marking Django migration as applied...')
                self.stdout.write('   Run: python manage.py migrate frontend 0045 --fake')
            else:
                self.stdout.write('')
                self.stdout.write(self.style.ERROR('❌ FAILED: Could not alter column type.'))
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('Reason: Insufficient database privileges'))
                self.stdout.write('')
                self.stdout.write('Solution:')
                self.stdout.write('  1. Contact your database administrator')
                self.stdout.write('  2. Share this SQL file: frontend/migrations/QUICK_SQL_FOR_DBA.sql')
                self.stdout.write('  3. Or ask them to run this SQL:')
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('     ALTER TABLE frontend_user'))
                self.stdout.write(self.style.WARNING('     ALTER COLUMN role_id TYPE VARCHAR(50) USING'))
                self.stdout.write(self.style.WARNING('         CASE'))
                self.stdout.write(self.style.WARNING('             WHEN role_id IS NULL THEN NULL'))
                self.stdout.write(self.style.WARNING('             ELSE role_id::text'))
                self.stdout.write(self.style.WARNING('         END;'))
        else:
            self.stdout.write(self.style.ERROR('❌ Could not find role_id column'))
    
    def check_column_type(self):
        """Check the current type of role_id column"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name, data_type, character_maximum_length 
                    FROM information_schema.columns 
                    WHERE table_name = 'frontend_user' AND column_name = 'role_id';
                """)
                result = cursor.fetchone()
                return result
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error checking column: {str(e)}'))
            return None
    
    def alter_column_type(self):
        """Attempt to alter the column type"""
        try:
            with connection.cursor() as cursor:
                # Attempt to alter the column
                cursor.execute("""
                    ALTER TABLE frontend_user 
                    ALTER COLUMN role_id TYPE VARCHAR(50) USING 
                        CASE 
                            WHEN role_id IS NULL THEN NULL
                            ELSE role_id::text
                        END;
                """)
                self.stdout.write(self.style.SUCCESS('  ✅ ALTER TABLE command executed successfully'))
                return True
        except ProgrammingError as e:
            error_msg = str(e)
            if 'must be owner' in error_msg.lower() or 'permission denied' in error_msg.lower():
                self.stdout.write(self.style.ERROR('  ❌ Permission denied: Must be table owner'))
                self.stdout.write(self.style.ERROR(f'     Error: {error_msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ Database error: {error_msg}'))
            return False
        except OperationalError as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Database connection error: {str(e)}'))
            return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Unexpected error: {str(e)}'))
            return False

