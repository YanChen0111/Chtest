# Slice 53: KnowledgeAdapter Provider Evaluation Review Audit Handoff Contract Task Plan

## Goal

Define the KnowledgeAdapter provider evaluation review audit handoff contract
after Slice 52 provider evaluation review summary export evidence exists, but
before any provider enablement, Haystack provider integration, LlamaIndex
provider integration, GraphRAG provider integration, provider SDK, external
call, vector database, embedding job, reranking job, background indexing,
runtime retrieval, provider-backed prompt context behavior, frontend page,
export/download endpoint, RBAC, tenants, or permissions exist.

This slice is contract-first. It documents how Chtest may package provider
evaluation review summary export evidence into one audit handoff bundle while
preserving summary export linkage, review decision linkage, provider
evaluation plan linkage, candidate provider metadata, decision groups,
license/reference evidence, KnowledgeEvidence normalization expectations,
provider_state recommendation, fallback behavior, disabled-by-default policy,
source hashes, and ReviewHistory.

## Product Value Answer

After this slice, Chtest can describe how provider evaluation review summary
export evidence is handed off as an auditable evidence-chain bundle. Future
planning can trace the summary export back to the review decision, provider
evaluation plan, candidate provider metadata, license/reference evidence,
KnowledgeEvidence normalization expectations, provider_state recommendation,
fallback behavior, disabled-by-default decision, source hashes, and
ReviewHistory without enabling providers, installing SDKs, calling providers,
running retrieval, mutating provider state, or changing prompt runtime
behavior.

## Current Evidence Baseline

- Slice 19 added deterministic local KnowledgeAdapter retrieval evidence with
  `knowledge_retrieval.json`, `deterministic_local`, `used_knowledge`, matched
  terms, source ids, and bounded snippets without external providers, vector
  search, embeddings, reranking, graph runtime, MCP runtime, RBAC, tenants, or
  permissions.
- Slice 50 defined `evaluate_knowledge_adapter_provider_plan` and
  `knowledge_adapter_provider_evaluation_plan` as inert provider planning
  evidence with candidate provider metadata, provider suitability status,
  KnowledgeEvidence normalization requirements, provider_state
  recommendation, disabled-by-default decision, fallback behavior, license
  review result, reference intake summary, metrics, source hashes,
  ReviewHistory links, failure code, and visible reason.
- Slice 51 defined `review_knowledge_adapter_provider_evaluation` and
  `knowledge_adapter_provider_evaluation_review_decision` as local review
  decision evidence with accepted_for_planning, accepted_with_constraints,
  blocked, needs_revision, unsupported, accepted constraints, blocked reasons,
  unsupported reasons, requested revision fields, unresolved safety questions,
  PromptVersion/SkillVersion trace, ReviewHistory links, failure code, and
  visible reason.
- Slice 52 defined `export_knowledge_adapter_provider_evaluation_review_summary`
  and `knowledge_adapter_provider_evaluation_review_summary_export` as summary
  export evidence with provider evaluation review decision artifact linkage,
  provider evaluation plan artifact linkage, review summary status, exported
  decision groups, provider suitability summary, license/reference summary,
  KnowledgeEvidence normalization summary, provider_state summary, disabled by
  default summary, fallback summary, metrics summary, source traceability
  summary, ReviewHistory summary, failure code, and visible reason.
- Current provider evaluation review summary export evidence does not approve
  or enable providers, mutate KnowledgeAdapterConfig runtime state, create
  provider-backed prompt context evidence, expose a download endpoint,
  generate reports, install SDKs, or set `used_knowledge=true`.

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
  `used_knowledge=true`, deterministic retrieval behavior change, prompt
  eligibility change, or generated-case auto-approval.
- No frontend page, report generation behavior, report renderer,
  export/download endpoint, export-download endpoint, backend feature API,
  endpoint, router, service, worker, queue, scheduler, migration, or package
  upgrade.
