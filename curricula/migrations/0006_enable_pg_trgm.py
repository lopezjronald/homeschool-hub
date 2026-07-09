# Enable the pg_trgm extension for misspelling-tolerant (trigram) search.
# CreateExtension is a no-op on non-PostgreSQL backends, so SQLite dev/test
# databases migrate cleanly.

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0005_curriculumresource'),
    ]

    operations = [
        TrigramExtension(),
    ]
