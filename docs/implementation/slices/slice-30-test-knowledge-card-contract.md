# Slice 30: Test Knowledge Card Contract Task Plan

## Goal

Define the evidence contract that lets generated test cases cite structured
testing knowledge before Chtest adds any heavier RAG runtime.

Slice 19 proved deterministic local ContextArtifact retrieval. Slice 30 takes
the next small step toward the final RAG and agent direction: convert testing
knowledge into reviewable cards and make generated-case evidence explicit. The
slice is contract-first and evidence-first; it does not index, embed, rerank, or
call external knowledge providers.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- `docs/implementation/11-final-rag-agent-strategy.md`
- Recent evidence slices:
  - `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`
  - `docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md`
  - `docs/implementation/slices/slice-29-execution-run-manifest.md`

## Product Value Answer

After this slice, a test engineer can review generated test cases and see which
testing knowledge supports them, which risks or requirements they cover, why the
case exists, and what review findings must be resolved before the case enters
the library.

## Preconditions

- ContextArtifact is backed by Artifact rows and can be used as local prompt
  context.
- Deterministic local KnowledgeAdapter retrieval can record retrieval evidence
  without vector infrastructure.
- GeneratedCaseCandidate already has requirement refs, risk refs, AI reason,
  duplicate reference, and human review status.
- Artifact evidence can reference same-project local files and safe metadata.
- Review gates remain mandatory before generated cases become TestCase records.

## Non-goals

- No RAG runtime, external KnowledgeAdapter provider call, provider SDK,
  background indexing pipeline, vector database, embedding service, semantic
  search, reranking, chunking pipeline, GraphRAG runtime, graph database, or
  offline graph extraction job.
- No MCP runtime, MCP server/client transport, marketplace, plugin install,
  remote MCP call, or ToolDefinition behavior change.
- No frontend implementation, broad redesign, dashboard, knowledge editor,
  graph view, model leaderboard, eval console, or report generation change.
- No generated-case auto-approval, automatic TestCase promotion, review bypass,
  automation execution, runner behavior change, or business source modification.
- No artifact upload, mutation, delete, signed URL, cloud storage, remote URL
  fetch, arbitrary filesystem read, credentials, OAuth, API key storage, RBAC,
  tenants, permissions, team workflow, remote CI provider behavior, PR comments,
  deploy, release, merge, push, or scheduling.

## Slice Boundary

- Define `TestKnowledgeCard` as a local project testing-knowledge contract
  derived from ContextArtifact, reviewed cases, accepted/rejected generated
  cases, execution evidence, reports, or manually curated testing notes.
- Define `KnowledgeEvidence` as the normalized evidence item that agents and
  generated cases may cite.
- Define generated-case evidence fields for source knowledge evidence ids,
  covered risk ids, generation reason, automation readiness, quality score,
  review findings, and coverage gap notes.
- Define artifact paths and fixture evidence for knowledge-card extraction and
  generated-case review.
- Add one golden fixture document showing requirement text, knowledge cards,
  knowledge evidence, generated candidates, review findings, and evidence ids.
- Keep all implementation in this slice behind contracts and fixtures first.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Test Knowledge Card Contract task plan | done | `test -f docs/implementation/slices/slice-30-test-knowledge-card-contract.md && rg -n "Test Knowledge Card|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-30-test-knowledge-card-contract.md NEXT_AI_TASK.md && git diff --check` | pending | planning-only scope |
| Define TestKnowledgeCard and KnowledgeEvidence contracts | done | `rg -n "TestKnowledgeCard|KnowledgeEvidence|source_knowledge_evidence_ids|coverage_gap_notes|RAG runtime|MCP runtime" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-30-test-knowledge-card-contract.md && git diff --check` | pending | contract-only |
| Add test knowledge card golden fixture | planned | `test -f docs/fixtures/18-test-knowledge-card-contract-golden.md && rg -n "TestKnowledgeCard|KnowledgeEvidence|GeneratedCaseCandidate|review_findings|coverage_gap_notes" docs/fixtures/18-test-knowledge-card-contract-golden.md docs/implementation/slices/slice-30-test-knowledge-card-contract.md && git diff --check` | pending | fixture-only |
| Add contract smoke for generated-case evidence fields | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_contract_golden.py -q && git diff --check` | pending | schema/evidence proof only |
| Slice 30 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add Test Knowledge Card Contract Task Plan

Goal: Select and plan the smallest knowledge-driven V2 slice before contracts,
fixtures, or implementation.

Expected files:

- `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-30-test-knowledge-card-contract.md
rg -n "Test Knowledge Card|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-30-test-knowledge-card-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Creates the Slice 30 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to contracts, fixtures, and golden proof for structured
  testing knowledge evidence.
