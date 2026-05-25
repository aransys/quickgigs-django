# QuickGigs

A modern freelance gig marketplace built with Django 5. Employers post
short-term projects, freelancers apply with cover letters, and featured
listings are upgraded via Stripe Checkout.

**🌐 Live demo:** <https://quickgigs-tblp.onrender.com>

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

This repo is a ground-up overhaul of an earlier final-year college version.
The old project still lives in git history; everything you see today is the
new shape.

## Highlights

- **Django 5.1** with a single env-driven settings module — no
  platform-specific branches or hardcoded hostnames.
- **Tailwind UI** delivered via the Play CDN, plus **HTMX** and **Alpine.js**
  for interactive bits. The previous bespoke CSS (3,741 lines) is gone.
- **Stripe Checkout** for featured-gig upgrades, with a proper
  signature-verified webhook handler that's idempotent on event IDs.
- **Postgres in production** (Render), **sqlite locally** — both driven by a
  single `DATABASE_URL`.
- **Render Blueprint** for one-click deploy via `render.yaml`. Docker +
  docker-compose included for portable local-and-prod environments.
- **pytest-django** test suite, fixtures, model/view/form coverage, webhook
  stubs. **66 tests, all green.**
- **Ruff** for linting and formatting; `pyproject.toml` for tool config.

## Quick start

### Local development (no Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Or use the Makefile shortcuts (`make help` lists them all):

```bash
make dev    # install deps + migrate
make run    # start the dev server
make test   # run the test suite
make lint   # ruff check
```

### Local development (Docker)

```bash
cp .env.example .env
docker compose up --build
```

Web on <http://localhost:8000>, Postgres on `localhost:5432`. Create an admin
user inside the container:

```bash
docker compose exec web ./scripts/entrypoint.sh manage createsuperuser
```

## Configuration

Every setting is read from environment variables. `.env.example` documents
the full list. The important ones:

| Variable                      | Purpose                                       |
| ----------------------------- | --------------------------------------------- |
| `DJANGO_SECRET_KEY`           | Required. Generate with `secrets.token_urlsafe(64)`. |
| `DJANGO_DEBUG`                | `False` in production — toggles all security headers. |
| `DJANGO_ALLOWED_HOSTS`        | Comma-separated hostnames.                    |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated. Include the scheme.          |
| `DATABASE_URL`                | e.g. `postgres://user:pass@host:5432/db`.     |
| `STRIPE_PUBLISHABLE_KEY`      | Optional — payments disable if blank.         |
| `STRIPE_SECRET_KEY`           | Optional — payments disable if blank.         |
| `STRIPE_WEBHOOK_SECRET`       | Required for `/payments/webhook/` to work.    |
| `FEATURED_GIG_PRICE`          | GBP. Defaults to 9.99.                        |

## Project layout

```
quickgigs-django/
├── accounts/          # Profiles, signup, role selection (employer | freelancer)
├── core/              # Home, about, contact, shared context processors
├── gigs/              # Gig postings + applications (core domain)
├── payments/          # Stripe Checkout + webhook (idempotent)
├── quickgigs_project/ # Settings, URLs, WSGI/ASGI
├── templates/         # Project-level templates (base + partials)
├── scripts/           # entrypoint.sh
├── Dockerfile         # Multi-stage, non-root, slim
├── docker-compose.yml # web + Postgres
├── render.yaml        # Render Blueprint (one-click deploy)
├── Makefile           # Common developer commands (`make help`)
├── pyproject.toml     # Tool config (ruff, pytest, coverage)
├── conftest.py        # Shared pytest fixtures
├── requirements.txt   # Production deps
└── requirements-dev.txt
```

## Deploying to Render

Render reads `render.yaml` and creates a free Postgres + web service in one
shot.

1. Push your fork of this repo to GitHub.
2. Render dashboard → **New +** → **Blueprint** → pick the repo → **Apply**.
3. Fill in `STRIPE_PUBLISHABLE_KEY` / `STRIPE_SECRET_KEY` when prompted (or
   leave blank to disable payments on the live site).
4. After the first deploy, update `DJANGO_ALLOWED_HOSTS` and
   `DJANGO_CSRF_TRUSTED_ORIGINS` to match the actual hostname Render
   assigned (Render appends a short suffix when the base name is taken).

To create a superuser on the live site (Render's free tier has no Shell
tab), run `createsuperuser` locally pointed at the remote Postgres:

```bash
DATABASE_URL="postgres://…copied from Render…" \
DJANGO_SECRET_KEY="anything-for-this-one-command" \
python manage.py createsuperuser
```

## Stripe webhook (local development)

Forward Stripe events to your local server with the Stripe CLI:

```bash
stripe listen --forward-to localhost:8000/payments/webhook/
```

Copy the printed `whsec_…` into your `.env` as `STRIPE_WEBHOOK_SECRET` and
restart the server. Now real test payments flip the gig to `is_featured=True`
via the webhook (the success page is just a UX confirmation).

## Tests

```bash
pytest               # all tests
pytest gigs/         # one app
pytest -k webhook    # by keyword
pytest --cov         # with coverage
```

Tests run against an in-memory sqlite DB (settings switches automatically
when pytest is detected).

## What this is not

- A production-ready marketplace. There's no escrow, no messaging, no rating
  system — by design.
- An attempt to solve every freelance-platform problem. It's a focused,
  educational implementation that ships clean.

## License

MIT. See `LICENSE`.
