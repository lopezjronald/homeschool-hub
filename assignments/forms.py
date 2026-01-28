from datetime import date

from django import forms

from curricula.models import Curriculum
from students.models import Student

from .models import Assignment


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["child", "curriculum", "title", "description", "due_date", "status"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields["child"].queryset = Student.objects.filter(parent=user)
            self.fields["curriculum"].queryset = Curriculum.objects.filter(parent=user)

    def clean_due_date(self):
        due_date = self.cleaned_data.get("due_date")
        # Only validate on create (instance has no pk yet)
        if due_date and not self.instance.pk:
            if due_date < date.today():
                raise forms.ValidationError("Due date cannot be in the past.")
        return due_date

    def clean_child(self):
        child = self.cleaned_data.get("child")
        if child and self.user and child.parent != self.user:
            raise forms.ValidationError("Invalid child selection.")
        return child

    def clean_curriculum(self):
        curriculum = self.cleaned_data.get("curriculum")
        if curriculum and self.user and curriculum.parent != self.user:
            raise forms.ValidationError("Invalid curriculum selection.")
        return curriculum


class AssignmentStatusForm(forms.Form):
    """Simple form for updating assignment status only (used by students via magic link)."""

    status = forms.ChoiceField(choices=Assignment.STATUS_CHOICES)


class ResourceLinkForm(forms.Form):
    """Form for adding external resource links to an assignment."""

    url = forms.URLField(
        widget=forms.URLInput(attrs={"placeholder": "https://example.com/resource"})
    )
    label = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Optional label"}),
    )

    def clean_url(self):
        url = self.cleaned_data.get("url", "")
        # Only allow http and https schemes
        if url:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                raise forms.ValidationError(
                    "Only HTTP and HTTPS URLs are allowed."
                )
        return url
