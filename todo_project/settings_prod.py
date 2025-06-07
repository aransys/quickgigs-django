import os

from .settings import *

# Security settings
DEBUG = False
ALLOWED_HOSTS = ["your-app-name.herokuapp.com", "localhost"]

# Database configuration for PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DATABASE_NAME"),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": os.environ.get("DATABASE_PORT", "5432"),
    }
}

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Enable WhiteNoise for serving static files
MIDDLEWARE = ["whitenoise.middleware.WhiteNoiseMiddleware"] + MIDDLEWARE
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
