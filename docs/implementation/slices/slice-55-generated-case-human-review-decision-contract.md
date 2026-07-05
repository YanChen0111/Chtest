# Slice 55: Generated Case Human Review Decision Contract Task Plan

## Goal

Define the Generated Case Human Review Decision contract after Slice 54
generated case human review evidence packages exist, but before any actual
GeneratedCaseCandidate approve/reject mutation, request optimization mutation,
TestCase promotion, AutomationDraft creation, backend runtime API, frontend
page, provider integration, provider SDK, external call, vector database,
embedding job, reranking job, graph runtime, MCP runtime, runtime retrieval,
RBAC, tenants, or permissions exist.

This slice is contract-first. It documents how Chtest may record a local
human-review decision artifact that consumes a generated case human review
evidence package while preserving candidate evidence, review findings,
dedup/readiness signals, prompt-context lineage, ReviewHistory links, failure
code, and visible reason. The decision is audit evidence only; it is not the
runtime candidate approval/rejection action.

## Product Value Answer

After this slice, Chtest can describe reviewer intent for a generated case as
auditable decision evidence before any real candidate state change. Future
planning can distinguish accepted-for-future-promotion, accepted-with-edits,
optimization-needed, rejected-for-insufficient-evidence, blocked, duplicate,
and needs-more-evidence decisions without mutating GeneratedCaseCandidate
status, creating TestCases, creating automation drafts, running prompts,
calling providers, changing retrieval behavior, or adding UI/runtime surfaces.

## Current Evidence Baseline

- Slice 54 defined
  `build_generated_case_human_review_evidence_package` and
  `generated_case_human_review_evidence_package` as human-review evidence
  packaging. The package preserves GeneratedCaseCandidate id/status,
  candidate summary, evidence chain completeness, missing/conflicting evidence
  summaries, review blocker summary, dedup/readiness summary, human review
  checklist, source hashes, source manifest ids, prompt-context lineage, and
  ReviewHistory links.
- GeneratedCaseCandidate state transitions already exist for real human review
  actions such as approve, approve_after_edit, reject, and
  request_optimization. This slice must not invoke or redefine those runtime
  transitions.
- ReviewHistory already records successful real review actions. This slice may
  link ReviewHistory evidence, but invalid decision input must not append a
  successful ReviewHistory decision.
- Prompt/skill contracts already state that agent output and review evidence
  cannot automatically promote a candidate into a TestCase.

## Non-goals

- No backend runtime API, endpoint, router, service, worker, queue, scheduler,
  migration, package upgrade, or broad GeneratedCaseCandidate CRUD.
- No frontend page, frontend store, component, report generation behavior,
  report renderer, export/download endpoint, or backend feature API.
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
- No artifact upload, Artifact mutation outside declared decision evidence,
  artifact delete, evidence package mutation, source artifact mutation, prompt
  context evidence mutation, GeneratedCaseCandidate content mutation,
  KnowledgeEvidence mutation, TestKnowledgeCard mutation, ReviewHistory
  mutation, historical evidence mutation, RBAC, tenants, or permissions.

## Contract Boundary To Define

The follow-up contract task should define:

### Decision Vocabulary

The contract should preserve these exact planning terms so Task 2 can update
the data, API, state, artifact, and prompt/skill contracts consistently:

- Generated Case Human Review Decision.
- Generated case human review evidence package artifact id.
- `generated_case_human_review_evidence_package_artifact_id`.
- GeneratedCaseCandidate id.
- Candidate status.
- Candidate summary.
- Evidence chain completeness.
- Missing evidence summary.
- Conflicting evidence summary.
- Review blocker summary.
- Dedup/readiness summary.
- Human review checklist.
- `quality_score`.
- `review_findings_json`.
- `coverage_gap_notes`.
- `automation_readiness`.
- Dedup findings.
- Duplicate candidate ids.
- Duplicate-of case id.
- Prompt context lineage artifact ids.
- Source hashes.
- Source manifest ids.
- ReviewHistory ids.
- ReviewHistory links.
- Review decision.
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
- Failure code.
- Visible reason.

