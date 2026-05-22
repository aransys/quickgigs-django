# QuickGigs

A modern freelance gig marketplace built with Django. Employers post short-term
projects, freelancers apply with cover letters, and featured listings are
upgraded via Stripe Checkout.

```
        ┌──────────┐  post gigs        ┌──────────────┐
        │ Employer │ ───────────────▶  │              │
        └──────────┘                   │              │
                                       │   QuickGigs  │
        ┌──────────┐  browse + apply   │              │
        │Freelancer│ ◀───────────────▶ │              │
        └──────────┘                   └──────────────┘
                                              │
                                       ┌──────▼──────┐
                                       │   Stripe    │ ← featured-gig payments
                                       └─────────────┘
```

This repo is a complete overhaul of an earlier college-final-year version. The
old project still lives in git history; everything you see today is the new
shape.

## Highlights

- **Django 5.1** with a single, env-driven settings module — no
  platform-specific branches, no hardcoded hostnames.
- **Tailwind UI** delivered via the play CDN, plus HTMX and Alpine.js for
  interactive bits. The previous bespoke CSS (3,741 lines) is gone.
- **Stripe Checkout** for featured-gig upgrades, with a proper
  signature-verified webhook handler that's idempotent on event IDs.
- **Postgres-first** (Postgres 16 in Docker, sqlite locally) via a single
  `DATABASE_URL`.
- **Docker + docker-compose** for one-command local dev that's identical to
  prod.
- **pytest-django** test suite with fixtures, model/view/form coverage, and
  webhook stubs.
- **Ruff** for linting and formatting, `pyproject.toml` for tool config.

## Quick start

### With Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

The app is on <http://localhost:8000>. Postgres is on `localhost:5432`.

Create an admin user once the containers are up:

```bash
docker compose exec web ./scripts/entrypoint.sh manage createsuperuser
```

### Without Docker

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Or use the Makefile shortcuts:

```bash
make dev   # install deps + run migrations
make run   # start the dev server
```

## Configuration

Every setting reads from environment variables. `.env.example` documents the
full list. The important ones:

| Variable                    | Purpose                                       |
| --------------------------- | --------------------------------------------- |
| `DJANGO_SECRET_KEY`         | Required. Generate with `secrets.token_urlsafe(64)`. |
| `DJANGO_DEBUG`              | `False` in production. Toggles all security headers. |
| `DJANGO_ALLOWED_HOSTS`      | Comma-separated.                              |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated. Include the scheme.        |
| `DATABASE_URL`              | e.g. `postgres://user:pass@host:5432/db`.     |
| `STRIPE_PUBLISHABLE_KEY`    | Optional — payments disable if blank.         |
| `STRIPE_SECRET_KEY`         | Optional — payments disable if blank.         |
| `STRIPE_WEBHOOK_SECRET`     | Required for `/payments/webhook/` to work.    |
| `FEATURED_GIG_PRICE`        | GBP. Defaults to 9.99.                        |

## Project layout

```
quickgigs-django/
├── accounts/          # Profiles, signup, role selection (employer | freelancer)
├── core/              # Home, about, contact, shared context processors
├── gigs/              # Gig postings + applications (core domain)
├── payments/          # Stripe Checkout + webhook (idempotent)
├── quickgigs_project/ # Settings, URLs, WSGI/ASGI
├── templates/         # Project-level templates (base, partials)
├── static/            # Project-level static (currently just placeholders;
│                      #   styling comes from the Tailwind CDN)
├── scripts/           # entrypoint.sh, cleanup-legacy.sh
├── Dockerfile         # Multi-stage, non-root, slim
├── docker-compose.yml # web + Postgres
├── Makefile           # Common developer commands (`make help`)
├── pyproject.toml     # Tool config (ruff, pytest, coverage)
├── requirements.txt   # Production deps
└── requirements-dev.txt
```

## Common tasks

```bash
make test     # run the test suite (pytest)
make lint     # ruff check
make format   # ruff format
make check    # ruff + manage.py check --deploy
make migrate  # apply migrations
```

## Stripe webhook

Local development: forward Stripe events with their CLI to bypass the public
internet.

```bash
stripe listen --forward-to localhost:8000/payments/webhook/
```

Copy the printed `whsec_…` into your `.env` as `STRIPE_WEBHOOK_SECRET`. The
handler:

- Verifies the signature.
- Skips already-seen event IDs (idempotency).
- On `checkout.session.completed`, marks the linked `Payment` complete and
  flips the gig to `is_featured=True` inside a single transaction.
- Persists every event to `PaymentEvent` for auditability.

## Tests

```bash
pytest               # all tests
pytest gigs/         # just the gigs app
pytest -k webhook    # by keyword
pytest --cov         # with coverage (configured in pyproject.toml)
```

Tests use an in-memory sqlite database so they're fast (settings switches to
`:memory:` when pytest is detected).

## Migration story

If you're upgrading an existing instance:

1. Back up your database. Always.
2. Run `bash scripts/cleanup-legacy.sh` to remove pre-overhaul files
   (committed venvs, leaked `.env`, old docs, etc.).
3. `pip install -r requirements.txt -r requirements-dev.txt`.
4. `python manage.py migrate` — the new migrations add `slug` to Gig, replace
   `PaymentHistory` with `PaymentEvent`, and widen the `UserProfile.user_type`
   choices to include `unset`.

## What this is not

- An MVP for real production traffic. It's a learning project that happens to
  be well structured. Treat it as a starting point, not a shipped product.
- A full-featured marketplace. There's no escrow, no messaging, no rating
  system — by design.

## License

MIT. See `LICENSE`.
