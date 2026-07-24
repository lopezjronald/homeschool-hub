# Lingua — Build Spec (v1)

The executable spec for the Spanish acquisition module inside Steadfast Scholars. Read alongside
`DECISIONS.md` (why) and `ARCHITECTURE.md` (diagrams). Jira project **LGA**.

---

## 1. Context

A solo developer (active-duty USAF) is building a Spanish language-acquisition module for his two
homeschooled daughters (9 and 12), inside the existing `homeschool-hub` Django platform, reusing its
domain, storage (R2), auth, email, and Anthropic integration — architected to lift out into a standalone
product later. The pedagogy is settled and evidence-based (comprehensible input at i+1, co-equal
listening, required output *later*, spacing effect, transparent-orthography reading, cognate awareness,
short daily sessions, low affective filter). It is implemented as system behavior, not marketing copy.

**The two learners are two independent axes.** The 9-year-old needs parent scaffolding
(`support_level = PARENT_MEDIATED`) but has **no content ceiling** — she advances on demonstrated
comprehension. The 12-year-old is `GUIDED` with the FSRS scheduler. Never cap a bright learner's content
because she needs support (D-64/D-65); never lengthen a session because material got harder (D-66).

## 2. Environment & conventions (must follow — from Step-1 recon)

- Django 6.0.1 · Python 3.12 · Postgres · Heroku single **web** dyno (no worker) · R2 (boto3 + django-storages).
- **Frontend:** server-rendered templates + **vanilla-JS IIFEs + Bootstrap 5.3.3**. No HTMX, no SPA, no build step.
  Use Django 6.0 core `{% partialdef %}`/`{% partial %}`. Extend `portal/base_portal.html` (kid) / `base.html` (parent).
- **Views** are fat + function-based (no CBVs/mixins). **Scoping** via `core/permissions.py` helpers for parent
  surfaces; kid surfaces resolve identity from the signed portal token, never `request.user`.
- **AI seam:** `from tutor import ai` → `ai.grade_work(*, rubric, answers, grade_level, subject, objectives="",
  client=None, timeout=...)`, `ai.review_draft`, `ai.suggest_words`, `ai.check_spelling`, `ai.is_configured()`.
  Lazy SDK import, `client=None` injection, `max_retries=0` in-request, typed `*NotConfigured`/`*Error`.
- **Background work:** `threading.Thread(daemon=True)` gated by a settings flag (False under the test runner) +
  `connections.close_all()` in `finally` + `select_for_update` idempotency + a `*_pending` mgmt command on
  Heroku Scheduler as the backstop. Two timeout tiers (in-request 24s / background 110s).
- **Content authoring:** `seed_*`/`generate_*` management-command pairs run LOCALLY; durable assets committed to
  static or uploaded to R2; prod links via `--link-only`. Nothing heavy runs on the web dyno.
- **Tests:** `django.test.TestCase` + `setUpTestData` + injected fakes; `collectstatic --noinput` before `test`.
- **Mastery scale** (`tutor/mastery.py`): no_evidence<beginning<developing<proficient<mastered, bar=proficient.
  Speak this scale; never introduce numeric grades. "AI proposes, parent finalizes."

## 3. Architecture rules (load-bearing — see CLAUDE.md)

- **D-03** No FK from `lingua` to any host model. Learner carries `host_student_id` (int → `students.Student.pk`).
  Deletion: inline purge in host `student_delete` + idempotent `lingua_prune_orphans` (no signals — repo has none).
- **D-04** Coupling via `lingua/ports.py` (AIClient ABC + DTOs, no Django/tutor import) + host `adapters/lingua_ai.py`
  (only file importing `tutor`) + `lingua/integrations/directory.py` (only code reading `students.Student`).
  No Storage/Emailer ports.
- **D-05** views → `services.py` → ORM. No repository layer.
- **D-13** CSP scoped per-response to Lingua views (author CSP-clean).
- **Extraction path:** `pg_dump --table='lingua_*'` (+ enumerate shared referenced tables); documented, tested.

## 4. Module layout

