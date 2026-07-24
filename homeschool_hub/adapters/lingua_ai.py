"""Host adapter: binds lingua.ports.AIClient to the host's Anthropic seam.

This is the ONLY file in the codebase that imports ``tutor`` on behalf of lingua
(D-04). It reuses tutor.ai's key handling, timeout tiers, and no-retry policy
while exposing a generic ``generate()`` to lingua. To extract lingua, reimplement
just this file against the new host and point LINGUA["AI_CLIENT"] at it.
"""
from lingua.ports import AIClient, AIResult
from tutor import ai


class TutorAIClient(AIClient):
    def is_configured(self) -> bool:
        return ai.is_configured()

    def generate(self, *, system, user, max_tokens=1024, timeout=None, meta=None) -> AIResult:
        if not ai.is_configured():
            raise ai.GraderNotConfigured("Anthropic API key is not configured.")
        # Reuse tutor.ai's client factory (api key, timeout tier, max_retries=0).
        client = ai._make_client(timeout=timeout) if timeout is not None else ai._make_client()
        model = (meta or {}).get("model") or ai.grading_model()
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception as exc:  # noqa: BLE001 — surface uniformly, like tutor.ai
            raise ai.GraderError(str(exc))
        text = next(
            (b.text for b in resp.content if getattr(b, "type", None) == "text"), ""
        )
        usage = {}
        u = getattr(resp, "usage", None)
        if u is not None:
            usage = {
                "input_tokens": getattr(u, "input_tokens", None),
                "output_tokens": getattr(u, "output_tokens", None),
            }
        return AIResult(text=text, usage=usage, model=model)