- No broad KnowledgeAdapter CRUD, automatic provider enablement, automatic
  knowledge ingestion, TestKnowledgeCard CRUD, automatic prompt eligibility,
  artifact upload, artifact mutation outside declared audit handoff evidence,
  artifact delete, historical evidence mutation, provider evaluation review
  summary export mutation, provider evaluation review decision mutation,
  provider evaluation plan artifact mutation, GeneratedCaseCandidate mutation,
  ToolInvocation creation, AITask execution behavior change, runner behavior
  change, remote CI provider behavior, RBAC, tenants, or permissions.

## Contract Boundary To Define

The follow-up contract task should define:

### Audit Handoff Vocabulary

The contract should preserve these exact planning terms so Task 2 can update
the data, API, state, artifact, and prompt/skill contracts consistently:

- KnowledgeAdapter provider evaluation review audit handoff.
- Provider evaluation review summary export artifact ids.
- Provider evaluation review decision artifact ids.
- Provider evaluation plan artifact ids.
- Candidate provider metadata.
- Review decision/status labels.
- Accepted constraints.
- Blocked reasons.
- Unsupported reasons.
- Requested revision fields.
- Unresolved safety questions.
- License/reference summaries.
- KnowledgeEvidence normalization summary.
- Provider_state summary.
- Disabled by default summary.
- Fallback summary.
- Metrics summary.
- Source manifest ids.
- Source hashes.
- ReviewHistory links.
- Evidence chain status.
- Included artifact ids.
- Excluded artifact reasons.
- Provider review decision group summary.
- Unresolved blocker summary.
- Unresolved safety question summary.
- Unresolved follow-up flags.
- Failure code.
- Visible reason.

- Audit handoff input:
  - canonical handoff action
    `build_knowledge_adapter_provider_evaluation_review_audit_handoff`;
  - provider evaluation review summary export artifact id and
    `knowledge_adapter_provider_evaluation_review_summary_export_artifact_id`;
  - provider evaluation review decision artifact id and
    `knowledge_adapter_provider_evaluation_review_decision_artifact_id`;
  - provider evaluation plan artifact id and
    `knowledge_adapter_provider_evaluation_plan_artifact_id`;
  - candidate provider name, provider family, adapter type, provider version,
    and adapter version;
  - review summary status, review decision, review status, and exported
    decision groups from the summary export artifact;
  - accepted constraints, blocked reasons, unsupported reasons, requested
    revision fields, unresolved safety questions, unresolved follow-up flags,
    reviewer note, and decision rationale;
  - provider suitability summary, license review summary, reference intake
    summary, documentation snapshot artifact ids, and reference intake URLs;
  - KnowledgeEvidence normalization summary, provider_state summary, disabled
    by default summary, fallback behavior summary, fallback labels, metrics
    summary, source traceability summary, source manifest ids, source hashes,
    and ReviewHistory links.
- Audit handoff output:
  - audit handoff artifact id when a later slice persists one;
  - artifact naming such as
    `knowledge_adapter_provider_evaluation_review_audit_handoff`;
  - handoff filename such as
    `knowledge_adapter_provider_evaluation_review_audit_handoff.json`;
- Audit handoff fields:
  - handoff summary;
  - evidence chain status values such as `complete`, `incomplete`, `blocked`,
    and `failed_validation`;
  - included artifact ids;
  - excluded artifact reasons;
  - provider review decision group summary;
  - unresolved blocker summary;
  - unresolved safety question summary;
  - unresolved follow-up flags;
  - provider suitability handoff summary;
  - license/reference handoff summary;
  - KnowledgeEvidence normalization handoff summary;
  - provider_state handoff summary;
  - disabled by default handoff summary;
  - fallback behavior handoff summary;
  - metrics handoff summary;
  - source traceability handoff summary;
  - ReviewHistory links, failure code, and visible reason.
