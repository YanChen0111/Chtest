# Slice 52: KnowledgeAdapter Provider Evaluation Review Summary Export Contract Task Plan

## Goal

Define the KnowledgeAdapter provider evaluation review summary export contract
after Slice 51 provider evaluation review decision evidence exists, but before
any provider enablement, Haystack provider integration, LlamaIndex provider
integration, GraphRAG provider integration, provider SDK, external call,
vector database, embedding job, reranking job, background indexing, runtime
retrieval, provider-backed prompt context behavior, frontend page,
export/download endpoint, RBAC, tenants, or permissions exist.

This slice is contract-first. It documents how Chtest may package a local
provider evaluation review decision artifact into a concise audit summary for
future planning while preserving accepted_for_planning,
accepted_with_constraints, blocked, needs_revision, unsupported, license
review, reference intake, KnowledgeEvidence normalization, provider_state,
fallback behavior, disabled by default policy, ReviewHistory, and visible
failure behavior.

## Product Value Answer

After this slice, Chtest can produce an auditable provider evaluation review
summary export contract from a local review decision. Future planning can read
one compact artifact that summarizes the reviewed provider, review decision,
constraints, blockers, unsupported reasons, requested revisions, license and
reference evidence, KnowledgeEvidence normalization expectations,
provider_state, fallback behavior, disabled by default decision, source
traceability, ReviewHistory, and failures. The provider remains disabled by
default and no provider runtime or export/download endpoint is created.

## Current Evidence Baseline

- Slice 19 added deterministic local KnowledgeAdapter retrieval evidence with
  `knowledge_retrieval.json`, `deterministic_local`, `used_knowledge`, matched
  terms, source ids, and bounded snippets without external providers, vector
  search, embeddings, reranking, graph runtime, MCP runtime, RBAC, tenants, or
  permissions.
- Slice 50 defined `evaluate_knowledge_adapter_provider_plan` and
  `knowledge_adapter_provider_evaluation_plan` as planning evidence for inert
  candidate providers. It captures provider suitability status, license review
  result, reference intake summary, KnowledgeEvidence normalization notes,
  provider_state recommendation, fallback behavior, disabled by default
  decision, metrics, source hashes, ReviewHistory links, failure code, and
  visible reason.
- Slice 51 defined `review_knowledge_adapter_provider_evaluation` and
  `knowledge_adapter_provider_evaluation_review_decision` as local review
  decision evidence for provider evaluation plans. It captures review decision
  and review status labels, reviewer note, accepted constraints, blocked
  reasons, unsupported reasons, requested revision fields, unresolved safety
  questions, ReviewHistory links, PromptVersion/SkillVersion trace, failure
  code, and visible reason.
- Current provider evaluation review decision evidence does not approve a
  provider, mutate KnowledgeAdapterConfig runtime state, create
  provider-backed prompt context evidence, expose a download endpoint, generate
  reports, or set `used_knowledge=true`.

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
  export-download endpoint, backend feature API, endpoint, router, service,
  worker, queue, scheduler, migration, or package upgrade.
- No broad KnowledgeAdapter CRUD, automatic provider enablement, automatic
  knowledge ingestion, TestKnowledgeCard CRUD, automatic prompt eligibility,
  artifact upload, artifact mutation outside declared summary export evidence,
  artifact delete, historical evidence mutation, provider evaluation review
  decision artifact mutation, provider evaluation plan artifact mutation,
  GeneratedCaseCandidate mutation, generated-case auto-approval, TestCase
  auto-promotion, ToolInvocation creation, AITask execution behavior change,
  runner behavior change, remote CI provider behavior, RBAC, tenants, or
  permissions.

## Contract Boundary To Define

The follow-up contract task should define:

### Review Summary Export Vocabulary

The contract should preserve these exact planning terms so Task 2 can update
the data, API, state, artifact, and prompt/skill contracts consistently:

- KnowledgeAdapter provider evaluation review decision artifact ids.
- Provider evaluation plan artifact ids.
- Review decision/status labels.
- Reviewer notes.
- Accepted constraints.
- Blocked reasons.
- Unsupported reasons.
- Requested revision fields.
- Unresolved safety questions.
- Source hashes.
- Source manifest ids.
- ReviewHistory links.
- Export artifact id.
- Review summary status.
- Exported decision groups.
- Provider suitability summary.
- License/reference summary.
- KnowledgeEvidence normalization summary.
- Fallback summary.
- Failure code.
- Visible reason.

