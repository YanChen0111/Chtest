# Slice 57: Generated Case Human Review Decision Audit Handoff Contract Task Plan

## Goal

Define the Generated Case Human Review Decision Audit Handoff contract after
Slice 56 generated case human review decision summary export evidence exists,
but before any actual GeneratedCaseCandidate approve/reject mutation, request
optimization mutation, TestCase promotion, AutomationDraft creation, backend
runtime API, frontend page, report generation behavior, export/download
endpoint, provider integration, provider SDK, external call, vector database,
embedding job, reranking job, graph runtime, MCP runtime, runtime retrieval,
RBAC, tenants, or permissions exist.

This slice is contract-first. It documents how Chtest may package generated
case human review decision summary export evidence into one audit handoff
bundle while preserving summary export linkage, source decision artifact
linkage, evidence package lineage, exported decision groups, included and
excluded artifact references, unresolved blockers, unresolved follow-up
flags, source traceability, ReviewHistory links, failure code, and visible
reason. The audit handoff is evidence-chain packaging only; it is not a
runtime report, download endpoint, approval batch, rejection batch,
optimization request, or TestCase promotion workflow.

## Product Value Answer

After this slice, Chtest can describe how generated-case human review decision
summary export evidence is handed off as an auditable evidence-chain bundle.
Future planning can trace a handoff back to the summary export, source
decision artifacts, evidence packages, exported decision groups,
unresolved follow-up flags, source hashes, source manifest ids, and
ReviewHistory without mutating GeneratedCaseCandidate status, creating
TestCases, creating automation drafts, rendering reports, exposing
export/download endpoints, running prompts, calling providers, changing
retrieval behavior, or adding UI/runtime surfaces.

## Current Evidence Baseline

- Slice 54 defined
  `build_generated_case_human_review_evidence_package` and
  `generated_case_human_review_evidence_package` as human-review evidence
  packaging with GeneratedCaseCandidate linkage, prompt-context lineage,
  source hashes, source manifest ids, and ReviewHistory links.
- Slice 55 defined
  `review_generated_case_human_review_evidence_package` and
  `generated_case_human_review_decision` as human-review decision evidence
  with decision labels, reviewer label/comment, accepted constraints,
  requested edit fields, optimization request summary, rejection/blocker
  reasons, duplicate resolution notes, ReviewHistory links, failure code, and
  visible reason.
- Slice 56 defined
  `build_generated_case_human_review_decision_summary_export` and
  `generated_case_human_review_decision_summary_export` as audit summary
  export evidence with exported decision groups, included/excluded decision
  artifact ids, excluded decision artifact reasons, source traceability
  summary, ReviewHistory summary, failure code, and visible reason.
- GeneratedCaseCandidate state transitions already exist for real human review
  actions such as approve, approve_after_edit, reject, and
  request_optimization. This slice must not invoke or redefine those runtime
  transitions.
- ReviewHistory already records successful real review actions. This slice may
  link ReviewHistory evidence, but invalid audit handoff input must not append
  a successful ReviewHistory decision or mutate historical review evidence.

## Non-goals

- No backend runtime API, endpoint, router, service, worker, queue, scheduler,
  migration, package upgrade, or broad GeneratedCaseCandidate CRUD.
- No frontend page, frontend store, component, report generation behavior,
  report renderer, export/download endpoint, export-download endpoint, or
  backend feature API.
- No actual GeneratedCaseCandidate approve/reject mutation, status mutation,
  request optimization mutation, TestCase promotion, AutomationDraft creation,
  ToolInvocation creation, TestRun/TestResult creation, runner behavior
  change, remote CI provider behavior, generated replacement evidence, or
  generated-case auto-approval.
- No prompt execution, AITask orchestration, automatic `used_knowledge=true`,
  deterministic retrieval behavior change, prompt eligibility change, or
  automatic knowledge ingestion.
