# Slice 41: TestKnowledgeCard Prompt Context Evidence Contract Task Plan

## Goal

Define the prompt context evidence contract for selected TestKnowledgeCard
records before any prompt assembly implementation, prompt runtime execution,
provider call, deterministic retrieval behavior change, vector index, frontend
page, backend feature API, broad TestKnowledgeCard CRUD, or automatic prompt
eligibility exists.

This slice is contract-first. It documents what selected TestKnowledgeCard
evidence may be placed into future prompt context while preserving prompt
context evidence, bounded snippet, source hash, retrieval boundary evidence,
source manifest, ReviewHistory, PromptVersion, SkillVersion, safe_to_show,
redaction, omission summaries, and failure behavior boundaries.

## Product Value Answer

After this slice, Chtest can describe exactly what knowledge-card evidence may
be supplied to a future AI prompt without letting retrieval selection become
unbounded prompt assembly. Users get auditable prompt context evidence: selected
card ids, safe snippets or source hashes, source evidence, prompt/skill trace
links, and omission reasons are recorded before any provider or runtime uses
the context.

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
- Artifact contracts preserve `prompt_input.json`, `context_manifest.json`,
  source manifest, ReviewHistory, and retrieval boundary evidence without
  requiring prompt assembly implementation.

## Non-goals

- No prompt assembly implementation, prompt runtime execution, LLM/provider
  call, provider SDK, credentials, OAuth, remote URL fetch, prompt runner,
  queue, scheduler, background worker, or AITask execution behavior change.
- No prompt runtime retrieval implementation, deterministic retrieval behavior
  change, deterministic retrieval ranking change, vector database, embeddings,
  reranking, background indexing, graph runtime, GraphRAG job, MCP runtime, or
  external KnowledgeAdapter provider call.
- No broad TestKnowledgeCard CRUD implementation, backend feature API,
  frontend page, migration, card table change, automatic prompt eligibility,
  automatic card creation from model output, automatic card approval,
  automatic knowledge ingestion, or KnowledgeIngestionAgent runtime.
- No artifact upload, artifact mutation, artifact delete, source artifact
  mutation, prompt eligibility artifact mutation, retrieval boundary artifact
  mutation, historical evidence mutation, ReviewHistory mutation,
  FailureAnalysis mutation, Report mutation, TestRun/TestResult mutation,
  TestCase mutation, GeneratedCaseCandidate mutation, KnowledgeEvidence
  mutation, or existing TestKnowledgeCard content mutation.
- No automatic duplicate merge, card replacement, card archive/delete,
  generated-case auto-approval, TestCase auto-promotion, runner behavior
  change, report generation behavior change, remote CI provider behavior, RBAC,
  tenants, permissions, or package upgrades.

## Contract Boundary To Define

The follow-up contract task should define:

- Prompt context evidence input:
  - prompt request id or AITask id when available;
  - PromptVersion id and SkillVersion id;
  - retrieval boundary artifact id;
  - selected TestKnowledgeCard ids;
  - selected source evidence ids;
  - source manifest artifact ids;
  - prompt eligibility artifact ids;
  - ReviewHistory ids;
  - `safe_to_show=true`;
  - redaction status;
  - unsupported claims and exclusion summaries when present.
- Context entry fields:
  - TestKnowledgeCard id;
  - knowledge_type, title, summary, and safe bounded snippet;
  - source hash or source quote/hash pointer;
  - source artifact ids and source section;
  - retrieval boundary artifact id;
  - prompt eligibility artifact id;
  - ReviewHistory id;
  - selection reason and source trace label;
  - omission reason when a selected card cannot be included.
- Safety requirements:
  - bounded snippet length and safe-to-show status are required;
  - redaction must be reviewed before any text enters prompt context;
  - source hash may replace text when snippet bounds or safety cannot be
    proven;
  - unsupported claims remain visible as exclusions or warnings, not prompt
    facts;
  - prompt context evidence must reference source artifacts rather than copy
    raw large source text.
- Outputs:
  - prompt context evidence artifact id;
  - selected context entries;
  - omitted card summaries and omission reasons;
  - source manifest ids and source hashes;
  - PromptVersion/SkillVersion trace;
  - context manifest references;
  - failure code for stale, unsafe, cross-project, revoked, unsupported,
    missing, unbounded, redaction-failed, or evidence-mismatched input.