- Decision input:
  - canonical decision action
    `review_generated_case_human_review_evidence_package`;
  - `generated_case_human_review_evidence_package_artifact_id`;
  - GeneratedCaseCandidate id/status and candidate summary;
  - evidence chain completeness, missing evidence summary, conflicting
    evidence summary, review blocker summary, dedup/readiness summary, human
    review checklist, `quality_score`, `review_findings_json`,
    `coverage_gap_notes`, `automation_readiness`, dedup findings, duplicate
    candidate ids, duplicate-of case id, prompt context lineage artifact ids,
    source hashes, source manifest ids, and ReviewHistory links.
- Decision output:
  - decision artifact id when a later slice persists one;
  - artifact naming such as `generated_case_human_review_decision`;
  - decision filename such as `generated_case_human_review_decision.json`;
  - review decision, decision status, reviewer label, reviewer comment,
    accepted constraints, requested edit fields, optimization request summary,
    rejection reasons, blocker reasons, duplicate resolution notes,
    ReviewHistory links, failure code, and visible reason.
- Safety requirements:
  - decision records are audit evidence only, not runtime candidate approval,
    rejection, optimization request, TestCase promotion, automation draft
    creation, prompt execution, provider execution, retrieval execution,
    report generation, or UI rendering;
  - `accepted_for_future_promotion` and `accepted_with_required_edits` remain
    future planning labels, not actual GeneratedCaseCandidate approval;
  - `needs_optimization` in this decision contract is evidence only and must
    not trigger the existing request_optimization transition;
  - `duplicate` and `rejected_for_insufficient_evidence` decisions must not
    hide, merge, archive, reject, or delete candidates;
  - decision input must not rewrite the Slice 54 evidence package, source
    evidence, prompt-context artifacts, ReviewHistory, or candidate content;
  - invalid, missing, stale, unsafe, cross-project, unbounded,
    evidence-package-missing, evidence-package-invalid, candidate-missing,
    candidate-mismatched, candidate-status-invalid, review-decision-missing,
    review-decision-invalid, reviewer-missing, quality-score-missing,
    review-findings-missing, dedup-inconclusive, readiness-unknown,
    review-history-missing, artifact-mismatched, source-hash-mismatched,
    credential-required, runtime-required, provider-required,
    approval-required, or promotion-required input must fail without appending
    a successful decision artifact.
- Runtime boundary:
  - this slice defines generated case human review decision artifact and
    contract semantics only;
  - it does not create runtime endpoints, render frontend pages, approve or
    reject GeneratedCaseCandidate rows, request optimization, promote
    TestCases, create AutomationDraft rows, upload artifacts, run prompts,
    execute AITasks, call providers, run retrieval, create vector indexes,
    create embeddings, rerank, run graph jobs, invoke MCP runtime, mutate
    source evidence, or change RBAC/tenant/permission behavior.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Generated Case Human Review Decision task plan | done | `if (-not (Test-Path docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md)) { exit 1 }; rg -n "Generated Case Human Review Decision|generated_case_human_review_decision|review_generated_case_human_review_evidence_package|generated_case_human_review_evidence_package_artifact_id|accepted_for_future_promotion|accepted_with_required_edits|needs_optimization|rejected_for_insufficient_evidence|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md; git diff --check` | `bd26296` | planning-only |
