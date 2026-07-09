# Steadfast Scholars

A calm, private homeschool web app for a single family (and their charter/reviewing
teacher). Plan every subject at its own level, let the children do their work in a
login-free kid portal, capture **mastery** (not grades) as it grows, and print a
report a charter Educational Specialist can trust.

- **Live:** Heroku app `steadfast-scholars` (`https://steadfast-scholars-*.herokuapp.com`)
- **Stack:** Django 6 · PostgreSQL · Bootstrap 5.3 (server-rendered, no SPA) · WhiteNoise
- **Design system:** "Scholar's Grove / AURORA" — `static/css/aurora-scholars.css`
  (`--ss-forest #0F3D2E`, `--ss-green #1E7A50`, `--ss-amber #EBA83A`)

---

## What it does

| Area | What it is |
|---|---|
| **Children & levels** | Each child has a school Level; every subject runs at its own grade. |
| **Curricula** | Built-in courses (literature/writing/math) with chapters & lessons, plus **online subjects** (Beast Academy, DIVE/Saxon) that launch out to the provider, and pinned **resource links** (answer keys, read-alouds). |
| **Kid portal** | A **login-free**, token-gated page showing only that child's subjects and their single next step. Typing, matching, fill-in-the-blank/cloze, "draw on the sentence," with spelling help. Autosaves; celebrates turn-in. |
| **AI grading + writing coach** | On turn-in, the assistant gives the child warm feedback (never a grade) and **drafts** a mastery level for the parent to confirm. On drafts, a writing coach suggests — never rewrites. |
| **Work log & Progress** | Every submission lands in the work log; Progress shows per-subject standing and mastery-over-time trends. |
| **Charter report** | One click prints a date-range report (work log + finalized mastery + trends) to save as PDF. See `worklog:sample_report` for a demo. |
| **Onboarding** | A stateful **setup checklist** on the hub + guided empty states drive a new parent to their first finalized mastery review (see `core/services.py::get_setup_progress`). |
| **Sharing** | Invite a co-parent, guardian, grandparent, or teacher with exactly the access you choose (roles live per family). |

---

## Apps

```
accounts    Custom user (email-unique); roles are NOT here — they live per family.
core        Family, FamilyMembership (roles), invitations, permissions, hub services.
students    Student (child) + Level; token-gated portal identity.
curricula   Curriculum, lessons, CurriculumPlacement, built-in blueprints, resources.
worklog     WorkLogEntry (the spine), completion + charter reports.
tutor       Questions/response types, MasteryAssessment, AI grading, writing coach, trends.
portal      Login-free kid portal (signed tokens), "what's next" surface, autosave.
activities  External activities (music, coding) + login-time check-in nudge.
dashboard   "Progress" — real signals (placements + work log + mastery).
assignments Legacy (kept, not in nav).
```

### Key concepts

- **Roles / permissions** (`core/permissions.py`): a user's role is defined **per family**
  via `core.FamilyMembership.role`. `EDIT_ROLES = (parent, guardian, admin)`;
  `VIEW_ROLES` adds `teacher, grandparent`. Use `scoped_queryset` / `viewable_queryset`
  / `editable_queryset` / `can_edit_family` — never re-implement scoping.
- **Legacy fallback:** records with `family IS NULL` belong to the user in their `parent` FK
  (pre-family-model data). A user with no memberships is treated as a standalone parent.
- **Mastery, not grades:** `tutor.models.MasteryAssessment` — the AI writes a `DRAFT`
  (`graded_by=None`); the parent finalizes to `FINALIZED`. Only finalized rows hit the report.
- **Kid portal auth:** signed tokens (`portal/tokens.py`), no login. Answers autosave via
  `static/js/portal-autosave.js` (collects `[data-question]` fields into a hidden JSON input).

---

## Local development

