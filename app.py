"""
WSGI application entry point for Render deployment.
This file serves as a fallback if render.yaml is not recognized.
"""

import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickgigs_project.settings_prod')

# Set Render-specific environment variables if not already set
if not os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
    # Try to get the hostname from the request or set a default
    os.environ['RENDER_EXTERNAL_HOSTNAME'] = 'quickgigs-django.onrender.com'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Create the WSGI application
app = get_wsgi_application()