- Does not add product code, frontend code, backend runtime behavior,
  migrations, package upgrades, vector infrastructure, provider integrations,
  RAG runtime, or MCP runtime.

Commit message:

```text
docs(v2): add test knowledge card contract plan
```

## Task 2: Define TestKnowledgeCard And KnowledgeEvidence Contracts

Goal: Clarify the data, API, state, and artifact contracts before adding any
schema or implementation.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard|KnowledgeEvidence|source_knowledge_evidence_ids|coverage_gap_notes|RAG runtime|MCP runtime" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-30-test-knowledge-card-contract.md
git diff --check
```

Acceptance:

- Data contract defines local `TestKnowledgeCard` and normalized
  `KnowledgeEvidence` fields, including source artifacts, safe-to-show,
  allowed-for-prompt, risk/requirement/module classification, confidence, and
  evidence artifact references.
- API contract defines read/write or future API boundaries without enabling
  external retrieval, indexing, or provider calls in this task.
- State-machine contract states knowledge-card status changes must not trigger
  retrieval jobs, indexing, embeddings, graph extraction, or generated-case
  promotion.
- Artifact contract defines knowledge-card and generated-case evidence files
  and same-project artifact reference rules.
- GeneratedCaseCandidate contract defines evidence ids, risk coverage,
  generation reason, automation readiness, quality score, review findings, and
  coverage gap notes.
- Contract preserves review gates and the no RAG runtime, MCP runtime, vector,
  embedding, reranking, external provider, RBAC, tenant, permission, and remote
  CI provider boundary.

Commit message:

```text
docs(v2): define test knowledge card contract
```

## Task 3: Add Test Knowledge Card Golden Fixture

Goal: Provide an AI-readable example that shows how testing knowledge evidence
supports generated cases and review findings.

Expected files:

- `docs/fixtures/18-test-knowledge-card-contract-golden.md`
- `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/fixtures/18-test-knowledge-card-contract-golden.md
rg -n "TestKnowledgeCard|KnowledgeEvidence|GeneratedCaseCandidate|review_findings|coverage_gap_notes" docs/fixtures/18-test-knowledge-card-contract-golden.md docs/implementation/slices/slice-30-test-knowledge-card-contract.md
git diff --check
```

Acceptance:

- Fixture includes a compact requirement, source ContextArtifact references,
  TestKnowledgeCard examples, KnowledgeEvidence examples, generated case
  candidates, review findings, coverage gap notes, and evidence ids.
- Fixture shows accepted, needs-review, and rejected evidence conditions.
- Fixture explains that provider schemas are normalized into Chtest evidence.
- Fixture does not imply any vector database, external provider, graph runtime,
  auto-approval, frontend behavior, or execution behavior exists.

Commit message:

```text
docs(fixtures): add test knowledge card contract golden
```

## Task 4: Add Contract Smoke For Generated-Case Evidence Fields

Goal: Prove the backend schemas preserve structured knowledge evidence on
generated candidates without creating runtime retrieval behavior.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_contract_golden.py`
- backend schema/model files only when required by the contract
- `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden proves generated-case evidence fields can be serialized and read back
  through the relevant schema or API boundary.
- Golden proves knowledge evidence references are structured data and do not
  create TestCase records, runner executions, reports, external provider calls,
  retrieval jobs, vector indexes, graph jobs, or artifact mutations.
- If database models are not yet implemented, the task must stay schema/fixture
  level and document the missing implementation as the next task instead of
  inventing a runtime.

Commit message:

```text
test(golden): add test knowledge card contract smoke
```

## Slice 30 Completion Gate

Goal: Validate the contract-first knowledge-card slice and hand off the next
small implementation task.

Expected files:

- `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 30 task table records completed task commits.
- Contract and fixture documents agree on field names and non-goals.
- Verification passes or records a concrete blocker.
- `NEXT_AI_TASK.md` points to the next narrow V2 task.

Commit message:

```text
docs(v2): complete test knowledge card contract slice
```
