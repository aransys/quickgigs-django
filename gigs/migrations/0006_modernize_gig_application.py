"""Schema modernization for the gigs app.

* Add ``featured_until`` to Gig.
* Replace Application.unique_together with a named UniqueConstraint.
* Add helpful Application indexes.

(The earlier draft of this migration also added a ``slug`` field to Gig,
but a Django + PostgreSQL interaction around the auto-generated
``_like`` operator-class index made the migration impossible to apply
cleanly on production. Slugs weren't used in URLs anyway, so the field
was dropped before going live.)
"""

from __future__ import annotations

from django.db import migrations, models


def drop_slug_if_exists(apps, schema_editor):
    """Idempotently drop any leftover slug column from earlier deploy attempts.

    Only runs on PostgreSQL. On sqlite (the test suite) the in-memory DB
    is always fresh, so there's nothing to clean up.
    """
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        # Drop any slug-related indexes first (no-op if absent).
        cursor.execute("""
            DO $$
            DECLARE
                idx record;
            BEGIN
                FOR idx IN
                    SELECT indexname FROM pg_indexes
                    WHERE schemaname = current_schema()
                      AND tablename = 'gigs_gig'
                      AND indexname LIKE '%slug%'
                LOOP
                    EXECUTE 'DROP INDEX IF EXISTS ' || quote_ident(idx.indexname);
                END LOOP;
                IF EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'gigs_gig_slug_key'
                ) THEN
                    ALTER TABLE gigs_gig DROP CONSTRAINT gigs_gig_slug_key;
                END IF;
            END
            $$;
        """)
        # Then drop the column itself if it exists.
        cursor.execute("ALTER TABLE gigs_gig DROP COLUMN IF EXISTS slug")


def noop(apps, schema_editor):
    """No-op reverse."""


class Migration(migrations.Migration):
    dependencies = [
        ("gigs", "0005_gig_gigs_gig_employe_460f0b_idx_and_more"),
    ]

    operations = [
        # Defensive cleanup — drop any slug residue from earlier failed
        # attempts on the same database. No-op on a clean DB.
        migrations.RunPython(drop_slug_if_exists, noop),

        migrations.AddField(
            model_name="gig",
            name="featured_until",
            field=models.DateTimeField(blank=True, null=True),
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
                fields=["applicant", "-created_at"],
                name="apps_appl_applicant_created_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="application",
            index=models.Index(
                fields=["gig", "status"],
                name="apps_appl_gig_status_idx",
            ),
        ),
    ]
