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

Case generation P0/P1 optimization and the AutomationDraft reviewer-input UX
optimization are complete.

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
7. A pre-generation decision-table gate records reviewer acknowledgement before
   final candidate generation and persists the acknowledged dimension list into
   CaseGenerationAgent prompt input evidence.
8. GeneratedCaseCandidate now persists explicit `coverage_dimensions` from the
   CaseGenerationAgent output; missing or invalid coverage dimensions fail
   schema validation, and the frontend displays persisted dimensions instead of
   deriving them from text heuristics.
9. Prompt, Skill, mock provider, API contract, data-model contract, and golden
   fixture expectations now require coverage dimensions for generated cases.
10. Knowledge-card review now keeps vector-index coverage honest: cards that
    become stale, unsafe, duplicate, or archived mark existing indexes stale and
    are excluded from prompt-ready index coverage.
11. The AutomationDraft page loads active reviewed TestCases and project
    TestCommands instead of requiring testers to paste UUIDs.
12. TestCase choices show title, priority, test type, and a short id; API/Newman
    and JMeter execution choices only show compatible active TestCommands.
13. The AutomationDraft reviewer flow exposes four visible stages: select case,
    approve plan, review draft, and collect execution evidence.
14. The generate action stays disabled until a TestCase is selected, and missing
    compatible TestCommands produce a configuration-oriented hint.

## Product Value Answer

The user can now see whether case generation is running, failed, or complete;
avoid accepting wrong-domain generated cases; review each candidate without
state leaking from the previous candidate; confirm the requirement/design matrix
before generation; and understand persisted test-dimension coverage before
promoting generated cases. The automation reviewer can also select named assets,
see the current workflow stage, and avoid launching API/JMeter with the wrong
TestCommand type.

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
frontend/src/stores/automation.ts
frontend/src/views/automation/AutomationDraftReviewView.vue
frontend/src/views/automation/AutomationDraftReviewView.spec.ts
frontend/src/views/cases/CaseGenerationReviewView.vue
frontend/src/views/cases/CaseGenerationReviewView.spec.ts
frontend/src/views/extension/KnowledgeBaseView.vue
frontend/src/views/extension/KnowledgeBaseView.spec.ts
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/05-prompt-skill-contract.md
docs/contracts/08-mock-provider-contract.md
docs/fixtures/01-golden-requirement-to-case.md
prompts/case_generation/v1.md
skills/test-case-generation-skill/v1.md
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
D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/automation/AutomationDraftReviewView.spec.ts src/layouts/WorkbenchLayout.spec.ts src/views/execution/PytestExecutionView.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts
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
- Automation reviewer, layout, and related execution suite passes.
- Frontend build passes with only the existing Vite chunk-size warning.
- `git diff --check` passes.

## Commit Message

```text
fix(frontend): simplify automation reviewer inputs
```

## Next Task

Repair the local acceptance database baseline on a copy of the current database
before continuing the browser reviewer smoke. The current database has no
Alembic version record, is missing current GeneratedCaseCandidate columns, and
contains PromptVersion rows whose content conflicts with the current registry
files. Define a safe, tested upgrade/diagnostic path; do not silently overwrite
prompt registry truth or mutate the only local database copy. Docker/compose
runtime repair remains out of scope until the local engine is fixed outside this
repo.
