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
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickgigs_project.settings')

# Setup Django
django.setup()

# Configure logging
logger = logging.getLogger(__name__)

# Run migrations if needed
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
        migrations_table_exists = cursor.fetchone() is not None
    
    if not migrations_table_exists:
        logger.info("Migrations table not found. Running migrations...")
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=True)
        logger.info("Migrations completed successfully!")
    else:
        logger.info("Migrations table exists. Checking for pending migrations...")
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=True)
        logger.info("All migrations are up to date!")
except Exception as e:
    logger.error(f"Error running migrations: {e}")
    # Don't exit - let the app continue

# Get the WSGI application
application = get_wsgi_application()
