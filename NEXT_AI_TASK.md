# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 31: Generated Case Knowledge Evidence Persistence.

## Current Task

Slice 31 Task 3: Persist Generated-Case Knowledge Evidence Fields.

## Product Value Answer

After this task, generated case candidates persist and return normalized
knowledge evidence fields through the existing backend data flow.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md`
8. `docs/fixtures/18-test-knowledge-card-contract-golden.md`
9. `memory/08-session-handoff.md`
10. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, and provider implementation
  docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/cases/models.py
backend/app/modules/cases/schemas.py
backend/app/modules/cases/service.py
backend/app/alembic/versions/<new-migration>.py
backend/app/tests/db/test_case_generation_models.py
backend/app/tests/api/test_case_generation.py
docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Use TDD. Do not add frontend code, package upgrades, external provider
integrations, vector database, embeddings, reranking, background indexing,
graph runtime, MCP runtime, TestKnowledgeCard CRUD, artifact upload/mutation/
delete, generated-case auto-approval, runner behavior changes, report
generation behavior changes, remote CI provider behavior, RBAC, tenants, or
permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py backend/app/tests/api/test_case_generation.py -q
git diff --check
```

Expected result: database/API focused tests pass, knowledge evidence fields are
persisted and listed with backward-compatible defaults, and diff check passes.

## Acceptance

- GeneratedCaseCandidate model persists all Slice 31 evidence fields with safe
  defaults.
- Migration adds only generated_case_candidates columns required by this slice.
- Case generation persistence copies normalized fields from AI output when
  present and uses safe defaults when absent.
- Candidate list API returns the fields.
- Existing case generation behavior remains backward-compatible.
- No TestCase, TestRun, Report, retrieval job, vector index, graph job,
  provider call, artifact mutation, or review bypass is introduced.

## Commit Message

```text
feat(cases): persist generated case knowledge evidence
```

## Next Task

Slice 31 Task 4: Add Generated-Case Knowledge Evidence Golden Smoke.
