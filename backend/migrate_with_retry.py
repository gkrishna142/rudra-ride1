"""
Run migrations with automatic retry on connection errors
"""
import os
import sys
import time
import subprocess

def run_migrate_with_retry(max_retries=5, wait_seconds=30):
    """Run migrate command with retry logic"""
    print("=" * 60)
    print("Running Migrations with Retry Logic")
    print("=" * 60)
    
    for attempt in range(1, max_retries + 1):
        print(f"\nAttempt {attempt} of {max_retries}...")
        
        # Close connections first
        try:
            import django
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
            django.setup()
            
            from django.db import connections
            for conn in connections.all():
                try:
                    conn.close()
                except:
                    pass
            print("✓ Closed existing connections")
        except:
            pass
        
        # Run migrate
        try:
            result = subprocess.run(
                [sys.executable, 'manage.py', 'migrate'],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("\n✓ Migrations completed successfully!")
                print(result.stdout)
                return True
            else:
                print(f"\n✗ Migration failed:")
                print(result.stderr)
                
                if "connection slots" in result.stderr or "server login" in result.stderr:
                    if attempt < max_retries:
                        print(f"\n⚠ Connection pool exhausted. Waiting {wait_seconds} seconds before retry...")
                        time.sleep(wait_seconds)
                        continue
                    else:
                        print("\n✗ Max retries reached. Connection pool is still exhausted.")
                        print("\nPlease:")
                        print("  1. Wait 2-3 minutes and try again")
                        print("  2. Contact database administrator to clear connections")
                        print("  3. Or increase connection limit for app_user")
                        return False
                else:
                    print("\n✗ Migration failed with different error. Check the error above.")
                    return False
                    
        except subprocess.TimeoutExpired:
            print(f"\n✗ Migration timed out after 60 seconds")
            if attempt < max_retries:
                print(f"Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)
                continue
            else:
                return False
        except Exception as e:
            print(f"\n✗ Error: {e}")
            if attempt < max_retries:
                print(f"Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)
                continue
            else:
                return False
    
    return False

if __name__ == '__main__':
    success = run_migrate_with_retry(max_retries=3, wait_seconds=30)
    sys.exit(0 if success else 1)

