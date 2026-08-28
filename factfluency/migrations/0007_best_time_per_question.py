# Best-time records changed meaning: they now store milliseconds PER QUESTION,
# because rounds grow from 12 to 20 questions and a whole-round total set on
# day one could never be beaten again. Rows written under the old meaning would
# render as "45.0s a question" until the first clean full round overwrote them.

from django.db import migrations


def per_question(apps, schema_editor):
    PersonalRecord = apps.get_model("factfluency", "PersonalRecord")
    for record in PersonalRecord.objects.filter(record_type="best_time").select_related("session"):
        n = record.session.num_attempted if record.session else 0
        if n and n >= 2:
            record.value = round(record.value / n)
            record.save(update_fields=["value"])
        else:
            # A record with no session behind it, or from a degenerate round,
            # cannot be converted honestly — and the new rule would not have
            # granted it at all.
            record.delete()


def whole_round(apps, schema_editor):
    PersonalRecord = apps.get_model("factfluency", "PersonalRecord")
    for record in PersonalRecord.objects.filter(record_type="best_time").select_related("session"):
        n = record.session.num_attempted if record.session else 0
        if n:
            record.value = record.value * n
            record.save(update_fields=["value"])


class Migration(migrations.Migration):

    dependencies = [
        ("factfluency", "0006_alter_attempt_client_uuid_and_more"),
    ]

    operations = [
        migrations.RunPython(per_question, whole_round),
    ]
