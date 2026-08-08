"""Template helpers for the tutor app."""

import re

import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# Links to outside resources (http/https) should open in a new tab so a kid
# doesn't lose their lesson/journal when they follow a video or article. Only
# external links are rewritten — internal (relative) links stay in-tab.
_EXTERNAL_LINK_RE = re.compile(r'<a (?![^>]*\btarget=)href="https?://')


def _external_links_new_tab(html):
    return _EXTERNAL_LINK_RE.sub(
        '<a target="_blank" rel="noopener noreferrer" href="', html,
    )


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
    return mark_safe(_external_links_new_tab(html))


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
    return mark_safe(_external_links_new_tab(html))
