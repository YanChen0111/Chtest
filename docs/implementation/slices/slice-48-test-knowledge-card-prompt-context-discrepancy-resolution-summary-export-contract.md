# Slice 48: TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export Contract Task Plan

## Goal

Define the prompt context discrepancy resolution summary export contract for
future packaging of TestKnowledgeCard discrepancy resolution review evidence
before any frontend page, report generation behavior change, export/download
endpoint, prompt assembly implementation, prompt runtime execution, provider
call, deterministic retrieval behavior change, vector index, backend feature
API, broad TestKnowledgeCard CRUD, automatic prompt eligibility, or automatic
discrepancy remediation exists.

This slice is contract-first. It documents how a future resolution summary
export may package accepted, rejected, acknowledged, clarification-needed, and
later-review-resolved discrepancy resolution evidence while preserving
resolution review artifact ids, discrepancy artifact ids, review summary export
artifact ids, affected citation ids, resolution outcome summary, clarification
requested fields, resolution status, source hashes, context manifest
references, PromptVersion, SkillVersion, and ReviewHistory.

## Product Value Answer

After this slice, Chtest can describe how prompt context discrepancy resolution
review evidence is summarized for a future handoff without changing frontend
pages, report generation behavior, evidence storage, prompt assembly, provider
behavior, export endpoints, or retrieval runtime. Users get an auditable
resolution summary export contract: resolution outcome summary,
accepted/rejected/acknowledged discrepancy groups, unresolved clarification
fields, follow-up flags, source hashes, and ReviewHistory remain visible
before any UI, report generator, download endpoint, provider, or prompt
runtime consumes the summary.

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
- Current contracts do not define a resolution summary export boundary for
  packaging resolution review evidence into a future handoff summary.

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
  mutation, discrepancy resolution review mutation, discrepancy artifact
  mutation, review summary export mutation, audit review decision mutation,
  audit summary mutation, prompt context consumption mutation, prompt context
  evidence mutation, retrieval boundary artifact mutation, prompt eligibility
  artifact mutation, historical evidence mutation, ReviewHistory mutation
  outside declared resolution summary export evidence, FailureAnalysis
  mutation, Report mutation, TestRun/TestResult mutation, TestCase mutation,
  GeneratedCaseCandidate mutation, KnowledgeEvidence mutation, PromptVersion
  mutation, SkillVersion mutation, or existing TestKnowledgeCard content
  mutation.
- No automatic discrepancy resolution, automatic duplicate merge, card
  replacement, card archive/delete, generated-case auto-approval, TestCase
  auto-promotion, runner behavior change, remote CI provider behavior, RBAC,
  tenants, permissions, or package upgrades.

## Contract Boundary To Define

The follow-up contract task should define:

- Resolution summary export input:
  - prompt request id or AITask id when available;
  - prompt context discrepancy resolution review artifact id;
  - prompt context review discrepancy artifact id;
  - prompt context audit review summary export artifact id;
  - prompt context audit review decision artifact id;
  - prompt context audit summary artifact id;
  - prompt context consumption artifact id;
  - prompt context evidence artifact id;
  - context manifest artifact id;
  - `used_knowledge` decision;
  - resolution action;
  - resulting resolution status;
  - accepted discrepancy ids;
  - rejected discrepancy ids;
  - acknowledged discrepancy ids;
  - clarification requested fields;
  - affected citation ids;
  - evidence gap summary;
  - mismatch reason;
  - reviewer note and follow-up flags;
  - unsupported claim references;
  - source hashes or source quote/hash pointers;
  - PromptVersion id/name/version and SkillVersion id/name/version;
  - ReviewHistory ids, discrepancy ReviewHistory id, and resolution review
    ReviewHistory id.
- Resolution summary export fields:
  - resolution summary export id or artifact id when a later slice defines one;
  - resolution summary export action when a later slice defines one;
  - resolution outcome summary;
  - accepted discrepancy group;
  - rejected discrepancy group;
  - acknowledged discrepancy group;
  - clarification requested field group;
  - unresolved follow-up flag group;
  - reviewer comment summary;
  - resulting resolution status group;
  - source manifest ids and source hashes;
  - context manifest references;
  - PromptVersion/SkillVersion trace;
  - ReviewHistory links;
  - failure code when resolution summary export input is invalid.
- Safety requirements:
  - resolution summary exports are evidence packages about resolution review
    decisions, not mutation of resolution reviews, discrepancy records, review
    summary exports, review decisions, audit summaries, prompt context
    consumption evidence, prompt context evidence, or underlying knowledge
    evidence;
  - exported resolution outcome does not create prompt eligibility, approve
    TestKnowledgeCard content, approve generated cases, alter
    `used_knowledge`, mark skipped evidence as cited, invent citations, or
    auto-resolve other discrepancies;
  - accepted/rejected/acknowledged discrepancy groups, clarification requested
    fields, affected citation ids, unresolved follow-up flags, unsupported
    claims, skipped evidence, source hashes, evidence gap summary, and mismatch
    reasons must remain visible instead of being filtered, deleted, or
    rewritten;
  - invalid, stale, mismatched, unsafe, revoked, cross-project, unsupported, or
    incomplete input must fail without appending a successful summary export.
