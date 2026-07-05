# Slice 50: KnowledgeAdapter Provider Evaluation Plan Contract Task Plan

## Goal

Define the KnowledgeAdapter provider evaluation plan contract before any
Haystack provider integration, LlamaIndex provider integration, provider SDK,
external call, vector database, embedding job, reranking job, background
indexing, runtime retrieval, provider-backed prompt context behavior, frontend
page, RBAC, tenants, or permissions exist.

This slice is contract-first. It documents how Chtest may evaluate future
KnowledgeAdapter providers as disabled-by-default candidates while preserving
KnowledgeEvidence normalization, provider_state, fallback behavior, license
and version review, reference intake, metrics, ReviewHistory, and visible
failure behavior.

## Product Value Answer

After this slice, Chtest can describe how future Haystack, LlamaIndex, or other
KnowledgeAdapter providers will be evaluated before integration. Users get a
clear provider evaluation plan: provider names, versions, licenses, reference
intake, KnowledgeEvidence normalization requirements, provider_state, metrics,
fallback behavior, disabled by default policy, ReviewHistory, and failure
reasons remain reviewable before any provider SDK, external call, vector
database, embedding, reranking, runtime retrieval, UI, RBAC, tenants, or
permissions are added.

## Current Evidence Baseline

- Slice 19 added deterministic local KnowledgeAdapter retrieval evidence with
  `knowledge_retrieval.json`, `deterministic_local`, `used_knowledge`, matched
  terms, source ids, and bounded snippets without external providers, vector
  search, embeddings, reranking, graph runtime, MCP runtime, RBAC, tenants, or
  permissions.
- Slice 30 and Slice 31 established `TestKnowledgeCard` and
  `KnowledgeEvidence` shapes for normalized source evidence.
- Slice 33 defined MCP-ready ToolDefinition and KnowledgeAdapter safety
  contracts, including provider_state display metadata, disabled/unhealthy
  fallback behavior, and no MCP runtime or external provider calls.
- Current `KnowledgeAdapterConfig` supports `not_configured`, `disabled`, and
  `configured_stub`, with `provider_type=deterministic_local` scoped to the
  local stub.
- Current contracts say future Haystack, LlamaIndex, GraphRAG, or other
  provider payloads must normalize into KnowledgeEvidence before use.
- Slice 49 closed the TestKnowledgeCard prompt-context discrepancy resolution
  audit handoff contract chain, so the next provider-facing work should define
  evaluation gates before any new retrieval provider is implemented.

## Non-goals

- No Haystack provider integration, LlamaIndex provider integration,
  GraphRAG provider integration, provider SDK, API key handling, credentials,
  OAuth, remote URL fetch, external call, network retrieval, or provider
  runtime.
- No vector database, embedding model, embedding service, embedding vectors,
  semantic index, ANN search, reranking service, background indexing job,
  crawler, document chunking pipeline, graph runtime, or MCP runtime.
- No runtime retrieval implementation, prompt runtime execution,
  provider-backed prompt context evidence, provider-backed prompt context
  consumption, provider-backed audit summary, automatic `used_knowledge=true`,
  or prompt assembly implementation.
- No frontend page, dashboard, report generation behavior, export/download
  endpoint, backend feature API, endpoint, router, service, worker, queue,
  scheduler, migration, or package upgrade.
- No broad KnowledgeAdapter CRUD, automatic provider enablement, automatic
  knowledge ingestion, automatic card creation from model output,
  TestKnowledgeCard CRUD, prompt eligibility changes, artifact upload,
  artifact mutation, artifact delete, historical evidence mutation,
  generated-case auto-approval, runner behavior changes, remote CI provider
  behavior, RBAC, tenants, or permissions.

## Contract Boundary To Define

The follow-up contract task should define:

- Provider evaluation input:
  - provider evaluation plan action
    `evaluate_knowledge_adapter_provider_plan`, with evaluation-only labels
    such as `evaluate_provider_candidate`, `record_provider_evaluation`,
    `block_provider_candidate`, or `request_provider_evaluation_revision`;
  - candidate provider name;
  - provider family such as Haystack, LlamaIndex, GraphRAG, or local adapter;
  - provider version and adapter version;
  - license name, license URL, and license compatibility notes;
  - reference intake URLs or documentation snapshot artifact ids;
  - supported retrieval modes;
  - supported source types;
  - expected KnowledgeEvidence normalization fields;
  - expected provider_state values;
  - disabled by default policy;
  - fallback behavior expectations;
  - metrics to collect;
  - safety, redaction, and source-hash requirements;
  - ReviewHistory ids when human review exists.
- Provider evaluation outputs:
  - provider evaluation plan id or artifact id when a later slice persists one;
  - provider suitability status such as `not_evaluated`, `suitable`,
    `suitable_with_constraints`, `blocked`, `needs_revision`, or
    `unsupported`;
  - normalized KnowledgeEvidence requirements;
  - provider_state recommendation;
  - disabled by default decision;
  - fallback behavior summary;
  - license review result;
  - reference intake summary;
  - metrics plan;
  - blocker reasons;
  - fallback labels such as `fallback_required`,
    `local_no_knowledge_fallback`, `normalization_required`,
    `citation_traceability_required`, and `license_review_required`;
  - unresolved safety questions;
  - source manifest ids and source hashes;
  - ReviewHistory links;
  - failure code and visible reason.
- Evaluation metrics:
  - evidence normalization completeness;
  - source traceability coverage;
  - redaction safety status;
  - fallback coverage;
  - unsupported payload fields;
  - deterministic/local parity notes;
  - latency or cost estimates as metadata only;
  - provider_state health metadata without runtime calls.