- Safety requirements:
  - audit handoff records are evidence-chain packages, not mutation of
    provider evaluation review summary export artifacts, provider evaluation
    review decision artifacts, provider evaluation plan artifacts,
    provider metadata, KnowledgeEvidence records, KnowledgeAdapterConfig
    runtime state, provider_state, historical evidence, or runtime retrieval
    behavior;
  - accepted_for_planning and accepted_with_constraints remain future-planning
    labels, not runtime integration approvals;
  - evidence chain status does not enable providers, install SDKs, create
    credentials, fetch remote URLs, create vector indexes, run retrieval,
    assemble prompts, generate reports, expose download endpoints, or mark
    `used_knowledge=true`;
  - included artifact ids, excluded artifact reasons, unresolved blocker
    summary, unresolved safety questions, unresolved follow-up flags,
    unsupported reasons, requested revision fields, source hashes, and
    ReviewHistory links must remain visible instead of being filtered,
    deleted, or rewritten;
  - invalid, stale, unsafe, unlicensed, license-unknown, version-unknown,
    reference-missing, reference-mismatched, normalization-unsupported,
    provider-state-unsafe, fallback-missing, summary-export-missing,
    summary-export-invalid, review-decision-missing, review-decision-invalid,
    evaluation-plan-missing, evaluation-plan-mismatched,
    review-decision-mismatched, cross-project, unbounded, credential-required,
    runtime-required, or provider-enable-required input must fail without
    appending a successful audit handoff.
- Runtime boundary:
  - this slice defines provider evaluation review audit handoff artifact and
    contract semantics only;
  - it does not install packages, call providers, run retrieval, create vector
    indexes, create embeddings, rerank, run graph jobs, invoke MCP runtime,
    change prompt context runtime behavior, generate reports, expose
    export/download endpoints, enable providers, mutate the summary export
    artifact, mutate the reviewed decision artifact, mutate the provider
    evaluation plan artifact, or mutate KnowledgeAdapterConfig outside
    declared audit handoff evidence.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add KnowledgeAdapter provider evaluation review audit handoff task plan | done | `if (-not (Test-Path docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md)) { exit 1 }; rg -n "KnowledgeAdapter Provider Evaluation Review Audit Handoff|provider evaluation review audit handoff|knowledge_adapter_provider_evaluation_review_audit_handoff|provider evaluation review summary export artifact|provider evaluation review decision artifact|provider evaluation plan artifact|evidence chain status|included artifact ids|excluded artifact reasons|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md; git diff --check` | `1dd952a` | planning-only |
| Define KnowledgeAdapter provider evaluation review audit handoff contracts | done | `rg -n "KnowledgeAdapter Provider Evaluation Review Audit Handoff|knowledge_adapter_provider_evaluation_review_audit_handoff|build_knowledge_adapter_provider_evaluation_review_audit_handoff|provider evaluation review summary export artifact|provider evaluation review decision artifact|provider evaluation plan artifact|evidence chain status|included artifact ids|excluded artifact reasons|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md && git diff --check` | `e747a96` | contract-only |
| Add KnowledgeAdapter provider evaluation review audit handoff golden smoke | done | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_audit_handoff_contract_golden.py -q && git diff --check` | pending | no provider/runtime/export endpoint integration |
| Slice 53 completion gate | planned | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_audit_handoff_contract_golden.py backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_summary_export_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add KnowledgeAdapter Provider Evaluation Review Audit Handoff Task Plan

Goal: Create a narrow plan for KnowledgeAdapter provider evaluation review
audit handoff before contract edits, provider enablement, provider
integrations, provider SDKs, external calls, vector infrastructure, runtime
retrieval, frontend pages, export/download endpoints, RBAC, tenants,
permissions, or package upgrades.

Expected files:

- `docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```powershell
if (-not (Test-Path docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md)) { exit 1 }
rg -n "KnowledgeAdapter Provider Evaluation Review Audit Handoff|provider evaluation review audit handoff|knowledge_adapter_provider_evaluation_review_audit_handoff|provider evaluation review summary export artifact|provider evaluation review decision artifact|provider evaluation plan artifact|evidence chain status|included artifact ids|excluded artifact reasons|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Acceptance:

- Slice 53 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit message.
- The plan names audit handoff inputs and outputs, summary export artifact
  linkage, review decision artifact linkage, provider evaluation plan artifact
  linkage, evidence chain status, included/excluded artifact handling,
  unresolved follow-up flags, ReviewHistory, failure behavior, and forbidden
  side effects.
- The plan excludes provider enablement, provider integration, provider SDKs,
  external calls, vector database, embeddings, reranking, runtime retrieval,
  UI, export/download endpoints, RBAC, tenants, permissions, and package
  upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add knowledge adapter provider evaluation review audit handoff plan
```

