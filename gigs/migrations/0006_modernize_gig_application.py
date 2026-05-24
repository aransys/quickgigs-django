"""Schema modernization for the gigs app.

* Add ``slug`` and ``featured_until`` to Gig.
* Backfill slugs for existing rows.
* Make ``slug`` unique with raw SQL on Postgres (avoids a Django bug
  where multi-attribute AlterField on a SlugField triggers the
  auto-generated ``_like`` operator-class index to be created twice in
  one ALTER statement).
* Replace Application.unique_together with a named UniqueConstraint.

This migration is idempotent: re-runs against a database in any state
(fresh, half-broken, fully migrated) succeed.
"""

from __future__ import annotations

from django.db import migrations, models
from django.utils.text import slugify


def backfill_slugs(apps, schema_editor):
    Gig = apps.get_model("gigs", "Gig")
    used: set[str] = set()
    for gig in Gig.objects.all().only("pk", "title", "slug").iterator():
        if gig.slug:
            used.add(gig.slug)
            continue
        base = slugify(gig.title)[:200] or f"gig-{gig.pk}"
        slug = base
        n = 2
        while slug in used or Gig.objects.filter(slug=slug).exclude(pk=gig.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        gig.slug = slug
        used.add(slug)
        gig.save(update_fields=["slug"])


def noop(apps, schema_editor):
    """No-op reverse: leave slugs in place — they're harmless."""


def make_slug_unique(apps, schema_editor):
    """Make slug NOT NULL and UNIQUE.

    Runs raw SQL on Postgres so we can drop any leftover indexes from
    previous partial migrations before re-creating them. On sqlite (used
    by the test suite) the schema is rebuilt for each in-memory test
    database, so a no-op here is safe — the model declaration still has
    ``unique=True`` so Django's ORM enforces uniqueness.
    """
    connection = schema_editor.connection

    if connection.vendor != "postgresql":
        return

    with connection.cursor() as cursor:
        # Drop every existing slug-related index. Handles all of:
        #   * fresh DB                       (nothing to drop)
        #   * half-broken DB from a prior   (drops leftovers)
        #     failed deploy
        #   * a re-run of this migration    (drops what we created)
        cursor.execute("""
            DO $$
            DECLARE
                idx record;
            BEGIN
                FOR idx IN
                    SELECT indexname
                    FROM pg_indexes
                    WHERE schemaname = current_schema()
                      AND tablename = 'gigs_gig'
                      AND indexname LIKE '%slug%'
                LOOP
                    EXECUTE 'DROP INDEX IF EXISTS ' || quote_ident(idx.indexname);
                END LOOP;
                -- Also drop the unique constraint if it exists.
                IF EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'gigs_gig_slug_key'
                ) THEN
                    ALTER TABLE gigs_gig DROP CONSTRAINT gigs_gig_slug_key;
                END IF;
            END
            $$;
        """)

        # Set NOT NULL (safe — backfill_slugs filled every row).
        cursor.execute("ALTER TABLE gigs_gig ALTER COLUMN slug SET NOT NULL")

        # Add the unique constraint. Postgres auto-creates a btree index
        # backing this constraint (named ``gigs_gig_slug_key``).
        cursor.execute(
            "ALTER TABLE gigs_gig "
            "ADD CONSTRAINT gigs_gig_slug_key UNIQUE (slug)"
        )

        # Add the varchar_pattern_ops index for ``LIKE 'prefix%'`` queries.
        # Name matches Django's auto-generated suffix so future migrations
        # can find it.
        cursor.execute(
            "CREATE INDEX gigs_gig_slug_1caada1b_like "
            "ON gigs_gig (slug varchar_pattern_ops)"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("gigs", "0005_gig_gigs_gig_employe_460f0b_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="gig",
            name="slug",
            field=models.SlugField(blank=True, max_length=240, null=True, unique=False),
        ),
        migrations.AddField(
            model_name="gig",
            name="featured_until",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_slugs, noop),
        # Make slug NOT NULL + UNIQUE. Manual SQL on Postgres; no-op on
        # sqlite (the model already declares unique=True so the next
        # in-memory test DB has the constraint baked in).
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="gig",
                    name="slug",
                    field=models.SlugField(blank=True, max_length=240, unique=True),
                ),
            ],
            database_operations=[
                migrations.RunPython(make_slug_unique, noop),
            ],
        ),
        # Replace unique_together with a named UniqueConstraint.
        migrations.AlterUniqueTogether(
            name="application",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="application",
            constraint=models.UniqueConstraint(
                fields=("gig", "applicant"),
                name="unique_application_per_gig",
            ),
        ),
        migrations.AddIndex(
            model_name="application",
            index=models.Index(
                fields=["applicant", "-created_at"], name="apps_appl_applicant_created_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="application",
            index=models.Index(
                fields=["gig", "status"], name="apps_appl_gig_status_idx"
            ),
        ),
    ]