- Safety requirements:
  - provider evaluation records are planning evidence only;
  - provider_state remains display/health metadata and must not start runtime
    retrieval;
  - disabled by default is the safe outcome until a later scoped integration
    explicitly enables a provider;
  - fallback behavior must preserve local/no-knowledge evidence instead of
    fabricating KnowledgeEvidence;
  - raw provider payloads, credentials, secrets, API keys, OAuth material,
    embedding vectors, vector store payloads, reranker traces, graph payloads,
    and remote fetch payloads must not be copied into reviewed evidence.
- Failure behavior:
  - missing, stale, unsafe, unlicensed, license-unknown, version-unknown,
    reference-missing, reference-mismatched, normalization-unsupported,
    redaction-failed, provider-state-unsafe, fallback-missing,
    cross-project, unbounded, credential-required, or runtime-required input
    must produce a failure code and visible reason and must not mark a provider
    ready for integration.
- Runtime boundary:
  - this slice defines provider evaluation plan artifact and contract semantics
    only;
  - it does not install packages, call providers, run retrieval, create vector
    indexes, create embeddings, rerank, run graph jobs, invoke MCP runtime,
    change prompt context runtime behavior, enable providers, or mutate
    KnowledgeAdapterConfig outside declared evaluation evidence.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add KnowledgeAdapter provider evaluation plan task plan | done | `test -f docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md && rg -n "KnowledgeAdapter Provider Evaluation Plan|Haystack|LlamaIndex|provider evaluation|KnowledgeEvidence|provider_state|fallback behavior|license|reference intake|disabled by default|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md NEXT_AI_TASK.md && git diff --check` | `65a5658` | planning-only scope |
| Define KnowledgeAdapter provider evaluation plan contracts | done | `rg -n "KnowledgeAdapter Provider Evaluation Plan|knowledge_adapter_provider_evaluation_plan|evaluate_knowledge_adapter_provider_plan|Haystack|LlamaIndex|KnowledgeEvidence|provider_state|fallback behavior|license review|reference intake|disabled by default|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md && git diff --check` | `c2fcfba` | contract-only |
| Add KnowledgeAdapter provider evaluation plan golden smoke | done | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_plan_contract_golden.py -q && git diff --check` | pending | no provider/runtime integration |
| Slice 50 completion gate | planned | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_plan_contract_golden.py backend/app/tests/golden/test_mcp_ready_tool_knowledge_safety_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add KnowledgeAdapter Provider Evaluation Plan Task Plan

Goal: Create a narrow plan for KnowledgeAdapter provider evaluation before
contract edits, provider SDKs, external calls, vector infrastructure, runtime
retrieval, frontend pages, or package upgrades.

Expected files:

- `docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md
rg -n "KnowledgeAdapter Provider Evaluation Plan|Haystack|LlamaIndex|provider evaluation|KnowledgeEvidence|provider_state|fallback behavior|license|reference intake|disabled by default|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 50 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names Haystack, LlamaIndex, provider evaluation inputs and outputs,
  KnowledgeEvidence normalization, provider_state, fallback behavior, license
  review, version/reference intake, disabled by default policy, metrics,
  evaluation-only actions, provider suitability status labels, ReviewHistory,
  failure behavior, and non-goals.
- The plan excludes provider integration, provider SDKs, external calls,
  vector database, embeddings, reranking, background indexing, runtime
  retrieval, UI, RBAC, tenants, permissions, and package upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add knowledge adapter provider evaluation plan
```

## Task 2: Define KnowledgeAdapter Provider Evaluation Plan Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future provider evaluation boundary before any provider integration.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "KnowledgeAdapter Provider Evaluation Plan|knowledge_adapter_provider_evaluation_plan|evaluate_knowledge_adapter_provider_plan|Haystack|LlamaIndex|KnowledgeEvidence|provider_state|fallback behavior|license review|reference intake|disabled by default|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md
git diff --check
```

Acceptance:

- Contracts define provider evaluation inputs, outputs, status labels,
  KnowledgeEvidence normalization, provider_state, disabled by default policy,
  fallback behavior, license/version/reference intake, metrics, ReviewHistory,
  failure behavior, and forbidden side effects.
- Contracts keep Haystack/LlamaIndex provider integration, SDKs, external
  calls, vector database, embeddings, reranking, background indexing, runtime
  retrieval, UI, RBAC, tenants, permissions, and package upgrades out of
  scope.
- `NEXT_AI_TASK.md` points to Task 3.

Commit message:

```text
docs(v2): define knowledge adapter provider evaluation plan contracts
```

## Task 3: Add KnowledgeAdapter Provider Evaluation Plan Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving provider
evaluation remains planning evidence and cannot enable a provider runtime.

Expected files:

- `backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_plan_contract_golden.py`
- `docs/fixtures/38-knowledge-adapter-provider-evaluation-plan-golden.md`
- `docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_plan_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names KnowledgeAdapter Provider Evaluation Plan, Haystack,
  LlamaIndex, provider evaluation, KnowledgeEvidence, provider_state, fallback
  behavior, license review, reference intake, disabled by default policy,
  metrics, ReviewHistory, failure behavior, and forbidden side effects.
- Golden proves no provider SDK, external call, vector database, embedding,
  reranking, background indexing, runtime retrieval, UI, RBAC, tenants,
  permissions, or package upgrade is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 50 Completion Gate.

Commit message:

```text
test(golden): add knowledge adapter provider evaluation plan smoke
```

## Slice 50 Completion Gate

Goal: Validate Slice 50 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_plan_contract_golden.py backend/app/tests/golden/test_mcp_ready_tool_knowledge_safety_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 50 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete knowledge adapter provider evaluation plan slice
```
