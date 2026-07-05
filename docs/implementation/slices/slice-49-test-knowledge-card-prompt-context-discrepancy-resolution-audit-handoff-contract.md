# Slice 49: TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff Contract Task Plan

## Goal

Define the prompt context discrepancy resolution audit handoff contract for a
future final audit bundle that links TestKnowledgeCard discrepancy resolution
summary export evidence back to resolution reviews, discrepancy records, review
evidence, audit evidence, prompt context consumption, prompt context evidence,
source hashes, context manifests, PromptVersion, SkillVersion, and
ReviewHistory before any frontend page, report generation behavior change,
export/download endpoint, prompt assembly implementation, prompt runtime
execution, provider call, deterministic retrieval behavior change, vector
index, backend feature API, broad TestKnowledgeCard CRUD, automatic prompt
eligibility, or automatic discrepancy remediation exists.

This slice is contract-first. It documents how a future audit handoff may
preserve the evidence chain for resolved or unresolved prompt context
discrepancies while naming handoff summary, evidence chain status, included
artifact ids, excluded artifact reasons, unresolved follow-up flags, source
hashes, context manifest references, PromptVersion, SkillVersion, and
ReviewHistory.

## Product Value Answer

After this slice, Chtest can describe how the prompt context discrepancy
resolution chain is handed off as auditable evidence without changing frontend
pages, report generation behavior, evidence storage, prompt assembly, provider
behavior, export endpoints, or retrieval runtime. Users get a clear final
handoff contract: the included artifact ids, excluded artifact reasons,
evidence chain status, unresolved follow-up flags, source hashes, and
ReviewHistory remain visible before any UI, report generator, provider, prompt
runtime, or external archive consumes the handoff.

## Current Evidence Baseline

- Slice 19 defined deterministic local ContextArtifact retrieval evidence and
  `knowledge_retrieval.json` without adding vector search, embeddings,
  reranking, graph runtime, MCP runtime, or external providers.
- Existing PromptVersion and SkillVersion contracts require prompt input
  artifacts and context manifests for traceability.
- Slice 30 defined `TestKnowledgeCard` and `KnowledgeEvidence` contract
  shapes, including `safe_to_show` and `allowed_for_prompt`.
- Slice 39 defined human-reviewed prompt eligibility for TestKnowledgeCard
  records.
- Slice 40 defined a read-only TestKnowledgeCard Retrieval Boundary with
  `select_prompt_eligible_cards`, selected/excluded card evidence, and
  `excluded_card_reason`.
- Slice 41 defined bounded TestKnowledgeCard Prompt Context Evidence with
  `build_prompt_context_evidence`, safe bounded snippet/source hash entries,
  source manifests, retrieval boundary artifacts, PromptVersion/SkillVersion
  trace, context manifest links, omission reasons, and failure behavior.
- Slice 42 defined TestKnowledgeCard Prompt Context Consumption with
  `consume_prompt_context_evidence`, `prompt_context_consumption`,
  `used_knowledge` semantics, output citations, skipped evidence, source hash
  references, PromptVersion/SkillVersion trace, ReviewHistory links, and
  failure behavior.
- Slice 43 defined TestKnowledgeCard Prompt Context Audit Summary with
  `summarize_prompt_context_consumption`, `prompt_context_audit_summary`,
  usage status, cited/skipped entries, unsupported claim summaries, source
  hashes, context manifest links, PromptVersion/SkillVersion trace,
  ReviewHistory, review flags, and failure behavior.
- Slice 44 defined TestKnowledgeCard Prompt Context Audit Review Decision with
  `review_prompt_context_audit_summary`,
  `prompt_context_audit_review_decision`, review action, accepted,
  needs_clarification, rejected actions, accepted/questioned/rejected citation
  ids, follow-up flags, ReviewHistory, and failure behavior.
