"""Fold the two retired roles into the one view-only tier.

`guardian` used to mean FULL access, which is the opposite of what a household
means by the word, and `grandparent` was a second name for "may look". Both are
now `teacher`, the single view-only role.

PENDING INVITATIONS ARE MIGRATED TOO, and that is the part that actually
matters. A membership is created when an invitation is ACCEPTED, so an invite
sent last week naming `guardian` would quietly mint a role that no longer exists
— days after this migration ran and found nothing to fix.

Production held two memberships, both `parent`, and one pending invite, also
`parent`, when this was written. So this is expected to be a no-op there; it
exists for the databases where it is not.
"""

from django.db import migrations

RETIRED = {"guardian": "teacher", "grandparent": "teacher"}


def retire(apps, schema_editor):
    for model_name, field in (("FamilyMembership", "role"), ("Invitation", "role")):
        model = apps.get_model("core", model_name)
        for old, new in RETIRED.items():
            model.objects.filter(**{field: old}).update(**{field: new})


def unretire(apps, schema_editor):
    """Deliberately not reversible in the sense of restoring the old labels.

    Nothing records which `teacher` rows used to be guardians, and guessing
    would hand somebody edit access they were never meant to regain. Reversing
    the schema is fine; the data stays where it is.
    """
    return


class Migration(migrations.Migration):

    dependencies = [("core", "0006_two_grantable_roles")]

    operations = [migrations.RunPython(retire, unretire)]
