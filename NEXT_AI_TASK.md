# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. The current focus is V2 acceptance stabilization through the local
dev/browser workflow. Docker runtime work remains intentionally skipped by the
user because the local Docker Desktop/WSL engine cannot be repaired in this
session.

## Current Slice

V2 acceptance stabilization: make the local-first AI testing workbench feel
acceptance-ready for the main reviewer workflow from requirement review to case
generation, knowledge grounding, automation planning, automation draft review,
and local execution evidence surfaces.

## Current Task

Case generation P0/P1 optimization is complete.

Completed P0/P1 behaviors:

1. Case generation is observable as an asynchronous task instead of a hidden
   long-running request.
2. The frontend shows CaseGenerationTask/AITask ids, status, and recoverable
   failure details before attempting to load candidates.
3. Wrong-domain output is blocked with `CASE_GENERATION_DOMAIN_MISMATCH` and
   cannot persist candidates.
4. The candidate review page separates generation entry, candidate list,
   selected candidate detail, edit form, review result, and review history so
   switching candidates does not show a previous candidate's review result.
5. Requirement document selection is explicit and does not auto-select the
   first document without saved context.
6. The case review surface includes a lightweight testing-dimension coverage
   matrix for main flow, negative path, boundary, state, permission, channel,
   device/current conditions, and risk references.
7. Knowledge-card review now keeps vector-index coverage honest: cards that
   become stale, unsafe, duplicate, or archived mark existing indexes stale and
   are excluded from prompt-ready index coverage.

## Product Value Answer

The user can now see whether case generation is running, failed, or complete;
avoid accepting wrong-domain generated cases; review each candidate without
state leaking from the previous candidate; and understand basic test-dimension
coverage before promoting generated cases.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/04-ai-vibecoding-governance.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `memory/08-session-handoff.md`
8. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Docker Desktop, WSL, container runtime recovery, broad roadmap, migration,
  enterprise collaboration, marketplace, distributed execution, cloud storage,
  cloud CI/provider integration, RBAC, tenants, permissions, or unrelated
  deleted golden-chain files unless a concrete verification failure requires
  them.

## Expected Files

Default write boundary for the next local evidence risk:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
backend/app/modules/cases/*
backend/app/modules/knowledge/*
backend/app/tests/api/test_case_generation.py
backend/app/tests/api/test_test_knowledge_cards.py
frontend/src/api/cases.ts
frontend/src/stores/cases.ts
frontend/src/stores/extension.ts
frontend/src/views/cases/CaseGenerationReviewView.vue
frontend/src/views/cases/CaseGenerationReviewView.spec.ts
frontend/src/views/extension/KnowledgeBaseView.vue
frontend/src/views/extension/KnowledgeBaseView.spec.ts
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
```

Only edit files that are directly required to fix a verification blocker. Do
not revert unrelated dirty-worktree changes.

## Verification Commands

Use focused verification first:

```bash
backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_test_knowledge_cards.py -q
```

```bash
backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_test_knowledge_cards.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_model_connection_config.py backend/app/tests/api/test_extension_surface.py -q
```

```bash
D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/settings/ProjectSettingsView.spec.ts src/views/extension/KnowledgeBaseView.spec.ts src/views/requirements/RequirementReviewView.spec.ts src/views/cases/CaseGenerationReviewView.spec.ts
```

```bash
D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run build
git diff --check
```

Docker/compose runtime verification is intentionally skipped until the machine's
Docker Desktop Linux Engine is repaired outside this repo.

## Acceptance

- Backend focused case-generation suite passes.
- Backend related acceptance suite passes.
- Frontend settings, knowledge, requirement review, and case generation suite
  passes.
- Frontend build passes with only the existing Vite chunk-size warning.
- `git diff --check` passes.

## Commit Message

```text
fix(cases): harden generation review workflow
```

## Next Task

Continue non-Docker V2 acceptance stabilization with the next smallest local
evidence risk: add a requirement clarification/decision-table gate before final
case generation, then persist explicit `coverage_dimensions` from the
CaseGenerationAgent output instead of deriving coverage heuristically in the
frontend.