- Slice 45 defined TestKnowledgeCard Prompt Context Audit Review Summary Export
  with `export_prompt_context_audit_review_summary`,
  `prompt_context_audit_review_summary_export`, review outcome summary,
  accepted/questioned/rejected citation groups, unresolved follow-up flags,
  unsupported claim references, ReviewHistory links, source hashes, context
  manifest references, PromptVersion/SkillVersion trace, and failure behavior.
- Slice 46 defined TestKnowledgeCard Prompt Context Review Discrepancy Tracking
  with `track_prompt_context_review_discrepancy`,
  `prompt_context_review_discrepancy`, discrepancy type, affected citation ids,
  evidence gap summary, mismatch reason, reviewer note, severity, resolution
  status, unresolved follow-up flags, unsupported claim references,
  ReviewHistory links, and failure behavior.
- Slice 47 defined TestKnowledgeCard Prompt Context Discrepancy Resolution
  Review with `review_prompt_context_discrepancy_resolution`,
  `prompt_context_discrepancy_resolution_review`, resolution action,
  accepted/rejected/acknowledged discrepancy ids, clarification requested
  fields, resulting resolution status, ReviewHistory links, source hashes,
  context manifest references, failure code, and visible reason.
- Slice 48 defined TestKnowledgeCard Prompt Context Discrepancy Resolution
  Summary Export with `export_prompt_context_discrepancy_resolution_summary`,
  `prompt_context_discrepancy_resolution_summary_export`, resolution outcome
  summary, accepted/rejected/acknowledged discrepancy groups, clarification
  requested field groups, unresolved follow-up flag groups, reviewer comment
  summary, resulting resolution status group, ReviewHistory links, source
  hashes, context manifest references, failure code, and visible reason.
- Current contracts do not define a final audit handoff boundary that packages
  the discrepancy resolution evidence chain without acting as a report
  renderer, download endpoint, external archive integration, or runtime prompt
  input generator.

## Non-goals

- No frontend page, report generation behavior change, report renderer,
  export/download endpoint, dashboard, backend feature API, endpoint, router,
  service, worker, queue, scheduler, or background job.
- No prompt assembly implementation, prompt runtime execution, LLM/provider
  call, provider SDK, credentials, OAuth, remote URL fetch, prompt runner,
  AITask execution behavior change, model output behavior implementation,
  automatic citation generation, automatic `used_knowledge=true` marking,
  prompt input generation, or runtime prompt template rendering.
- No prompt runtime retrieval implementation, deterministic retrieval behavior
  change, deterministic retrieval ranking change, vector database, embeddings,
  reranking, background indexing, graph runtime, GraphRAG job, MCP runtime, or
  external KnowledgeAdapter provider call.
- No broad TestKnowledgeCard CRUD implementation, migration, card table change,
  automatic prompt eligibility, automatic card creation from model output,
  automatic card approval, automatic knowledge ingestion, or
  KnowledgeIngestionAgent runtime.
- No artifact upload, artifact mutation, artifact delete, source artifact
  mutation, resolution summary export mutation, resolution review mutation,
  discrepancy artifact mutation, review summary export mutation, audit review
  decision mutation, audit summary mutation, prompt context consumption
  mutation, prompt context evidence mutation, retrieval boundary artifact
  mutation, prompt eligibility artifact mutation, historical evidence mutation,
  ReviewHistory mutation outside declared audit handoff evidence,
  FailureAnalysis mutation, Report mutation, TestRun/TestResult mutation,
  TestCase mutation, GeneratedCaseCandidate mutation, KnowledgeEvidence
  mutation, PromptVersion mutation, SkillVersion mutation, or existing
  TestKnowledgeCard content mutation.
- No automatic discrepancy resolution, automatic duplicate merge, card
  replacement, card archive/delete, generated-case auto-approval, TestCase
  auto-promotion, runner behavior change, remote CI provider behavior, RBAC,
  tenants, permissions, external archive integration, or package upgrades.

## Contract Boundary To Define

The follow-up contract task should define:

