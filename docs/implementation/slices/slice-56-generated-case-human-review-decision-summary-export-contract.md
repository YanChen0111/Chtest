# Slice 56: Generated Case Human Review Decision Summary Export Contract Task Plan

## Goal

Define the Generated Case Human Review Decision Summary Export contract after
Slice 55 generated case human review decision artifacts exist, but before any
actual GeneratedCaseCandidate approve/reject mutation, request optimization
mutation, TestCase promotion, AutomationDraft creation, backend runtime API,
frontend page, report generation behavior, export/download endpoint, provider
integration, provider SDK, external call, vector database, embedding job,
reranking job, graph runtime, MCP runtime, runtime retrieval, RBAC, tenants,
or permissions exist.

This slice is contract-first. It documents how Chtest may package one or more
generated case human review decision artifacts into a bounded summary export
artifact while preserving decision labels, reviewer notes, requested edits,
optimization requests, rejection/blocker reasons, duplicate notes,
ReviewHistory links, source traceability, failure code, and visible reason.
The summary export is audit evidence only; it is not a runtime report,
download endpoint, approval batch, rejection batch, optimization request, or
TestCase promotion workflow.

## Product Value Answer

After this slice, Chtest can describe generated-case human review outcomes in
one compact summary export artifact before any real candidate state change.
Future planning can group accepted-for-future-promotion,
accepted-with-required-edits, needs-optimization,
rejected-for-insufficient-evidence, blocked, duplicate, needs-more-evidence,
and failed-validation decision evidence without mutating
GeneratedCaseCandidate status, creating TestCases, creating automation drafts,
running prompts, calling providers, changing retrieval behavior, rendering
reports, exposing export/download endpoints, or adding UI/runtime surfaces.

## Current Evidence Baseline

- Slice 54 defined
  `build_generated_case_human_review_evidence_package` and
  `generated_case_human_review_evidence_package` as human-review evidence
  packaging. The package preserves GeneratedCaseCandidate id/status,
  candidate summary, evidence chain completeness, missing/conflicting evidence
  summaries, review blocker summary, dedup/readiness summary, human review
  checklist, prompt-context lineage, source hashes, source manifest ids, and
  ReviewHistory links.
- Slice 55 defined
  `review_generated_case_human_review_evidence_package` and
  `generated_case_human_review_decision` as human-review decision evidence.
  The decision preserves `generated_case_human_review_evidence_package_artifact_id`,
  decision label/status, reviewer label/comment, accepted constraints,
  requested edit fields, optimization request summary, rejection/blocker
  reasons, duplicate resolution notes, ReviewHistory links, failure code, and
  visible reason.
- GeneratedCaseCandidate state transitions already exist for real human review
  actions such as approve, approve_after_edit, reject, and
  request_optimization. This slice must not invoke or redefine those runtime
  transitions.
- ReviewHistory already records successful real review actions. This slice may
  link ReviewHistory evidence, but invalid summary export input must not
  append a successful ReviewHistory decision or mutate historical review
  evidence.

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
- No artifact upload, Artifact mutation outside declared summary export
  evidence, artifact delete, decision artifact mutation, evidence package
  mutation, source artifact mutation, prompt context evidence mutation,
  GeneratedCaseCandidate content mutation, KnowledgeEvidence mutation,
  TestKnowledgeCard mutation, ReviewHistory mutation, historical evidence
  mutation, RBAC, tenants, or permissions.

## Contract Boundary To Define

The follow-up contract task should define:

### Summary Export Vocabulary

The contract should preserve these exact planning terms so Task 2 can update
the data, API, state, artifact, and prompt/skill contracts consistently:

- Generated Case Human Review Decision Summary Export.
- Generated case human review decision artifact id.
- `generated_case_human_review_decision_artifact_id`.
- Generated case human review evidence package artifact id.
- `generated_case_human_review_evidence_package_artifact_id`.
- GeneratedCaseCandidate id.
- Candidate status.
- Candidate summary.
- Decision label.
- Decision status.
- Decision labels:
  `accepted_for_future_promotion`, `accepted_with_required_edits`,
  `needs_optimization`, `rejected_for_insufficient_evidence`, `blocked`,
  `duplicate`, `needs_more_evidence`, and `failed_validation`.
