# Slice 40: TestKnowledgeCard Retrieval Boundary Contract Task Plan

## Goal

Define the read-only retrieval boundary for TestKnowledgeCard prompt context
before any prompt runtime retrieval implementation, deterministic retrieval
behavior change, vector index, frontend page, backend feature API, broad
TestKnowledgeCard CRUD, or automatic prompt eligibility exists.

This slice is contract-first. It documents how a future workflow may consider
prompt-eligible TestKnowledgeCard records for prompt context while preserving
`allowed_for_prompt`, `prompt_eligible`, `safe_to_show`, source evidence,
source manifest, ReviewHistory, prompt eligibility artifact evidence, exclusion
reason, and retrieval evidence boundaries.

## Product Value Answer

After this slice, Chtest can describe exactly which reviewed
TestKnowledgeCard records may be considered for future prompt context without
accidentally making retrieval runtime behavior part of prompt eligibility.
Users get a second explicit safety boundary: prompt eligibility is necessary
for reuse, but stale, unsafe, cross-project, revoked, unsupported, missing, or
unbounded evidence can still exclude a card from prompt context.

## Current Evidence Baseline

- Slice 19 defined deterministic local ContextArtifact retrieval evidence and
  kept vector databases, embeddings, reranking, graph runtime, MCP runtime, and
  external providers out of scope.
- Slice 30 defined `TestKnowledgeCard` and `KnowledgeEvidence` contract shapes,
  including `safe_to_show` and `allowed_for_prompt`.
- Slice 36 defined TestKnowledgeCard handoff candidates and kept
  `allowed_for_prompt=false`.
- Slice 37 defined candidate review and deferred prompt eligibility.
- Slice 38 defined reviewed creation and kept created cards
  `allowed_for_prompt=false` by default.
- Slice 39 defined human-reviewed prompt eligibility and allowed
  `allowed_for_prompt=true` only through `mark_card_prompt_eligible`.
- Artifact contracts preserve source manifest, source artifact ids, redaction
  evidence, ReviewHistory, and prompt eligibility evidence without changing
  prompt runtime retrieval behavior.

## Non-goals

- No prompt runtime retrieval implementation, deterministic retrieval behavior
  change, vector database, embeddings, reranking, background indexing, graph
  runtime, GraphRAG job, MCP runtime, provider calls, provider SDK,
  credentials, OAuth, remote URL fetch, queue, scheduler, or background worker.
- No broad TestKnowledgeCard CRUD implementation, backend feature API,
  frontend page, migration, card table change, automatic prompt eligibility,
  automatic card creation from model output, automatic card approval, automatic
  knowledge ingestion, or KnowledgeIngestionAgent runtime.
- No artifact upload, artifact mutation, artifact delete, source artifact
  mutation, prompt eligibility artifact mutation, historical evidence
  mutation, ReviewHistory mutation, FailureAnalysis mutation, Report mutation,
  TestRun/TestResult mutation, TestCase mutation, GeneratedCaseCandidate
  mutation, KnowledgeEvidence mutation, or existing TestKnowledgeCard content
  mutation.
- No automatic duplicate merge, card replacement, card archive/delete,
  generated-case auto-approval, TestCase auto-promotion, runner behavior
  change, report generation behavior change, remote CI provider behavior, RBAC,
  tenants, permissions, or package upgrades.

## Contract Boundary To Define

The follow-up contract task should define:

- Selection input:
  - reviewed TestKnowledgeCard id;
  - `allowed_for_prompt=true`;
  - `prompt_eligible` state evidence;
  - prompt eligibility artifact id;
  - creation artifact id;
  - source manifest and same-project source artifact ids;
  - source quote/hash and source span;
  - ReviewHistory ids for creation and prompt eligibility;
  - redaction report artifact id;
  - `safe_to_show=true`;
  - unsupported claims and failure code when present.
- Eligibility filters:
  - card belongs to the same project as the prompt request;
  - card is active or otherwise selectable by future scoped policy;
  - prompt eligibility is not denied, revision-requested, or revoked;
  - source evidence remains bounded, same-project, safe, and reviewed;
  - source manifest, source quote/hash, redaction, and ReviewHistory evidence
    remain present.
- Exclusion behavior:
  - `allowed_for_prompt=false` always excludes a card;
  - denied, revoked, revision-requested, stale, cross-project, unsafe,
    unsupported, missing, unbounded, redaction-failed, or evidence-mismatched
    cards are excluded;
  - every exclusion records an `excluded_card_reason` or failure code in
    future retrieval evidence without mutating the card.
