#!/usr/bin/env python
"""
Startup script for Render deployment.
This script runs migrations and then starts the application.
"""

import os
import sys
import django
import subprocess

def run_migrations():
    """Run Django migrations"""
    print("Checking if migrations need to be run...")
    
    try:
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickgigs_project.settings')
        
        # Setup Django
        django.setup()
        
        # Check if migrations table exists
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

if __name__ == "__main__":
    run_migrations()
