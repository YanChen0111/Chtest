# Slice 58: Generated Case Human Review Decision Application Preflight Contract Task Plan

## Goal

Define the Generated Case Human Review Decision Application Preflight contract
after Slice 57 generated case human review decision audit handoff evidence
exists, but before any actual GeneratedCaseCandidate approve/reject mutation,
request optimization mutation, TestCase promotion, AutomationDraft creation,
backend runtime API, frontend page, report generation behavior,
export/download endpoint, provider integration, provider SDK, external call,
vector database, embedding job, reranking job, graph runtime, MCP runtime,
runtime retrieval, RBAC, tenants, or permissions exist.

This slice is contract-first. It documents how Chtest may preflight whether
an audit handoff is eligible to drive a future real GeneratedCaseCandidate
review action while preserving audit handoff linkage, summary export linkage,
source decision artifacts, evidence package lineage, decision-label mapping,
candidate status, requested edit fields, accepted constraints, optimization
request summaries, rejection reasons, blocker reasons, duplicate resolution
notes, evidence chain status, unresolved follow-up flags, source traceability,
ReviewHistory handoff links, failure code, and visible reason. The preflight
is eligibility evidence only; it is not the review action itself, a status
mutation, approval batch, rejection batch, optimization request, TestCase
promotion workflow, runtime report, or download endpoint.

## Product Value Answer

After this slice, Chtest can describe the guardrail between audit handoff
evidence and the existing real GeneratedCaseCandidate review actions. Future
planning can prove which candidates are eligible or ineligible for a mapped
review action from the handoff without approving candidates, rejecting
candidates, requesting optimization, creating TestCases, creating automation
drafts, running prompts, calling providers, changing retrieval behavior,
rendering reports, exposing export/download endpoints, or adding UI/runtime
surfaces.

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
  artifact ids, source traceability summary, ReviewHistory summary, failure
  code, and visible reason.
- Slice 57 defined
  `build_generated_case_human_review_decision_audit_handoff` and
  `generated_case_human_review_decision_audit_handoff` as evidence-chain
  handoff packaging with evidence chain status, included artifact ids,
  excluded artifact reasons, decision-label handoff summaries, unresolved
  follow-up flags, unresolved blocker summary, source traceability handoff
  summary, ReviewHistory links, failure code, and visible reason.
- Existing runtime `case-review` actions can approve, approve after edit,
  reject, or mark needs optimization. This slice must not invoke, wrap, or
  redefine those runtime actions.
- ReviewHistory already records successful real review actions. This slice may
  link ReviewHistory evidence, but invalid preflight input must not append a
  successful ReviewHistory decision or mutate historical review evidence.

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
- No artifact upload, Artifact mutation outside declared preflight evidence,
  artifact delete, audit handoff artifact mutation, summary export artifact
  mutation, decision artifact mutation, evidence package mutation, source
  artifact mutation, prompt context evidence mutation, GeneratedCaseCandidate
  content mutation, TestCase mutation, KnowledgeEvidence mutation,
  TestKnowledgeCard mutation, ReviewHistory mutation, historical evidence
  mutation, RBAC, tenants, or permissions.

## Contract Boundary To Define

The follow-up contract task should define:

### Application Preflight Vocabulary

The contract should preserve these exact planning terms so Task 2 can update
the data, API, state, artifact, and prompt/skill contracts consistently:

- Generated Case Human Review Decision Application Preflight.
- Generated case human review decision audit handoff artifact id.
- `generated_case_human_review_decision_audit_handoff_artifact_id`.
- Generated case human review decision summary export artifact id.
- `generated_case_human_review_decision_summary_export_artifact_id`.
- Generated case human review decision artifact ids.
- `generated_case_human_review_decision_artifact_id`.
- Generated case human review evidence package artifact ids.
- `generated_case_human_review_evidence_package_artifact_id`.
- GeneratedCaseCandidate id.
- Candidate status.
- Decision label.
- Mapped review action.
- Eligibility status.
- Eligible candidate ids.
- Ineligible candidate ids.
- Blocked action reasons.
- Required edit summary.
- Required human confirmation summary.
- Accepted constraints.
- Requested edit fields.
- Optimization request summary.
- Rejection reasons.
- Blocker reasons.
- Duplicate resolution notes.
- Evidence chain status.
- Unresolved follow-up flags.
- Unresolved blocker summary.
- ReviewHistory handoff links.
- Source traceability handoff summary.
- Preflight artifact id.
- Preflight summary.
- Failure code.
- Visible reason.

- Application preflight input:
  - canonical preflight action
    `preflight_generated_case_human_review_decision_application`;
  - `generated_case_human_review_decision_audit_handoff_artifact_id`;
  - `generated_case_human_review_decision_summary_export_artifact_id`;
  - source `generated_case_human_review_decision_artifact_id` values;
  - linked `generated_case_human_review_evidence_package_artifact_id` values;
  - GeneratedCaseCandidate id/status, decision label, requested edit fields,
    accepted constraints, optimization request summary, rejection reasons,
    blocker reasons, duplicate resolution notes, evidence chain status,
    unresolved follow-up flags, unresolved blocker summary, source
    traceability handoff summary, ReviewHistory handoff links, source hashes,
    source manifest ids, failure code, and visible reason from the audit
    handoff.
