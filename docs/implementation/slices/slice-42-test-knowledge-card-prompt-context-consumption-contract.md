# Slice 42: TestKnowledgeCard Prompt Context Consumption Contract Task Plan

## Goal

Define the prompt context consumption contract for future agents that receive
TestKnowledgeCard prompt context evidence before any prompt assembly
implementation, prompt runtime execution, provider call, deterministic
retrieval behavior change, vector index, frontend page, backend feature API,
broad TestKnowledgeCard CRUD, or automatic prompt eligibility exists.

This slice is contract-first. It documents how future agent inputs may
reference TestKnowledgeCard prompt context evidence and how future outputs may
cite consumed knowledge while preserving prompt context evidence artifact ids,
context manifest links, source hashes, PromptVersion, SkillVersion,
ReviewHistory, `used_knowledge` semantics, output citations, review gates, and
failure behavior boundaries.

## Product Value Answer

After this slice, Chtest can describe exactly when an AI workflow is allowed to
say it used TestKnowledgeCard knowledge. Users get auditable consumption
evidence: the agent input references the prompt context evidence artifact, the
output cites bounded card evidence by source hash/context entry, and
`used_knowledge=true` is allowed only when the consumed evidence and citations
are valid.

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
- Current contracts keep `used_knowledge=false` unless deterministic local
  evidence exists. Slice 41 explicitly does not auto-mark `used_knowledge=true`
  and does not write runtime `prompt_input.json`.

## Non-goals

- No prompt assembly implementation, prompt runtime execution, LLM/provider
  call, provider SDK, credentials, OAuth, remote URL fetch, prompt runner,
  queue, scheduler, background worker, or AITask execution behavior change.
- No prompt runtime retrieval implementation, deterministic retrieval behavior
  change, deterministic retrieval ranking change, vector database, embeddings,
  reranking, background indexing, graph runtime, GraphRAG job, MCP runtime, or
  external KnowledgeAdapter provider call.
- No model output behavior implementation, automatic citation generation,
  automatic `used_knowledge=true` marking, prompt input generation, or runtime
  prompt template rendering.
- No broad TestKnowledgeCard CRUD implementation, backend feature API,
  frontend page, migration, card table change, automatic prompt eligibility,
  automatic card creation from model output, automatic card approval,
  automatic knowledge ingestion, or KnowledgeIngestionAgent runtime.
- No artifact upload, artifact mutation, artifact delete, source artifact
  mutation, prompt context evidence mutation, retrieval boundary artifact
  mutation, prompt eligibility artifact mutation, historical evidence mutation,
  ReviewHistory mutation, FailureAnalysis mutation, Report mutation,
  TestRun/TestResult mutation, TestCase mutation, GeneratedCaseCandidate
  mutation, KnowledgeEvidence mutation, PromptVersion mutation, SkillVersion
  mutation, or existing TestKnowledgeCard content mutation.
- No automatic duplicate merge, card replacement, card archive/delete,
  generated-case auto-approval, TestCase auto-promotion, runner behavior
  change, report generation behavior change, remote CI provider behavior, RBAC,
  tenants, permissions, or package upgrades.

## Contract Boundary To Define

The follow-up contract task should define:

- Prompt context consumption input:
  - prompt request id or AITask id when available;
  - consuming agent step name and intended output artifact type;
  - PromptVersion id/name/version and SkillVersion id/name/version;
  - prompt context evidence artifact id;
  - `test_knowledge_card_prompt_context_evidence.json` artifact reference;
  - context manifest artifact id;
  - selected TestKnowledgeCard ids and consumed context entry ids;
  - source manifest ids, source artifact ids, source sections, and source
    hashes;
  - retrieval boundary artifact id;
  - prompt eligibility artifact ids;
  - ReviewHistory ids;
  - omission summaries and unsupported claims when present.
- Consumption decision fields:
  - future scoped action name such as `consume_prompt_context_evidence`;
  - `used_knowledge=false` when no valid prompt context evidence is consumed;
  - `used_knowledge=true` only when the input references valid prompt context
    evidence and output citations point back to consumed entries;
  - consumed TestKnowledgeCard ids;
  - consumed prompt context entry ids;
  - consumed source hashes or source quote/hash pointers;
  - skipped evidence ids and skip reasons;
  - citation mismatch, stale evidence, unsafe evidence, or revoked evidence
    failure codes.
- Output citation fields:
  - output artifact id and agent step name;
  - cited TestKnowledgeCard id;
  - cited prompt context evidence artifact id;
  - cited context entry id;
  - cited source hash or source quote/hash pointer;
  - source artifact id and source section;
  - PromptVersion/SkillVersion trace;
  - ReviewHistory id;
  - citation confidence or citation status;
  - unsupported claim marker when output text cannot be traced to consumed
    evidence.
- Safety requirements:
  - outputs may cite only prompt context evidence that was included in the
    agent input contract;
  - `used_knowledge=true` requires at least one valid consumed citation;
  - a citation must reference a source hash/context entry rather than raw large
    source text;
  - stale, unsafe, revoked, cross-project, redaction-failed, unbounded, or
    unsupported evidence must be omitted or must fail the consumption contract;
  - unsupported claims remain visible as warnings or review findings, not
    knowledge-backed facts.
