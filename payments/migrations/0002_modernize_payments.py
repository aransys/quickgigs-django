"""Modernize the payments models.

* Rename ``stripe_payment_id`` to ``stripe_session_id`` and add
  ``stripe_payment_intent`` (the previous schema mashed both into one).
* Add ``currency``.
* Drop the home-grown ``PaymentHistory`` audit trail and replace it with
  ``PaymentEvent``, which keys off Stripe's idempotent event IDs.
"""

from __future__ import annotations

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0001_initial"),
        ("gigs", "0006_modernize_gig_application"),
    ]

    operations = [
        migrations.RenameField(
            model_name="payment",
            old_name="stripe_payment_id",
            new_name="stripe_session_id",
        ),
        migrations.AddField(
            model_name="payment",
            name="stripe_payment_intent",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="payment",
            name="currency",
            field=models.CharField(default="gbp", max_length=3),
        ),
        migrations.AlterField(
            model_name="payment",
            name="payment_type",
            field=models.CharField(
                choices=[
                    ("featured_gig", "Featured gig upgrade"),
                    ("gig_posting", "Gig posting fee"),
                    ("application_boost", "Application boost"),
                ],
                max_length=32,
            ),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(
                fields=["user", "-created_at"], name="pay_pay_user_created_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["status"], name="pay_pay_status_idx"),
        ),
        migrations.DeleteModel(name="PaymentHistory"),
        migrations.CreateModel(
            name="PaymentEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("event_type", models.CharField(max_length=80)),
                ("stripe_event_id", models.CharField(max_length=255, unique=True)),
                ("raw", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "payment",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="events",
                        to="payments.payment",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
