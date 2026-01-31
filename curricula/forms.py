from urllib.parse import urlparse

from django import forms

from .models import Curriculum


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