- Retrieval evidence outputs:
  - selected TestKnowledgeCard ids and excluded TestKnowledgeCard ids;
  - source evidence ids and prompt eligibility artifact ids;
  - source manifest artifact id and source quote/hash;
  - ReviewHistory ids;
  - safe_to_show/redaction status;
  - selection reason and exclusion reason;
  - bounded snippet or source hash only, not raw large source text.
- Runtime boundary:
  - this slice defines contract semantics only;
  - no retrieval endpoint, ranking, prompt assembly, vector index, embedding,
    reranking, graph traversal, provider call, MCP runtime call, background
    indexing, or UI behavior is added.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestKnowledgeCard retrieval boundary task plan | done | `test -f docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md && rg -n "TestKnowledgeCard Retrieval Boundary|allowed_for_prompt|prompt_eligible|retrieval evidence|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md NEXT_AI_TASK.md && git diff --check` | `2db2bff` | planning-only scope |
| Define TestKnowledgeCard retrieval boundary contracts | done | `rg -n "TestKnowledgeCard Retrieval Boundary|select_prompt_eligible_cards|excluded_card_reason|allowed_for_prompt|prompt_eligible|safe_to_show|source manifest|retrieval evidence|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md && git diff --check` | `d334d8c` | contract-only |
| Add TestKnowledgeCard retrieval boundary golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_retrieval_boundary_contract_golden.py -q && git diff --check` | pending | no runtime retrieval |
| Slice 40 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_retrieval_boundary_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_eligibility_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add TestKnowledgeCard Retrieval Boundary Task Plan

Goal: Create a narrow plan for the retrieval boundary before contract edits or
runtime implementation.

Expected files:

- `docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md
rg -n "TestKnowledgeCard Retrieval Boundary|allowed_for_prompt|prompt_eligible|retrieval evidence|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 40 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names read-only selection inputs, prompt eligibility filters,
  `safe_to_show`, source evidence, source manifest, ReviewHistory, retrieval
  evidence outputs, exclusion behavior, failure behavior, and non-goals.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add test knowledge card retrieval boundary plan
```

## Task 2: Define TestKnowledgeCard Retrieval Boundary Contracts

Goal: Update data, API, state-machine, and artifact contracts with the
read-only TestKnowledgeCard retrieval boundary for future prompt context.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard Retrieval Boundary|select_prompt_eligible_cards|excluded_card_reason|allowed_for_prompt|prompt_eligible|safe_to_show|source manifest|retrieval evidence|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md
git diff --check
```

Acceptance:

- Contracts define selection inputs, eligibility filters, source evidence,
  safe_to_show/redaction requirements, retrieval evidence outputs, exclusion
  reasons, and failure behavior.
- Contracts keep prompt runtime retrieval, deterministic ranking changes,
  vector indexes, embeddings, reranking, graph jobs, provider calls, MCP
  runtime, broad CRUD, automatic eligibility, and historical evidence mutation
  out of scope.
- Contracts make `allowed_for_prompt=true` necessary but not sufficient for
  future prompt-context selection.

Commit message:

```text
docs(v2): define test knowledge card retrieval boundary contracts
```

## Task 3: Add TestKnowledgeCard Retrieval Boundary Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving retrieval boundary
selection cannot bypass prompt eligibility, safe-to-show, source evidence,
redaction, ReviewHistory, or exclusion gates.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_retrieval_boundary_contract_golden.py`
- `docs/fixtures/28-test-knowledge-card-retrieval-boundary-golden.md`
- `docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_retrieval_boundary_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names selection inputs, `allowed_for_prompt`, `prompt_eligible`,
  `safe_to_show`, source manifest, ReviewHistory, prompt eligibility artifact
  evidence, retrieval evidence outputs, exclusion reasons, failure behavior,
  and forbidden side effects.
- Golden proves no prompt runtime retrieval implementation, deterministic
  ranking change, vector index, embedding, reranking, graph job, provider call,
  MCP runtime, broad CRUD, automatic eligibility, historical evidence mutation,
  RBAC, tenants, or permissions is created by the contract.

Commit message:

```text
test(golden): add test knowledge card retrieval boundary smoke
```

## Slice 40 Completion Gate

Goal: Validate Slice 40 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_retrieval_boundary_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_eligibility_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 40 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.

Commit message:

```text
docs(v2): complete test knowledge card retrieval boundary slice
```
