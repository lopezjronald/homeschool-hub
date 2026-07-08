from urllib.parse import urlparse

from django import forms

from .blueprints import BLUEPRINTS
from .models import Curriculum, CurriculumDocument


class CurriculumForm(forms.ModelForm):
    """Form for creating and editing curricula."""

    class Meta:
        model = Curriculum
        fields = ["name", "subject", "grade_level", "website_url"]
        widgets = {
            "website_url": forms.URLInput(
                attrs={"placeholder": "https://example.com"}
            ),
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


class ApplyBlueprintForm(forms.Form):
    """Choose a built-in blueprint to populate a curriculum's structure."""

    blueprint = forms.ChoiceField(
        choices=[(slug, bp["name"]) for slug, bp in BLUEPRINTS.items()],
        label="Curriculum blueprint",
    )
