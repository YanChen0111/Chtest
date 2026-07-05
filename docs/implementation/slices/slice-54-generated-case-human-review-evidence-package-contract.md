# Slice 54: Generated Case Human Review Evidence Package Contract Task Plan

## Goal

Define the Generated Case Human Review Evidence Package contract after
GeneratedCaseCandidate evidence fields, prompt-context evidence contracts,
CaseReviewAgent findings, dedup findings, automation readiness signals, and
ReviewHistory exist, but before any new runtime API, frontend page,
automation draft creation, TestCase promotion, GeneratedCaseCandidate
approve/reject mutation, provider integration, provider SDK, external call,
vector database, embedding job, reranking job, graph runtime, MCP runtime,
runtime retrieval, RBAC, tenants, or permissions exist.

This slice is contract-first. It documents how Chtest may package a generated
case candidate and its review evidence into one human-review evidence bundle
while preserving source knowledge evidence ids, display evidence refs,
quality score, review findings, coverage gap notes, automation readiness,
dedup findings, prompt-context evidence lineage, ReviewHistory, failure code,
and visible reason.

## Product Value Answer

After this slice, Chtest can describe the evidence a human reviewer should see
before approving, rejecting, requesting optimization, or later promoting a
GeneratedCaseCandidate. The package keeps candidate content, knowledge
evidence, prompt-context evidence, review findings, dedup/readiness signals,
missing/conflicting evidence, and ReviewHistory visible without approving or
rejecting candidates, creating TestCases, creating automation drafts, running
prompts, calling providers, changing retrieval behavior, or adding UI/runtime
surfaces.

## Current Evidence Baseline

- The GeneratedCaseCandidate data contract already includes
  `source_knowledge_evidence_ids`, `knowledge_evidence_refs_json`,
  `automation_readiness`, `quality_score`, `review_findings_json`,
  `coverage_gap_notes`, `duplicate_of_case_id`, status, and human review
  comment fields.
- Data rules state that `quality_score` is review evidence only and must not
  auto-approve a candidate or create a TestCase.
- API rules return candidate evidence fields with safe defaults and state that
  `source_knowledge_evidence_ids`, `knowledge_evidence_refs`, `quality_score`,
  `review_findings`, and `coverage_gap_notes` must not create TestCase rows,
  approve candidates, execute automation, generate reports, run retrieval,
  index vectors, create embeddings, run graph jobs, call external providers,
  mutate artifacts, invoke MCP runtime, or call remote CI providers.
- Agent workflow contracts define CaseReviewAgent, DedupAgent, and
  AutomationReadinessAgent outputs as evidence only. Human review remains
  mandatory before candidate approval, rejection, optimization decisions, or
  TestCase creation.
- Prior prompt-context slices define evidence/consumption/audit/discrepancy
  handoff artifacts that can be referenced by a future evidence package
  without mutating prompt context evidence or changing `used_knowledge`.

## Non-goals

- No backend runtime API, endpoint, router, service, worker, queue, scheduler,
  migration, package upgrade, or broad GeneratedCaseCandidate CRUD.
- No frontend page, frontend store, component, report generation behavior,
  report renderer, export/download endpoint, or backend feature API.
- No provider integration, provider SDK, external call, credential handling,
  OAuth, remote URL fetch, vector database, vector index, embedding model,
  embedding service, embedding vectors, semantic index, ANN search, reranking,
  background indexing, graph runtime, GraphRAG job, MCP runtime, runtime
  retrieval, provider-backed prompt context evidence, or prompt assembly.
- No prompt execution, AITask orchestration, automatic `used_knowledge=true`,
  deterministic retrieval behavior change, prompt eligibility change, or
  automatic knowledge ingestion.
- No GeneratedCaseCandidate approve/reject mutation, TestCase promotion,
  automation draft creation, ToolInvocation creation, TestRun/TestResult
  creation, runner behavior change, remote CI provider behavior, generated
  replacement evidence, or generated-case auto-approval.
- No artifact upload, Artifact mutation outside declared evidence package
  output, artifact delete, source artifact mutation, prompt context evidence
  mutation, GeneratedCaseCandidate content mutation, KnowledgeEvidence
  mutation, TestKnowledgeCard mutation, ReviewHistory mutation, historical
  evidence mutation, RBAC, tenants, or permissions.

## Contract Boundary To Define

The follow-up contract task should define:

### Evidence Package Vocabulary

The contract should preserve these exact planning terms so Task 2 can update
the data, API, state, artifact, and prompt/skill contracts consistently:

- Generated Case Human Review Evidence Package.
- GeneratedCaseCandidate ids.
- Candidate summary.
- Candidate status.
- Candidate title, priority, test type, precondition, steps, expected results,
  input data, tags, requirement refs, risk refs, and AI reason.