- Audit handoff input:
  - prompt request id or AITask id when available;
  - prompt context discrepancy resolution summary export artifact id;
  - prompt context discrepancy resolution review artifact id;
  - prompt context review discrepancy artifact id;
  - prompt context audit review summary export artifact id;
  - prompt context audit review decision artifact id;
  - prompt context audit summary artifact id;
  - prompt context consumption artifact id;
  - prompt context evidence artifact id;
  - context manifest artifact id;
  - `used_knowledge` decision;
  - resolution outcome summary;
  - accepted discrepancy group;
  - rejected discrepancy group;
  - acknowledged discrepancy group;
  - clarification requested fields and clarification requested field group;
  - resulting resolution status group;
  - affected citation ids;
  - evidence gap summary;
  - mismatch reason;
  - unresolved follow-up flags;
  - unsupported claim references;
  - source hashes or source quote/hash pointers;
  - PromptVersion id/name/version and SkillVersion id/name/version;
  - ReviewHistory ids across discrepancy, resolution review, and summary export
    evidence.
- Audit handoff fields:
  - audit handoff id or artifact id when a later slice defines one;
  - audit handoff action when a later slice defines one;
  - handoff summary;
  - evidence chain status such as complete, incomplete, blocked, or
    failed_validation;
  - included artifact ids;
  - excluded artifact reasons;
  - unresolved follow-up flags;
  - unresolved evidence gaps;
  - unsupported claim references;
  - source manifest ids and source hashes;
  - context manifest references;
  - PromptVersion/SkillVersion trace;
  - ReviewHistory links;
  - failure code when audit handoff input is invalid.
- Safety requirements:
  - audit handoff records are evidence chain packages, not mutation of
    resolution summary exports, resolution reviews, discrepancy records, review
    summary exports, review decisions, audit summaries, prompt context
    consumption evidence, prompt context evidence, or underlying knowledge
    evidence;
  - evidence chain status does not create prompt eligibility, approve
    TestKnowledgeCard content, approve generated cases, alter
    `used_knowledge`, mark skipped evidence as cited, invent citations, or
    auto-resolve discrepancies;
  - included artifact ids, excluded artifact reasons, unresolved follow-up
    flags, unsupported claims, skipped evidence, source hashes, evidence gap
    summary, and mismatch reasons must remain visible instead of being
    filtered, deleted, or rewritten;
  - invalid, stale, mismatched, unsafe, revoked, cross-project, unsupported, or
    incomplete input must fail without appending a successful audit handoff.
- Outputs:
  - prompt context discrepancy resolution audit handoff artifact id when a
    later scoped workflow persists one;
  - handoff summary;
  - evidence chain status;
  - included artifact ids;
  - excluded artifact reasons;
  - unresolved follow-up flags;
  - unresolved evidence gaps;
  - unsupported claim references;
  - ReviewHistory links;
  - source manifest ids and source hashes;
  - PromptVersion/SkillVersion trace;
  - context manifest references;
  - failure code and visible reason.
- Runtime boundary:
  - this slice defines audit handoff artifact and contract semantics only;
  - it does not render a frontend page, change report generation behavior,
    expose an export/download endpoint, assemble prompts, call providers, run
    AITasks, change retrieval ranking, write runtime `prompt_input.json`,
    auto-mark `used_knowledge`, generate model citations, auto-resolve
    discrepancies, upload artifacts, or mutate artifacts outside declared
    discrepancy resolution audit handoff evidence.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestKnowledgeCard prompt context discrepancy resolution audit handoff task plan | done | `test -f docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md && rg -n "TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff|audit handoff|handoff summary|evidence chain status|included artifact ids|excluded artifact reasons|resolution outcome summary|accepted discrepancy group|rejected discrepancy group|acknowledged discrepancy group|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md NEXT_AI_TASK.md && git diff --check` | `7669597` | planning-only scope |
