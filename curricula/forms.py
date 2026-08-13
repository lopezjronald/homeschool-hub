from urllib.parse import urlparse

from django import forms

from .blueprints import BLUEPRINTS
from .models import Curriculum, CurriculumDocument, CurriculumResource


class CurriculumForm(forms.ModelForm):
    """Form for creating and editing curricula.

    The availability choice is asked outright rather than defaulted. Defaulting
    either way bites: default-on and a course you loaded for next year appears in
    a child's portal today; default-off and a course you added to start Monday is
    silently missing with nothing to explain why.
    """

    is_active = forms.TypedChoiceField(
        label="Ready for her?",
        coerce=lambda v: v == "True",
        choices=(("True", "Available now — she can see it and start"),
                 ("False", "Save for later — load it now, switch it on when she's ready")),
        widget=forms.RadioSelect,
        initial="True",
        # Optional on purpose: a POST that predates this field (or omits it) must
        # keep working and mean "available", rather than failing validation or —
        # worse — silently coercing to hidden.
        required=False,
    )

    def clean_is_active(self):
        # Read the raw post rather than cleaned_data: an absent field and an
        # explicit "off" both arrive as falsey once coerced, and they must mean
        # different things. add_prefix so a prefixed form still finds its field.
        raw = self.data.get(self.add_prefix("is_active"))
        if raw in (None, ""):
            return self.instance.is_active if self.instance.pk else True
        return raw == "True"

    class Meta:
        model = Curriculum
        fields = ["name", "subject", "grade_level", "website_url", "is_online", "is_active"]
        widgets = {
            "website_url": forms.URLInput(
                attrs={"placeholder": "https://example.com"}
            ),
        }
        help_texts = {
            "is_online": "Tick this for a subject done on an external site (Beast "
                         "Academy, DIVE, etc.) — the child's portal opens the website "
                         "above instead of showing in-app lessons.",
        }

    def clean_website_url(self):
        url = self.cleaned_data.get("website_url", "").strip()
        if url:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                raise forms.ValidationError(
                    "Only HTTP and HTTPS URLs are allowed."
                )
        return url


class CurriculumDocumentForm(forms.ModelForm):
    """Upload a source document (instructor guide, textbook, etc.) for a curriculum."""

    class Meta:
        model = CurriculumDocument
        fields = ["title", "doc_type", "file"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "e.g. Home Instructor's Guide 3A"}
            ),
        }


class CurriculumResourceForm(forms.ModelForm):
    """Add an external resource link (answer key, guide, video, …) to a curriculum."""

    class Meta:
        model = CurriculumResource
        fields = ["label", "url", "resource_type", "teacher_only", "notes"]
        widgets = {
            "label": forms.TextInput(attrs={"placeholder": "e.g. Answer Key"}),
            "url": forms.URLInput(attrs={"placeholder": "https://…"}),
            "notes": forms.TextInput(attrs={"placeholder": "Optional note"}),
        }

    def clean_url(self):
        url = (self.cleaned_data.get("url") or "").strip()
        if url and urlparse(url).scheme not in ("http", "https"):
            raise forms.ValidationError("Only HTTP and HTTPS URLs are allowed.")
        return url


class ApplyBlueprintForm(forms.Form):
    """Choose a built-in blueprint to populate a curriculum's structure."""

    blueprint = forms.ChoiceField(
        choices=[(slug, bp["name"]) for slug, bp in BLUEPRINTS.items()],
        label="Curriculum blueprint",
    )
