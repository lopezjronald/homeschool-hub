"""Seed the ten strategy clusters and their facts (HH-203).

A data migration so the levels exist the moment the app deploys — Heroku's
release phase runs migrate, so there is no manual step between a deploy and a
child being able to play.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    from factfluency.seed import seed

    seed(apps)


def backwards(apps, schema_editor):
    apps.get_model("factfluency", "Level").objects.all().delete()
    apps.get_model("factfluency", "Fact").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [("factfluency", "0001_initial")]

    operations = [migrations.RunPython(forwards, backwards)]