- No provider integration, provider SDK, external call, credential handling,
  OAuth, remote URL fetch, vector database, vector index, embedding model,
  embedding service, embedding vectors, semantic index, ANN search, reranking,
  background indexing, graph runtime, GraphRAG job, MCP runtime, runtime
  retrieval, or provider-backed prompt context evidence.
- No artifact upload, Artifact mutation outside declared audit handoff
  evidence, artifact delete, summary export artifact mutation, decision
  artifact mutation, evidence package mutation, source artifact mutation,
  prompt context evidence mutation, GeneratedCaseCandidate content mutation,
  KnowledgeEvidence mutation, TestKnowledgeCard mutation, ReviewHistory
  mutation, historical evidence mutation, RBAC, tenants, or permissions.

## Contract Boundary To Define

The follow-up contract task should define:

### Audit Handoff Vocabulary

The contract should preserve these exact planning terms so Task 2 can update
the data, API, state, artifact, and prompt/skill contracts consistently:

- Generated Case Human Review Decision Audit Handoff.
- Generated case human review decision summary export artifact id.
- `generated_case_human_review_decision_summary_export_artifact_id`.
- Generated case human review decision artifact ids.
- `generated_case_human_review_decision_artifact_id`.
- Generated case human review evidence package artifact ids.
- `generated_case_human_review_evidence_package_artifact_id`.
- Exported decision groups.
- Included decision artifact ids.
- Excluded decision artifact ids.
- Excluded decision artifact reasons.
- Source traceability summary.
- ReviewHistory summary.
- ReviewHistory ids.
- ReviewHistory links.
- Handoff artifact id.
- Handoff summary.
- Evidence chain status.
- Included artifact ids.
- Excluded artifact reasons.
- Accepted-for-future-promotion handoff summary.
- Accepted-with-required-edits handoff summary.
- Needs-optimization handoff summary.
- Rejected-for-insufficient-evidence handoff summary.
- Blocked handoff summary.
- Duplicate handoff summary.
- Needs-more-evidence handoff summary.
- Failed-validation handoff summary.
- Unresolved follow-up flags.
- Unresolved blocker summary.
- Source traceability handoff summary.
- Failure code.
- Visible reason.

- Audit handoff input:
  - canonical handoff action
    `build_generated_case_human_review_decision_audit_handoff`;
  - `generated_case_human_review_decision_summary_export_artifact_id`;
  - source `generated_case_human_review_decision_artifact_id` values;
  - linked `generated_case_human_review_evidence_package_artifact_id` values;
  - exported decision groups, included decision artifact ids, excluded
    decision artifact ids, excluded decision artifact reasons, source
    traceability summary, ReviewHistory summary, source manifest ids, source
    hashes, failure code, and visible reason from the summary export artifact.
- Audit handoff output:
  - audit handoff artifact id when a later slice persists one;
  - artifact naming such as
    `generated_case_human_review_decision_audit_handoff`;
  - handoff filename such as
    `generated_case_human_review_decision_audit_handoff.json`;
  - handoff action
    `build_generated_case_human_review_decision_audit_handoff`;
  - handoff summary;
  - evidence chain status values such as `complete`, `incomplete`, `blocked`,
    and `failed_validation`;
  - included artifact ids;
  - excluded artifact reasons;
  - accepted-for-future-promotion handoff summary;
  - accepted-with-required-edits handoff summary;
  - needs-optimization handoff summary;
  - rejected-for-insufficient-evidence handoff summary;
  - blocked handoff summary;
  - duplicate handoff summary;
  - needs-more-evidence handoff summary;
  - failed-validation handoff summary;
  - unresolved follow-up flags;
  - unresolved blocker summary;
  - source traceability handoff summary;
  - ReviewHistory links, failure code, and visible reason.
