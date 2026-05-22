"""Modernize the UserProfile model.

* Add an ``updated_at`` field (mirror of Gig).
* Widen ``user_type`` choices to include an explicit ``unset`` so we can
  tell the difference between "just signed up" and "freelancer".
* Bump ``phone`` max_length to 32 to accommodate international formats.
"""

from __future__ import annotations

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_userprofile_hourly_rate"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="user_type",
            field=models.CharField(
                choices=[
                    ("employer", "Employer"),
                    ("freelancer", "Freelancer"),
                    ("unset", "Not chosen yet"),
                ],
                default="unset",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="phone",
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
