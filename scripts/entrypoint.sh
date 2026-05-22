#!/usr/bin/env bash
#
# Container entrypoint for QuickGigs.
#
# Modes:
#   web       — production: collectstatic, migrate, gunicorn (default)
#   web-dev   — development: migrate, runserver with autoreload
#   migrate   — run migrations and exit
#   manage    — pass remaining args to manage.py
#   bash      — drop into a shell

set -euo pipefail

cmd=${1:-web}
shift || true

run_migrations() {
  echo "→ Applying database migrations…"
  python manage.py migrate --noinput
}

collect_static() {
  echo "→ Collecting static files…"
  python manage.py collectstatic --noinput --clear
}

case "$cmd" in
  web)
    collect_static
    run_migrations
    echo "→ Starting gunicorn on :${PORT:-8000}…"
    exec gunicorn quickgigs_project.wsgi:application \
      --bind "0.0.0.0:${PORT:-8000}" \
      --workers "${GUNICORN_WORKERS:-3}" \
      --timeout "${GUNICORN_TIMEOUT:-60}" \
      --access-logfile - \
      --error-logfile -
    ;;
  web-dev)
    run_migrations
    echo "→ Starting Django runserver on :${PORT:-8000}…"
    exec python manage.py runserver "0.0.0.0:${PORT:-8000}"
    ;;
  migrate)
    run_migrations
    ;;
  manage)
    exec python manage.py "$@"
    ;;
  bash|sh)
    exec bash
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    echo "Usage: $0 {web|web-dev|migrate|manage [args]|bash}" >&2
    exit 1
    ;;
esac