- Provider evaluation review summary export input:
  - canonical export action
    `export_knowledge_adapter_provider_evaluation_review_summary`;
  - provider evaluation review decision artifact id and
    `knowledge_adapter_provider_evaluation_review_decision_artifact_id`;
  - provider evaluation plan artifact id and
    `knowledge_adapter_provider_evaluation_plan_artifact_id`;
  - candidate provider name, provider family, adapter type, provider version,
    and adapter version;
  - provider suitability status, review decision, and review status from the
    review decision artifact;
  - reviewer label, local reviewer id when available, reviewer note, accepted
    constraints, blocked reasons, unsupported reasons, requested revision
    fields, unresolved safety questions, and decision rationale;
  - license review result, reference intake summary, reference intake URLs,
    and documentation snapshot artifact ids;
  - expected KnowledgeEvidence normalization fields and KnowledgeEvidence
    normalization notes;
  - provider_state recommendation and disabled by default decision;
  - fallback behavior summary and fallback labels;
  - metrics plan, evidence normalization completeness, source traceability
    coverage, redaction safety status, fallback coverage, source manifest ids,
    source hashes, and ReviewHistory links.
- Provider evaluation review summary export output:
  - provider evaluation review summary export id or artifact id when a later
    slice persists one;
  - artifact naming such as
    `knowledge_adapter_provider_evaluation_review_summary_export`;
  - summary filename such as
    `knowledge_adapter_provider_evaluation_review_summary_export.json`;
  - summary status values such as `not_exported`, `exported_for_planning`,
    and `failed_validation`;
  - exported review decision groups for `accepted_for_planning`,
    `accepted_with_constraints`, `blocked`, `needs_revision`, and
    `unsupported`;
  - provider suitability summary, license review summary, reference intake
    summary, KnowledgeEvidence normalization summary, provider_state summary,
    disabled by default summary, fallback behavior summary, metrics summary,
    source traceability summary, ReviewHistory summary, failure code, and
    visible reason.
- Summary export behavior:
  - review summary exports are audit evidence only and must not enable
    providers;
  - accepted_for_planning and accepted_with_constraints remain future-planning
    labels, not runtime integration approvals;
  - blocked and unsupported summaries must preserve blocker reasons,
    unsupported reasons, and unresolved safety questions;
  - needs_revision summaries must preserve requested revision fields and must
    not rewrite the provider evaluation review decision artifact or underlying
    provider evaluation plan artifact;
  - disabled by default remains mandatory until a later scoped integration
    explicitly defines provider enablement;
  - summary export means a stored evidence artifact contract, not a report
    generator, frontend page, or export/download endpoint.
- Failure behavior:
  - missing, stale, unsafe, unlicensed, license-unknown, version-unknown,
    reference-missing, reference-mismatched, normalization-unsupported,
    provider-state-unsafe, fallback-missing, review-decision-missing,
    review-decision-invalid, summary-export-invalid,
    evaluation-plan-mismatched, review-decision-mismatched, cross-project,
    unbounded, credential-required, or runtime-required input must produce a
    failure code and visible reason and must not append a successful summary
    export.
- Runtime boundary:
  - this slice defines provider evaluation review summary export artifact and
    contract semantics only;
  - it does not install packages, call providers, run retrieval, create vector
    indexes, create embeddings, rerank, run graph jobs, invoke MCP runtime,
    change prompt context runtime behavior, generate reports, expose
    export/download endpoints, enable providers, mutate the reviewed decision
    artifact, or mutate KnowledgeAdapterConfig outside declared summary export
    evidence.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add KnowledgeAdapter provider evaluation review summary export task plan | done | `test -f docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md && rg -n "KnowledgeAdapter Provider Evaluation Review Summary Export|provider evaluation review summary export|export_knowledge_adapter_provider_evaluation_review_summary|knowledge_adapter_provider_evaluation_review_summary_export|provider evaluation review decision artifact|accepted_for_planning|accepted_with_constraints|blocked|needs_revision|unsupported|KnowledgeEvidence|provider_state|fallback behavior|license review|reference intake|disabled by default|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md && git diff --check` | `a066b42` | planning-only |
