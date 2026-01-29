"""
Django management command to close all database connections
Usage: python manage.py close_connections
"""
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = 'Close all database connections to resolve "too many clients" error'

    def handle(self, *args, **options):
        self.stdout.write('Closing all database connections...')
        
        closed_count = 0
        for conn in connections.all():
            try:
                conn.close()
                closed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Closed connection: {conn.alias}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error closing {conn.alias}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully closed {closed_count} connection(s)')
        )

