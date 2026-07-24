# Extracting Lingua to a standalone product

Lingua is built to lift out of Steadfast Scholars with minimal refactoring
(D-01…D-09). This is the documented, tested extraction path. It replaces the
dedicated-Postgres-schema idea (D-07), which fought Django's migration model —
Django already prefixes every table with the app label, so the `lingua` app's
tables are all named `lingua_*` for free (verified by
`LinguaTablePrefixTests.test_all_lingua_tables_are_prefixed`).

## What makes extraction cheap (the rules that were followed)

- **No FK from lingua to any host model (D-03).** The learner is a plain
  `Learner.host_student_id` integer, never a ForeignKey. So no lingua table
  depends on a host table at the DB level.
- **All host coupling is behind adapters (D-04):**
  - `lingua/integrations/directory.py` — the ONLY lingua code that imports
    `students`. Reimplement this one file against the new host.
  - `homeschool_hub/adapters/lingua_ai.py` — the ONLY file importing `tutor`;
    bound via `settings.LINGUA["AI_CLIENT"]`. Point that setting at a new adapter.
  - Storage + email use Django's own `STORAGES` / mail — nothing lingua-specific.
- **Service layer, no repositories (D-05).** Views → `lingua/services.py` → ORM.

## Data extraction

All lingua data lives in `lingua_*` tables in the default (`public`) schema:

```bash
pg_dump "$DATABASE_URL" --table='lingua_*' > lingua_data.sql
```

That captures every lingua table (`lingua_learner`, `lingua_learnerprofile`, and
future content/review tables). Restore into the standalone DB, then let Django
create the rest of a fresh schema via `migrate`.

### Shared tables the subset references (host-owned, NOT dumped by the glob)

- `auth`/`accounts_customuser` — only if the new product reuses the host's users;
  otherwise the standalone app maps `host_student_id` to its own learner source.
- `students_student` — resolved only through `integrations/directory.py`; the
  standalone app provides its own implementation, so this table is NOT needed.

Because lingua holds no FK into these, the dump restores cleanly on its own; the
"shared" tables matter only for resolving `host_student_id` display info, which is
the adapter's job in the new host.

## Code extraction checklist

1. Copy the `lingua/` package into the new project; add `"lingua"` to `INSTALLED_APPS`.
2. Provide the four settings keys under `LINGUA` (`DEFAULT_LANGUAGE`, `DEFAULT_VARIANT`,
   `MONTHLY_COST_CEILING_USD`, `TTS_PROVIDER`, `AI_CLIENT`).
3. Implement two adapters for the new host:
   - an `AIClient` (see `lingua/ports.py`) and point `LINGUA["AI_CLIENT"]` at it;
   - `lingua/integrations/directory.py` against the new host's learner source.
4. Wire the deletion hook (call `lingua.services.delete_learner_for_student` from
   the host's learner-delete path) + schedule `manage.py lingua_prune_orphans`.
5. `migrate` (fresh schema) or restore the `pg_dump --table='lingua_*'` subset.
6. Run `manage.py test lingua` — the D-03/D-04 guard tests confirm the boundary
   is still intact in the new home.