- Outputs:
  - prompt context discrepancy resolution summary export artifact id when a
    later scoped workflow persists one;
  - resolution outcome summary;
  - accepted discrepancy group;
  - rejected discrepancy group;
  - acknowledged discrepancy group;
  - clarification requested fields;
  - unresolved follow-up flags;
  - reviewer comment summary;
  - ReviewHistory links;
  - source manifest ids and source hashes;
  - PromptVersion/SkillVersion trace;
  - context manifest references;
  - failure code and visible reason.
- Runtime boundary:
  - this slice defines resolution summary export artifact and contract
    semantics only;
  - it does not render a frontend page, change report generation behavior,
    expose an export/download endpoint, assemble prompts, call providers, run
    AITasks, change retrieval ranking, write runtime `prompt_input.json`,
    auto-mark `used_knowledge`, generate model citations, auto-resolve
    discrepancies, or mutate artifacts outside declared discrepancy resolution
    summary export evidence.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestKnowledgeCard prompt context discrepancy resolution summary export task plan | done | `test -f docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md && rg -n "TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export|resolution summary export|resolution outcome summary|accepted discrepancy group|rejected discrepancy group|acknowledged discrepancy group|clarification requested fields|resolution status|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md NEXT_AI_TASK.md && git diff --check` | `6c17232` | planning-only scope |
| Define TestKnowledgeCard prompt context discrepancy resolution summary export contracts | done | `rg -n "TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export|prompt_context_discrepancy_resolution_summary_export|export_prompt_context_discrepancy_resolution_summary|resolution outcome summary|accepted discrepancy group|rejected discrepancy group|acknowledged discrepancy group|clarification requested fields|resolution status|ReviewHistory|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md && git diff --check` | `e351933` | contract-only |
| Add TestKnowledgeCard prompt context discrepancy resolution summary export golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_summary_export_contract_golden.py -q && git diff --check` | pending | no frontend/report/export runtime |
| Slice 48 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_summary_export_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_review_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export Task Plan

Goal: Create a narrow plan for prompt context discrepancy resolution summary
exports before contract edits, frontend/report/export changes, or runtime
implementation.

Expected files:

- `docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md
rg -n "TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export|resolution summary export|resolution outcome summary|accepted discrepancy group|rejected discrepancy group|acknowledged discrepancy group|clarification requested fields|resolution status|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 48 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names resolution summary export inputs, resolution outcome summary,
  accepted/rejected/acknowledged discrepancy groups, clarification requested
  fields, resolution status, ReviewHistory, failure behavior, and non-goals.
- The plan excludes frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  calls, retrieval ranking changes, vector indexes, embeddings, reranking,
  graph jobs, MCP runtime, broad CRUD, automatic eligibility, and historical
  evidence mutation.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add test knowledge card prompt context discrepancy resolution summary export plan
```

## Task 2: Define TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future resolution summary export boundary for prompt context
discrepancy resolution review evidence.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export|prompt_context_discrepancy_resolution_summary_export|export_prompt_context_discrepancy_resolution_summary|resolution outcome summary|accepted discrepancy group|rejected discrepancy group|acknowledged discrepancy group|clarification requested fields|resolution status|ReviewHistory|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md
git diff --check
```

Acceptance:

- Contracts define resolution summary export inputs, resolution review artifact
  references, discrepancy artifact references, resolution outcome summary,
  accepted/rejected/acknowledged discrepancy groups, clarification requested
  fields, resolution status, ReviewHistory, source hashes, context manifest
  links, PromptVersion/SkillVersion trace, failure behavior, and forbidden
  side effects.
- Contracts require summary export to preserve underlying resolution reviews,
  discrepancy records, review summary exports, review decisions, audit
  summaries, consumption evidence, and knowledge artifacts without inventing,
  mutating, or automatically resolving evidence.
- Contracts keep frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  calls, retrieval ranking changes, vector indexes, embeddings, reranking,
  graph jobs, MCP runtime, broad CRUD, automatic eligibility, and historical
  evidence mutation out of scope.

Commit message:

```text
docs(v2): define test knowledge card prompt context discrepancy resolution summary export contracts
```

## Task 3: Add TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving prompt context
discrepancy resolution summary export cannot mutate resolution review evidence,
discrepancy tracking evidence, review summary exports, review decisions, audit
summaries, create prompt eligibility, rewrite `used_knowledge`, or imply
frontend/report/export runtime behavior.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_summary_export_contract_golden.py`
- `docs/fixtures/36-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-golden.md`
- `docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_summary_export_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names resolution review artifact id, discrepancy artifact id,
  resolution outcome summary, accepted/rejected/acknowledged discrepancy
  groups, clarification requested fields, resolution status, ReviewHistory,
  failure behavior, and forbidden side effects.
- Golden proves no frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  call, retrieval ranking change, vector index, embedding, reranking, graph
  job, MCP runtime, broad CRUD, automatic eligibility, historical evidence
  mutation, RBAC, tenants, or permissions is created by the contract.

Commit message:

```text
test(golden): add test knowledge card prompt context discrepancy resolution summary export smoke
```

## Slice 48 Completion Gate

Goal: Validate Slice 48 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_summary_export_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_review_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 48 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.

Commit message:

```text
docs(v2): complete test knowledge card prompt context discrepancy resolution summary export slice
```