## Task 2: Define KnowledgeAdapter Provider Evaluation Review Audit Handoff Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future provider evaluation review audit handoff boundary before any
provider integration, provider enablement, or export/download endpoint.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "KnowledgeAdapter Provider Evaluation Review Audit Handoff|knowledge_adapter_provider_evaluation_review_audit_handoff|build_knowledge_adapter_provider_evaluation_review_audit_handoff|provider evaluation review summary export artifact|provider evaluation review decision artifact|provider evaluation plan artifact|evidence chain status|included artifact ids|excluded artifact reasons|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md
git diff --check
```

Acceptance:

- Contracts define provider evaluation review audit handoff inputs, outputs,
  evidence chain status labels, summary export artifact linkage, review
  decision artifact linkage, provider evaluation plan artifact linkage,
  included/excluded artifact handling, provider review decision group summary,
  unresolved blocker summary, unresolved safety question summary,
  KnowledgeEvidence normalization, provider_state, disabled by default policy,
  fallback behavior, license/reference evidence, metrics, ReviewHistory,
  failure behavior, and forbidden side effects.
- Contracts keep provider enablement, Haystack/LlamaIndex provider
  integration, SDKs, external calls, vector database, embeddings, reranking,
  background indexing, runtime retrieval, UI, export/download endpoints, RBAC,
  tenants, permissions, and package upgrades out of scope.
- `NEXT_AI_TASK.md` points to Task 3.

Commit message:

```text
docs(v2): define knowledge adapter provider evaluation review audit handoff contracts
```

## Task 3: Add KnowledgeAdapter Provider Evaluation Review Audit Handoff Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving audit handoff
remains evidence-chain packaging and cannot enable a provider runtime, mutate
provider evaluation evidence, or create an export/download endpoint.

Expected files:

- `backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_audit_handoff_contract_golden.py`
- `docs/fixtures/41-knowledge-adapter-provider-evaluation-review-audit-handoff-golden.md`
- `docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_audit_handoff_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names KnowledgeAdapter Provider Evaluation Review Audit Handoff,
  provider evaluation review audit handoff, provider evaluation review summary
  export artifact, provider evaluation review decision artifact, provider
  evaluation plan artifact, evidence chain status, included artifact ids,
  excluded artifact reasons, provider review decision group summary,
  unresolved blocker summary, unresolved safety question summary, unresolved
  follow-up flags,
  KnowledgeEvidence, provider_state, fallback behavior, disabled by default
  policy, ReviewHistory, failure behavior, and forbidden side effects.
- Golden proves no provider SDK, external call, vector database, embedding,
  reranking, background indexing, runtime retrieval, provider-backed prompt
  context evidence, UI, export/download endpoint, RBAC, tenants, permissions,
  package upgrade, or provider-state mutation is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 53 Completion Gate.

Commit message:

```text
test(golden): add knowledge adapter provider evaluation review audit handoff smoke
```

## Slice 53 Completion Gate

Goal: Validate Slice 53 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_audit_handoff_contract_golden.py backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_summary_export_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 53 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete knowledge adapter provider evaluation review audit handoff slice
```
