# Generated by Django 4.2.8 on 2023-12-11 10:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("flight_service", "0002_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="airport",
            old_name="closes_big_city",
            new_name="closest_big_city",
        ),
    ]