- Safety requirements:
  - audit handoff records are evidence-chain packages, not mutation of
    summary export artifacts, decision artifacts, evidence packages,
    GeneratedCaseCandidate content, KnowledgeEvidence records, ReviewHistory,
    historical evidence, or runtime retrieval behavior;
  - accepted-for-future-promotion and accepted-with-required-edits handoff
    summaries remain future-planning labels, not runtime
    GeneratedCaseCandidate approval;
  - needs-optimization handoff summaries must not trigger the existing
    request_optimization transition;
  - evidence chain status does not approve candidates, reject candidates,
    promote TestCases, create AutomationDraft rows, assemble prompts, generate
    reports, expose download endpoints, or mark `used_knowledge=true`;
  - included artifact ids, excluded artifact reasons, unresolved blocker
    summary, unresolved follow-up flags, source hashes, and ReviewHistory
    links must remain visible instead of being filtered, deleted, or
    rewritten;
  - invalid, stale, unsafe, cross-project, unbounded,
    summary-export-missing, summary-export-invalid, summary-export-mismatched,
    decision-artifact-missing, decision-artifact-invalid,
    decision-artifact-mismatched, evidence-package-missing,
    evidence-package-mismatched, decision-label-unsupported,
    review-history-missing, source-hash-mismatched, artifact-mismatched,
    credential-required, runtime-required, provider-required,
    approval-required, optimization-required, or promotion-required input must
    fail without appending a successful audit handoff.
- Runtime boundary:
  - this slice defines generated case human review decision audit handoff
    artifact and contract semantics only;
  - it does not create runtime endpoints, render frontend pages, generate
    reports, expose export/download endpoints, approve or reject
    GeneratedCaseCandidate rows, request optimization, promote TestCases,
    create AutomationDraft rows, upload artifacts, run prompts, execute
    AITasks, call providers, run retrieval, create vector indexes, create
    embeddings, rerank, run graph jobs, invoke MCP runtime, mutate source
    evidence, or change RBAC/tenant/permission behavior.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Generated Case Human Review Decision Audit Handoff task plan | done | `if (-not (Test-Path docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md)) { exit 1 }; rg -n "Generated Case Human Review Decision Audit Handoff|generated_case_human_review_decision_audit_handoff|build_generated_case_human_review_decision_audit_handoff|generated_case_human_review_decision_summary_export_artifact_id|generated_case_human_review_decision_artifact_id|generated_case_human_review_evidence_package_artifact_id|evidence chain status|unresolved follow-up flags|source traceability handoff summary|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md; git diff --check` | pending | planning-only |
| Define Generated Case Human Review Decision Audit Handoff contracts | planned | `rg -n "Generated Case Human Review Decision Audit Handoff|generated_case_human_review_decision_audit_handoff|build_generated_case_human_review_decision_audit_handoff|generated_case_human_review_decision_summary_export_artifact_id|generated_case_human_review_decision_artifact_id|generated_case_human_review_evidence_package_artifact_id|evidence chain status|included artifact ids|excluded artifact reasons|unresolved follow-up flags|source traceability handoff summary|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md && git diff --check` | pending | contract-only |
| Add Generated Case Human Review Decision Audit Handoff golden smoke | planned | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_audit_handoff_contract_golden.py -q && git diff --check` | pending | no approval/promotion/runtime/report/export integration |
| Slice 57 completion gate | planned | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_audit_handoff_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add Generated Case Human Review Decision Audit Handoff Task Plan

Goal: Create a narrow plan for Generated Case Human Review Decision Audit
Handoff before contract edits, backend runtime APIs, frontend pages, reports,
export/download endpoints, candidate approval/rejection, request optimization,
TestCase promotion, automation drafts, provider integrations, provider SDKs,
external calls, vector infrastructure, runtime retrieval, RBAC, tenants,
permissions, or package upgrades.

Expected files:

- `docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```powershell
if (-not (Test-Path docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md)) { exit 1 }
rg -n "Generated Case Human Review Decision Audit Handoff|generated_case_human_review_decision_audit_handoff|build_generated_case_human_review_decision_audit_handoff|generated_case_human_review_decision_summary_export_artifact_id|generated_case_human_review_decision_artifact_id|generated_case_human_review_evidence_package_artifact_id|evidence chain status|unresolved follow-up flags|source traceability handoff summary|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Acceptance:

- Slice 57 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit message.
- The plan names summary export artifact linkage, source decision artifact
  linkage, evidence package artifact linkage, evidence chain status, handoff
  summaries, unresolved follow-up flags, source traceability handoff summary,
  failure behavior, artifact boundaries, and forbidden side effects.
- The plan excludes runtime APIs, frontend, provider integration, provider
  SDKs, external calls, vector database, embeddings, reranking, prompt
  execution, AITask orchestration, actual candidate approval/rejection
  mutation, request optimization mutation, TestCase promotion, automation
  draft creation, report rendering, export/download endpoints, RBAC, tenants,
  permissions, and package upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add generated case human review decision audit handoff plan
```

