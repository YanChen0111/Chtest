# Slice 06: Requirement To Case Task Plan

## Goal

Create the V1 mainline from requirement capture to reviewed test cases.

This slice must use the existing AI runtime, Prompt/Skill registry, mock
provider, ContextArtifact support, and Project Core. It should make the golden
requirement fixture reviewable and traceable without adding automation draft,
execution, CI/CD, RAG runtime, MCP runtime, RBAC, or multi-user scope.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/contracts/08-mock-provider-contract.md`
- `docs/fixtures/01-golden-requirement-to-case.md`
- `docs/implementation/01-v1-delivery-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`

## Preconditions

- Slice 03 Project Core is complete.
- Slice 04 AI Runtime Core is complete.
- Slice 05 Prompt and Skill Registry is complete.
- Slice 02.5 Frontend Foundation is complete before frontend tasks.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Requirement Review models and migration | done | `backend/.venv/bin/python -m pytest backend/app/tests/db/test_requirement_review_models.py -q` | `75c845c` | Requirement, RequirementReview, RiskItem |
| Add Requirement API | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirements.py -q` | `85f5d5a` | Create/get/list requirements |
| Add Requirement Review API and mock agent flow | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py -q` | `290db19` | Start review, persist review and risks |
| Add Case Generation models and migration | done | `backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py -q` | `069ebf9` | CaseGenerationTask, GeneratedCaseCandidate, TestCase |
| Add Case Generation API and mock agent flow | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py -q` | `67b2ca8` | Generate/list candidates |
| Add Case Review API | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_review.py -q` | `c7c120f` | approve, approve_after_edit, reject, needs_optimization |
| Add Requirement To Case golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py -q` | `9c2c7d3` | Fixture-aligned backend flow |
| Add Requirement Review frontend shell | done | `npm --prefix frontend run test -- --run` | `ddfa055` | Requirement input and review result shell |
| Add Case Generation Review frontend shell | done | `npm --prefix frontend run test -- --run` | `dc2217c` | Candidate review shell |

## Task 1: Add Requirement Review Models And Migration

Goal: Add Requirement, RequirementReview, and RiskItem models matching the data
contract.

Expected files:

- `backend/app/modules/requirements/__init__.py`
- `backend/app/modules/requirements/models.py`
- `backend/app/modules/requirements/schemas.py`
- `backend/alembic/versions/<revision>_requirement_review.py`
- `backend/app/tests/db/test_requirement_review_models.py`

Verification command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_requirement_review_models.py -q
```

Non-goals:

- Do not add RequirementReviewAgent execution.
- Do not add CaseGenerationTask, GeneratedCaseCandidate, or TestCase yet.
- Do not add frontend pages.
- Do not add RAG runtime, MCP runtime, RBAC, tenants, or permissions.

Commit message:

```text
feat(requirements): add requirement review models
```

## Task 2: Add Requirement API

Goal: Add create/read/list behavior for manual Requirement records.

Expected files:

- `backend/app/modules/requirements/router.py`
- `backend/app/modules/requirements/service.py`
- `backend/app/modules/requirements/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_requirements.py`

Verification command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirements.py -q
```

Non-goals:

- Do not start AI review in this task.
- Do not generate risks or cases.
- Do not implement frontend.

Commit message:

```text
feat(requirements): add requirement api
```

## Task 3: Add Requirement Review API And Mock Agent Flow

Goal: Add `POST /api/requirements/{id}/review` and
`GET /api/requirements/{id}/review` using the existing AI runtime foundation,
active prompt/skill versions, and deterministic mock provider output.

Expected files:

- `backend/app/modules/requirements/router.py`
- `backend/app/modules/requirements/service.py`
- `backend/app/modules/requirements/schemas.py`
- `backend/app/tests/api/test_requirement_review.py`

Verification command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py -q
```

Non-goals:

- Do not add real LLM provider calls.
- Do not add external RAG; local ContextArtifact ids are explicit only.
- Do not add case generation in this task.
- Do not bypass schema validation before persisting review and risks.

Commit message:

```text
feat(requirements): add mock requirement review flow
```

## Task 4: Add Case Generation Models And Migration

Goal: Add CaseGenerationTask, GeneratedCaseCandidate, and TestCase models.

Expected files:

- `backend/app/modules/cases/__init__.py`
- `backend/app/modules/cases/models.py`
- `backend/app/modules/cases/schemas.py`
- `backend/alembic/versions/<revision>_case_generation.py`
- `backend/app/tests/db/test_case_generation_models.py`

Verification command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py -q
```

Non-goals:

