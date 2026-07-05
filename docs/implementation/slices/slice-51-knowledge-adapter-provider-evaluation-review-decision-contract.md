# Slice 51: KnowledgeAdapter Provider Evaluation Review Decision Contract Task Plan

## Goal

Define the KnowledgeAdapter provider evaluation review decision contract after
Slice 50 provider evaluation plan evidence exists, but before any provider
enablement, Haystack provider integration, LlamaIndex provider integration,
GraphRAG provider integration, provider SDK, external call, vector database,
embedding job, reranking job, background indexing, runtime retrieval,
provider-backed prompt context behavior, frontend page, RBAC, tenants, or
permissions exist.

This slice is contract-first. It documents how Chtest may review a provider
evaluation plan artifact and record a local decision such as accepted for
future consideration, accepted with constraints, blocked, unsupported, or needs
revision while preserving license review, reference intake, KnowledgeEvidence
normalization, provider_state, fallback behavior, metrics, disabled by default
policy, ReviewHistory, and visible failure behavior.

## Product Value Answer

After this slice, Chtest can make an auditable local review decision on a
KnowledgeAdapter provider evaluation plan. A reviewer can accept a provider for
future consideration, accept with constraints, block it, mark it unsupported,
or request revision while preserving license review, reference intake,
normalization, safety, fallback, metrics, provider_state, disabled by default,
and ReviewHistory evidence. The provider remains disabled by default and no
provider runtime is created.

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
- Slice 50 defined `evaluate_knowledge_adapter_provider_plan` and
  `knowledge_adapter_provider_evaluation_plan` as planning evidence for inert
  candidate providers. It captures provider suitability status, license review
  result, reference intake summary, KnowledgeEvidence normalization notes,
  provider_state recommendation, fallback behavior, disabled by default
  decision, metrics, source hashes, ReviewHistory links, failure code, and
  visible reason.
- Current provider evaluation evidence does not by itself approve a provider,
  mutate KnowledgeAdapterConfig runtime state, create provider-backed prompt
  context evidence, or set `used_knowledge=true`.

## Non-goals

- No provider enablement, Haystack provider integration, LlamaIndex provider
  integration, GraphRAG provider integration, provider SDK, package upgrade,
  API key handling, credentials, OAuth, remote URL fetch, external call,
  network retrieval, or provider runtime.
- No vector database, vector index, embedding model, embedding service,
  embedding vectors, semantic index, ANN search, reranking service, background
  indexing job, crawler, document chunking pipeline, graph runtime, GraphRAG
  job, MCP runtime, or runtime retrieval.
- No provider-backed prompt context evidence, prompt assembly implementation,
  prompt runtime execution, runtime `prompt_input.json`, automatic
  `used_knowledge=true`, deterministic retrieval behavior change, or prompt
  eligibility change.
- No frontend page, report generation behavior, export/download endpoint,
  backend feature API, endpoint, router, service, worker, queue, scheduler,
  migration, or package upgrade.
- No broad KnowledgeAdapter CRUD, automatic provider enablement, automatic
  knowledge ingestion, TestKnowledgeCard CRUD, automatic prompt eligibility,
  artifact upload, artifact mutation outside declared review decision
  evidence, artifact delete, historical evidence mutation,
  GeneratedCaseCandidate mutation, generated-case auto-approval, TestCase
  auto-promotion, ToolInvocation creation, AITask execution behavior change,
  runner behavior change, remote CI provider behavior, RBAC, tenants, or
  permissions.

## Contract Boundary To Define

The follow-up contract task should define:

- Provider evaluation review input:
  - canonical review action
    `review_knowledge_adapter_provider_evaluation`;
  - provider evaluation plan artifact id and
    `knowledge_adapter_provider_evaluation_plan_artifact_id`;
  - candidate provider name, provider family, adapter type, provider version,
    and adapter version;
  - provider suitability status from the evaluation plan;
  - license name, license URL, license compatibility notes, and license review
    result;
  - reference intake summary, reference intake URLs, and documentation snapshot
    artifact ids;
  - expected KnowledgeEvidence normalization fields and KnowledgeEvidence
    normalization notes;
  - provider_state recommendation and disabled by default decision;
  - fallback behavior summary and fallback labels;
  - metrics plan, metric set, evidence normalization completeness, source
    traceability coverage, redaction safety status, and fallback coverage;
  - blocker reasons, unresolved safety questions, source manifest ids, source
    hashes, and ReviewHistory ids when human review exists.
- Provider evaluation review outputs:
  - provider evaluation review decision id or artifact id when a later slice
    persists one;
  - artifact naming such as
    `knowledge_adapter_provider_evaluation_review_decision`;
  - review decision values such as `accepted_for_planning`,
    `accepted_with_constraints`, `blocked`, `needs_revision`, and
    `unsupported`;
  - review status values such as `not_reviewed`, `accepted_for_planning`,
    `accepted_with_constraints`, `blocked`, `needs_revision`, `unsupported`,
    and `failed_validation`;
  - reviewer label, local reviewer id when available, reviewer note, accepted
    constraints, blocked reasons, unsupported reasons, requested revision
    fields, unresolved safety questions, decision rationale, source manifest
    ids, source hashes, ReviewHistory links, failure code, and visible reason.
- Review decision behavior:
  - review decisions are audit evidence only and must not enable providers;
  - accepted for planning or accepted with constraints means accepted for
    future planning, not runtime integration;
  - blocked and unsupported decisions must preserve blocker reasons and
    unresolved safety questions;
  - needs revision decisions must preserve requested revision fields and must
    not rewrite the underlying provider evaluation plan artifact;
  - disabled by default remains mandatory until a later scoped integration
    explicitly defines provider enablement.