## Task 2: Define Generated Case Human Review Decision Audit Handoff Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future generated case human review decision audit handoff boundary
before any runtime API, frontend, report rendering, export/download endpoint,
candidate approval/rejection, request optimization, TestCase promotion,
automation draft creation, or provider/retrieval runtime behavior.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Generated Case Human Review Decision Audit Handoff|generated_case_human_review_decision_audit_handoff|build_generated_case_human_review_decision_audit_handoff|generated_case_human_review_decision_summary_export_artifact_id|generated_case_human_review_decision_artifact_id|generated_case_human_review_evidence_package_artifact_id|evidence chain status|included artifact ids|excluded artifact reasons|unresolved follow-up flags|source traceability handoff summary|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md
git diff --check
```

Acceptance:

- Contracts define generated case human review decision audit handoff inputs,
  outputs, summary export artifact linkage, decision artifact linkage,
  evidence package artifact linkage, evidence chain status, included artifact
  ids, excluded artifact reasons, unresolved follow-up flags, source
  traceability handoff summary, ReviewHistory, failure behavior, and forbidden
  side effects.
- Contracts keep backend runtime APIs, frontend, report rendering,
  export/download endpoints, provider integrations, SDKs, external calls,
  vector database, embeddings, reranking, prompt execution, candidate
  approval/rejection, request optimization, TestCase promotion, automation
  draft creation, RBAC, tenants, permissions, and package upgrades out of
  scope.
- `NEXT_AI_TASK.md` points to Task 3.

Commit message:

```text
docs(v2): define generated case human review decision audit handoff contracts
```

## Task 3: Add Generated Case Human Review Decision Audit Handoff Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving the generated case
human review decision audit handoff remains evidence-chain packaging and
cannot approve or reject candidates, request optimization, promote TestCases,
create automation drafts, render reports, expose export/download endpoints, or
create runtime/provider/retrieval behavior.

Expected files:

- `backend/app/tests/golden/test_generated_case_human_review_decision_audit_handoff_contract_golden.py`
- `docs/fixtures/45-generated-case-human-review-decision-audit-handoff-golden.md`
- `docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_audit_handoff_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names Generated Case Human Review Decision Audit Handoff,
  `generated_case_human_review_decision_audit_handoff`,
  `build_generated_case_human_review_decision_audit_handoff`, summary export
  artifact id, decision artifact id, evidence package artifact id, evidence
  chain status, included artifact ids, excluded artifact reasons, unresolved
  follow-up flags, source traceability handoff summary, ReviewHistory, failure
  behavior, and forbidden side effects.
- Golden proves no backend runtime API, frontend, report renderer,
  export/download endpoint, provider SDK, external call, vector database,
  embedding, reranking, prompt execution, candidate approval/rejection,
  request optimization mutation, TestCase promotion, automation draft
  creation, RBAC, tenants, permissions, package upgrade, or source evidence
  mutation is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 57 Completion Gate.

Commit message:

```text
test(golden): add generated case human review decision audit handoff smoke
```

## Slice 57 Completion Gate

Goal: Validate Slice 57 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_audit_handoff_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 57 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete generated case human review decision audit handoff slice
```
