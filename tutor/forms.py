from django import forms

from . import mastery


class AssessmentRequestForm(forms.Form):
    """Rubric + the child's work to send to the AI grader."""

    rubric = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="What should the work demonstrate? One criterion per line works well.",
    )
    answers = forms.CharField(
        label="The child's work",
        widget=forms.Textarea(attrs={"rows": 6}),
        help_text="Type or paste what the child did (their answers, writing, or a description).",
    )

    def clean_rubric(self):
        value = self.cleaned_data.get("rubric", "").strip()
        if not value:
            raise forms.ValidationError("A rubric is required.")
        return value

    def clean_answers(self):
        value = self.cleaned_data.get("answers", "").strip()
        if not value:
            raise forms.ValidationError("The child's work is required.")
        return value


class FinalizeForm(forms.Form):
    """Parent's final mastery decision (may override the AI)."""

    final_level = forms.ChoiceField(
        choices=mastery.CHOICES,
        label="Final mastery level",
    )
