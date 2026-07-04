# Slice 45: TestKnowledgeCard Prompt Context Audit Review Summary Export Contract Task Plan

## Goal

Define the prompt context audit review summary export contract for future
packaging of TestKnowledgeCard prompt context audit review decisions before any
frontend page, report generation behavior change, export/download endpoint,
prompt assembly implementation, prompt runtime execution, provider call,
deterministic retrieval behavior change, vector index, backend feature API,
broad TestKnowledgeCard CRUD, or automatic prompt eligibility exists.

This slice is contract-first. It documents how a future export summary may
package accepted, questioned, and rejected prompt context audit review decision
evidence while preserving review decision artifact ids, audit summary artifact
ids, prompt context consumption artifact ids, output citations, skipped
evidence, unsupported claims, source hashes, context manifest references,
PromptVersion, SkillVersion, ReviewHistory, unresolved follow-up flags, and
failure behavior boundaries.

## Product Value Answer

After this slice, Chtest can describe how reviewed knowledge-usage audit
decisions can be summarized for a future handoff or export without changing
frontend pages, report generation behavior, evidence storage, prompt assembly,
provider behavior, or retrieval runtime. Users get an auditable export-summary
contract: review outcomes, accepted/questioned/rejected citations, unresolved
follow-up flags, unsupported claims, source hashes, and ReviewHistory remain
visible before any UI, report generator, download endpoint, provider, or prompt
runtime consumes the summary.

## Current Evidence Baseline

- Slice 19 defined deterministic local ContextArtifact retrieval evidence and
  `knowledge_retrieval.json` without adding vector search, embeddings,
  reranking, graph runtime, MCP runtime, or external providers.
- Existing PromptVersion and SkillVersion contracts require prompt input
  artifacts and context manifests for traceability.
- Slice 30 defined `TestKnowledgeCard` and `KnowledgeEvidence` contract shapes,
  including `safe_to_show` and `allowed_for_prompt`.
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
- Current contracts do not define a summary export boundary for prompt context
  audit review decisions.

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
  mutation, audit review decision mutation, audit summary mutation, prompt
  context consumption mutation, prompt context evidence mutation, retrieval
  boundary artifact mutation, prompt eligibility artifact mutation, historical
  evidence mutation, ReviewHistory mutation outside declared summary export
  evidence, FailureAnalysis mutation, Report mutation, TestRun/TestResult
  mutation, TestCase mutation, GeneratedCaseCandidate mutation,
  KnowledgeEvidence mutation, PromptVersion mutation, SkillVersion mutation, or
  existing TestKnowledgeCard content mutation.
- No automatic duplicate merge, card replacement, card archive/delete,
  generated-case auto-approval, TestCase auto-promotion, runner behavior
  change, remote CI provider behavior, RBAC, tenants, permissions, or package
  upgrades.

## Contract Boundary To Define

The follow-up contract task should define:

- Export summary input:
  - prompt request id or AITask id when available;
  - prompt context audit review decision artifact id;
  - audit summary artifact id;
  - prompt context consumption artifact id;
  - prompt context evidence artifact id;
  - context manifest artifact id;
  - `used_knowledge` decision;
  - usage status;
  - review action and review outcome;
  - accepted citation ids;
  - questioned citation ids;
  - rejected citation ids;
  - output citation ids;
  - cited TestKnowledgeCard ids;
  - cited context entry ids;
  - cited source hashes or source quote/hash pointers;
  - skipped evidence ids and skip reasons;
  - unsupported claims;
  - unresolved follow-up flags and requested clarification fields;
  - failure reasons from the review decision;
  - PromptVersion id/name/version and SkillVersion id/name/version;
  - ReviewHistory ids and review decision ReviewHistory id.
- Export summary fields:
  - export summary id or artifact id when a later slice defines one;
  - export summary action when a later slice defines one;
  - review outcome summary;
  - accepted citation group;
  - questioned citation group;
  - rejected citation group;
  - unresolved follow-up flag group;
  - unsupported claim references;
  - reviewer comment summary;
  - source manifest ids and source hashes;
  - context manifest references;
  - PromptVersion/SkillVersion trace;
  - ReviewHistory links;
  - failure code when the export summary input is invalid.
- Safety requirements:
  - export summaries are evidence packages about review decisions, not mutation
    of review decisions, audit summaries, prompt context consumption evidence,
    prompt context evidence, or underlying knowledge evidence;
  - exported `accepted` citations do not create prompt eligibility, approve
    TestKnowledgeCard content, approve generated cases, or alter
    `used_knowledge`;
  - questioned/rejected citations, needs_clarification, unresolved follow-up
    flags, unsupported claims, skipped evidence, and source hashes must remain
    visible instead of being filtered, deleted, or rewritten;
  - invalid, stale, mismatched, unsafe, revoked, cross-project, unsupported, or
    incomplete input must fail without appending a successful export summary.
- Outputs:
  - prompt context audit review summary export artifact id when a later scoped
    workflow persists one;
  - review outcome summary;
  - accepted/questioned/rejected citation groups;
  - unresolved follow-up flags;
  - unsupported claim references;
  - reviewer comment summary;
  - ReviewHistory links;
  - source manifest ids and source hashes;
  - PromptVersion/SkillVersion trace;
  - context manifest references;
  - failure code and visible reason.
