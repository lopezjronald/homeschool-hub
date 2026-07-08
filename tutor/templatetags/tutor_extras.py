"""Template helpers for the tutor app."""

import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdownify")
def markdownify(text):
    """Render trusted, editor-authored Markdown (e.g. a teaching guide) to HTML.

    Content comes from parents/admins, not the public, so raw HTML is allowed.
    """
    if not text:
        return ""
    html = md.markdown(
        text,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    return mark_safe(html)