- `source_knowledge_evidence_ids`.
- `knowledge_evidence_refs_json`.
- `quality_score`.
- `review_findings_json`.
- `coverage_gap_notes`.
- `automation_readiness`.
- Dedup findings.
- Duplicate candidate ids.
- Duplicate-of case id.
- Automation readiness blockers.
- Prompt context evidence artifact ids.
- Prompt context consumption artifact ids.
- Prompt context audit summary artifact ids.
- Prompt context audit review decision artifact ids.
- Prompt context audit review summary export artifact ids.
- Prompt context discrepancy resolution audit handoff artifact ids.
- ReviewHistory ids.
- ReviewHistory links.
- Evidence chain completeness.
- Missing evidence summary.
- Conflicting evidence summary.
- Review blocker summary.
- Dedup/readiness summary.
- Human review checklist.
- Failure code.
- Visible reason.

- Evidence package input:
  - canonical package action
    `build_generated_case_human_review_evidence_package`;
  - `GeneratedCaseCandidate` id and candidate status;
  - candidate content fields: title, priority, test type, precondition, steps,
    expected results, input data, tags, requirement refs, risk refs, AI reason,
    generation reason, covered risk ids, and duplicate-of case id;
  - knowledge evidence fields:
    `source_knowledge_evidence_ids` and `knowledge_evidence_refs_json`;
  - review evidence fields:
    `quality_score`, `review_findings_json`, `coverage_gap_notes`,
    `automation_readiness`, dedup findings, duplicate candidate ids,
    automation readiness blockers, reviewer comments, and ReviewHistory ids;
  - prompt-context lineage fields: prompt context evidence artifact ids,
    prompt context consumption artifact ids, prompt context audit summary
    artifact ids, prompt context audit review decision artifact ids, prompt
    context audit review summary export artifact ids, prompt context
    discrepancy resolution audit handoff artifact ids, source hashes, and
    source manifest ids.
- Evidence package output:
  - evidence package artifact id when a later slice persists one;
  - artifact naming such as `generated_case_human_review_evidence_package`;
  - package filename such as
    `generated_case_human_review_evidence_package.json`;
  - candidate summary, evidence chain completeness, missing evidence summary,
    conflicting evidence summary, review blocker summary, dedup/readiness
    summary, human review checklist, included artifact ids, excluded artifact
    reasons, ReviewHistory links, failure code, and visible reason.
- Safety requirements:
  - evidence package records are human-review evidence bundles, not approval,
    rejection, optimization, TestCase promotion, automation draft creation,
    prompt execution, provider execution, retrieval execution, report
    generation, or UI rendering;
  - `quality_score`, `review_findings_json`, `coverage_gap_notes`,
    `automation_readiness`, dedup findings, missing evidence summary,
    conflicting evidence summary, and human review checklist must remain review
    aids only;
  - `source_knowledge_evidence_ids`, `knowledge_evidence_refs_json`,
    prompt-context artifact ids, source hashes, source manifest ids, and
    ReviewHistory links must remain visible instead of being filtered,
    deleted, rewritten, or converted into approval decisions;
  - invalid, missing, stale, unsafe, cross-project, unbounded, evidence-missing,
    candidate-missing, candidate-mismatched, candidate-status-invalid,
    knowledge-evidence-missing, prompt-context-evidence-missing,
    review-findings-missing, dedup-inconclusive, readiness-unknown,
    review-history-missing, artifact-mismatched, source-hash-mismatched,
    credential-required, runtime-required, provider-required,
    approval-required, or promotion-required input must fail without appending
    a successful evidence package.
- Runtime boundary:
  - this slice defines generated case human review evidence package artifact
    and contract semantics only;
  - it does not create runtime endpoints, render frontend pages, create or
    mutate review decisions, approve/reject GeneratedCaseCandidate rows,
    promote TestCases, create automation drafts, upload artifacts, run prompts,
    execute AITasks, call providers, run retrieval, create vector indexes,
    create embeddings, rerank, run graph jobs, invoke MCP runtime, mutate
    source evidence, or change RBAC/tenant/permission behavior.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Generated Case Human Review Evidence Package task plan | done | `if (-not (Test-Path docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md)) { exit 1 }; rg -n "Generated Case Human Review Evidence Package|generated_case_human_review_evidence_package|GeneratedCaseCandidate|source_knowledge_evidence_ids|knowledge_evidence_refs_json|quality_score|review_findings_json|coverage_gap_notes|automation_readiness|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md; git diff --check` | pending | planning-only |
| Define Generated Case Human Review Evidence Package contracts | planned | `rg -n "Generated Case Human Review Evidence Package|generated_case_human_review_evidence_package|build_generated_case_human_review_evidence_package|GeneratedCaseCandidate|source_knowledge_evidence_ids|knowledge_evidence_refs_json|quality_score|review_findings_json|coverage_gap_notes|automation_readiness|dedup findings|human review checklist|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md && git diff --check` | pending | contract-only |
| Add Generated Case Human Review Evidence Package golden smoke | planned | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_evidence_package_contract_golden.py -q && git diff --check` | pending | no approval/promotion/runtime integration |
| Slice 54 completion gate | planned | `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_evidence_package_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add Generated Case Human Review Evidence Package Task Plan