- Reviewer label.
- Reviewer comment.
- Accepted constraints.
- Requested edit fields.
- Optimization request summary.
- Rejection reasons.
- Blocker reasons.
- Duplicate resolution notes.
- ReviewHistory ids.
- ReviewHistory links.
- Source hashes.
- Source manifest ids.
- Summary export artifact id.
- Exported decision groups.
- Accepted-for-future-promotion summary.
- Accepted-with-required-edits summary.
- Needs-optimization summary.
- Rejected-for-insufficient-evidence summary.
- Blocked summary.
- Duplicate summary.
- Needs-more-evidence summary.
- Failed-validation summary.
- Included decision artifact ids.
- Excluded decision artifact ids.
- Excluded decision artifact reasons.
- Source traceability summary.
- Failure code.
- Visible reason.

- Summary export input:
  - canonical summary export action
    `build_generated_case_human_review_decision_summary_export`;
  - one or more `generated_case_human_review_decision_artifact_id` values;
  - each decision's
    `generated_case_human_review_evidence_package_artifact_id`;
  - GeneratedCaseCandidate id/status and candidate summary;
  - review decision, decision label, decision status, reviewer label,
    reviewer comment, accepted constraints, requested edit fields,
    optimization request summary, rejection reasons, blocker reasons,
    duplicate resolution notes, ReviewHistory links, source hashes, and source
    manifest ids.
- Summary export output:
  - summary export artifact id when a later slice persists one;
  - artifact naming such as
    `generated_case_human_review_decision_summary_export`;
  - summary filename such as
    `generated_case_human_review_decision_summary_export.json`;
  - summary action
    `build_generated_case_human_review_decision_summary_export`;
  - summary status values such as `not_exported`,
    `exported_for_human_review_audit`, and `failed_validation`;
  - exported decision groups for `accepted_for_future_promotion`,
    `accepted_with_required_edits`, `needs_optimization`,
    `rejected_for_insufficient_evidence`, `blocked`, `duplicate`,
    `needs_more_evidence`, and `failed_validation`;
  - accepted-for-future-promotion summary,
    accepted-with-required-edits summary, needs-optimization summary,
    rejected-for-insufficient-evidence summary, blocked summary, duplicate
    summary, needs-more-evidence summary, failed-validation summary, included
    decision artifact ids, excluded decision artifact ids, excluded decision
    artifact reasons, source traceability summary, ReviewHistory summary,
    failure code, and visible reason.
- Summary export behavior:
  - summary exports are audit evidence only and must not approve or reject
    candidates;
  - accepted-for-future-promotion and accepted-with-required-edits summaries
    remain future planning labels, not runtime GeneratedCaseCandidate
    approval;
  - needs-optimization summaries must preserve optimization request summary
    but must not trigger the existing request_optimization transition;
  - rejected-for-insufficient-evidence, blocked, duplicate, and
    needs-more-evidence summaries must preserve visible reasons and must not
    hide, merge, archive, reject, or delete candidates;
  - failed-validation summaries must preserve failure code and visible reason;
  - summary export input must not rewrite decision artifacts, evidence
    packages, source evidence, prompt-context artifacts, ReviewHistory, or
    candidate content;
  - summary export means a stored evidence artifact contract, not a report
    generator, frontend page, or export/download endpoint.
- Failure behavior:
  - missing, stale, unsafe, cross-project, unbounded,
    decision-artifact-missing, decision-artifact-invalid,
    decision-artifact-mismatched, evidence-package-missing,
    evidence-package-mismatched, candidate-missing, candidate-mismatched,
    candidate-status-invalid, review-decision-missing,
    review-decision-invalid, decision-label-unsupported,
    reviewer-missing, source-hash-mismatched, review-history-missing,
    artifact-mismatched, summary-export-invalid, credential-required,
    runtime-required, provider-required, approval-required,
    optimization-required, or promotion-required input must produce a failure
    code and visible reason and must not append a successful summary export.