- Failure behavior:
  - missing, stale, unsafe, unlicensed, license-unknown, version-unknown,
    reference-missing, reference-mismatched, normalization-unsupported,
    provider-state-unsafe, fallback-missing, review-decision-invalid,
    evaluation-plan-mismatched, cross-project, unbounded, credential-required,
    or runtime-required input must produce a failure code and visible reason
    and must not append a successful review decision.
- Runtime boundary:
  - this slice defines provider evaluation review decision artifact and
    contract semantics only;
  - it does not install packages, call providers, run retrieval, create vector
    indexes, create embeddings, rerank, run graph jobs, invoke MCP runtime,
    change prompt context runtime behavior, enable providers, or mutate
    KnowledgeAdapterConfig outside declared review decision evidence.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add KnowledgeAdapter provider evaluation review decision task plan | done | `test -f docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md && rg -n "KnowledgeAdapter Provider Evaluation Review Decision|provider evaluation review|review_knowledge_adapter_provider_evaluation|review decision|accepted with constraints|blocked|needs revision|unsupported|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md NEXT_AI_TASK.md && git diff --check` | `48ecad5` | planning-only |
| Define KnowledgeAdapter provider evaluation review decision contracts | done | `rg -n "KnowledgeAdapter Provider Evaluation Review Decision|knowledge_adapter_provider_evaluation_review_decision|review_knowledge_adapter_provider_evaluation|provider evaluation plan artifact id|license review|reference intake|KnowledgeEvidence normalization|provider_state|fallback behavior|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md && git diff --check` | `5659644` | contract-only |
| Add KnowledgeAdapter provider evaluation review decision golden smoke | done | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_decision_contract_golden.py -q && git diff --check` | `3df4f9d` | no provider/runtime integration |
| Slice 51 completion gate | done | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_decision_contract_golden.py backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_plan_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add KnowledgeAdapter Provider Evaluation Review Decision Task Plan

Goal: Create a narrow plan for KnowledgeAdapter provider evaluation review
decisions before contract edits, provider enablement, provider integrations,
provider SDKs, external calls, vector infrastructure, runtime retrieval,
frontend pages, RBAC, tenants, permissions, or package upgrades.

Expected files:

- `docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md
rg -n "KnowledgeAdapter Provider Evaluation Review Decision|provider evaluation review|review_knowledge_adapter_provider_evaluation|review decision|accepted with constraints|blocked|needs revision|unsupported|provider suitability status|disabled by default|KnowledgeEvidence|provider_state|fallback behavior|license review|reference intake|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 51 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names provider evaluation review inputs and outputs, human review
  decision semantics, review decisions, provider suitability status,
  accepted with constraints, blocked, needs revision, unsupported,
  KnowledgeEvidence normalization, provider_state, fallback behavior,
  license/reference intake, disabled by default policy, ReviewHistory,
  failure behavior, and forbidden side effects.
- The plan excludes provider enablement, provider integration, provider SDKs,
  external calls, vector database, embeddings, reranking, background indexing,
  runtime retrieval, UI, RBAC, tenants, permissions, and package upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add knowledge adapter provider evaluation review decision plan
```

## Task 2: Define KnowledgeAdapter Provider Evaluation Review Decision Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future provider evaluation review decision boundary before any
provider integration.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "KnowledgeAdapter Provider Evaluation Review Decision|knowledge_adapter_provider_evaluation_review_decision|review_knowledge_adapter_provider_evaluation|provider evaluation plan artifact id|license review|reference intake|KnowledgeEvidence normalization|provider_state|fallback behavior|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md
git diff --check
```

Acceptance:

- Contracts define provider evaluation review inputs, outputs, review decision
  labels, review status labels, provider suitability status,
  KnowledgeEvidence normalization, provider_state, disabled by default policy,
  fallback behavior, license/version/reference intake, metrics, ReviewHistory,
  failure behavior, and forbidden side effects.
- Contracts keep provider enablement, Haystack/LlamaIndex provider
  integration, SDKs, external calls, vector database, embeddings, reranking,
  background indexing, runtime retrieval, UI, RBAC, tenants, permissions, and
  package upgrades out of scope.
- `NEXT_AI_TASK.md` points to Task 3.

Commit message:

```text
docs(v2): define knowledge adapter provider evaluation review decision contracts
```

## Task 3: Add KnowledgeAdapter Provider Evaluation Review Decision Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving review decisions
remain audit evidence and cannot enable a provider runtime.

Expected files:

- `backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_decision_contract_golden.py`
- `docs/fixtures/39-knowledge-adapter-provider-evaluation-review-decision-golden.md`
- `docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_decision_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names KnowledgeAdapter Provider Evaluation Review Decision, provider
  evaluation review, review decision, accepted with constraints, blocked,
  needs revision, unsupported, provider suitability status, KnowledgeEvidence,
  provider_state, fallback behavior, license review, reference intake,
  disabled by default policy, ReviewHistory, failure behavior, and forbidden
  side effects.
- Golden proves no provider SDK, external call, vector database, embedding,
  reranking, background indexing, runtime retrieval, provider-backed prompt
  context evidence, UI, RBAC, tenants, permissions, or package upgrade is
  created by the contract.
- `NEXT_AI_TASK.md` points to Slice 51 Completion Gate.

Commit message:

```text
test(golden): add knowledge adapter provider evaluation review decision smoke
```

## Slice 51 Completion Gate

Goal: Validate Slice 51 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_decision_contract_golden.py backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_plan_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 51 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete knowledge adapter provider evaluation review decision slice
```
