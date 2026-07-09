from django import forms

from core.permissions import editable_queryset, scoped_queryset, user_can_edit
from curricula.models import Curriculum
from students.models import Student

from .models import WorkLogEntry


class WorkLogEntryForm(forms.ModelForm):
    """Create/edit a work log entry, scoped to what the user may access.

    Mirrors ``assignments.forms.AssignmentForm``: child/curriculum querysets are
    narrowed via the permission helpers and re-validated in ``clean_*`` so a user
    cannot post a child/curriculum outside their family.
    """

    class Meta:
        model = WorkLogEntry
        fields = ["child", "date", "subject", "curriculum", "description", "attachment"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "subject": forms.TextInput(attrs={"placeholder": "e.g. Math, Reading, Nature walk"}),
        }

    def __init__(self, *args, user=None, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self._family = family
        if user:
            self.fields["child"].queryset = self._allowed_students()
            self.fields["curriculum"].queryset = self._allowed_curricula()
        # Curriculum is optional on the model; make the empty choice friendly.
        self.fields["curriculum"].required = False
        self.fields["curriculum"].empty_label = "— None —"

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


class WorkLogReportForm(forms.Form):
    """Filter the completion report by child and date range.

    A GET form for oversight (teachers, grandparents, parents): the child
    dropdown is scoped to students the user may view in the selected family.
    """

    child = forms.ModelChoiceField(
        queryset=Student.objects.none(),
        required=False,
        empty_label="All children",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    start = forms.DateField(
        required=False,
        label="From",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    end = forms.DateField(
        required=False,
        label="To",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    def __init__(self, *args, user=None, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Student.objects.none()
        if user:
            if user_can_edit(user):
                qs = editable_queryset(Student.objects.all(), user)
            elif family:
                qs = scoped_queryset(Student.objects.all(), user, family)
        self.fields["child"].queryset = qs

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start"), cleaned.get("end")
        if start and end and start > end:
            raise forms.ValidationError("The start date must be on or before the end date.")
        return cleaned
