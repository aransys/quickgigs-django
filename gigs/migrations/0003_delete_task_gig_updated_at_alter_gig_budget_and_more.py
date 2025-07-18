# Generated by Django 4.2.21 on 2025-06-28 16:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gigs', '0002_alter_task_options_gig'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Task',
        ),
        migrations.AddField(
            model_name='gig',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='gig',
            name='budget',
            field=models.DecimalField(decimal_places=2, help_text='Budget in USD', max_digits=8, validators=[django.core.validators.MinValueValidator(0.01)]),
        ),
        migrations.AlterField(
            model_name='gig',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='gig',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
    ]