| Define TestKnowledgeCard prompt context discrepancy resolution audit handoff contracts | done | `rg -n "TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff|prompt_context_discrepancy_resolution_audit_handoff|build_prompt_context_discrepancy_resolution_audit_handoff|handoff summary|evidence chain status|included artifact ids|excluded artifact reasons|unresolved evidence gaps|ReviewHistory|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md && git diff --check` | `e2d912e` | contract-only |
| Add TestKnowledgeCard prompt context discrepancy resolution audit handoff golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_audit_handoff_contract_golden.py -q && git diff --check` | pending | no frontend/report/export runtime |
| Slice 49 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_audit_handoff_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_summary_export_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff Task Plan

Goal: Create a narrow plan for prompt context discrepancy resolution audit
handoff before contract edits, frontend/report/export changes, or runtime
implementation.

Expected files:

- `docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md
rg -n "TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff|audit handoff|handoff summary|evidence chain status|included artifact ids|excluded artifact reasons|resolution outcome summary|accepted discrepancy group|rejected discrepancy group|acknowledged discrepancy group|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 49 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names audit handoff inputs, handoff summary, evidence chain status,
  included artifact ids, excluded artifact reasons, unresolved follow-up flags,
  ReviewHistory, failure behavior, and non-goals.
- The plan excludes frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  calls, retrieval ranking changes, vector indexes, embeddings, reranking,
  graph jobs, MCP runtime, broad CRUD, automatic eligibility, and historical
  evidence mutation.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add test knowledge card prompt context discrepancy resolution audit handoff plan
```

## Task 2: Define TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future audit handoff boundary for prompt context discrepancy
resolution evidence chains.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff|prompt_context_discrepancy_resolution_audit_handoff|build_prompt_context_discrepancy_resolution_audit_handoff|handoff summary|evidence chain status|included artifact ids|excluded artifact reasons|unresolved evidence gaps|ReviewHistory|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md
git diff --check
```

Acceptance:

- Contracts define audit handoff inputs, resolution summary export artifact
  references, resolution review artifact references, discrepancy artifact
  references, handoff summary, evidence chain status, included artifact ids,
  excluded artifact reasons, unresolved follow-up flags, ReviewHistory, source
  hashes, context manifest links, PromptVersion/SkillVersion trace, failure
  behavior, and forbidden side effects.
- Contracts require audit handoff to preserve underlying resolution summaries,
  resolution reviews, discrepancy records, review summary exports, review
  decisions, audit summaries, consumption evidence, and knowledge artifacts
  without inventing, mutating, or automatically resolving evidence.
- Contracts keep frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  calls, retrieval ranking changes, vector indexes, embeddings, reranking,
  graph jobs, MCP runtime, broad CRUD, automatic eligibility, and historical
  evidence mutation out of scope.

Commit message:

```text
docs(v2): define test knowledge card prompt context discrepancy resolution audit handoff contracts
```

## Task 3: Add TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving prompt context
discrepancy resolution audit handoff cannot mutate resolution summary export
evidence, resolution reviews, discrepancy tracking evidence, review evidence,
create prompt eligibility, rewrite `used_knowledge`, or imply frontend/report/
export runtime behavior.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_audit_handoff_contract_golden.py`
- `docs/fixtures/37-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-golden.md`
- `docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_audit_handoff_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names resolution summary export artifact id, audit handoff artifact
  id, handoff summary, evidence chain status, included artifact ids, excluded
  artifact reasons, unresolved follow-up flags, ReviewHistory, failure
  behavior, and forbidden side effects.
- Golden proves no frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  call, retrieval ranking change, vector index, embedding, reranking, graph
  job, MCP runtime, broad CRUD, automatic eligibility, historical evidence
  mutation, RBAC, tenants, or permissions is created by the contract.

Commit message:

```text
test(golden): add test knowledge card prompt context discrepancy resolution audit handoff smoke
```

## Slice 49 Completion Gate

Goal: Validate Slice 49 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_audit_handoff_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_summary_export_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 49 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.

Commit message:

```text
docs(v2): complete test knowledge card prompt context discrepancy resolution audit handoff slice
```
