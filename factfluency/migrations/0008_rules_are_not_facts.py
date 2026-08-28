# "Does it really need to be 59 facts?" — no. 36 of the first level's 59 forms
# were two RULES (times zero, times one) inflated into nineteen Leitner cards,
# seventeen of them drills of n/1 and n/n — the documented confusion pair,
# which blurs precisely when drilled side by side. The rules keep three
# examples each; their division forms go entirely.
#
# Historical models only — no live seed() call (0004 taught us that lesson).

from django.db import migrations

#: The rule facts that stay, three examples per rule.
KEEP = {(0, 2), (0, 6), (0, 9), (1, 3), (1, 7), (1, 9)}


def trim(apps, schema_editor):
    Fact = apps.get_model("factfluency", "Fact")
    StudentFactState = apps.get_model("factfluency", "StudentFactState")

    for fact in Fact.objects.filter(factor_a__in=(0, 1)):
        if (fact.factor_a, fact.factor_b) not in KEEP:
            fact.delete()          # cascades states and attempts
        else:
            # The survivors are multiplication-only now: their n/1 and n/n
            # state rows must not linger and keep counting toward mastery.
            StudentFactState.objects.filter(fact=fact).exclude(
                operation="mult").delete()


def noop(apps, schema_editor):
    # Recreating deleted rule facts is seed()'s job on the live models; the
    # reverse of this migration is `manage.py shell -c "from factfluency.seed
    # import seed; seed()"`, not something a historical model can do.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("factfluency", "0007_best_time_per_question"),
    ]

    operations = [
        migrations.RunPython(trim, noop),
    ]
