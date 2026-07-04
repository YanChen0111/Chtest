# Slice 37: TestKnowledgeCard Candidate Review Contract Task Plan

## Goal

Define the human review contract for TestKnowledgeCard handoff candidates
before any TestKnowledgeCard CRUD, backend feature API, frontend page,
migration, automatic card creation, or prompt-eligibility automation exists.

This slice is contract-first. It documents how a reviewer can accept, reject,
request revision, or route duplicate/merge decisions for a handoff candidate
without creating, mutating, merging, archiving, or making prompt-eligible
TestKnowledgeCard rows in this slice.

## Product Value Answer

After this slice, Chtest can safely review TestKnowledgeCard handoff candidates
before they become reusable testing knowledge. Users get an auditable human
gate for candidate quality, source evidence, duplicate/merge handling, and
prompt eligibility separation, while `allowed_for_prompt=false` remains the
default until a later explicit card workflow grants eligibility.

## Current Evidence Baseline

- Slice 30 defined `TestKnowledgeCard` and `KnowledgeEvidence` contract
  shapes.
- Slice 35 defined the KnowledgeFeedbackDraft review gate and ReviewHistory
  linkage for feedback decisions.
- Slice 36 defined TestKnowledgeCard handoff candidates, source evidence,
  duplicate/merge hints, `safe_to_show`, `allowed_for_prompt=false`,
  `review_required=true`, and `test_knowledge_card_handoff.json`.
- `ReviewHistory` already records local append-only review attribution events.
- Existing Artifact contracts preserve source evidence, unsupported claims,
  and review evidence without granting CRUD or prompt eligibility.

## Non-goals

- No TestKnowledgeCard CRUD implementation, backend feature API, frontend page,
  migration, card table change, automatic card creation, automatic card
  approval, automatic prompt eligibility, automatic knowledge ingestion, or
  KnowledgeIngestionAgent runtime.
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

- Candidate review input:
  - TestKnowledgeCard handoff candidate id or artifact id;
  - source KnowledgeFeedbackDraft id;
  - previous feedback ReviewHistory id and review artifact id;
  - `test_knowledge_card_handoff.json`;
  - `candidate_card_json`;
  - same-project source artifact ids;
  - source quote/hash and source span;
  - duplicate_knowledge_card_ids and merge_hint;
  - unsupported claims and failure code when present.
- Review actions:
  - approve_candidate_for_creation;
  - reject_candidate;
  - request_candidate_revision;
  - flag_duplicate;
  - request_merge_review;
  - defer_prompt_eligibility.
- Candidate review outputs:
  - candidate review decision;
  - reviewer label and comment;
  - ReviewHistory append-only event or reference;
  - candidate review artifact;
  - reviewed source evidence ids;
  - duplicate/merge routing;
  - prompt eligibility decision defaulted to deferred;
  - failure code for invalid or unsafe handoff candidates.
- Prompt eligibility boundary:
  - candidate approval is not prompt eligibility;
  - `allowed_for_prompt=false` remains mandatory for candidates;
  - prompt eligibility requires a later explicit card workflow after a reviewed
    TestKnowledgeCard row exists.
- Duplicate/merge boundary:
  - duplicate hints help reviewers route a candidate;
  - merge review must not automatically merge, archive, replace, delete, or
    relabel existing TestKnowledgeCard rows.
- Failure and fallback behavior:
  - unsafe, missing, cross-project, unbounded, or unsupported source evidence
    rejects the candidate or requests revision;
  - unsupported claims remain visible and must not become card facts;
  - rejected candidates remain auditable and cannot be reused as positive
    knowledge.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestKnowledgeCard candidate review task plan | done | `test -f docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md && rg -n "TestKnowledgeCard Candidate Review|TestKnowledgeCard handoff|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md NEXT_AI_TASK.md && git diff --check` | `052756a` | planning-only scope |
| Define TestKnowledgeCard candidate review contracts | done | `rg -n "TestKnowledgeCard Candidate Review|approve_candidate_for_creation|reject_candidate|request_candidate_revision|flag_duplicate|request_merge_review|defer_prompt_eligibility|ReviewHistory|candidate review artifact" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md && git diff --check` | `1341d1f` | contract-only |
| Add TestKnowledgeCard candidate review golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_candidate_review_contract_golden.py -q && git diff --check` | pending | no CRUD/runtime |
| Slice 37 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_candidate_review_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_handoff_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add TestKnowledgeCard Candidate Review Contract Task Plan

Goal: Create a narrow plan for the candidate review boundary before contract
edits or runtime implementation.

Expected files:

- `docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md
rg -n "TestKnowledgeCard Candidate Review|TestKnowledgeCard handoff|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 37 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names TestKnowledgeCard handoff candidates, review actions,
  ReviewHistory, artifact evidence, duplicate/merge handling, prompt
  eligibility, human review, and non-goals.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add test knowledge card candidate review plan
```

## Task 2: Define TestKnowledgeCard Candidate Review Contracts

Goal: Update data, API, state-machine, and artifact contracts with the human
review boundary for TestKnowledgeCard handoff candidates.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard Candidate Review|approve_candidate_for_creation|reject_candidate|request_candidate_revision|flag_duplicate|request_merge_review|defer_prompt_eligibility|ReviewHistory|candidate review artifact" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md
git diff --check
```

Acceptance:

- Contracts define candidate review input, actions, output evidence,
  duplicate/merge routing, prompt eligibility separation, and failure behavior.
- Contracts keep TestKnowledgeCard creation, merge/archive/delete, and prompt
  eligibility behind explicit later human-reviewed workflows.
- Contracts require `allowed_for_prompt=false` for candidates and preserve
  unsupported claims.
- Contracts forbid CRUD/API/frontend implementation, automatic card creation,
  automatic prompt eligibility, historical evidence mutation, provider calls,
  MCP runtime, vector/graph runtime, artifact mutation, RBAC, tenants, and
  permissions.

Commit message:

```text
docs(v2): define test knowledge card candidate review contracts
```

## Task 3: Add TestKnowledgeCard Candidate Review Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving candidate review
cannot bypass card creation, duplicate/merge, or prompt eligibility gates.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_candidate_review_contract_golden.py`
- `docs/fixtures/25-test-knowledge-card-candidate-review-golden.md`
- `docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_candidate_review_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names TestKnowledgeCard candidate review actions, ReviewHistory,
  candidate review artifact, handoff source evidence, duplicate/merge routing,
  prompt eligibility separation, unsupported claims, and human review.
- Golden proves no TestKnowledgeCard CRUD, automatic row creation, automatic
  prompt eligibility, automatic merge/archive/delete, historical evidence
  mutation, provider call, vector index, graph job, MCP runtime, artifact
  mutation, review bypass, auto-promotion, RBAC, tenants, or permissions is
  created by the contract.

Commit message:

```text
test(golden): add test knowledge card candidate review smoke
```

## Slice 37 Completion Gate

Goal: Validate Slice 37 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_candidate_review_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_handoff_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 37 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete test knowledge card candidate review slice
```
