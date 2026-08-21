"""Template helpers for the tutor app."""

import re

import markdown as md
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


# Links to outside resources (http/https) should open in a new tab so a kid
# doesn't lose their lesson/journal when they follow a video or article. Only
# external links are rewritten — internal (relative) links stay in-tab. The href
# itself is matched with a lookahead (never consumed) so the scheme survives; the
# negative lookahead keeps a second pass from double-injecting target=.
_EXTERNAL_LINK_RE = re.compile(r'<a (?=href="https?://)(?![^>]*\btarget=)')


def _external_links_new_tab(html):
    return _EXTERNAL_LINK_RE.sub(
        '<a target="_blank" rel="noopener noreferrer" ', html,
    )


@register.filter(name="markdownify_typed")
def markdownify_typed(text):
    """Markdown from a field a HUMAN TYPED INTO. Formatting renders; HTML does not.

    ``markdownify`` deliberately passes raw HTML through, which is right for
    content that only ever comes from a seeder or an admin. A rubric is not
    that: `tutor.forms.AssessmentRequestForm.rubric` is a plain textarea any
    editor can post to, and the finished assessment is read by every VIEW role —
    including `teacher`, the charter-oversight account, which can hold
    memberships across several families. Rendering that unescaped would let an
    editor in one family run script in an overseer's session.

    Escaping FIRST and rendering after keeps everything a rubric actually needs
    — headings, bold, the standards table — while `<script>` arrives as the four
    visible characters someone typed.
    """
    if not text:
        return ""
    html = md.markdown(
        escape(text),
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    return mark_safe(_external_links_new_tab(html))


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
