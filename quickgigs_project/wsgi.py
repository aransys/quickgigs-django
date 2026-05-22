"""WSGI entry point for QuickGigs.

Migrations are NOT run here — that belongs in a release step / entrypoint
(see ``scripts/entrypoint.sh``). Running migrations on every worker boot
causes race conditions and slow cold starts.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quickgigs_project.settings")

application = get_wsgi_application()
