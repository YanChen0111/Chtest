# Slice 39: TestKnowledgeCard Prompt Eligibility Contract Task Plan

## Goal

Define the human-reviewed prompt eligibility contract for TestKnowledgeCard
records before any prompt runtime retrieval change, vector index, frontend page,
backend feature API, broad TestKnowledgeCard CRUD, or automatic prompt
eligibility exists.

This slice is contract-first. It documents how a reviewer may mark, deny,
request revision for, or revoke prompt eligibility while preserving
safe_to_show, redaction, source evidence, ReviewHistory, prompt eligibility
reason, and artifact evidence boundaries.

## Product Value Answer

After this slice, Chtest can safely decide which reviewed TestKnowledgeCard
records are allowed to enter prompt context without letting card creation,
model confidence, schema validity, or source presence automatically make
knowledge reusable. Users get an auditable human gate for `allowed_for_prompt`
that is separate from card creation and retrieval runtime behavior.

## Current Evidence Baseline

- Slice 30 defined `TestKnowledgeCard.allowed_for_prompt` as prompt
  eligibility and `safe_to_show` as server-computed display safety.
- Slice 36 defined handoff candidates and kept `allowed_for_prompt=false`.
- Slice 37 defined candidate review and deferred prompt eligibility.
- Slice 38 defined reviewed creation and kept created cards
  `allowed_for_prompt=false` by default.
- `ReviewHistory` already records local append-only review attribution events.
- Artifact contracts already preserve source manifests, redaction evidence, and
  review evidence without changing retrieval runtime behavior.

## Non-goals

- No broad TestKnowledgeCard CRUD implementation, backend feature API,
  frontend page, migration, card table change, automatic prompt eligibility,
  prompt runtime retrieval change, deterministic retrieval behavior change,
  vector database, embeddings, reranking, background indexing, graph runtime,
  GraphRAG job, MCP runtime, provider calls, provider SDK, credentials, OAuth,
  remote URL fetch, queue, scheduler, or background worker.
- No automatic card creation from model output, automatic card approval,
  automatic knowledge ingestion, KnowledgeIngestionAgent runtime, automatic
  duplicate merge, card replacement, card archive/delete, generated-case
  auto-approval, TestCase auto-promotion, runner behavior change, report
  generation behavior change, remote CI provider behavior, RBAC, tenants,
  permissions, or package upgrades.
- No artifact upload, artifact mutation, artifact delete, historical evidence
  mutation, ReviewHistory mutation, FailureAnalysis mutation, Report mutation,
  TestRun/TestResult mutation, TestCase mutation, GeneratedCaseCandidate
  mutation, KnowledgeEvidence mutation, or existing TestKnowledgeCard content
  mutation outside a later explicitly scoped workflow.

## Contract Boundary To Define

The follow-up contract task should define:

- Prompt eligibility input:
  - reviewed TestKnowledgeCard id;
  - creation artifact id;
  - source manifest and same-project source artifact ids;
  - source quote/hash and source span;
  - ReviewHistory ids for creation and prior reviews;
  - redaction report artifact id;
  - safe_to_show status;
  - unsupported claims and failure code when present.
- Review actions:
  - mark_card_prompt_eligible;
  - deny_card_prompt_eligibility;
  - request_prompt_eligibility_revision;
  - revoke_card_prompt_eligibility.
- Eligibility requirements:
  - `safe_to_show=true`;
  - redaction status is reviewed;
  - reviewed source citations and source manifest are present;
  - prompt eligibility reason is non-empty;
  - ReviewHistory and prompt eligibility artifact evidence are recorded;
  - unsupported claims are resolved or explicitly excluded.
- Outputs:
  - eligibility decision;
  - reviewer label/comment;
  - prompt eligibility reason;
  - ReviewHistory append-only event or reference;
  - prompt eligibility artifact;
  - `allowed_for_prompt=true` only for successful human approval;
  - failure code for denial, revision, revoke, or invalid evidence.
