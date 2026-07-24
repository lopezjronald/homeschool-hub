"""Per-view Content Security Policy for lingua (D-13).

Django 6.0 ships CSP, but flipping it on site-wide would break the host's legacy
pages (dozens of inline styles + CDN Bootstrap). So we leave ``SECURE_CSP`` empty
(no global header) and set a locked-down policy PER RESPONSE on lingua views only,
via the ``@lingua_csp`` decorator. The ContentSecurityPolicyMiddleware emits the
header only where ``response._csp_config`` is set — so the blast radius is exactly
the lingua module. lingua templates are authored CSP-clean (external JS/CSS, a
``{{ csp_nonce }}`` on any unavoidable inline script, no inline handlers/styles).
"""
import functools

from django.utils.csp import CSP

# A strict policy suited to pages that render AI-generated text + audio for kids.
# No 'unsafe-inline' anywhere; nonce is available for any unavoidable inline
# script. Extend media-src/frame-src when the public-R2 audio path (M1) and the
# YouTube listening embeds (M2) land — keep those additions here, scoped.
LINGUA_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF, CSP.NONCE],
    "style-src": [CSP.SELF],
    "img-src": [CSP.SELF, "data:"],
    "media-src": [CSP.SELF],
    "font-src": [CSP.SELF],
    "connect-src": [CSP.SELF],
    "base-uri": [CSP.SELF],
    "form-action": [CSP.SELF],
    "object-src": [CSP.NONE],
    "frame-ancestors": [CSP.NONE],
}


def lingua_csp(view):
    """Attach the scoped lingua CSP to this view's response (D-13).

    Leaves a policy already set by the view untouched, so a specific view can
    widen (e.g. add a media/frame host) without fighting the decorator.
    """
    @functools.wraps(view)
    def _wrapped(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        if getattr(response, "_csp_config", None) is None:
            response._csp_config = dict(LINGUA_CSP)
        return response

    return _wrapped