| Define Generated Case Human Review Decision contracts | done | `rg -n "Generated Case Human Review Decision|generated_case_human_review_decision|review_generated_case_human_review_evidence_package|generated_case_human_review_evidence_package_artifact_id|accepted_for_future_promotion|accepted_with_required_edits|needs_optimization|rejected_for_insufficient_evidence|blocked|duplicate|needs_more_evidence|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md && git diff --check` | `cb533a6` | contract-only |
| Add Generated Case Human Review Decision golden smoke | done | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_contract_golden.py -q && git diff --check` | `781041a` | no approval/promotion/runtime integration |
| Slice 55 completion gate | done | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add Generated Case Human Review Decision Task Plan

Goal: Create a narrow plan for Generated Case Human Review Decision before
contract edits, backend runtime APIs, frontend pages, candidate
approval/rejection, request optimization, TestCase promotion, automation
drafts, provider integrations, provider SDKs, external calls, vector
infrastructure, runtime retrieval, RBAC, tenants, permissions, or package
upgrades.

Expected files:

- `docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```powershell
if (-not (Test-Path docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md)) { exit 1 }
rg -n "Generated Case Human Review Decision|generated_case_human_review_decision|review_generated_case_human_review_evidence_package|generated_case_human_review_evidence_package_artifact_id|accepted_for_future_promotion|accepted_with_required_edits|needs_optimization|rejected_for_insufficient_evidence|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Acceptance:

- Slice 55 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit message.
- The plan names evidence package artifact linkage, GeneratedCaseCandidate
  id/status, candidate summary, evidence chain completeness,
  missing/conflicting evidence summaries, review blocker summary,
  dedup/readiness summary, human review checklist, decision labels, reviewer
  label/comment, accepted constraints, requested edit fields, optimization
  request summary, rejection/blocker reasons, duplicate resolution notes,
  ReviewHistory, failure behavior, artifact boundaries, and forbidden side
  effects.
- The plan excludes runtime APIs, frontend, provider integration, provider
  SDKs, external calls, vector database, embeddings, reranking, prompt
  execution, AITask orchestration, actual candidate approval/rejection
  mutation, request optimization mutation, TestCase promotion, automation
  draft creation, artifact upload, RBAC, tenants, permissions, and package
  upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add generated case human review decision plan
```

## Task 2: Define Generated Case Human Review Decision Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future generated case human review decision boundary before any
runtime API, frontend, candidate approval/rejection, request optimization,
TestCase promotion, automation draft creation, or provider/retrieval runtime
behavior.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Generated Case Human Review Decision|generated_case_human_review_decision|review_generated_case_human_review_evidence_package|generated_case_human_review_evidence_package_artifact_id|accepted_for_future_promotion|accepted_with_required_edits|needs_optimization|rejected_for_insufficient_evidence|blocked|duplicate|needs_more_evidence|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md
git diff --check
```

Acceptance:

- Contracts define generated case human review decision inputs, outputs,
  evidence package linkage, decision labels, reviewer label/comment, accepted
  constraints, requested edit fields, optimization request summary,
  rejection/blocker reasons, duplicate resolution notes, ReviewHistory,
  failure behavior, and forbidden side effects.
- Contracts keep backend runtime APIs, frontend, provider integrations, SDKs,
  external calls, vector database, embeddings, reranking, prompt execution,
  candidate approval/rejection, request optimization, TestCase promotion,
  automation draft creation, RBAC, tenants, permissions, and package upgrades
  out of scope.
- `NEXT_AI_TASK.md` points to Task 3.

Commit message:

```text
docs(v2): define generated case human review decision contracts
```

## Task 3: Add Generated Case Human Review Decision Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving the generated case
human review decision remains decision evidence and cannot approve or reject
candidates, request optimization, promote TestCases, create automation drafts,
or create runtime/provider/retrieval behavior.

Expected files:

- `backend/app/tests/golden/test_generated_case_human_review_decision_contract_golden.py`
- `docs/fixtures/43-generated-case-human-review-decision-golden.md`
- `docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names Generated Case Human Review Decision,
  `generated_case_human_review_decision`,
  `review_generated_case_human_review_evidence_package`, evidence package
  artifact id, decision labels, reviewer label/comment, requested edit fields,
  optimization request summary, rejection/blocker reasons, duplicate
  resolution notes, ReviewHistory, failure behavior, and forbidden side
  effects.
- Golden proves no backend runtime API, frontend, provider SDK, external call,
  vector database, embedding, reranking, prompt execution, candidate
  approval/rejection, request optimization mutation, TestCase promotion,
  automation draft creation, RBAC, tenants, permissions, package upgrade, or
  source evidence mutation is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 55 Completion Gate.

Commit message:

```text
test(golden): add generated case human review decision smoke
```

## Slice 55 Completion Gate

Goal: Validate Slice 55 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 55 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete generated case human review decision slice
```
