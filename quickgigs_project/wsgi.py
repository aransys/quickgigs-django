"""
WSGI config for quickgigs_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
import django
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickgigs_project.settings')

# Setup Django
django.setup()

# Run migrations if needed
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
        migrations_table_exists = cursor.fetchone() is not None
    
    if not migrations_table_exists:
        print("Migrations table not found. Running migrations...")
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=True)
        print("Migrations completed successfully!")
    else:
        print("Migrations table exists. Checking for pending migrations...")
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=True)
        print("All migrations are up to date!")
except Exception as e:
    print(f"Error running migrations: {e}")
    # Don't exit - let the app continue

# Get the WSGI application
application = get_wsgi_application()
