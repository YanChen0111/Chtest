# Chtest V1 Development Process

## 1. Purpose

This document defines the V1 development process. Detailed AI coding governance is defined in `docs/implementation/04-ai-vibecoding-governance.md` and is mandatory for all implementation work.

The purpose is to ensure future AI sessions can continue from stable facts, write contract-aligned code, verify every small step, commit safely, and leave usable handoff notes.

## 2. Required Development Loop

```text
Choose one Slice
  -> choose one Task
  -> define Task Definition Of Ready
  -> read memory + contracts + fixture + governance
  -> write or run focused test/smoke
  -> implement minimal code
  -> run verification
  -> fix failures
  -> git diff self-review
  -> commit
  -> update dev-log and handoff
```

The authoritative Task loop, Git rules, testing rules, rollback rules, and handoff rules are in `04-ai-vibecoding-governance.md`.

## 3. Required Reading Before Development

Minimum reading set:

1. `memory/README.md`
2. `memory/13-ai-readable-project-brief.md`
3. `memory/08-session-handoff.md`
4. `docs/product/01-positioning-and-scope.md`
5. `docs/contracts/01-data-model-contract.md`
6. `docs/contracts/02-api-contract.md`
7. `docs/contracts/03-state-machines.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`
9. `memory/11-implementation-slices.md`

Task-specific reading:

| Task Area | Additional Reading |
|---|---|
| Requirement to cases | `docs/fixtures/01-golden-requirement-to-case.md` |
| Case to automation | `docs/fixtures/02-golden-case-to-playwright.md` |
| Git quality | `docs/fixtures/03-golden-cicd-quality.md` |
| Prompt/Skill | `docs/contracts/05-prompt-skill-contract.md` |
| Artifact/Report | `docs/contracts/04-artifact-contract.md` |
| Error handling | `docs/contracts/06-error-code-contract.md` |
| Seed data | `docs/contracts/07-seed-data-contract.md` |
| Mock Provider | `docs/contracts/08-mock-provider-contract.md` |
| Docker/deploy | `docs/deployment/01-docker-environment.md` |

## 4. Slice Definition Of Done

Each Slice is complete only when:

- All Slice Tasks have status `done` or a documented blocked/unfinished reason.
- Every completed Task has a commit.
- Every completed Task has a verification command and result.
- Data model changes match `docs/contracts/01-data-model-contract.md`.
- API changes match `docs/contracts/02-api-contract.md`.
- State transitions match `docs/contracts/03-state-machines.md`.
- Relevant fixture or smoke path exists.
- UI or API verification entry exists when applicable.
- Artifacts/logs/errors are handled when applicable.
- Slice completion updates `memory/07-dev-log.md`.
- Slice completion updates `memory/08-session-handoff.md` with commit table and next Task.
- If the session ends before Slice completion, `memory/08-session-handoff.md` Task table is updated; `memory/07-dev-log.md` is updated only for major context changes.
- `git status --short` is clean or remaining changes are explicitly documented.

## 5. Technology Stack Lock

V1 uses:

- Backend: FastAPI.
- ORM: SQLAlchemy 2.
- Schema: Pydantic v2.
- Migration: Alembic.
- DB: PostgreSQL.
- Queue: Redis + RQ.
- Frontend: Vue 3 + TypeScript + Vite.
- UI: Arco Design Vue.
- Runner: pytest / subprocess allowlist.
- Web automation: Playwright.
- Deploy: Docker Compose.
- LLM: Mock Provider + OpenAI-compatible Provider.

Changing the main stack requires an ADR before implementation.

## 6. AI File-Writing Strategy

| Scenario | Strategy |
|---|---|
| Requirement/TestCase to automation | AI creates AutomationDraft only; no direct target-repo write |
| Git unit-test support | AI creates UnitTestPatch; approval required; test directories only |
| Business source | AI auto-modification is forbidden in V1 |
| Tool execution | Only ToolDefinition allowlisted commands |
| Report generation | Conclusions must reference evidence/artifacts |

## 7. Recommended Implementation Order

1. Platform Foundation.
2. Project Core.
3. AI Runtime Core.
4. Requirement To Case.
5. AutomationDraft + TestRunner.
6. Playwright minimal loop.
7. CI/CD Management support workflow.
8. Report + Failure Analysis.
9. Extension Surface.

## 8. Session Finish Format

When a Slice completes, update `memory/08-session-handoff.md` with:

```text
Completed:
Verification:
Changed files:
Commits:
Unverified items:
Risks:
Next recommended Task:
Latest stable commit:
```

Update `memory/07-dev-log.md` only when a Slice completes or when a major context change must be preserved.
