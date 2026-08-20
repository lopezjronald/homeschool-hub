from django import forms

from activities.models import ExternalActivity
from core.permissions import editable_queryset, scoped_queryset, user_can_edit
from students.models import Student

from .models import CalendarEvent


def _family_child_queryset(user, family):
    """Children pickable for an event — scoped to the SELECTED family, so a
    multi-family editor can't file family B's event against family A's child
    (the HH-140 bug class). Falls back to the editable set only when no family
    is selected (legacy single-user accounts)."""
    if user and family:
        return scoped_queryset(Student.objects.all(), user, family)
    if user and user_can_edit(user):
        return editable_queryset(Student.objects.all(), user)
    return Student.objects.none()

WEEKDAY_CHOICES = [
    (0, "Mon"), (1, "Tue"), (2, "Wed"), (3, "Thu"), (4, "Fri"), (5, "Sat"), (6, "Sun"),
]


class CalendarEventForm(forms.ModelForm):
    """Add/edit a calendar event, child picker scoped to the family."""

    repeat_weekdays = forms.TypedMultipleChoiceField(
        choices=WEEKDAY_CHOICES, coerce=int, required=False,
        widget=forms.CheckboxSelectMultiple,
        label="On which days?",
        help_text="Leave unchecked to repeat on the start date's weekday.",
    )

    class Meta:
        model = CalendarEvent
        fields = [
            "title", "event_type", "child", "date", "start_time", "end_time",
            "location", "repeats_weekly", "repeat_weekdays", "repeat_until",
            "notes", "activity",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control form-control-lg",
                                            "placeholder": "e.g. Jiu-jitsu, LRM with Mrs. Lee"}),
            "event_type": forms.Select(attrs={"class": "form-select"}),
            "child": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control",
                                               "placeholder": "e.g. Bonney Field, Zoom"}),
            "repeats_weekly": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "repeat_until": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "form-control",
                                           "placeholder": "Anything to remember…"}),
            "activity": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        child_qs = _family_child_queryset(user, family)
        self.fields["child"].queryset = child_qs
        self.fields["child"].required = False
        self.fields["child"].empty_label = "Whole family"
        if user and user_can_edit(user):
            act_qs = editable_queryset(ExternalActivity.objects.all(), user)
        elif user and family:
            act_qs = scoped_queryset(ExternalActivity.objects.all(), user, family)
        else:
            act_qs = ExternalActivity.objects.none()
        self.fields["activity"].queryset = act_qs
        self.fields["activity"].required = False
        self.fields["activity"].empty_label = "— none —"
        self.fields["activity"].label = "Linked program"

    def clean_child(self):
        child = self.cleaned_data.get("child")
        if child and self.user and not self.fields["child"].queryset.filter(pk=child.pk).exists():
            raise forms.ValidationError("Invalid child selection.")
        return child

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_time"), cleaned.get("end_time")
        if start and end and end <= start:
            self.add_error("end_time", "End time must be after the start time.")
        if end and not start:
            self.add_error("start_time", "Add a start time (or clear the end time for all-day).")
        date, until = cleaned.get("date"), cleaned.get("repeat_until")
        if date and until and until < date:
            self.add_error("repeat_until", "The repeat-until date is before the start date.")
        if cleaned.get("repeat_weekdays") and not cleaned.get("repeats_weekly"):
            cleaned["repeats_weekly"] = True  # checking days clearly means "repeat"
        if cleaned.get("event_type") == CalendarEvent.TYPE_BREAK:
            # Breaks are whole days off — times don't apply.
            cleaned["start_time"] = None
            cleaned["end_time"] = None
        return cleaned