- Outputs:
  - prompt context consumption artifact id when a later slice defines one;
  - `used_knowledge` decision;
  - consumed knowledge citations;
  - omitted or skipped evidence summaries;
  - source manifest ids and source hashes;
  - PromptVersion/SkillVersion trace;
  - context manifest references;
  - failure code for missing, stale, unsafe, cross-project, revoked,
    unsupported, unbounded, citation-mismatched, context-mismatched,
    prompt-version-mismatched, skill-version-mismatched, redaction-failed, or
    evidence-mismatched input.
- Runtime boundary:
  - this slice defines artifact and contract semantics only;
  - it does not assemble prompts, call providers, run AITasks, change retrieval
    ranking, write runtime `prompt_input.json`, auto-mark `used_knowledge`,
    generate model citations, or change frontend behavior.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestKnowledgeCard prompt context consumption task plan | done | `test -f docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md && rg -n "TestKnowledgeCard Prompt Context Consumption|prompt context evidence|used_knowledge|PromptVersion|SkillVersion|source hash|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md NEXT_AI_TASK.md && git diff --check` | `990e757` | planning-only scope |
| Define TestKnowledgeCard prompt context consumption contracts | done | `rg -n "TestKnowledgeCard Prompt Context Consumption|prompt_context_consumption|consume_prompt_context_evidence|used_knowledge|prompt context evidence artifact|citation|PromptVersion|SkillVersion|source hash|context manifest|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md && git diff --check` | `e3aa956` | contract-only |
| Add TestKnowledgeCard prompt context consumption golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_consumption_contract_golden.py -q && git diff --check` | `9da8cc8` | no prompt runtime |
| Slice 42 completion gate | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_consumption_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_evidence_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add TestKnowledgeCard Prompt Context Consumption Task Plan

Goal: Create a narrow plan for prompt context consumption before contract edits
or runtime implementation.

Expected files:

- `docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md
rg -n "TestKnowledgeCard Prompt Context Consumption|prompt context evidence|used_knowledge|PromptVersion|SkillVersion|source hash|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 42 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names prompt context evidence inputs, consumption/citation rules,
  `used_knowledge`, PromptVersion/SkillVersion, source hash/context manifest
  links, failure behavior, and non-goals.
- The plan excludes prompt assembly implementation, prompt runtime execution,
  provider calls, retrieval ranking changes, vector indexes, embeddings,
  reranking, graph jobs, MCP runtime, broad CRUD, automatic eligibility, and
  historical evidence mutation.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add test knowledge card prompt context consumption plan
```

## Task 2: Define TestKnowledgeCard Prompt Context Consumption Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the prompt context consumption boundary for future AI outputs that cite
TestKnowledgeCard prompt context evidence.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard Prompt Context Consumption|prompt_context_consumption|consume_prompt_context_evidence|used_knowledge|prompt context evidence artifact|citation|PromptVersion|SkillVersion|source hash|context manifest|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md
git diff --check
```

Acceptance:

- Contracts define prompt context consumption input, prompt context evidence
  artifact references, context manifest links, consumed TestKnowledgeCard ids,
  consumed source hashes, PromptVersion/SkillVersion trace, ReviewHistory ids,
  output citations, `used_knowledge` semantics, skipped evidence summaries,
  and failure behavior.
- Contracts require `used_knowledge=true` only when valid prompt context
  evidence is consumed and output citations point to consumed evidence.
- Contracts keep prompt assembly implementation, prompt runtime execution,
  provider calls, retrieval ranking changes, vector indexes, embeddings,
  reranking, graph jobs, MCP runtime, broad CRUD, automatic eligibility, and
  historical evidence mutation out of scope.

Commit message:

```text
docs(v2): define test knowledge card prompt context consumption contracts
```

## Task 3: Add TestKnowledgeCard Prompt Context Consumption Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving prompt context
consumption cannot set `used_knowledge=true` or cite TestKnowledgeCard content
without prompt context evidence, source hashes, context manifest links, and
PromptVersion/SkillVersion trace.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_prompt_context_consumption_contract_golden.py`
- `docs/fixtures/30-test-knowledge-card-prompt-context-consumption-golden.md`
- `docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_consumption_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names prompt context evidence artifact id, context manifest,
  `used_knowledge`, consumed TestKnowledgeCard ids, source hash, output
  citations, PromptVersion, SkillVersion, ReviewHistory, skipped evidence,
  failure behavior, and forbidden side effects.
- Golden proves no prompt assembly implementation, prompt runtime execution,
  provider call, retrieval ranking change, vector index, embedding, reranking,
  graph job, MCP runtime, broad CRUD, automatic eligibility, historical
  evidence mutation, RBAC, tenants, or permissions is created by the contract.

Commit message:

```text
test(golden): add test knowledge card prompt context consumption smoke
```

## Slice 42 Completion Gate

Goal: Validate Slice 42 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_consumption_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_evidence_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 42 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.

Commit message:

```text
docs(v2): complete test knowledge card prompt context consumption slice
```
