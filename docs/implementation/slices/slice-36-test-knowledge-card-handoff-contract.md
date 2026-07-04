# Slice 36: TestKnowledgeCard Handoff Contract Task Plan

## Goal

Define the contract boundary for turning an approved KnowledgeFeedbackDraft
handoff payload into a future TestKnowledgeCard candidate before any
TestKnowledgeCard CRUD, backend feature API, frontend page, migration, or
prompt-eligibility automation exists.

This slice is contract-first. It documents the payload shape, source evidence,
duplicate/merge hints, and human review gates needed for a later card-creation
workflow without creating or mutating card rows in this slice.

## Product Value Answer

After this slice, Chtest can safely carry human-reviewed feedback toward
structured testing knowledge without letting draft AI output silently become a
prompt-eligible TestKnowledgeCard. Users get an auditable bridge from approved
KnowledgeFeedbackDraft entries to reviewed card candidates, with source
evidence, safe-to-show checks, duplicate/merge guidance, and
`allowed_for_prompt=false` by default.

## Current Evidence Baseline

- Slice 30 defined `TestKnowledgeCard` and `KnowledgeEvidence` as local
  testing-knowledge contracts.
- Slice 34 defined `KnowledgeFeedbackDraft` as draft-only agent output that
  must not create or approve TestKnowledgeCard rows.
- Slice 35 defined the human review gate for KnowledgeFeedbackDraft and an
  optional future `handoff_payload_json` boundary.
- `ReviewHistory` already records local append-only review attribution events.
- `TestKnowledgeCard.safe_to_show` and `TestKnowledgeCard.allowed_for_prompt`
  are server-side decisions and must not be granted by model confidence.

## Non-goals

- No TestKnowledgeCard CRUD implementation, backend feature API, frontend page,
  migration, card table change, automatic card creation, automatic card
  approval, automatic prompt eligibility, or automatic knowledge ingestion.
- No KnowledgeFeedbackAgent runtime, orchestration, queue, background job,
  scheduler, provider calls, provider SDK, credentials, OAuth, remote URL
  fetch, MCP runtime, vector database, embeddings, reranking, background
  indexing, graph runtime, or GraphRAG job.
- No artifact upload, artifact mutation, artifact delete, historical evidence
  mutation, ReviewHistory mutation, FailureAnalysis mutation, Report mutation,
  TestRun/TestResult mutation, TestCase mutation, or GeneratedCaseCandidate
  mutation.
- No generated-case auto-approval, runner behavior change, report generation
  behavior change, remote CI provider behavior, RBAC, tenants, permissions, or
  package upgrades.

## Contract Boundary To Define

The follow-up contract task should define:

- Handoff input:
  - approved KnowledgeFeedbackDraft id;
  - review action and review decision;
  - ReviewHistory id;
  - feedback review artifact id;
  - source artifact ids;
  - source entity type and id;
  - source quote or source hash;
  - source section/span when available;
  - unsupported claims that must remain visible.
- Candidate output fields:
  - `knowledge_type` mapped from `draft_knowledge_type`;
  - title, summary, and body text;
  - source type, source entity reference, and source artifact ids;
  - source quote/hash and optional section/span;
  - related requirement, risk, testcase, generated-case, run, report, or
    failure ids;
  - tags, confidence, safe_to_show, and `allowed_for_prompt=false`;
  - duplicate/merge hints and suggested canonical card id when available;
  - evidence artifact ids and validation artifact id.
- Review boundary:
  - a successful handoff creates only a candidate payload until a later scoped
    workflow explicitly creates TestKnowledgeCard rows;
  - human review is required before TestKnowledgeCard row creation;
  - human review is required again before `allowed_for_prompt=true`;
  - model confidence must not approve a card or grant prompt eligibility.
- Failure and fallback behavior:
  - invalid, unsafe, missing, or cross-project source evidence rejects the
    handoff or requests revision;
  - unsupported claims remain visible and cannot become card body facts;
  - duplicate/merge uncertainty is preserved instead of fabricating a canonical
    card;
  - rejected handoffs remain auditable and cannot be reused as positive
    knowledge.
