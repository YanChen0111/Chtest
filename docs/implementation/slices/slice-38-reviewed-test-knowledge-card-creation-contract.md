# Slice 38: Reviewed TestKnowledgeCard Creation Contract Task Plan

## Goal

Define the reviewed creation contract for turning an approved
TestKnowledgeCard candidate into a future TestKnowledgeCard record before any
broad TestKnowledgeCard CRUD, backend feature API, frontend page, migration,
or prompt-eligibility automation exists.

This slice is contract-first. It documents the creation input, card field
mapping, source evidence, duplicate/merge preconditions, creation artifact,
failure behavior, and prompt eligibility boundary needed for a later scoped
implementation.

## Product Value Answer

After this slice, Chtest can describe exactly how a human-approved candidate
may become a reviewed TestKnowledgeCard record without opening generic CRUD or
letting model output create reusable knowledge automatically. Users get an
auditable creation boundary that preserves source evidence and keeps
`allowed_for_prompt=false` until a later explicit prompt-eligibility workflow
grants reuse.

## Current Evidence Baseline

- Slice 30 defined `TestKnowledgeCard` and `KnowledgeEvidence` contract
  shapes.
- Slice 36 defined TestKnowledgeCard handoff candidates with source evidence,
  duplicate/merge hints, `safe_to_show`, `review_required=true`, and
  `allowed_for_prompt=false`.
- Slice 37 defined candidate review actions, candidate review artifact
  evidence, ReviewHistory linkage, duplicate/merge routing, and prompt
  eligibility deferral.
- `ReviewHistory` already records local append-only review attribution events.
- Existing Artifact contracts preserve source evidence and review evidence
  without creating broad artifact mutation or provider behavior.

## Non-goals

- No broad TestKnowledgeCard CRUD implementation, list/update/delete API,
  frontend page, migration, table change, automatic card creation from model
  output, automatic card approval, automatic prompt eligibility, automatic
  knowledge ingestion, or KnowledgeIngestionAgent runtime.
- No provider calls, provider SDK, credentials, OAuth, remote URL fetch, MCP
  runtime, vector database, embeddings, reranking, background indexing, graph
  runtime, GraphRAG job, queue, scheduler, or background worker.
- No artifact upload, artifact mutation, artifact delete, historical evidence
  mutation, ReviewHistory mutation, FailureAnalysis mutation, Report mutation,
  TestRun/TestResult mutation, TestCase mutation, GeneratedCaseCandidate
  mutation, or KnowledgeEvidence mutation.
- No automatic duplicate merge, card replacement, card archive/delete,
  generated-case auto-approval, TestCase auto-promotion, runner behavior
  change, report generation behavior change, remote CI provider behavior, RBAC,
  tenants, permissions, or package upgrades.

## Contract Boundary To Define

The follow-up contract task should define:

- Reviewed creation input:
  - approved candidate review action;
  - candidate review artifact id;
  - TestKnowledgeCard handoff artifact id;
  - source KnowledgeFeedbackDraft id;
  - ReviewHistory ids for feedback review and candidate review;
  - candidate_card_json;
  - same-project source artifact ids;
  - source quote/hash and source span;
  - duplicate/merge decision evidence;
  - unsupported claims and failure code when present.
- Creation action:
  - create_reviewed_test_knowledge_card as a future scoped action, not broad
    CRUD.
- Created card field mapping:
  - project_id and optional module_id;
  - title, knowledge_type, summary, body;
  - source_type, source_artifact_id/source_artifact_ids, source_section,
    source_quote_or_hash, source_document_version;
  - related requirement, risk, and reviewed test case ids;
  - tags, test_type, risk_level, module_key, api_endpoint, applicability;
  - confidence, safe_to_show, redaction_applied, redaction report artifact id;
  - evidence_artifact_ids, last_verified_at, status;
  - `allowed_for_prompt=false` by default.
- Creation outputs:
  - created TestKnowledgeCard id only in a later scoped implementation;
  - creation ReviewHistory reference;
  - creation artifact;
  - source manifest;
  - duplicate/merge precondition result;
  - prompt eligibility decision defaulted to deferred.
- Prompt eligibility boundary:
  - creation approval is not prompt eligibility;
  - created cards default to `allowed_for_prompt=false`;
  - prompt eligibility requires a later explicit workflow with reviewed source
    citations and safe-to-show evidence.
