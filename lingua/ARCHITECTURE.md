# Lingua — Architecture Diagrams

Five diagrams for the Spanish acquisition module. See `SPEC.md` (build) and `DECISIONS.md` (rationale).

---

## 1. Module boundary — the "no FK across the seam" rule

The dashed red edge is the load-bearing rule (D-03): `lingua` never holds a ForeignKey into the host.
The learner is a plain `host_student_id` int resolved through the UserDirectory adapter; the only code that
imports `tutor` is the host's `lingua_ai.py` adapter. This is what makes the module extractable.

```mermaid
flowchart TB
  subgraph HOST["Steadfast Scholars (host platform)"]
    Student["students.Student<br/>PK = host_student_id"]
    TutorAI["tutor.ai<br/>Anthropic seam: grade_work(), is_configured()"]
    Storages["Django STORAGES (R2 / filesystem)"]
    subgraph ADAPTERS["host composition root — the ONLY code importing tutor / students"]
      AIAdapter["adapters/lingua_ai.py<br/>implements lingua.ports.AIClient"]
      DirAdapter["lingua/integrations/directory.py<br/>host_student_id → name, level"]
    end
  end

  subgraph LINGUA["lingua app — extractable module (public schema, lingua_* tables)"]
    Ports["ports.py<br/>AIClient ABC + DTOs<br/>no Django, no tutor import"]
    Services["services.py<br/>orchestration (mirrors tutor.grading)"]
    Models["models.py<br/>Learner(host_student_id:int, NO FK)<br/>Story · ReviewItem · ..."]
    Views["views.py (fat, function-based)<br/>+ vanilla-JS templates"]
  end

  Views --> Services
  Services --> Models
  Services -->|depends on interface| Ports
  AIAdapter -.implements.-> Ports
  AIAdapter --> TutorAI
  Services -->|plain int, via| DirAdapter
  DirAdapter -->|reads| Student
  Models -. "host_student_id: plain int — NO ForeignKey (load-bearing)" .-> Student
  Models --> Storages

  classDef nofk stroke-dasharray:5 5,stroke:#c0392b,color:#c0392b;
  class Student nofk
```

---

## 2. Content authoring pipeline (runs LOCALLY, like the manga `generate_*` flow)

AI generation → LLM-critic pre-filter → frequency-band leveling → Polly TTS + word timings → R2 →
parent batch approval → published. Nothing heavy runs on the web dyno (D-16).

```mermaid
sequenceDiagram
  actor Parent
  participant CLI as generate_stories (mgmt cmd, LOCAL)
  participant AI as AIClient → tutor.ai
  participant Critic as LLM-critic pre-filter
  participant Level as Freq-band filter (SUBTLEX)
  participant TTS as Amazon Polly (neural es-MX)
  participant R2 as R2 (public, immutable)
  participant DB as lingua DB

  Parent->>CLI: run generate (theme, level, count)
  CLI->>AI: generate story (fenced prompt, no child PII)
  AI-->>CLI: draft text
  CLI->>Critic: rate naturalness / errors / false-friends
  Critic-->>CLI: pass / flag (flagged dropped pre-queue)
  CLI->>Level: frequency-band scan
  Level-->>CLI: level + out-of-band word flags
  CLI->>TTS: synthesize (numerals spelled out)
  TTS-->>CLI: mp3 + speech marks (UTF-8 byte offsets)
  CLI->>CLI: byte→char map → flat timing JSON {i,s,e,cs,ce}
  CLI->>R2: upload mp3 + timing.json (content-hash key, immutable)
  CLI->>DB: ContentDraft(status=pending_approval) + AuditEvent
  Parent->>DB: batch review (~10) → approve
  DB-->>DB: status=approved (approver + ts) → visible to learner
```

---

## 3. Daily learning session flow

Branches by `support_level`; the session-length cap is a hard constraint set by support_level, not by
content level (D-66); the scheduler splits Leitner (parent-graded) vs FSRS (two-button).