```
lingua/
  apps.py  models.py  admin.py  urls.py  views.py  services.py  ports.py
  schedulers/{leitner.py, fsrs.py}      leveling.py   profiles.py   audio.py
  integrations/directory.py
  templates/lingua/    static/lingua/    management/commands/{generate_stories,tts_build,lingua_prune_orphans,...}
data/                                   # SUBTLEX-ESP dict, false-friend YAML (+ attribution)
homeschool_hub/adapters/lingua_ai.py    # host adapter (only file importing tutor.ai)
```

## 5. Phased build order (with stop-and-ask gates)

**v1 = M0 → M2 only.** M3–M5 are backlog: ticket, mark deferred, do not build.

### M0 — Foundation & spikes  *(gate: run all four spikes; record outcomes in DECISIONS.md before M1)*
1. Scaffold `lingua` app; `LINGUA={}` settings; URL namespace; templates/static dirs; scoped CSP.
2. `Learner` (`host_student_id`, `language`, `variant`) + `LearnerProfile` (`track_profile`, `support_level`,
   `content_ceiling`); `profiles.py` constants; `integrations/directory.py` (UserDirectory).
3. `ports.py` (AIClient ABC + DTOs) + host `adapters/lingua_ai.py`; injected fake for tests.
4. Orphan story: inline purge hook + `lingua_prune_orphans`; fix the pre-existing host `student.delete()`
   `ProtectedError` (worklog uses `on_delete=PROTECT`) — flag, handle gracefully.
5. Compliance seeds (E-13, start early): `AuditEvent`, `purge_stale`, written retention/info-sec note,
   child-safety system-prompt prepend, cost-ceiling ($25/mo) accounting + hard stop, PII guard, injection fence.
6. **Spikes:** SPIKE-01 (Polly timings), SPIKE-02 (voices w/ kids), SPIKE-03 (freq-band leveling), SPIKE-04
   (gen+critic+approve ×12).  **← STOP: review spike outcomes with the operator before M1.**

### M1 — A child reads one story with synced audio  *(gate: 9-yo reads one approved story end-to-end)*
- **E-04 Audio:** `audio.py` — Polly synth + speech marks → byte→char map → flat `{i,s,e,cs,ce}` JSON; public
  immutable R2 path; content-hash keys; `tts_build` command (local, `--link-only`).
- **E-03 Content:** `Story`/`Theme`/`StoryWord`/`ContentDraft`; `generate_stories` (local) → LLM-critic pre-filter
  → freq-band leveling → `pending_approval`; batch-approval UI; theme rotation; cognate detector + false-friend YAML.
- **E-05 Reading:** vanilla-JS read-along player (rAF highlight, tap-to-seek binary search); read-aloud (no record);
  shared-reading + dialogic prompts; tap-a-word lookup (lemmatize + offline dict + add-to-SRS); cognate flags;
  comprehension checks (picture-match/retell early, short-answer older); reading-volume + known-words metric;
  child-facing AI-disclosure line; graceful degradation to plain text.

### M2 — A daily habit  *(gate: both kids run a capped daily session with review + reread)*
- **E-06 Listening:** reuse `activities.ExternalActivity` (curated YouTube + level + minutes check-in);
  minutes into hero metric; optional transcript reveal.