- Do not add AutomationDraft.
- Do not create official TestCase records from candidates without review.
- Do not implement duplicate detection beyond schema placeholders.

Commit message:

```text
feat(cases): add case generation models
```

## Task 5: Add Case Generation API And Mock Agent Flow

Goal: Add `POST /api/case-generation/tasks` and
`GET /api/case-generation/tasks/{id}/candidates` using deterministic mock
provider output.

Expected files:

- `backend/app/modules/cases/router.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_case_generation.py`

Verification command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py -q
```

Non-goals:

- Do not let generated candidates enter the TestCase library automatically.
- Do not add frontend review UI.
- Do not add AutomationDraft or execution logic.

Commit message:

```text
feat(cases): add mock case generation flow
```

## Task 6: Add Case Review API

Goal: Add candidate review actions that can approve, approve after edit, reject,
or request optimization, with approved candidates creating TestCase records.

Expected files:

- `backend/app/modules/cases/router.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/tests/api/test_case_review.py`

Verification command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_review.py -q
```

Non-goals:

- Do not implement CaseReviewAgent optimization in this task beyond the
  `needs_optimization` state.
- Do not execute or automate approved cases.
- Do not add frontend.

Commit message:

```text
feat(cases): add case review api
```

## Task 7: Add Requirement To Case Golden Smoke

Goal: Add a backend smoke test aligned to
`docs/fixtures/01-golden-requirement-to-case.md`.

Expected files:

- `backend/app/tests/golden/test_requirement_to_case.py`

Verification command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py -q
```

Non-goals:

- Do not add browser automation.
- Do not cover AutomationDraft or execution.

Commit message:

```text
test(golden): add requirement to case smoke
```

## Task 8: Add Requirement Review Frontend Shell

Goal: Add the first Requirement Review view shell for creating a requirement and
viewing review/risk results.

Expected files:

- `frontend/src/views/requirements/RequirementReviewView.vue`
- `frontend/src/api/requirements.ts`
- `frontend/src/stores/requirements.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `frontend/src/views/requirements/RequirementReviewView.spec.ts`

Verification command:

```bash
npm --prefix frontend run test -- --run
```

Non-goals:

- Do not add full case review UI.
- Do not add AutomationDraft entry points.

Commit message:

```text
feat(frontend): add requirement review shell
```

## Task 9: Add Case Generation Review Frontend Shell

Goal: Add a read/review shell for generated case candidates.

Expected files:

- `frontend/src/views/cases/CaseGenerationReviewView.vue`
- `frontend/src/api/cases.ts`
- `frontend/src/stores/cases.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `frontend/src/views/cases/CaseGenerationReviewView.spec.ts`

Verification command:

```bash
npm --prefix frontend run test -- --run
```

Non-goals:

- Do not add AutomationDraft UI.
- Do not add low-code test authoring.

Commit message:

```text
feat(frontend): add case generation review shell
```

## Slice Completion Gate

- Requirement can be created and reviewed with deterministic mock output.
- RequirementReview and RiskItem persist fixture-aligned scores and risks.
- CaseGenerationTask can generate at least five fixture-aligned candidates.
- Generated candidates remain review-gated and do not become TestCase records
  until approved.
- Case review can approve, approve after edit, reject, and request optimization.
- Golden fixture smoke passes.
- Frontend shells expose the requirement review and candidate review flow without
  adding AutomationDraft or execution behavior.

## Completion Evidence

Status: complete on 2026-06-29.

Product value answer:

```text
Chtest can run the V1 requirement-to-case mainline with deterministic mock AI:
create/review a requirement, generate candidate cases, review candidates, and
promote approved candidates into TestCase records, with first frontend shells for
requirement review and candidate review.
```

Verification commands:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/golden/test_requirement_to_case.py -q
npm --prefix frontend run test -- --run
```

Verification results:

- Backend Requirement Review / Case Generation / Case Review / Golden smoke:
  `15 passed`.
- Frontend workbench shell tests: `7 passed`, `10 tests passed`.

Commits:

- `75c845c` Requirement Review models and migration.
- `85f5d5a` Requirement API.
- `290db19` Requirement Review API and mock flow.
- `069ebf9` Case Generation models and migration.
- `67b2ca8` Case Generation API and mock flow.
- `c7c120f` Case Review API.
- `9c2c7d3` Requirement To Case golden smoke.
- `ddfa055` Requirement Review frontend shell.
- `dc2217c` Case Generation Review frontend shell.

Non-goals kept out:

- AutomationDraft, execution, Playwright, CI/CD quality, report center, real
  provider, RAG runtime, MCP runtime, RBAC, tenants, and permissions.
