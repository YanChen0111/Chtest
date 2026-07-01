# Slice 31: Generated Case Knowledge Evidence Persistence Task Plan

## Goal

Persist and return generated-case knowledge evidence fields through the existing
case generation flow.

Slice 30 defined TestKnowledgeCard, KnowledgeEvidence, generated-case evidence
fields, fixture examples, and a schema-level golden smoke. Slice 31 is the
smallest implementation bridge: when CaseGenerationAgent output includes
normalized knowledge evidence fields, Chtest stores them on
GeneratedCaseCandidate and returns them from the candidate list API.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
- `docs/fixtures/18-test-knowledge-card-contract-golden.md`

## Product Value Answer

After this slice, generated case candidates can carry and expose normalized
knowledge evidence, risk coverage, generation reason, automation readiness,
quality score, review findings, and coverage gap notes in the real
CaseGeneration data flow, without adding a RAG runtime or bypassing review.

## Preconditions

- GeneratedCaseCandidate contract fields are defined in
  `docs/contracts/01-data-model-contract.md`.
- Candidate list API response fields are defined in
  `docs/contracts/02-api-contract.md`.
- State-machine rules keep knowledge evidence as review evidence only.
- Artifact rules define `knowledge_evidence` and `case_review_findings`.
- Current backend already persists GeneratedCaseCandidate rows and lists them
  through `/api/case-generation/tasks/{id}/candidates`.

## Non-goals

- No TestKnowledgeCard table implementation, knowledge-card CRUD API, knowledge
  ingestion agent, extraction pipeline, knowledge editor, graph view, frontend
  implementation, or dashboard.
- No RAG runtime, external KnowledgeAdapter provider call, vector database,
  embedding service, reranking, semantic search, background indexing, graph
  runtime, GraphRAG job, provider SDK, remote URL fetch, OAuth, or API key
  storage.
- No MCP runtime, MCP server/client transport, marketplace, plugin install,
  remote MCP call, or ToolDefinition behavior change.
- No generated-case auto-approval, automatic TestCase promotion, review bypass,
  automation execution, runner behavior change, report generation change,
  artifact upload/mutation/delete, cloud storage, RBAC, tenants, permissions,
  team workflow, remote CI provider behavior, PR comments, deploy, release,
  merge, push, or scheduling.

## Slice Boundary

- Add GeneratedCaseCandidate persistence for:
  - `source_knowledge_evidence_ids`;
  - `knowledge_evidence_refs_json`;
  - `covered_risk_ids`;
  - `generation_reason`;
  - `automation_readiness`;
  - `quality_score`;
  - `review_findings_json`;
  - `coverage_gap_notes`.
- Accept these fields only when they are already present in AI task output or
  test fixtures as normalized evidence data.
- Return these fields from the candidate list API.
- Keep absent fields backward-compatible with defaults.
- Add focused database/API/golden coverage proving fields persist and remain
  review evidence only.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Generated Case Knowledge Evidence Persistence task plan | done | `test -f docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md && rg -n "Generated Case Knowledge Evidence Persistence|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md NEXT_AI_TASK.md && git diff --check` | pending | planning-only scope |
| Confirm persistence contract boundary | done | `rg -n "source_knowledge_evidence_ids|knowledge_evidence_refs_json|review_findings_json|coverage_gap_notes|RAG runtime|MCP runtime" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md && git diff --check` | pending | contract clarification only |
| Persist generated-case knowledge evidence fields | done | `backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py backend/app/tests/api/test_case_generation.py -q && git diff --check` | pending | model/migration/API path |
| Add generated-case knowledge evidence golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_generated_case_knowledge_evidence_persistence_golden.py -q && git diff --check` | pending | end-to-end proof |
| Slice 31 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py backend/app/tests/api/test_case_generation.py backend/app/tests/golden/test_generated_case_knowledge_evidence_persistence_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add Generated Case Knowledge Evidence Persistence Task Plan

Goal: Define the smallest post-Slice-30 implementation bridge before changing
models, migrations, API responses, or tests.

Expected files:

- `docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md
rg -n "Generated Case Knowledge Evidence Persistence|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Creates the Slice 31 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to GeneratedCaseCandidate evidence-field persistence and
  API display.
