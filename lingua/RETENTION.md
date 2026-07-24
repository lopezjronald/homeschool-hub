# Lingua — Data Retention & Information-Security Note

A short, written retention + info-security policy (D-56). Retention is not
indefinite; limits are enforced in code by `manage.py purge_stale` (run on a
schedule). Keep this note current as models are added.

## Principles
- **Data minimization.** Store the least that makes the mastery/reading record
  useful. No child PII is ever sent to an AI/TTS API (D-52). The audit trail
  logs *decisions*, never prompts/answers/child free-text (D-57).
- **No indefinite retention.** Every time-bounded store has a purge rule below.
- **Extraction-safe.** No FK from lingua to host models (D-03); deleting a host
  child purges lingua rows inline + via `lingua_prune_orphans`.

## Retention rules (enforced by `purge_stale`)
| Data | Rule | Enforcement |
|---|---|---|
| `AuditEvent` | purge after **~18 months** (`LINGUA["AUDIT_RETENTION_DAYS"]`, default 548) | `manage.py purge_stale` |
| Unfinalized `ContentDraft` (M1) | purge unapproved drafts after ~90 days | *to add with M1* |
| `ReadingSession` / logs (M1–M2) | keep current + 1 school year, then purge | *to add with M1–M2* |
| Learner + finalized records | retain while the learner is active; purged on host-child deletion | inline purge + `lingua_prune_orphans` |

## Information-security notes
- Secrets (Anthropic key, AWS creds) live only in env vars / the platform config,
  never in the repo. The AIClient adapter is the only path to the model.
- Child access is tokenless (host `portal_key`); lingua adds no new child login.
- CSP is scoped to lingua views (`@lingua_csp`); AI output is escaped, never
  `mark_safe`d.

## Operational
- Schedule `purge_stale` and `lingua_prune_orphans` on Heroku Scheduler (~daily).
- **External-users hard gate:** before any non-family child uses this, the COPPA
  program (verifiable parental consent, posted notices, deletion-on-request, a
  data agreement covering Anthropic) must be in place — see DECISIONS.md D-54/D-58.
