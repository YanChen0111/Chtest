# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 06: Requirement To Case Mainline.

## Current Task

Task 3: Add Requirement Review API and mock agent flow.

## Product Value Answer

After this task, Chtest can start a deterministic mock RequirementReviewAgent
flow, persist review scores and risks, and let users retrieve review evidence
for a Requirement.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-06-requirement-to-case.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/05-prompt-skill-contract.md`
7. `docs/contracts/08-mock-provider-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Case generation, case review, frontend, AutomationDraft, Playwright, CI/CD,
  report center, RAG runtime, MCP runtime, and migration reference docs unless a
  concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/requirements/router.py
backend/app/modules/requirements/service.py
backend/app/modules/requirements/schemas.py
backend/app/tests/api/test_requirement_review.py
```

Read existing AI Runtime worker/provider/service patterns only as needed to
reuse AITask, PromptVersion, SkillVersion, and deterministic mock provider
behavior.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py -q
```

Expected result: Requirement Review API focused test passes.

## Acceptance

- Add `POST /api/requirements/{id}/review` and `GET /api/requirements/{id}/review`.
- Start review creates an AITask using active prompt/skill versions and mock
  provider behavior.
- Persist RequirementReview scores, issues, clarification questions, test design
  notes, and RiskItem rows only after schema-valid mock output.
- Response preserves `use_knowledge=false` semantics: explicit
  `context_artifact_ids` are still recorded and returned as used context.
- Do not add case generation, frontend, real provider, external RAG runtime, MCP
  runtime, RBAC, tenants, or permissions.
- `git status --short` shows only expected requirements API/service/schema/test
  files and required task docs before commit.

## Commit Message

```text
feat(requirements): add mock requirement review flow
```

## Next Task

Slice 06 Task 4: Add Case Generation models and migration.
