from django.db import migrations, models


def mark_the_childs_own_uploads(apps, schema_editor):
    """Backfill: a row with no uploader came from the portal, so the child put it
    there herself.

    The new column defaults to "parent", which is right for every row created
    before the portal door existed — the checklist has always recorded who was
    signed in. It is wrong for anything uploaded through the portal in the hour
    between that shipping and this migration, and those are exactly the rows with
    a null uploader.
    """
    LessonWork = apps.get_model("curricula", "LessonWork")
    LessonWork.objects.filter(uploaded_by__isnull=True).update(source="child")


def unmark(apps, schema_editor):
    """Reversing only drops the column, so there is nothing to undo."""


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0014_lesson_work'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonwork',
            name='source',
            field=models.CharField(
                choices=[('child', 'The child, from her portal'),
                         ('parent', 'A grown-up, from the lesson checklist')],
                default='parent', max_length=10),
        ),
        migrations.RunPython(mark_the_childs_own_uploads, unmark),
    ]
