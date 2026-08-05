"""Split curated listening into rotatable videos and permanent shelves (LGA-102)."""

from django.db import migrations, models
import django.db.models.deletion


# A LOCAL copy of lingua.listening.classify_url, on purpose. A migration must not
# import app code: this file has to keep meaning the same thing years from now,
# and the runtime helper is free to change. `test_kind_classifier_matches_the_migration`
# holds the two in agreement while both exist.
_VIDEO_MARKERS = ("/watch", "youtu.be/", "/shorts/", "/live/", "/embed/")


def _classify(url):
    text = (url or "").lower()
    return "video" if any(m in text for m in _VIDEO_MARKERS) else "shelf"


def set_kind_from_url(apps, schema_editor):
    """Stamp existing rows.

    Every row seeded to date is a channel or a playlist, so a blanket default of
    "shelf" would also be correct TODAY — but not the moment someone adds a video
    by hand in the admin. Classifying is correct in both worlds.
    """
    Resource = apps.get_model("lingua", "ListeningResource")
    for resource in Resource.objects.all().only("id", "url"):
        Resource.objects.filter(pk=resource.pk).update(kind=_classify(resource.url))


def unset_kind(apps, schema_editor):
    """Nothing to undo — the column goes with the reverse of AddField."""


class Migration(migrations.Migration):

    dependencies = [("lingua", "0032_drop_station_visit")]

    operations = [
        migrations.AddField(
            model_name="listeningresource",
            name="kind",
            field=models.CharField(
                choices=[
                    ("video", "One video — can be watched and rotated out"),
                    ("shelf", "Channel or playlist — an endless well, always shown"),
                ],
                default="video",
                max_length=8,
            ),
        ),
        migrations.RunPython(set_kind_from_url, unset_kind),
        migrations.CreateModel(
            name="ListeningPick",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("learner", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="listening_picks", to="lingua.learner")),
                ("resource", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="picks", to="lingua.listeningresource")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="listeningpick",
            index=models.Index(fields=["learner", "created_at"],
                               name="lingua_list_learner_43203c_idx"),
        ),
    ]