- Runtime boundary:
  - this slice defines generated case human review decision summary export
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
| Add Generated Case Human Review Decision Summary Export task plan | done | `if (-not (Test-Path docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md)) { exit 1 }; rg -n "Generated Case Human Review Decision Summary Export|generated_case_human_review_decision_summary_export|build_generated_case_human_review_decision_summary_export|generated_case_human_review_decision_artifact_id|accepted_for_future_promotion|accepted_with_required_edits|needs_optimization|rejected_for_insufficient_evidence|blocked|duplicate|needs_more_evidence|failed_validation|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md; git diff --check` | pending | planning-only |
| Define Generated Case Human Review Decision Summary Export contracts | planned | `rg -n "Generated Case Human Review Decision Summary Export|generated_case_human_review_decision_summary_export|build_generated_case_human_review_decision_summary_export|generated_case_human_review_decision_artifact_id|generated_case_human_review_evidence_package_artifact_id|exported decision groups|included decision artifact ids|excluded decision artifact reasons|source traceability summary|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md && git diff --check` | pending | contract-only |
| Add Generated Case Human Review Decision Summary Export golden smoke | planned | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_summary_export_contract_golden.py -q && git diff --check` | pending | no approval/promotion/runtime/report/export integration |
| Slice 56 completion gate | planned | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_summary_export_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add Generated Case Human Review Decision Summary Export Task Plan

Goal: Create a narrow plan for Generated Case Human Review Decision Summary
Export before contract edits, backend runtime APIs, frontend pages, reports,
export/download endpoints, candidate approval/rejection, request optimization,
TestCase promotion, automation drafts, provider integrations, provider SDKs,
external calls, vector infrastructure, runtime retrieval, RBAC, tenants,
permissions, or package upgrades.

Expected files:

- `docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```powershell
if (-not (Test-Path docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md)) { exit 1 }
rg -n "Generated Case Human Review Decision Summary Export|generated_case_human_review_decision_summary_export|build_generated_case_human_review_decision_summary_export|generated_case_human_review_decision_artifact_id|accepted_for_future_promotion|accepted_with_required_edits|needs_optimization|rejected_for_insufficient_evidence|blocked|duplicate|needs_more_evidence|failed_validation|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Acceptance:

- Slice 56 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit message.
- The plan names decision artifact linkage, evidence package artifact linkage,
  decision labels, exported decision groups, included/excluded decision
  artifact ids, source traceability summary, failure behavior, artifact
  boundaries, and forbidden side effects.
- The plan excludes runtime APIs, frontend, provider integration, provider
  SDKs, external calls, vector database, embeddings, reranking, prompt
  execution, AITask orchestration, actual candidate approval/rejection
  mutation, request optimization mutation, TestCase promotion, automation
  draft creation, report rendering, export/download endpoints, RBAC, tenants,
  permissions, and package upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add generated case human review decision summary export plan
```

## Task 2: Define Generated Case Human Review Decision Summary Export Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future generated case human review decision summary export boundary
before any runtime API, frontend, report rendering, export/download endpoint,
candidate approval/rejection, request optimization, TestCase promotion,
automation draft creation, or provider/retrieval runtime behavior.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Generated Case Human Review Decision Summary Export|generated_case_human_review_decision_summary_export|build_generated_case_human_review_decision_summary_export|generated_case_human_review_decision_artifact_id|generated_case_human_review_evidence_package_artifact_id|exported decision groups|included decision artifact ids|excluded decision artifact reasons|source traceability summary|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md
git diff --check
```

Acceptance:

- Contracts define generated case human review decision summary export inputs,
  outputs, decision artifact linkage, evidence package artifact linkage,
  exported decision groups, included/excluded decision artifact ids, source
  traceability summary, ReviewHistory, failure behavior, and forbidden side
  effects.
- Contracts keep backend runtime APIs, frontend, report rendering,
  export/download endpoints, provider integrations, SDKs, external calls,
  vector database, embeddings, reranking, prompt execution, candidate
  approval/rejection, request optimization, TestCase promotion, automation
  draft creation, RBAC, tenants, permissions, and package upgrades out of
  scope.
- `NEXT_AI_TASK.md` points to Task 3.

Commit message:

```text
docs(v2): define generated case human review decision summary export contracts
```

## Task 3: Add Generated Case Human Review Decision Summary Export Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving the generated case
human review decision summary export remains audit evidence and cannot approve
or reject candidates, request optimization, promote TestCases, create
automation drafts, render reports, expose export/download endpoints, or create
runtime/provider/retrieval behavior.

Expected files:

- `backend/app/tests/golden/test_generated_case_human_review_decision_summary_export_contract_golden.py`
- `docs/fixtures/44-generated-case-human-review-decision-summary-export-golden.md`
- `docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_summary_export_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names Generated Case Human Review Decision Summary Export,
  `generated_case_human_review_decision_summary_export`,
  `build_generated_case_human_review_decision_summary_export`, decision
  artifact id, evidence package artifact id, decision labels, exported
  decision groups, included/excluded decision artifact ids, source
  traceability summary, ReviewHistory, failure behavior, and forbidden side
  effects.
- Golden proves no backend runtime API, frontend, report renderer,
  export/download endpoint, provider SDK, external call, vector database,
  embedding, reranking, prompt execution, candidate approval/rejection,
  request optimization mutation, TestCase promotion, automation draft
  creation, RBAC, tenants, permissions, package upgrade, or source evidence
  mutation is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 56 Completion Gate.

Commit message:

```text
test(golden): add generated case human review decision summary export smoke
```

## Slice 56 Completion Gate

Goal: Validate Slice 56 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_summary_export_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 56 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete generated case human review decision summary export slice
```