- Runtime boundary:
  - this slice defines summary export artifact and contract semantics only;
  - it does not render a frontend page, change report generation behavior,
    expose an export/download endpoint, assemble prompts, call providers, run
    AITasks, change retrieval ranking, write runtime `prompt_input.json`,
    auto-mark `used_knowledge`, generate model citations, or mutate artifacts
    outside declared summary export evidence.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestKnowledgeCard prompt context audit review summary export task plan | done | `test -f docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md && rg -n "TestKnowledgeCard Prompt Context Audit Review Summary Export|audit review decision|summary export|accepted|needs_clarification|rejected_for_missing_evidence|rejected_for_unsupported_claim|rejected_for_citation_mismatch|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md NEXT_AI_TASK.md && git diff --check` | `a5fe0c8` | planning-only scope |
| Define TestKnowledgeCard prompt context audit review summary export contracts | done | `rg -n "TestKnowledgeCard Prompt Context Audit Review Summary Export|prompt_context_audit_review_summary_export|export_prompt_context_audit_review_summary|audit review decision artifact|review outcome summary|accepted citation group|questioned citation group|rejected citation group|unresolved follow-up flags|unsupported claim references|ReviewHistory|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md && git diff --check` | pending | contract-only |
| Add TestKnowledgeCard prompt context audit review summary export golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_summary_export_contract_golden.py -q && git diff --check` | pending | no frontend/report/export runtime |
| Slice 45 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_summary_export_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_decision_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add TestKnowledgeCard Prompt Context Audit Review Summary Export Task Plan

Goal: Create a narrow plan for prompt context audit review summary exports
before contract edits, frontend/report/export changes, or runtime
implementation.

Expected files:

- `docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md
rg -n "TestKnowledgeCard Prompt Context Audit Review Summary Export|audit review decision|summary export|accepted|needs_clarification|rejected_for_missing_evidence|rejected_for_unsupported_claim|rejected_for_citation_mismatch|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 45 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names export summary inputs, review outcome outputs,
  accepted/questioned/rejected citation groups, unresolved follow-up flags,
  unsupported claim references, ReviewHistory, failure behavior, and non-goals.
- The plan excludes frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  calls, retrieval ranking changes, vector indexes, embeddings, reranking,
  graph jobs, MCP runtime, broad CRUD, automatic eligibility, and historical
  evidence mutation.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add test knowledge card prompt context audit review summary export plan
```

## Task 2: Define TestKnowledgeCard Prompt Context Audit Review Summary Export Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the future summary export boundary for prompt context audit review
decisions.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard Prompt Context Audit Review Summary Export|prompt_context_audit_review_summary_export|export_prompt_context_audit_review_summary|audit review decision artifact|review outcome summary|accepted citation group|questioned citation group|rejected citation group|unresolved follow-up flags|unsupported claim references|ReviewHistory|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md
git diff --check
```

Acceptance:

- Contracts define export summary input, audit review decision artifact
  references, audit summary artifact references, review outcome summary,
  accepted/questioned/rejected citation groups, unresolved follow-up flags,
  unsupported claim references, ReviewHistory, source hashes, context manifest
  links, PromptVersion/SkillVersion trace, failure behavior, and forbidden side
  effects.
- Contracts require export summaries to preserve underlying review decisions,
  audit summaries, consumption evidence, and knowledge artifacts without
  inventing or mutating evidence.
- Contracts keep frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  calls, retrieval ranking changes, vector indexes, embeddings, reranking,
  graph jobs, MCP runtime, broad CRUD, automatic eligibility, and historical
  evidence mutation out of scope.

Commit message:

```text
docs(v2): define test knowledge card prompt context audit review summary export contracts
```

## Task 3: Add TestKnowledgeCard Prompt Context Audit Review Summary Export Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving prompt context
audit review summary exports cannot mutate review decisions, audit summaries,
create prompt eligibility, rewrite `used_knowledge`, or imply frontend/report/
export runtime behavior.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_summary_export_contract_golden.py`
- `docs/fixtures/33-test-knowledge-card-prompt-context-audit-review-summary-export-golden.md`
- `docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_summary_export_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names audit review decision artifact id, audit summary artifact id,
  review outcome summary, accepted citation group, questioned citation group,
  rejected citation group, unresolved follow-up flags, unsupported claim
  references, ReviewHistory, failure behavior, and forbidden side effects.
- Golden proves no frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  call, retrieval ranking change, vector index, embedding, reranking, graph
  job, MCP runtime, broad CRUD, automatic eligibility, historical evidence
  mutation, RBAC, tenants, or permissions is created by the contract.

Commit message:

```text
test(golden): add test knowledge card prompt context audit review summary export smoke
```

## Slice 45 Completion Gate

Goal: Validate Slice 45 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_summary_export_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_decision_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 45 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.

Commit message:

```text
docs(v2): complete test knowledge card prompt context audit review summary export slice
```
