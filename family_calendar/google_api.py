"""Talking to Google Calendar as the app's own service account (HH-168).

Hand-rolled rather than google-api-python-client. The three things that library
would do for us here — mint a JWT, swap it for an access token, POST some JSON —
are the forty lines below, written against PyJWT and requests, both of which are
already pinned. The library's transitive tree (httplib2, protobuf,
googleapis-common-protos, its own auth stack) is not worth carrying on a slug
that is already 225MB of a 500MB ceiling.

The whole module is inert unless GOOGLE_CALENDAR_SA_JSON is set, so a deploy
without the key behaves exactly as it did before the feature existed.
"""

import json
import logging
import threading
import time

import jwt
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TOKEN_URL = "https://oauth2.googleapis.com/token"
API_ROOT = "https://www.googleapis.com/calendar/v3"

# Full read/write on events. The narrower calendar.events scope would also do,
# but calendarList.insert — how a service account discovers a calendar shared
# with it — needs the broader one.
SCOPE = "https://www.googleapis.com/auth/calendar"

# Google issues hour-long tokens. Re-mint a minute early so a request can never
# set off holding one that expires mid-flight.
_TOKEN_SKEW = 60

_lock = threading.Lock()
_cached_token = None
_cached_until = 0.0


class GoogleCalendarError(RuntimeError):
    """A call to Google failed. Carries the status so callers can tell a
    permission problem from an outage without parsing prose."""

    def __init__(self, message, *, status=None, body=""):
        super().__init__(message)
        self.status = status
        self.body = body


def is_configured():
    """True when there is a key to sign with AND somewhere to write to."""
    return bool(getattr(settings, "GOOGLE_CALENDAR_SA_JSON", "")
                and calendar_ids())


def calendar_ids():
    """The calendars every event is pushed to, in config order.

    Comma-separated because there are two of them and there will never be
    twenty; a whole model to hold two strings would be ceremony.
    """
    raw = getattr(settings, "GOOGLE_CALENDAR_IDS", "") or ""
    return [c.strip() for c in raw.split(",") if c.strip()]


def service_account():
    """The parsed key, or None when the feature is switched off.

    Raises on malformed JSON rather than returning None: a key that is present
    but broken is a misconfiguration to shout about, not a feature to silently
    disable.
    """
    raw = getattr(settings, "GOOGLE_CALENDAR_SA_JSON", "") or ""
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except ValueError as exc:
        raise GoogleCalendarError(
            "GOOGLE_CALENDAR_SA_JSON is not valid JSON — paste the whole key "
            "file, including the outer braces.") from exc
    for field in ("client_email", "private_key", "token_uri"):
        if not parsed.get(field):
            raise GoogleCalendarError(
                "GOOGLE_CALENDAR_SA_JSON is missing %r — that is not a service "
                "account key file." % field)
    return parsed


def access_token(*, force=False):
    """A bearer token, minted on demand and cached until it nearly expires."""
    global _cached_token, _cached_until

    with _lock:
        if not force and _cached_token and time.time() < _cached_until:
            return _cached_token

        sa = service_account()
        if sa is None:
            raise GoogleCalendarError("Google Calendar is not configured.")

        now = int(time.time())
        assertion = jwt.encode(
            {
                "iss": sa["client_email"],
                "scope": SCOPE,
                "aud": sa["token_uri"],
                "iat": now,
                "exp": now + 3600,
            },
            sa["private_key"],
            algorithm="RS256",
        )
        try:
            response = requests.post(
                sa["token_uri"],
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": assertion,
                },
                timeout=10,
            )
        except requests.RequestException as exc:
            raise GoogleCalendarError("Could not reach Google to get a token: %s" % exc)

        if response.status_code != 200:
            # The body carries Google's own diagnosis ("invalid_grant" for a
            # clock skew or a revoked key). Pass it through — guessing is worse.
            raise GoogleCalendarError(
                "Google refused the service account key (HTTP %s). %s"
                % (response.status_code, response.text[:400]),
                status=response.status_code, body=response.text[:400])

        payload = response.json()
        _cached_token = payload["access_token"]
        _cached_until = time.time() + int(payload.get("expires_in", 3600)) - _TOKEN_SKEW
        return _cached_token


def request(method, path, *, params=None, json_body=None, timeout=10):
    """One Calendar API call. Returns the decoded body, or None for a 204.

    Retries ONCE on a 401, re-minting the token first: a cached token can be
    revoked out from under us, and that is indistinguishable from expiry until
    Google says so.
    """
    url = path if path.startswith("http") else API_ROOT + path
    for attempt in (1, 2):
        token = access_token(force=(attempt == 2))
        try:
            response = requests.request(
                method, url,
                headers={"Authorization": "Bearer %s" % token},
                params=params, json=json_body, timeout=timeout,
            )
        except requests.RequestException as exc:
            raise GoogleCalendarError("Could not reach Google: %s" % exc)

        if response.status_code == 401 and attempt == 1:
            continue
        if response.status_code == 204 or not response.content:
            return None
        if 200 <= response.status_code < 300:
            return response.json()

        raise GoogleCalendarError(
            "Google returned HTTP %s for %s %s. %s"
            % (response.status_code, method, path, response.text[:400]),
            status=response.status_code, body=response.text[:400])


# Roles that can actually create and update events. writerWithoutPrivateAccess
# was added on 2026-07-07 and is the row directly above "writer" in the sharing
# menu — it writes non-private events fine and then behaves oddly around private
# ones, so it is reported as a near-miss rather than accepted silently.
ROLE_WRITER = "writer"
ROLE_OWNER = "owner"
ROLE_PARTIAL = "writerWithoutPrivateAccess"
WRITABLE_ROLES = (ROLE_WRITER, ROLE_OWNER)


def access_role(calendar_id):
    """What Google says this service account may do with ``calendar_id``.

    Reads the service account's own calendar list, adding the calendar to it
    first if it is not there. A calendar shared with a service account never
    appears automatically — nobody clicks "accept" on a robot's behalf — and
    calendarList.insert is the documented way to pick it up. It touches only
    the service account's list, never the humans'.
    """
    quoted = requests.utils.quote(calendar_id, safe="")
    try:
        entry = request("GET", "/users/me/calendarList/%s" % quoted)
    except GoogleCalendarError as exc:
        if exc.status != 404:
            raise
        entry = request("POST", "/users/me/calendarList",
                        json_body={"id": calendar_id})
    return (entry or {}).get("accessRole", "")