- Application preflight output:
  - preflight artifact id when a later slice persists one;
  - artifact naming such as
    `generated_case_human_review_decision_application_preflight`;
  - preflight filename such as
    `generated_case_human_review_decision_application_preflight.json`;
  - preflight action
    `preflight_generated_case_human_review_decision_application`;
  - preflight summary;
  - eligibility status values such as `eligible`, `ineligible`, `blocked`,
    and `failed_validation`;
  - mapped review action values such as `approve`, `approve_after_edit`,
    `request_optimization`, `reject`, and `none`;
  - eligible candidate ids;
  - ineligible candidate ids;
  - blocked action reasons;
  - required edit summary;
  - required human confirmation summary;
  - accepted-for-future-promotion preflight summary;
  - accepted-with-required-edits preflight summary;
  - needs-optimization preflight summary;
  - rejected-for-insufficient-evidence preflight summary;
  - blocked preflight summary;
  - duplicate preflight summary;
  - needs-more-evidence preflight summary;
  - failed-validation preflight summary;
  - ReviewHistory handoff links, source traceability handoff summary, failure
    code, and visible reason.
- Decision-label mapping behavior:
  - `accepted_for_future_promotion` may map to future `approve` only when the
    evidence chain status is complete, candidate status is reviewable, and
    required human confirmation remains explicit;
  - `accepted_with_required_edits` may map to future `approve_after_edit` only
    when requested edit fields are present and bounded;
  - `needs_optimization` may map to future `request_optimization` only when
    optimization request summary is present and bounded;
  - `rejected_for_insufficient_evidence` may map to future `reject` only when
    rejection reasons and visible reason are present;
  - `blocked`, `duplicate`, `needs_more_evidence`, and `failed_validation`
    must map to `none` and remain ineligible until a later explicit human
    action resolves them.
- Safety requirements:
  - preflight records are eligibility evidence, not mutation of audit handoff
    artifacts, summary export artifacts, decision artifacts, evidence
    packages, GeneratedCaseCandidate content/status, TestCase rows,
    KnowledgeEvidence records, ReviewHistory, historical evidence, or runtime
    retrieval behavior;
  - eligible candidate ids do not approve candidates, reject candidates,
    request optimization, promote TestCases, create AutomationDraft rows,
    assemble prompts, generate reports, expose download endpoints, or mark
    `used_knowledge=true`;
  - required human confirmation summary must remain visible for every eligible
    mapped review action;
  - ineligible candidate ids, blocked action reasons, unresolved blocker
    summary, unresolved follow-up flags, source hashes, and ReviewHistory
    handoff links must remain visible instead of being filtered, deleted, or
    rewritten;
  - invalid, stale, unsafe, cross-project, unbounded,
    audit-handoff-missing, audit-handoff-invalid, audit-handoff-mismatched,
    summary-export-missing, summary-export-invalid,
    summary-export-mismatched, decision-artifact-missing,
    decision-artifact-invalid, decision-artifact-mismatched,
    evidence-package-missing, evidence-package-mismatched, candidate-missing,
    candidate-mismatched, candidate-status-invalid,
    decision-label-unsupported, mapped-action-unsupported,
    required-edit-missing, required-confirmation-missing,
    review-history-missing, source-hash-mismatched, artifact-mismatched,
    credential-required, runtime-required, provider-required,
    approval-required, optimization-required, or promotion-required input must
    fail without appending a successful preflight.
- Runtime boundary:
  - this slice defines generated case human review decision application
    preflight artifact and contract semantics only;
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
| Add Generated Case Human Review Decision Application Preflight task plan | done | See Task 1 verification command | fe749e6 | planning-only |
| Define Generated Case Human Review Decision Application Preflight contracts | done | See Task 2 verification command | a5b385f | contract-only |
| Add Generated Case Human Review Decision Application Preflight golden smoke | done | See Task 3 verification command | pending | no approval/promotion/runtime/report/export integration |
| Slice 58 completion gate | planned | See completion gate verification command | pending | docs and handoff |

## Task 1: Add Generated Case Human Review Decision Application Preflight Task Plan

Goal: Create a narrow plan for Generated Case Human Review Decision
Application Preflight before contract edits, backend runtime APIs, frontend
pages, reports, export/download endpoints, candidate approval/rejection,
request optimization, TestCase promotion, automation drafts, provider
integrations, provider SDKs, external calls, vector infrastructure, runtime
retrieval, RBAC, tenants, permissions, or package upgrades.

Expected files:

