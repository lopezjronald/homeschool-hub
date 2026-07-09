from django.db import migrations


def create_profiles_seen(apps, schema_editor):
    """Give every existing user a profile marked as already-welcomed.

    Users who signed up before onboarding existed are already oriented — they
    shouldn't be interrupted by the first-run welcome page on their next login.
    New users (created after this migration) get a fresh profile with
    has_seen_welcome=False via UserProfile.get_for at login time.
    """
    User = apps.get_model("accounts", "CustomUser")
    UserProfile = apps.get_model("accounts", "UserProfile")
    existing = {p.user_id for p in UserProfile.objects.all()}
    UserProfile.objects.bulk_create(
        [
            UserProfile(user_id=uid, has_seen_welcome=True)
            for uid in User.objects.values_list("id", flat=True)
            if uid not in existing
        ]
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_userprofile"),
    ]

    operations = [
        migrations.RunPython(create_profiles_seen, noop),
    ]
