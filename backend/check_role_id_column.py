"""
Simple script to check the role_id column type.
Run with: python manage.py shell < check_role_id_column.py
Or use Django shell directly.
"""
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'frontend_user' AND column_name = 'role_id';
    """)
    result = cursor.fetchone()
    if result:
        column_name, data_type, max_length = result
        print(f"Column: {column_name}")
        print(f"Data Type: {data_type}")
        print(f"Max Length: {max_length}")
        
        if data_type == 'character varying' and max_length == 50:
            print("\n✅ Column type is correct (VARCHAR(50))")
            print("   You can now save role_id values like 'R001'")
        else:
            print(f"\n❌ Column type is {data_type}, expected 'character varying'")
            print("   Please run the database migration first.")
            print("   See: frontend/migrations/QUICK_SQL_FOR_DBA.sql")
    else:
        print("❌ Column not found")