Goal: Create a narrow plan for Generated Case Human Review Evidence Package
before contract edits, backend runtime APIs, frontend pages, candidate
approval/rejection, TestCase promotion, automation drafts, provider
integrations, provider SDKs, external calls, vector infrastructure, runtime
retrieval, RBAC, tenants, permissions, or package upgrades.

Expected files:

- `docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```powershell
if (-not (Test-Path docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md)) { exit 1 }
rg -n "Generated Case Human Review Evidence Package|generated_case_human_review_evidence_package|GeneratedCaseCandidate|source_knowledge_evidence_ids|knowledge_evidence_refs_json|quality_score|review_findings_json|coverage_gap_notes|automation_readiness|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Acceptance:

- Slice 54 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit message.
- The plan names GeneratedCaseCandidate ids, `source_knowledge_evidence_ids`,
  `knowledge_evidence_refs_json`, `quality_score`, `review_findings_json`,
  `coverage_gap_notes`, `automation_readiness`, dedup findings, prompt context
  evidence/consumption/audit/discrepancy handoff artifact ids, ReviewHistory,
  failure behavior, artifact boundaries, and forbidden side effects.
- The plan excludes runtime APIs, frontend, provider integration, provider
  SDKs, external calls, vector database, embeddings, reranking, prompt
  execution, AITask orchestration, TestCase promotion, GeneratedCaseCandidate
  approve/reject mutation, automation draft creation, artifact upload, RBAC,
  tenants, permissions, and package upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add generated case human review evidence package plan
```

## Task 2: Define Generated Case Human Review Evidence Package Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future generated case human review evidence package boundary before
any runtime API, frontend, candidate approval/rejection, TestCase promotion,
automation draft creation, or provider/retrieval runtime behavior.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Generated Case Human Review Evidence Package|generated_case_human_review_evidence_package|build_generated_case_human_review_evidence_package|GeneratedCaseCandidate|source_knowledge_evidence_ids|knowledge_evidence_refs_json|quality_score|review_findings_json|coverage_gap_notes|automation_readiness|dedup findings|human review checklist|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md
git diff --check
```

Acceptance:

- Contracts define generated case human review evidence package inputs,
  outputs, candidate summary, knowledge evidence linkage, prompt-context
  lineage, review findings, quality score, coverage gap notes, automation
  readiness, dedup findings, evidence chain completeness, missing/conflicting
  evidence summaries, review blocker summary, human review checklist,
  ReviewHistory, failure behavior, and forbidden side effects.
- Contracts keep backend runtime APIs, frontend, provider integrations, SDKs,
  external calls, vector database, embeddings, reranking, prompt execution,
  candidate approval/rejection, TestCase promotion, automation draft creation,
  RBAC, tenants, permissions, and package upgrades out of scope.
- `NEXT_AI_TASK.md` points to Task 3.

Commit message:

```text
docs(v2): define generated case human review evidence package contracts
```

## Task 3: Add Generated Case Human Review Evidence Package Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving the generated case
human review evidence package remains evidence packaging and cannot approve or
reject candidates, promote TestCases, create automation drafts, or create
runtime/provider/retrieval behavior.

Expected files:

- `backend/app/tests/golden/test_generated_case_human_review_evidence_package_contract_golden.py`
- `docs/fixtures/42-generated-case-human-review-evidence-package-golden.md`
- `docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_evidence_package_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names Generated Case Human Review Evidence Package,
  `generated_case_human_review_evidence_package`,
  `build_generated_case_human_review_evidence_package`, GeneratedCaseCandidate
  ids, `source_knowledge_evidence_ids`, `knowledge_evidence_refs_json`,
  `quality_score`, `review_findings_json`, `coverage_gap_notes`,
  `automation_readiness`, dedup findings, prompt-context artifact lineage,
  ReviewHistory, failure behavior, and forbidden side effects.
- Golden proves no backend runtime API, frontend, provider SDK, external call,
  vector database, embedding, reranking, prompt execution, candidate
  approval/rejection, TestCase promotion, automation draft creation, RBAC,
  tenants, permissions, package upgrade, or source evidence mutation is
  created by the contract.
- `NEXT_AI_TASK.md` points to Slice 54 Completion Gate.

Commit message:

```text
test(golden): add generated case human review evidence package smoke
```

## Slice 54 Completion Gate

Goal: Validate Slice 54 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

Verification Command:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_evidence_package_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 54 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

Commit message:

```text
docs(v2): complete generated case human review evidence package slice
```