- Does not add frontend code, TestKnowledgeCard CRUD, RAG runtime, external
  provider calls, vector infrastructure, graph runtime, MCP runtime, review
  bypass, runner behavior, or reports.

Commit message:

```text
docs(v2): add generated case knowledge evidence persistence plan
```

## Task 2: Confirm Persistence Contract Boundary

Goal: Ensure contracts explicitly describe persistence/display behavior before
backend implementation starts.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "source_knowledge_evidence_ids|knowledge_evidence_refs_json|review_findings_json|coverage_gap_notes|RAG runtime|MCP runtime" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md
git diff --check
```

Acceptance:

- Contracts state the fields are persisted on GeneratedCaseCandidate when
  present in normalized AI output.
- Contracts state list API returns the fields with safe defaults.
- Contracts state absent evidence remains backward-compatible.
- Contracts preserve no RAG runtime, MCP runtime, vector, embedding, reranking,
  external provider, graph runtime, auto-approval, runner, report, RBAC, tenant,
  permission, and remote CI provider boundaries.

Commit message:

```text
docs(v2): clarify generated case knowledge evidence persistence
```

## Task 3: Persist Generated-Case Knowledge Evidence Fields

Goal: Store and list the Slice 30 generated-case evidence fields in the current
backend data flow.

Expected files:

- `backend/app/modules/cases/models.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `backend/alembic/versions/<new-migration>.py`
- `backend/app/tests/db/test_case_generation_models.py`
- `backend/app/tests/api/test_case_generation.py`
- `docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py backend/app/tests/api/test_case_generation.py -q
git diff --check
```

Acceptance:

- GeneratedCaseCandidate model persists all Slice 31 evidence fields with safe
  defaults.
- Migration adds only generated_case_candidates columns required by this slice.
- Case generation persistence copies normalized fields from AI output when
  present and uses safe defaults when absent.
- Candidate list API returns the fields.
- Existing case generation behavior remains backward-compatible.
- No TestCase, TestRun, Report, retrieval job, vector index, graph job,
  provider call, artifact mutation, or review bypass is introduced.

Commit message:

```text
feat(cases): persist generated case knowledge evidence
```

## Task 4: Add Generated-Case Knowledge Evidence Golden Smoke

Goal: Prove the real case-generation API can expose persisted knowledge
evidence fields without side effects.

Expected files:

- `backend/app/tests/golden/test_generated_case_knowledge_evidence_persistence_golden.py`
- `docs/fixtures/18-test-knowledge-card-contract-golden.md`
- `docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_generated_case_knowledge_evidence_persistence_golden.py -q
git diff --check
```

Acceptance:

- Golden seeds or runs case generation with accepted and rejected knowledge
  evidence examples.
- Candidate list response includes evidence ids, knowledge evidence refs,
  covered risk ids, generation reason, automation readiness, quality score,
  review findings, and coverage gap notes.
- Golden proves evidence display creates no TestCase, TestRun, Report,
  retrieval job, vector index, graph job, provider call, or artifact mutation.

Commit message:

```text
test(golden): add generated case knowledge evidence persistence smoke
```

## Slice 31 Completion Gate

Goal: Validate Slice 31 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py backend/app/tests/api/test_case_generation.py backend/app/tests/golden/test_generated_case_knowledge_evidence_persistence_golden.py -q
git diff --check
```

Acceptance:

- Slice 31 task table records completed task commits.
- Focused database/API/golden verification passes.
- `NEXT_AI_TASK.md` points to the next narrow V2 task.

Commit message:

```text
docs(v2): complete generated case knowledge evidence persistence slice
```
