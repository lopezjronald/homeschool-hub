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


@register.filter(name="markdownify_inline")
def markdownify_inline(text):
    """Markdown for a single run of text (e.g. a question prompt): renders
    **bold**/*italic*/line breaks but strips the wrapping <p> tags (paragraph
    breaks become <br><br>) so the result stays valid inside a <label>."""
    if not text:
        return ""
    html = md.markdown(text, extensions=["nl2br"], output_format="html5").strip()
    if html.startswith("<p>") and html.endswith("</p>"):
        html = html[3:-4].replace("</p>\n<p>", "<br><br>").replace("</p><p>", "<br><br>")
    return mark_safe(html)