```mermaid
flowchart TD
  Start([Child opens portal via signed token]) --> Resolve[Resolve Student → Learner]
  Resolve --> Profile{support_level?}
  Profile -->|PARENT_MEDIATED / KIDS_EARLY| EarlyCap["cap ≤10 min · Leitner ≤15 · parent-as-grader"]
  Profile -->|GUIDED / KIDS_OLDER| OlderCap["cap ~15-20 min · FSRS two-button"]
  EarlyCap --> Plan[Daily Plan generator]
  OlderCap --> Plan
  Plan --> Reread{reread due?<br/>narrow-reading}
  Reread -->|yes: capped + rotated| ReadBlock
  Reread -->|no| NewStory["serve next story at/near content_ceiling<br/>(bounded choice: pick 1 of 3)"]
  NewStory --> ReadBlock[Reading block: read-along / shared]
  ReadBlock --> Listen[Listening: ExternalActivity minutes]
  Listen --> Review[Vocabulary review — scheduler by profile]
  Review --> Activity[One activity: phonics mini / comprehension check]
  Activity --> CapCheck{session cap reached?}
  CapCheck -->|no| Plan
  CapCheck -->|yes| Wrap["celebrate comprehension milestone<br/>log minutes + words + known-words"]
  Wrap --> Signal{k-of-n advance rule met?}
  Signal -->|yes| Nudge[parent-only: 'looks ready to move up']
  Signal -->|no| End([End])
  Nudge --> End
```

---

## 4. Data model ERD (v1)

`host_student_id` is shown as a non-FK reference (dotted) — the boundary rule made explicit. Lingua-internal
relations are ordinary CASCADE FKs. `ExternalActivity`/`ListeningLog` reuse the host activities app (N-02).

```mermaid
erDiagram
  Student ||..o| Learner : "host_student_id — plain int, NO FK"
  Learner ||--|| LearnerProfile : has
  Learner ||--o{ ReviewItem : owns
  Learner ||--o{ ReadingSession : logs
  Learner ||--o{ KnownWord : accumulates
  Learner ||--o{ AdvancementSignal : receives
  Theme ||--o{ Story : themes
  Story ||--|| StoryAudio : "per voice"
  Story ||--o{ StoryWord : "tokens (cognate/freq flags)"
  Story ||--o{ ComprehensionCheck : has
  Story ||--o| ContentDraft : "from approval"
  Story ||--o{ ReadingSession : "read in"
  VocabEntry ||--o{ ReviewItem : reviewed-as
  VocabEntry ||--o{ KnownWord : credited-as
  ContentDraft ||--o{ AuditEvent : logged
  ExternalActivity ||--o{ ListeningLog : "minutes (host reuse)"

  Learner {
    int host_student_id "NO FK — resolves via UserDirectory"
    string language "es"
    string variant "es-MX"
  }
  LearnerProfile {
    string track_profile "KIDS_EARLY|KIDS_OLDER"
    string support_level "PARENT_MEDIATED|GUIDED|INDEPENDENT"
    string content_ceiling "L1..L8"
  }
  ReviewItem {
    string scheduler "leitner|fsrs"
    json scheduler_state
    datetime due "indexed mirror"
    datetime paused_until
  }
  Story {
    string language "es"
    string level "L1..L8 (hand + freq-band)"
    text body
    fk theme
  }
  StoryAudio {
    string provider "polly"
    string voice "Mia"
    json timings "flat {i,s,e,cs,ce}"
    string r2_key "content-hash, public immutable"
  }
  ContentDraft {
    string status "pending_approval|approved"
    int approved_by "host user id"
    datetime approved_at
  }
```

---

## 5. Milestone roadmap — v1 cut line after M2

```mermaid
flowchart LR
  subgraph V1["v1 — SHIP (M0-M2)"]
    direction TB
    M0["M0 Foundation<br/>E-01 arch · E-02 spikes · E-13 compliance(start)"]
    M1["M1 Read one story w/ synced audio<br/>E-03 content+critic · E-04 Polly audio · E-05 reading"]
    M2["M2 Daily habit<br/>E-06 listening · E-07 review · E-08 phonics+daily-plan+reread"]
    M0 --> M1 --> M2
  end
  subgraph V2["v2+ — BACKLOG (deferred, ticketed)"]
    direction TB
    M3["M3 · E-09 full leveling+curriculum · E-10 dashboard+charter report"]
    M4["M4 · E-11 library books · E-12 tutoring (SPIKE-05 Cal.com)"]
    M5["M5 · E-14 teen/adult · F-05 output · F-13 human audio/aeneas · F-14 shadowing"]
    M3 --> M4 --> M5
  end
  SPIKE01[SPIKE-01 Polly timings] --> M1
  SPIKE03[SPIKE-03 leveling validate] --> M1
  SPIKE04[SPIKE-04 gen+critic+approve] --> M1
  M2 ==>|v1 cut line| M3
```