| Define KnowledgeAdapter provider evaluation review summary export contracts | done | `rg -n "KnowledgeAdapter Provider Evaluation Review Summary Export|knowledge_adapter_provider_evaluation_review_summary_export|export_knowledge_adapter_provider_evaluation_review_summary|provider evaluation review decision artifact|summary export|license review|reference intake|KnowledgeEvidence normalization|provider_state|fallback behavior|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md && git diff --check` | pending | contract-only |
| Add KnowledgeAdapter provider evaluation review summary export golden smoke | planned | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_summary_export_contract_golden.py -q && git diff --check` | pending | no provider/runtime/export endpoint integration |
| Slice 52 completion gate | planned | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_summary_export_contract_golden.py backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_decision_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add KnowledgeAdapter Provider Evaluation Review Summary Export Task Plan

Goal: Create a narrow plan for KnowledgeAdapter provider evaluation review
summary exports before contract edits, provider enablement, provider
integrations, provider SDKs, external calls, vector infrastructure, runtime
retrieval, frontend pages, export/download endpoints, RBAC, tenants,
permissions, or package upgrades.

Expected files:

- `docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md
rg -n "KnowledgeAdapter Provider Evaluation Review Summary Export|provider evaluation review summary export|export_knowledge_adapter_provider_evaluation_review_summary|knowledge_adapter_provider_evaluation_review_summary_export|provider evaluation review decision artifact|accepted_for_planning|accepted_with_constraints|blocked|needs_revision|unsupported|KnowledgeEvidence|provider_state|fallback behavior|license review|reference intake|disabled by default|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Acceptance:

- Slice 52 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names provider evaluation review summary export inputs and outputs,
  review decision artifact linkage, accepted/blocked/unsupported/revision
  decision groups, license/reference intake, KnowledgeEvidence normalization,
  provider_state, fallback behavior, disabled by default policy,
  ReviewHistory, failure behavior, and forbidden side effects.
- The plan excludes provider enablement, provider integration, provider SDKs,
  external calls, vector database, embeddings, reranking, background indexing,
  runtime retrieval, UI, export/download endpoints, RBAC, tenants,
  permissions, and package upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add knowledge adapter provider evaluation review summary export plan
```

## Task 2: Define KnowledgeAdapter Provider Evaluation Review Summary Export Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future provider evaluation review summary export boundary before any
provider integration or export/download endpoint.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "KnowledgeAdapter Provider Evaluation Review Summary Export|knowledge_adapter_provider_evaluation_review_summary_export|export_knowledge_adapter_provider_evaluation_review_summary|provider evaluation review decision artifact|summary export|license review|reference intake|KnowledgeEvidence normalization|provider_state|fallback behavior|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md
git diff --check
```

Acceptance:

- Contracts define provider evaluation review summary export inputs, outputs,
  summary export status labels, provider evaluation review decision artifact
  linkage, provider suitability status, KnowledgeEvidence normalization,
  provider_state, disabled by default policy, fallback behavior,
  license/version/reference intake, metrics, ReviewHistory, failure behavior,
  and forbidden side effects.
- Contracts keep provider enablement, Haystack/LlamaIndex provider
  integration, SDKs, external calls, vector database, embeddings, reranking,
  background indexing, runtime retrieval, UI, export/download endpoints, RBAC,
  tenants, permissions, and package upgrades out of scope.
- `NEXT_AI_TASK.md` points to Task 3.

Commit message:

```text
docs(v2): define knowledge adapter provider evaluation review summary export contracts
```

## Task 3: Add KnowledgeAdapter Provider Evaluation Review Summary Export Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving review summary
exports remain audit evidence and cannot enable a provider runtime or create an
export/download endpoint.

Expected files:

- `backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_summary_export_contract_golden.py`
- `docs/fixtures/40-knowledge-adapter-provider-evaluation-review-summary-export-golden.md`
- `docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_summary_export_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names KnowledgeAdapter Provider Evaluation Review Summary Export,
  provider evaluation review summary export, provider evaluation review
  decision artifact, accepted_for_planning, accepted_with_constraints,
  blocked, needs_revision, unsupported, provider suitability status,
  KnowledgeEvidence, provider_state, fallback behavior, license review,
  reference intake, disabled by default policy, ReviewHistory, failure
  behavior, and forbidden side effects.
- Golden proves no provider SDK, external call, vector database, embedding,
  reranking, background indexing, runtime retrieval, provider-backed prompt
  context evidence, UI, export/download endpoint, RBAC, tenants, permissions,
  or package upgrade is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 52 Completion Gate.

Commit message:

```text
test(golden): add knowledge adapter provider evaluation review summary export smoke
```

## Slice 52 Completion Gate

Goal: Validate Slice 52 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_summary_export_contract_golden.py backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_decision_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 52 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete knowledge adapter provider evaluation review summary export slice
```