- `docs/implementation/slices/slice-58-generated-case-human-review-decision-application-preflight-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```powershell
if (-not (Test-Path docs/implementation/slices/slice-58-generated-case-human-review-decision-application-preflight-contract.md)) { exit 1 }
rg -n "Generated Case Human Review Decision Application Preflight|generated_case_human_review_decision_application_preflight|preflight_generated_case_human_review_decision_application|generated_case_human_review_decision_audit_handoff_artifact_id|mapped review action|eligibility status|eligible candidate ids|ineligible candidate ids|blocked action reasons|required edit summary|required human confirmation summary|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-58-generated-case-human-review-decision-application-preflight-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Acceptance:

- Slice 58 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit message.
- The plan names audit handoff artifact linkage, summary export artifact
  linkage, decision artifact linkage, evidence package artifact linkage,
  mapped review action, eligibility status, eligible candidate ids,
  ineligible candidate ids, blocked action reasons, required edit summary,
  required human confirmation summary, ReviewHistory handoff links, failure
  behavior, artifact boundaries, and forbidden side effects.
- The plan excludes runtime APIs, frontend, provider integration, provider
  SDKs, external calls, vector database, embeddings, reranking, prompt
  execution, AITask orchestration, actual candidate approval/rejection
  mutation, request optimization mutation, TestCase promotion, automation
  draft creation, report rendering, export/download endpoints, RBAC, tenants,
  permissions, and package upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add generated case human review decision application preflight plan
```

## Task 2: Define Generated Case Human Review Decision Application Preflight Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future generated case human review decision application preflight
boundary before any runtime API, frontend, report rendering, export/download
endpoint, candidate approval/rejection, request optimization, TestCase
promotion, automation draft creation, or provider/retrieval runtime behavior.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-58-generated-case-human-review-decision-application-preflight-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Generated Case Human Review Decision Application Preflight|generated_case_human_review_decision_application_preflight|preflight_generated_case_human_review_decision_application|generated_case_human_review_decision_audit_handoff_artifact_id|generated_case_human_review_decision_summary_export_artifact_id|generated_case_human_review_decision_artifact_id|generated_case_human_review_evidence_package_artifact_id|mapped review action|eligibility status|eligible candidate ids|ineligible candidate ids|blocked action reasons|required edit summary|required human confirmation summary|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-58-generated-case-human-review-decision-application-preflight-contract.md
git diff --check
```

Acceptance:

- Contracts define generated case human review decision application preflight
  inputs, outputs, audit handoff artifact linkage, summary export artifact
  linkage, decision artifact linkage, evidence package artifact linkage,
  mapped review action, eligibility status, eligible candidate ids,
  ineligible candidate ids, blocked action reasons, required edit summary,
  required human confirmation summary, ReviewHistory handoff links, failure
  behavior, and forbidden side effects.
- Contracts keep backend runtime APIs, frontend, report rendering,
  export/download endpoints, provider integrations, SDKs, external calls,
  vector database, embeddings, reranking, prompt execution, candidate
  approval/rejection, request optimization, TestCase promotion, automation
  draft creation, RBAC, tenants, permissions, and package upgrades out of
  scope.
- `NEXT_AI_TASK.md` points to Task 3.

Commit message:

```text
docs(v2): define generated case human review decision application preflight contracts
```

## Task 3: Add Generated Case Human Review Decision Application Preflight Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving the generated case
human review decision application preflight remains eligibility evidence and
cannot approve or reject candidates, request optimization, promote TestCases,
create automation drafts, render reports, expose export/download endpoints, or
create runtime/provider/retrieval behavior.

Expected files:

- `backend/app/tests/golden/test_generated_case_human_review_decision_application_preflight_contract_golden.py`
- `docs/fixtures/46-generated-case-human-review-decision-application-preflight-golden.md`
- `docs/implementation/slices/slice-58-generated-case-human-review-decision-application-preflight-contract.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_application_preflight_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names Generated Case Human Review Decision Application Preflight,
  `generated_case_human_review_decision_application_preflight`,
  `preflight_generated_case_human_review_decision_application`, audit handoff
  artifact id, summary export artifact id, decision artifact id, evidence
  package artifact id, mapped review action, eligibility status, eligible
  candidate ids, ineligible candidate ids, blocked action reasons, required
  edit summary, required human confirmation summary, ReviewHistory handoff
  links, failure behavior, and forbidden side effects.
- Golden proves no backend runtime API, frontend, report renderer,
  export/download endpoint, provider SDK, external call, vector database,
  embedding, reranking, prompt execution, candidate approval/rejection,
  request optimization mutation, TestCase promotion, automation draft
  creation, RBAC, tenants, permissions, package upgrade, or source evidence
  mutation is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 58 Completion Gate.

Commit message:

```text
test(golden): add generated case human review decision application preflight smoke
```

## Slice 58 Completion Gate

Goal: Validate Slice 58 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-58-generated-case-human-review-decision-application-preflight-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_application_preflight_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 58 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete generated case human review decision application preflight slice
```