- Runtime boundary:
  - this slice defines artifact and contract semantics only;
  - it does not assemble prompts, call providers, run AITasks, change
    retrieval ranking, write prompt_input.json for runtime use, or change
    frontend behavior.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestKnowledgeCard prompt context evidence task plan | done | `test -f docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md && rg -n "TestKnowledgeCard Prompt Context Evidence|prompt context evidence|bounded snippet|source hash|retrieval boundary|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md NEXT_AI_TASK.md && git diff --check` | pending | planning-only scope |
| Define TestKnowledgeCard prompt context evidence contracts | planned | `rg -n "TestKnowledgeCard Prompt Context Evidence|prompt_context_evidence|bounded snippet|source hash|retrieval boundary artifact|PromptVersion|SkillVersion|omission reason|context manifest|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md && git diff --check` | pending | contract-only |
| Add TestKnowledgeCard prompt context evidence golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_evidence_contract_golden.py -q && git diff --check` | pending | no prompt runtime |
| Slice 41 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_evidence_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_retrieval_boundary_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add TestKnowledgeCard Prompt Context Evidence Task Plan

Goal: Create a narrow plan for prompt context evidence before contract edits or
runtime implementation.

Expected files:

- `docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md
rg -n "TestKnowledgeCard Prompt Context Evidence|prompt context evidence|bounded snippet|source hash|retrieval boundary|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 41 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names prompt context evidence inputs, bounded snippet/source hash
  outputs, source evidence, source manifest, retrieval boundary artifact,
  PromptVersion/SkillVersion trace, context manifest links, omission summaries,
  failure behavior, and non-goals.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add test knowledge card prompt context evidence plan
```

## Task 2: Define TestKnowledgeCard Prompt Context Evidence Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the prompt context evidence boundary for future TestKnowledgeCard prompt
use.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard Prompt Context Evidence|prompt_context_evidence|bounded snippet|source hash|retrieval boundary artifact|PromptVersion|SkillVersion|omission reason|context manifest|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md
git diff --check
```

Acceptance:

- Contracts define prompt context evidence input, safe bounded context entries,
  source hashes, source evidence references, PromptVersion/SkillVersion trace,
  context manifest links, omitted-card summaries, and failure behavior.
- Contracts keep prompt assembly implementation, prompt runtime execution,
  provider calls, retrieval ranking changes, vector indexes, embeddings,
  reranking, graph jobs, MCP runtime, broad CRUD, automatic eligibility, and
  historical evidence mutation out of scope.
- Contracts require `safe_to_show=true`, reviewed redaction, source evidence,
  retrieval boundary evidence, and prompt eligibility artifact evidence before
  card text can enter prompt context.

Commit message:

```text
docs(v2): define test knowledge card prompt context evidence contracts
```

## Task 3: Add TestKnowledgeCard Prompt Context Evidence Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving prompt context
evidence cannot bypass bounded snippets, source hashes, safe-to-show,
redaction, source evidence, retrieval boundary evidence, or prompt/skill trace
links.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_prompt_context_evidence_contract_golden.py`
- `docs/fixtures/29-test-knowledge-card-prompt-context-evidence-golden.md`
- `docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_evidence_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names prompt context evidence inputs, bounded snippet, source hash,
  source manifest, retrieval boundary artifact, prompt eligibility artifact,
  PromptVersion, SkillVersion, context manifest, omission reasons, failure
  behavior, and forbidden side effects.
- Golden proves no prompt assembly implementation, prompt runtime execution,
  provider call, retrieval ranking change, vector index, embedding, reranking,
  graph job, MCP runtime, broad CRUD, automatic eligibility, historical
  evidence mutation, RBAC, tenants, or permissions is created by the contract.

Commit message:

```text
test(golden): add test knowledge card prompt context evidence smoke
```

## Slice 41 Completion Gate

Goal: Validate Slice 41 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_evidence_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_retrieval_boundary_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 41 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.

Commit message:

```text
docs(v2): complete test knowledge card prompt context evidence slice
```