- Duplicate/merge boundary:
  - creation is blocked when duplicate/merge review is unresolved;
  - merge/archive/delete/replace/relabel remain out of scope unless a later
    workflow explicitly owns them.
- Failure and fallback behavior:
  - stale, rejected, revision-requested, duplicate-conflicted, cross-project,
    unsafe, missing, unbounded, or unsupported source evidence rejects creation;
  - unsupported claims remain visible and must not become card facts;
  - failed creation remains auditable and must not create fallback cards.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add reviewed TestKnowledgeCard creation task plan | done | `test -f docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md && rg -n "Reviewed TestKnowledgeCard Creation|approved candidate|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md NEXT_AI_TASK.md && git diff --check` | `972c572` | planning-only scope |
| Define reviewed TestKnowledgeCard creation contracts | done | `rg -n "Reviewed TestKnowledgeCard Creation|create_reviewed_test_knowledge_card|approved candidate|candidate review artifact|source manifest|allowed_for_prompt=false|duplicate|merge|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md && git diff --check` | pending | contract-only |
| Add reviewed TestKnowledgeCard creation golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_reviewed_test_knowledge_card_creation_contract_golden.py -q && git diff --check` | pending | no CRUD/runtime |
| Slice 38 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_reviewed_test_knowledge_card_creation_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_candidate_review_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add Reviewed TestKnowledgeCard Creation Contract Task Plan

Goal: Create a narrow plan for the reviewed creation boundary before contract
edits or runtime implementation.

Expected files:

- `docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md
rg -n "Reviewed TestKnowledgeCard Creation|approved candidate|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 38 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names approved candidate review, creation input, TestKnowledgeCard
  field mapping, source evidence, duplicate/merge preconditions,
  allowed_for_prompt, failure behavior, human review, and non-goals.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add reviewed test knowledge card creation plan
```

## Task 2: Define Reviewed TestKnowledgeCard Creation Contracts

Goal: Update data, API, state-machine, and artifact contracts with the reviewed
creation boundary for approved TestKnowledgeCard candidates.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Reviewed TestKnowledgeCard Creation|create_reviewed_test_knowledge_card|approved candidate|candidate review artifact|source manifest|allowed_for_prompt=false|duplicate|merge|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md
git diff --check
```

Acceptance:

- Contracts define reviewed creation input, created card field mapping,
  source evidence, source manifest, creation outputs, duplicate/merge
  preconditions, prompt eligibility separation, and failure behavior.
- Contracts keep broad CRUD, update/delete/list APIs, prompt eligibility,
  automatic card creation, and duplicate merge/archive/delete behind later
  explicitly scoped workflows.
- Contracts require `allowed_for_prompt=false` by default and preserve
  unsupported claims.
- Contracts forbid frontend/API/runtime implementation, migrations, provider
  calls, MCP runtime, vector/graph runtime, artifact mutation, historical
  evidence mutation, RBAC, tenants, and permissions.

Commit message:

```text
docs(v2): define reviewed test knowledge card creation contracts
```

## Task 3: Add Reviewed TestKnowledgeCard Creation Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving reviewed creation
cannot bypass source evidence, duplicate/merge, or prompt eligibility gates.

Expected files:

- `backend/app/tests/golden/test_reviewed_test_knowledge_card_creation_contract_golden.py`
- `docs/fixtures/26-reviewed-test-knowledge-card-creation-golden.md`
- `docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_reviewed_test_knowledge_card_creation_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names reviewed TestKnowledgeCard creation, approved candidate review,
  creation action, card field mapping, source evidence, source manifest,
  duplicate/merge preconditions, `allowed_for_prompt=false`, unsupported
  claims, ReviewHistory, and creation artifact evidence.
- Golden proves no broad TestKnowledgeCard CRUD, automatic card creation from
  model output, automatic prompt eligibility, automatic merge/archive/delete,
  historical evidence mutation, provider call, vector index, graph job, MCP
  runtime, artifact mutation, review bypass, auto-promotion, RBAC, tenants, or
  permissions is created by the contract.

Commit message:

```text
test(golden): add reviewed test knowledge card creation smoke
```

## Slice 38 Completion Gate

Goal: Validate Slice 38 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_reviewed_test_knowledge_card_creation_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_candidate_review_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 38 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete reviewed test knowledge card creation slice
```
