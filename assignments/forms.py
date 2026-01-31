from datetime import date

from django import forms

from core.permissions import editable_queryset, scoped_queryset, user_can_edit
from curricula.models import Curriculum
from students.models import Student

from .models import Assignment, AssignmentResourceLink


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["child", "curriculum", "title", "description", "due_date", "status"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self._family = family
        if user:
            self.fields["child"].queryset = self._allowed_students()
            self.fields["curriculum"].queryset = self._allowed_curricula()

    def _allowed_students(self):
        if not self.user:
            return Student.objects.none()
        if user_can_edit(self.user):
            return editable_queryset(Student.objects.all(), self.user)
        if self._family:
            return scoped_queryset(Student.objects.all(), self.user, self._family)
        return Student.objects.none()

    def _allowed_curricula(self):
        if not self.user:
            return Curriculum.objects.none()
        if user_can_edit(self.user):
            return editable_queryset(Curriculum.objects.all(), self.user)
        if self._family:
            return scoped_queryset(Curriculum.objects.all(), self.user, self._family)
        return Curriculum.objects.none()

    def clean_due_date(self):
        due_date = self.cleaned_data.get("due_date")
        # Only validate on create (instance has no pk yet)
        if due_date and not self.instance.pk:
            if due_date < date.today():
                raise forms.ValidationError("Due date cannot be in the past.")
        return due_date

    def clean_child(self):
        child = self.cleaned_data.get("child")
        if child and self.user:
            if not self._allowed_students().filter(pk=child.pk).exists():
                raise forms.ValidationError("Invalid child selection.")
        return child

    def clean_curriculum(self):
        curriculum = self.cleaned_data.get("curriculum")
        if curriculum and self.user:
            if not self._allowed_curricula().filter(pk=curriculum.pk).exists():
                raise forms.ValidationError("Invalid curriculum selection.")
        return curriculum


class AssignmentStatusForm(forms.Form):
    """Simple form for updating assignment status only (used by students via magic link)."""

    status = forms.ChoiceField(choices=Assignment.STATUS_CHOICES)


class ResourceLinkForm(forms.Form):
    """Form for adding external resource/assessment links to an assignment."""

    link_type = forms.ChoiceField(
        choices=AssignmentResourceLink.TYPE_CHOICES,
        initial=AssignmentResourceLink.TYPE_RESOURCE,
    )
    label = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "e.g. CAASPP Practice Test"}),
    )
    url = forms.URLField(
        widget=forms.URLInput(attrs={"placeholder": "https://example.com/resource"})
    )
    window_start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    window_end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def clean_label(self):
        label = self.cleaned_data.get("label", "").strip()
        if not label:
            raise forms.ValidationError("Label is required.")
        return label

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

    def clean(self):
        cleaned_data = super().clean()
        window_start = cleaned_data.get("window_start")
        window_end = cleaned_data.get("window_end")
        if window_start and window_end and window_start > window_end:
            raise forms.ValidationError(
                "Window start date must be on or before the end date."
            )
        return cleaned_data
