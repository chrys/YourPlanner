#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YourPlanner.settings')
django.setup()

from chatbot.models import FAQ
from django.db import connection

print(f"FAQ count: {FAQ.objects.count()}")
print(f"FAQ table name: {FAQ._meta.db_table}")

# Check if table exists
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chatbot_faq';")
    result = cursor.fetchone()
    if result:
        print("✓ Table EXISTS")
        # Check what's in it
        cursor.execute("SELECT COUNT(*) FROM chatbot_faq;")
        count = cursor.fetchone()[0]
        print(f"  Records in table: {count}")
    else:
        print("✗ Table DOES NOT exist")

# Also list all tables
print("\nAll tables in database:")
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table[0]}")
