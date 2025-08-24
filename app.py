"""
WSGI application entry point for Render deployment.
This file serves as a fallback if render.yaml is not recognized.
"""

import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickgigs_project.settings')

# Set Render-specific environment variables if not already set
if not os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
    # Try to get the hostname from the request or set a default
    os.environ['RENDER_EXTERNAL_HOSTNAME'] = 'quickgigs-django.onrender.com'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Setup Django
import django
django.setup()

# Run migrations if needed
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
        migrations_table_exists = cursor.fetchone() is not None
    
    if not migrations_table_exists:
        print("Migrations table not found. Running migrations...")
        import subprocess
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=True)
        print("Migrations completed successfully!")
    else:
        print("Migrations table exists. Checking for pending migrations...")
        import subprocess
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=True)
        print("All migrations are up to date!")
except Exception as e:
    print(f"Error running migrations: {e}")
    # Don't exit - let the app continue

# Create the WSGI application
app = get_wsgi_application()

# Override Django settings after import to ensure ALLOWED_HOSTS is set
from django.conf import settings
if not hasattr(settings, '_ALLOWED_HOSTS_OVERRIDE'):
    settings._ALLOWED_HOSTS_OVERRIDE = True
    settings.ALLOWED_HOSTS = [
        'quickgigs-django.onrender.com',
        'localhost',
        '127.0.0.1',
        '0.0.0.0'
    ]
