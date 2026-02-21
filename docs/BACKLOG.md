# Awesome OpenClaw Skills — Backlog

## Project Status

| Metric | Value |
|--------|-------|
| **Phase** | 4 of 5 (Web MVP complete) |
| **Done** | 32 tasks |
| **Remaining** | 17 tasks |
| **P0 Complete** | 100% |
| **P1 Complete** | ~75% |
| **CI** | GitHub Actions (audit + tests on PR) |

**Completed phases**: Foundation (ingestion, adapter), Verification (schema, evaluation, CI), Ranking & Docs, Web App MVP (browse, search, chat, rate, use, ClawHub links).

**Next focus**: Phase 5 — Comment/review storage, Report flow, Auth, Deployment, Docs site.

---

## Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Done
- **Priority**: P0 (critical) | P1 (high) | P2 (medium) | P3 (low)

---

## Phase 1: Foundation

### Ingestion

| ID | Task | Prio | Status |
|----|------|------|--------|
| I1 | ClawHub skill list fetch (script or API) | P0 | [x] |
| I2 | Normalize skill schema (SkillRecord) | P0 | [x] |
| I3 | Incremental sync (delta updates) | P1 | [x] |
| I4 | Support clawhub.biz as secondary source | P2 | [ ] |
| I5 | GitHub openclaw/clawhub bundled skills sync | P2 | [ ] |

### SKILL.md Adapter

| ID | Task | Prio | Status |
|----|------|------|--------|
| A1 | SKILL.md parsing and executable extraction | P0 | [x] |
| A2 | Support .js in scripts/ for analysis | P2 | [ ] |
| A3 | Per-script findings in report | P2 | [ ] |

---

## Phase 2: Verification

### Schema

| ID | Task | Prio | Status |
|----|------|------|--------|
| S1 | AgentSkills schema validation | P0 | [x] |
| S2 | Declared vs actual (metadata vs code) check | P1 | [ ] |
| S3 | Stricter name/description validation | P2 | [ ] |

### Evaluation

| ID | Task | Prio | Status |
|----|------|------|--------|
| E1 | Safe/unsafe fixtures in evaluation/ | P0 | [x] |
| E2 | test_static.py regression suite | P0 | [x] |
| E3 | test_schema.py format compliance | P0 | [x] |
| E4 | Optional runtime sandbox tests | P3 | [ ] |
| E5 | CI pipeline (skill-audit + evaluation on PR) | P1 | [x] |

---

## Phase 3: Ranking & Docs

### Ranking

| ID | Task | Prio | Status |
|----|------|------|--------|
| R1 | Composite score (safety, format, doc, community) | P0 | [x] |
| R2 | Tier assignment (featured, trusted, community, flagged) | P0 | [x] |
| R3 | skill-audit --rank CLI output | P0 | [x] |
| R4 | Integrate ClawHub community data (stars, downloads) | P1 | [ ] |
| R5 | registry.json generation | P0 | [x] |

### Usage Docs

| ID | Task | Prio | Status |
|----|------|------|--------|
| U1 | Auto-generate USAGE.md from metadata | P0 | [x] |
| U2 | Per-skill USAGE.md in skills_index/{name}/ | P1 | [ ] |
| U3 | Editable usage (override/custom docs) | P2 | [ ] |

---

## Phase 4: Web App MVP

### Browse & Search

| ID | Task | Prio | Status |
|----|------|------|--------|
| W1 | Web app scaffolding (Next.js/React) | P0 | [x] |
| W2 | Load registry.json, list skills | P0 | [x] |
| W3 | Filter by tier, grade, category | P1 | [x] |
| W4 | Keyword search | P1 | [x] |
| W5 | Semantic/vector search (optional) | P2 | [ ] |

### Install & Use

| ID | Task | Prio | Status |
|----|------|------|--------|
| W6 | Copy install command | P0 | [x] |
| W7 | Link to ClawHub skill page | P0 | [x] |
| W8 | One-click "Add to workspace" if supported | P2 | [ ] |

### Chat

| ID | Task | Prio | Status |
|----|------|------|--------|
| W9 | Chat UI component | P0 | [x] |
| W10 | LLM integration with skill-augmented context | P0 | [x] |
| W11 | Suggest skills from user query | P0 | [x] |
| W12 | Show install + usage in chat response | P0 | [x] |

---

## Phase 5: Web Full

### Rate & Review

| ID | Task | Prio | Status |
|----|------|------|--------|
| W13 | Star/rating UI | P1 | [x] |
| W14 | Comment/review storage | P1 | [ ] |
| W15 | Report skill flow | P1 | [ ] |
| W16 | Auth (GitHub OAuth) for ratings | P1 | [ ] |
| W17 | Sync ratings with ClawHub (optional) | P2 | [ ] |

### Polish

| ID | Task | Prio | Status |
|----|------|------|--------|
| W18 | Responsive design | P1 | [ ] |
| W19 | Deployment config (Vercel/self-host) | P1 | [ ] |
| W20 | Docs site from skills_index | P2 | [ ] |

---

## Dependency Graph (High Level)

```
I2 → I1, I3
A1 → I2
S1, E1-E3 → A1
R1-R3, U1 → S1
W1-W2 → R5
W9-W12 → W2
```

---

## Task Template

When adding new tasks, use:

```markdown
| ID | Task | Prio | Status |
|----|------|------|--------|
| XX | Description | P0/P1/P2/P3 | [ ] |
```

Acceptance criteria: 1–2 sentences per task.
