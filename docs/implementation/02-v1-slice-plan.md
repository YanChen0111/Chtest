# Chtest V1 Slice Plan

## 1. Goal

This document is the executable V1 slice plan. Each Slice must be independently deliverable, independently verifiable, and reversible.

All coding work must follow `docs/implementation/04-ai-vibecoding-governance.md`.

The V1 release spine is `docs/fixtures/00-v1-demo-path.md`. Slice work must optimize for one credible evidence loop before adding broad platform features. `docs/implementation/00-v0.1-walking-skeleton.md` is the early engineering checkpoint used to prove the platform spine before the full V1 Minimum Demo is complete.

## 2. Slice List

| Slice | Name | Goal |
|---:|---|---|
| 1 | Repository and Deploy Skeleton | Establish directories, Docker Compose, PostgreSQL, Redis |
| 2 | Backend Core | FastAPI, Settings, DB, Redis, Alembic, health/ready |
| 2.5 | Frontend Foundation | Vue 3, Vite, Arco, router, store, API shell |
| 3 | Project Core | Project, Module, Repository, Environment, TestCommand |
| 4 | AI Runtime Core | AITask, Artifact, ContextArtifact metadata, LLMCallLog, worker, mock provider |
| 5 | Prompt And Skill Registry | PromptVersion, SkillVersion, schema validation, version hash |
| 6 | Requirement Review | Requirement, RequirementReview, RiskItem, six-dimension scoring |
| 7 | Case Generation Candidate | CaseGenerationTask, GeneratedCaseCandidate, candidate cases |
| 8 | Case Review Window | Approve, edit then approve, reject, request optimization, create TestCase |
| 9 | Case Metrics | Acceptance rate, edit rate, rejection rate, field completeness, duplicate rate |
| 10 | Test Case Library | TestCase, module tree, basic test suite capability |
| 11 | AutomationDraft Foundation | AutomationDraft data model, API, review states |
| 12 | TestRunner Pytest Execution | pytest allowlist execution, docker runner preference, stdout/stderr/JUnit artifact, runtime snapshots |
| 13 | Playwright Minimal Loop | Playwright draft/existing test execution, trace/screenshot |
| 14 | Report And Failure Analysis | FailureAnalysis, Report, evidence manifest |
| 15 | CI/CD Management Foundation | CICDRun, CICDChangedFile, local diff analysis |
| 16 | UnitTestPatch And Regression | UnitTestPatch, PatchScopeGate, pytest regression |
| 17 | Extension Surface | RAG 知识库 surface, empty KnowledgeAdapter, MCP-ready Tool schema |

## 3. P0 Development Batches

Batch 1: Slice 1-5, including Slice 2.5.

- Goal: platform starts, connects DB/Redis, has a Vue/Arco frontend shell, creates projects, creates AI tasks, records context artifact metadata, loads Prompt/Skill.
- Real LLM is not required; use mock provider first.
- Eval bench starts with mock provider and records schema/evidence metrics.
- After Batch 1, run or implement the V0.1 Walking Skeleton smoke before expanding into all requirement/case pages.

Batch 1.5: V0.1 Walking Skeleton.

- Goal: API-first evidence spine: Project -> ContextArtifact -> mock AITask -> artifacts -> minimal pytest execution -> minimal report JSON.
- Source: `docs/implementation/00-v0.1-walking-skeleton.md`.
- This is an engineering checkpoint, not the final V1 product acceptance demo.

Batch 2: Slice 6-10.

- Goal: Golden Path 1, requirement to cases.

Batch 3: Slice 11-14.

- Goal: Golden Path 2 plus V1 Minimum Demo evidence loop, case to automation to report.

Batch 4: Slice 15-16.

- Goal: Golden Path 3, CI/CD-managed local Git diff to quality report.

## 4. Slice Task Table Template

Each active Slice must maintain a Task table in the implementation plan or `memory/08-session-handoff.md`.

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Backend health API | planned | `cd backend && uv run pytest app/tests/test_health.py -q` | - | - |

Allowed statuses:

```text
planned, doing, blocked, done, reverted
```

## 5. Slice Acceptance Template

Each Slice must declare:

```text
Models:
APIs:
State machines:
Fixtures:
Verification commands:
UI/API verification entry:
Artifacts/logs:
Memory updates:
Commits:
```

A missing item must be explicitly marked `not applicable` with a reason.

Each Slice must also name one product value answer:

```text
Product value answer:
```

## 6. Slice Completion Gate

A Slice is complete only when:

- Every Task is `done` or documented as `blocked` / `reverted`.
- Every completed Task has a commit.
- Every completed Task has a verification command and result.
- Slice-level tests or smoke checks pass.
- Golden Path fixture is checked when relevant.
- `docs/fixtures/00-v1-demo-path.md` remains closer to completion or explicitly unaffected.
- `docs/contracts/*` remain aligned with implementation.
- `memory/07-dev-log.md` and `memory/08-session-handoff.md` are updated.
- `git status --short` is clean or remaining changes are documented.
- Next Slice or next Task is named in handoff.

## 7. Commit Rhythm

- Do not commit an entire Slice at once.
- Commit each completed Task.
- Do not mix unrelated formatting with behavior.
- Do not mix multiple Slices in one commit.
- Commit message format follows `docs/implementation/04-ai-vibecoding-governance.md`.

## 8. Detailed Slice Task Plans

- `docs/implementation/00-v0.1-walking-skeleton.md`
- `docs/implementation/slices/slice-01-platform-foundation.md`
- `docs/implementation/slices/slice-02-backend-core.md`
- `docs/implementation/slices/slice-02-frontend-foundation.md`
- `docs/implementation/slices/slice-03-project-core.md`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`

Add one file per Slice as implementation approaches that Slice.
