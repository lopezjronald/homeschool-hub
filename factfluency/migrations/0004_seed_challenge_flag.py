"""Re-seed after is_challenge was added (HH-203).

Migration 0002 ran before the field existed, so on a database that has already
migrated the flag is still False everywhere. Re-running the seed here sets it,
and is harmless on a fresh database where 0002 already did.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    from factfluency.seed import seed

    seed(apps)


class Migration(migrations.Migration):

    dependencies = [("factfluency", "0003_level_is_challenge")]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
