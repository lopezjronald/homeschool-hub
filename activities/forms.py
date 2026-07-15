from django import forms
from django.utils import timezone

from core.permissions import editable_queryset, scoped_queryset, user_can_edit
from students.models import Student

from .models import ExternalActivity


def _child_queryset(user, family):
    """Children the user may log for, in the selected family."""
    if user and user_can_edit(user):
        return editable_queryset(Student.objects.all(), user)
    if user and family:
        return scoped_queryset(Student.objects.all(), user, family)
    return Student.objects.none()


class ActivityLogForm(forms.Form):
    """Log an activity session: WHICH children did it, and on WHAT date.

    One work-log entry is created per selected child, so 'Kaylin and Violet did
    jiu jitsu' marks each of them individually — and the date is chooseable, so
    forgotten days can be back-logged.
    """

    children = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Who did it?",
        error_messages={"required": "Pick at least one child."},
    )
    date = forms.DateField(
        initial=timezone.localdate,
        label="Date",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    def __init__(self, *args, user=None, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["children"].queryset = _child_queryset(user, family)

    def clean_date(self):
        when = self.cleaned_data["date"]
        if when > timezone.localdate():
            raise forms.ValidationError("That date is in the future.")
        return when


class ExternalActivityForm(forms.ModelForm):
    """Add/edit an external activity, with the child picker scoped to the family."""

    class Meta:
        model = ExternalActivity
        fields = ["title", "provider", "url", "emoji", "student", "cadence", "notes", "is_active"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2, "class": "form-control",
                                           "placeholder": "Anything to remember (schedule, login notes)…"}),
            "title": forms.TextInput(attrs={"class": "form-control form-control-lg",
                                            "placeholder": "e.g. Guitar"}),
            "provider": forms.TextInput(attrs={"class": "form-control",
                                               "placeholder": "e.g. School of Rock"}),
            "url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://…"}),
            "emoji": forms.TextInput(attrs={"class": "form-control text-center activity-emoji-input",
                                            "maxlength": 8, "aria-label": "Icon"}),
            "student": forms.Select(attrs={"class": "form-select"}),
            "cadence": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, user=None, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self._family = family
        if user:
            if user_can_edit(user):
                self.fields["student"].queryset = editable_queryset(Student.objects.all(), user)
            elif family:
                self.fields["student"].queryset = scoped_queryset(Student.objects.all(), user, family)
            else:
                self.fields["student"].queryset = Student.objects.none()
        self.fields["student"].required = False
        self.fields["student"].empty_label = "Whole family"

    def clean_student(self):
        student = self.cleaned_data.get("student")
        if student and self.user and not self.fields["student"].queryset.filter(pk=student.pk).exists():
            raise forms.ValidationError("Invalid child selection.")
        return student