- Artifact and trace rules:
  - handoff artifact records source ids, ReviewHistory id, review artifact id,
    reviewer action, prompt/skill versions when available, schema validation,
    duplicate/merge outcome, prompt eligibility default, and failure code.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestKnowledgeCard handoff task plan | done | `test -f docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md && rg -n "TestKnowledgeCard Handoff|KnowledgeFeedbackDraft|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md NEXT_AI_TASK.md && git diff --check` | `6ce8970` | planning-only scope |
| Define TestKnowledgeCard handoff contracts | done | `rg -n "TestKnowledgeCard handoff|KnowledgeFeedbackDraft|handoff_payload|allowed_for_prompt=false|duplicate|merge|safe_to_show|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md && git diff --check` | `de2b2be` | contract-only |
| Add TestKnowledgeCard handoff golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_handoff_contract_golden.py -q && git diff --check` | pending | no CRUD/runtime |
| Slice 36 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_handoff_contract_golden.py backend/app/tests/golden/test_knowledge_feedback_review_gate_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add TestKnowledgeCard Handoff Contract Task Plan

Goal: Create a narrow plan for the TestKnowledgeCard handoff boundary before
contract edits or runtime implementation.

Expected files:

- `docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md
rg -n "TestKnowledgeCard Handoff|KnowledgeFeedbackDraft|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 36 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names KnowledgeFeedbackDraft handoff payloads, TestKnowledgeCard
  candidate fields, source evidence, duplicate/merge hints, safe_to_show,
  allowed_for_prompt, human review, and non-goals.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add test knowledge card handoff plan
```

## Task 2: Define TestKnowledgeCard Handoff Contracts

Goal: Update data, API, state-machine, and artifact contracts with the
approved-feedback handoff boundary for future TestKnowledgeCard candidates.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard handoff|KnowledgeFeedbackDraft|handoff_payload|allowed_for_prompt=false|duplicate|merge|safe_to_show|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md
git diff --check
```

Acceptance:

- Contracts define handoff input, candidate payload fields, duplicate/merge
  hints, source evidence requirements, artifact trace, and failure behavior.
- Contracts keep card creation, card approval, and prompt eligibility behind
  explicit later human-reviewed workflows.
- Contracts require `allowed_for_prompt=false` by default and preserve
  unsupported claims.
- Contracts forbid automatic card creation, automatic prompt eligibility,
  historical evidence mutation, provider calls, MCP runtime, vector/graph
  runtime, CRUD/API/frontend implementation, RBAC, tenants, and permissions.

Commit message:

```text
docs(v2): define test knowledge card handoff contracts
```

## Task 3: Add TestKnowledgeCard Handoff Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving approved feedback
handoff remains a candidate payload and cannot bypass card review or prompt
eligibility rules.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_handoff_contract_golden.py`
- `docs/fixtures/24-test-knowledge-card-handoff-golden.md`
- `docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_handoff_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names approved KnowledgeFeedbackDraft handoff, ReviewHistory,
  feedback review artifact, TestKnowledgeCard candidate fields, source
  evidence, safe_to_show, `allowed_for_prompt=false`, duplicate/merge hints,
  unsupported claims, and human review.
- Golden proves no TestKnowledgeCard CRUD, automatic row creation, automatic
  prompt eligibility, historical evidence mutation, provider call, vector
  index, graph job, MCP runtime, artifact mutation, review bypass,
  auto-promotion, RBAC, tenants, or permissions is created by the contract.

Commit message:

```text
test(golden): add test knowledge card handoff smoke
```

## Slice 36 Completion Gate

Goal: Validate Slice 36 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_handoff_contract_golden.py backend/app/tests/golden/test_knowledge_feedback_review_gate_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 36 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete test knowledge card handoff slice
```