Requires Python 3.12+ and (for prod parity) PostgreSQL. SQLite works locally.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput   # manifest storage — run before tests
python manage.py createsuperuser
python manage.py runserver
```

Seed a demo family (idempotent — adopts an existing account/family if present):

```bash
python manage.py seed_family
```

### Environment variables

| Var | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Django secret | dev fallback |
| `DEBUG` | debug mode | `False` |
| `DATABASE_URL` | Postgres (Heroku sets this) | SQLite locally |
| `ANTHROPIC_API_KEY` | AI grading + writing coach | (AI features off if unset) |
| `TUTOR_MODEL` | Claude model id | `claude-opus-4-8` |
| `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` / `EMAIL_PORT` / `EMAIL_USE_TLS` | SMTP (Amazon SES). If `EMAIL_HOST` unset → console backend. | console |
| `DEFAULT_FROM_EMAIL` | verified sender for invites/verification | `no-reply@homeschool.local` |
| `USE_R2` | Cloudflare R2 media storage | `False` |

Email matters: registration sends a verification email — without a real backend a new
user can't verify. In prod, set the SES SMTP vars (see Deploy).

---

## Testing

```bash
python manage.py collectstatic --noinput   # required first (ManifestStaticFilesStorage)
python manage.py test
python manage.py check
```

Tests are per-app `tests.py`. Onboarding tests: `core.tests.SetupProgressTests`.

---

## Deploy (Heroku)

**Auto-deploy:** merging to GitHub `main` runs CI, and on success the `deploy` job in
`.github/workflows/ci.yml` pushes to Heroku (which runs the `release` migrate). This
needs a repo secret **`HEROKU_API_KEY`** (Settings → Secrets and variables → Actions);
generate one with `heroku authorizations:create`. Without the secret, the deploy job
skips with a warning.

**Manual deploy** (hotfix / bypass CI) — push any branch straight to Heroku's `main`:

```bash
git push heroku <your-branch>:main
```

`Procfile` runs `release: python manage.py migrate` on each deploy. Configure prod once:

```bash
# AI
heroku config:set ANTHROPIC_API_KEY=... TUTOR_MODEL=claude-opus-4-8 --app steadfast-scholars

# Email via Amazon SES (SMTP creds from the SES console; sender must be verified)
heroku config:set EMAIL_HOST=email-smtp.us-west-2.amazonaws.com \
  EMAIL_HOST_USER=... EMAIL_HOST_PASSWORD=... \
  DEFAULT_FROM_EMAIL="Steadfast Scholars <you@yourdomain>" --app steadfast-scholars

# Daily database backups
heroku pg:backups:schedule DATABASE_URL --at '02:00 America/Los_Angeles' --app steadfast-scholars

# Custom domain hosts + HSTS (a new hostname 400s until it's in ALLOWED_HOSTS)
heroku config:set \
  ALLOWED_HOSTS="<app>.herokuapp.com,steadfastscholars.com,www.steadfastscholars.com" \
  CSRF_TRUSTED_ORIGINS="https://steadfastscholars.com,https://www.steadfastscholars.com" \
  SECURE_HSTS_SECONDS=31536000 SECURE_HSTS_INCLUDE_SUBDOMAINS=true SECURE_HSTS_PRELOAD=false \
  --app steadfast-scholars
```

> Note: `SECURE_HSTS_PRELOAD` / `SECURE_HSTS_INCLUDE_SUBDOMAINS` default to **True** in prod, so
> set `SECURE_HSTS_PRELOAD=false` explicitly unless you really intend to preload (hard to undo).

Windows note: run the `heroku` CLI from **PowerShell**, not the bash shell. For prod
`manage.py shell` scripts, `cmd /c "heroku run --no-tty --app steadfast-scholars ""python manage.py shell"" < scriptfile"`
(PowerShell pipes inject a BOM that breaks the shell).

### Custom domain & email

`steadfastscholars.com` (+ `www`) are served via Heroku custom domains with auto-issued SSL
(Heroku ACM). DNS lives in **Squarespace**, which supports **ALIAS at the apex**, so the bare
domain points natively at Heroku: apex `@` = ALIAS → Heroku DNS target, `www` = CNAME → Heroku
DNS target. Email sends from `no-reply@steadfastscholars.com` (domain verified in SES us-west-2
via Easy DKIM; the domain's `DMARC p=reject` passes through DKIM alignment).

---

## Conventions

- Server-rendered Django templates + Bootstrap; **no SPA / React**.
- Reuse the AURORA design tokens/components; don't introduce a new visual language.
- Reuse `core/permissions.py` for all scoping.
- Commit messages are prefixed `HH-<n>:` (enforced by a commit-msg hook).
- This app is intentionally **single-family / private** — no public sharing of a family's data.