- Revocation/failure behavior:
  - revocation records a reason and keeps source evidence auditable;
  - unsafe, stale, cross-project, missing, unbounded, unsupported, or redaction
    failed evidence denies or requests revision;
  - denied/revoked cards must not enter prompt context.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestKnowledgeCard prompt eligibility task plan | done | `test -f docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md && rg -n "TestKnowledgeCard Prompt Eligibility|allowed_for_prompt|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md NEXT_AI_TASK.md && git diff --check` | `2c56822` | planning-only scope |
| Define TestKnowledgeCard prompt eligibility contracts | done | `rg -n "TestKnowledgeCard Prompt Eligibility|mark_card_prompt_eligible|deny_card_prompt_eligibility|request_prompt_eligibility_revision|revoke_card_prompt_eligibility|allowed_for_prompt|safe_to_show|prompt eligibility reason|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md && git diff --check` | `cb0c9b6` | contract-only |
| Add TestKnowledgeCard prompt eligibility golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_eligibility_contract_golden.py -q && git diff --check` | pending | no retrieval/runtime |
| Slice 39 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_eligibility_contract_golden.py backend/app/tests/golden/test_reviewed_test_knowledge_card_creation_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add TestKnowledgeCard Prompt Eligibility Contract Task Plan

Goal: Create a narrow plan for the prompt eligibility boundary before contract
edits or runtime implementation.

Expected files:

- `docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md
rg -n "TestKnowledgeCard Prompt Eligibility|allowed_for_prompt|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 39 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names TestKnowledgeCard prompt eligibility actions, safe_to_show,
  redaction, source evidence, ReviewHistory, prompt eligibility reason,
  artifact evidence, revocation/failure behavior, human review, and non-goals.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add test knowledge card prompt eligibility plan
```

## Task 2: Define TestKnowledgeCard Prompt Eligibility Contracts

Goal: Update data, API, state-machine, and artifact contracts with the human
review boundary for TestKnowledgeCard prompt eligibility.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard Prompt Eligibility|mark_card_prompt_eligible|deny_card_prompt_eligibility|request_prompt_eligibility_revision|revoke_card_prompt_eligibility|allowed_for_prompt|safe_to_show|prompt eligibility reason|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md
git diff --check
```

Acceptance:

- Contracts define prompt eligibility input, review actions, source evidence,
  safe_to_show/redaction requirements, outputs, artifact evidence, revocation,
  and failure behavior.
- Contracts keep prompt runtime retrieval, vector indexes, embeddings,
  reranking, graph jobs, provider calls, broad CRUD, automatic eligibility, and
  historical evidence mutation out of scope.
- Contracts require human review and prompt eligibility reason before
  `allowed_for_prompt=true`.

Commit message:

```text
docs(v2): define test knowledge card prompt eligibility contracts
```

## Task 3: Add TestKnowledgeCard Prompt Eligibility Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving prompt eligibility
cannot bypass safe-to-show, redaction, source evidence, or human review gates.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_prompt_eligibility_contract_golden.py`
- `docs/fixtures/27-test-knowledge-card-prompt-eligibility-golden.md`
- `docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_eligibility_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names prompt eligibility actions, `allowed_for_prompt`,
  `safe_to_show`, redaction, source manifest, ReviewHistory, prompt
  eligibility reason, artifact evidence, revocation/failure behavior, and
  forbidden side effects.
- Golden proves no prompt runtime retrieval change, vector index, embedding,
  reranking, graph job, provider call, MCP runtime, broad CRUD, automatic
  eligibility, historical evidence mutation, RBAC, tenants, or permissions is
  created by the contract.

Commit message:

```text
test(golden): add test knowledge card prompt eligibility smoke
```

## Slice 39 Completion Gate

Goal: Validate Slice 39 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_eligibility_contract_golden.py backend/app/tests/golden/test_reviewed_test_knowledge_card_creation_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 39 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete test knowledge card prompt eligibility slice
```