- **E-07 Vocab/Review:** one `ReviewItem` table (`scheduler_state` JSON + indexed `due` + `paused_until`);
  `schedulers/leitner.py` (parent-grader, ≤15, picture-first, auto-grade unambiguous recognition) +
  `schedulers/fsrs.py` (py-fsrs, got-it→Good/didn't→Again); auto-capture words from reading; return-flood cap;
  Leitner→FSRS graduation (fresh Card + optional warm-start).
- **E-08 Phonics + Daily Plan:** F-04 seeded phonics mini-lesson; `Daily Plan` generator (session-cap **hard
  constraint** by `support_level`; reread-first + narrow reading; bounded choice); advancement k-of-n rule +
  demotion dead-band + D-67 parent nudge; celebrate comprehension milestones (no streaks).

**← v1 CUT LINE. M3–M5 deferred (ticketed).**

### Deferred (backlog)
- **M3:** E-09 full leveling engine (simplemma + vendored readability + coverage + i+1 bootstrap + placement) +
  curriculum phase engine (F-07); E-10 parent dashboard (F-08) + charter-flexible report + derive-level-on-read.
- **M4:** E-11 library assignments (F-09, Open Library + Google Books, manual availability, metadata-only);
  E-12 tutoring (F-10, ManualSession + affiliate + iCal + age-gating; SPIKE-05 Cal.com).
- **M5:** E-14 teen/adult tracks (F-12); F-05 output scaffolding; F-13 human audio + aeneas; F-14 shadowing/dictation
  (transcribe-and-discard only).

## 6. v1 feature acceptance criteria

**F-01 Guided Reading** — read-along highlights the correct word within ~50ms of audio (rAF, not `timeupdate`);
tap-a-word seeks to that word AND opens definition+audio+add-to-SRS without leaving the page; tap resolves inflected
forms via lemmatization (`corrieron`→`correr`) with zero per-tap API calls; cognates flagged, false-friends warned;
shared-reading surfaces dialogic prompts; comprehension checks (picture-match/retell early, short-answer older) feed
the level engine; broken audio degrades to plain readable text (no 500); child sees the AI-disclosure line.

**F-02 Listening** — a leveled list of curated YouTube embeds (hand-assigned level) with a minutes check-in; minutes
roll into the hero metric; no copyrighted media stored; reuses `ExternalActivity`.

**F-03 Vocabulary Review** — words captured from reading auto-enter the deck; KIDS_EARLY = Leitner (picture-first,
parent taps got-it/missed, ≤15 active, <10 min, unambiguous recognition auto-graded); KIDS_OLDER = FSRS two-button
(got-it→Good/didn't→Again, never Hard/Easy); daily review capped by `support_level`; `paused_until` prevents a
return-from-absence flood.

**F-04 Phonics (seeded mini-lesson)** — one seeded lesson covering ñ, ll, rr, j, g/gu, silent h, vowel purity,
accents; gates into decoding practice; NOT a subsystem.

**F-06 Daily Plan** — assembles reading + listening + review + one activity; **respects the session-length cap as a
hard constraint** (never lengthened by harder content); reread-first + narrow reading (theme + difficulty), bounded
choice ("pick 1 of 3"); rereads capped per-story + rotated.

**Leveling (v1)** — a SUBTLEX frequency-band filter flags words outside the top-N band; story level is hand-assigned;
the k-of-n advancement rule surfaces a parent-confirmed "ready to move up" (≥4/5 checks proficient+, ≥3 lessons,
≥2 weeks, floor n≥3); demotion only on 3 consecutive beginning- (dead-band); D-67 signal is parent-only + debounced.

**Compliance (cross-cutting)** — no child PII to any API; child free-text fenced; $25/mo hard stop; `AuditEvent`
logs decisions (not payloads); child-safety system prompt prepended; child-facing AI disclosure present; no stored
voice; no copyrighted text; `purge_stale` + written retention note exist.

## 7. Spikes (timebox each; record the decision in DECISIONS.md)

| Spike | Question | Timebox |
|---|---|---|
| SPIKE-01 | Do Polly speech marks (byte→char, accents) highlight the source word accurately on one real story? | 1 evening |
| SPIKE-02 | Which of 2–3 es-MX neural voices do the kids actually engage with? | 1 evening |
| SPIKE-03 | Does the freq-band filter score Fluency Matters L1 novellas as "easy"? (validates the coverage layer) | 1 evening |
| SPIKE-04 | AI gen + LLM-critic + batch approval on ~12 stories — quality, safety, cost? | 2 evenings |
| SPIKE-05 | Cal.com self-hosting overhead on Heroku (deferred; gates D-41) | later |

## 8. Verification
- `python manage.py collectstatic --noinput` **then** `python manage.py test lingua`.
- One test per service function + per model invariant (TestCase, injected fake AIClient).
- Read-along JS verified with jsdom (repo idiom); leveling validated against SPIKE-03 texts.
- A subagent reviews the diff before any deploy (repo workflow). Deploy: feature branch → `git push heroku <branch>:main`.
