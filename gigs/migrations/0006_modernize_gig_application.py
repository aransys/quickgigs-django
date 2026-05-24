"""Schema modernization for the gigs app.

* Add ``slug`` and ``featured_until`` to Gig.
* Backfill slugs for existing rows.
* Replace Application.unique_together with a named UniqueConstraint.
* Add a few helpful indexes.

This migration is idempotent on Postgres — if a previous attempt
created the slug's auto-generated ``_like`` operator-class index and
then failed, the RunSQL guard below drops it before AlterField tries
to re-create it.
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
    """Reverse migration: leave slugs in place — they're harmless."""


def drop_leftover_slug_indexes(apps, schema_editor):
    """Drop slug indexes left behind by a previously failed migration run.

    Only runs on PostgreSQL — sqlite (used by the test suite) starts every
    test with a fresh in-memory database, so there's nothing to clean up.
    """
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP INDEX IF EXISTS gigs_gig_slug_1caada1b_like")
        cursor.execute("DROP INDEX IF EXISTS gigs_gig_slug_idx")


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
        # Defensive cleanup — see module docstring. No-op on a clean DB
        # and a no-op on sqlite.
        migrations.RunPython(drop_leftover_slug_indexes, noop),
        # Split the slug transition into TWO AlterField steps so we never
        # change null AND unique in a single Postgres ALTER, which has
        # been observed to attempt to create the auto-generated `_like`
        # operator-class index twice in the same statement.
        migrations.AlterField(
            model_name="gig",
            name="slug",
            field=models.SlugField(blank=True, max_length=240, unique=False),
        ),
        migrations.AlterField(
            model_name="gig",
            name="slug",
            field=models.SlugField(blank=True, max_length=240, unique=True),
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
