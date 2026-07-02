# Slice 31: Knowledge Prompt/Skill Seeds

## Goal

Add draft PromptVersion and SkillVersion seed files for the final
knowledge-driven agent flow without enabling RAG runtime, provider calls, vector
indexes, graph runtime, MCP runtime, or generated-case auto-approval.

Slice 30 defined `TestKnowledgeCard`, `KnowledgeEvidence`, and generated-case
evidence fields. Slice 31 makes the next low-conflict step: prepare versioned
prompt and skill seeds that future agents can load, validate, and evaluate.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- `docs/implementation/11-final-rag-agent-strategy.md`
- `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
- `docs/fixtures/18-test-knowledge-card-contract-golden.md`
- `docs/fixtures/05-minimal-prompt-skill-seeds.md`

## Product Value Answer

After this slice, Chtest has versioned prompt and skill seed files for
knowledge-card extraction, requirement understanding, risk analysis, coverage
analysis, test design, evidence-backed case generation/review, dedup,
automation readiness, and knowledge feedback, so future agent work can start
from traceable contracts instead of ad hoc prompts.

## Reference Notes

- Awesome LLM Apps is used only as a reference for focused agent/RAG app
  decomposition and skill-style reusable instructions.
- PageIndex-style ideas are used only as a reference for tree/section-level
  source traceability in knowledge-card extraction prompts.
- Microsoft GraphRAG-style relationship reasoning is used only as a review
  concept over already supplied local evidence. This slice does not run
  GraphRAG indexing or graph extraction.

## Non-goals

- No RAG runtime, external KnowledgeAdapter provider call, provider SDK,
  background indexing pipeline, vector database, embedding service, semantic
  search, reranking, chunking pipeline, GraphRAG runtime, graph database, or
  offline graph extraction job.
- No MCP runtime, MCP server/client transport, marketplace, plugin install,
  remote MCP call, or ToolDefinition behavior change.
- No frontend implementation, prompt editor, eval console, model leaderboard,
  dashboard, runner behavior, report generation behavior, or API behavior.
- No generated-case auto-approval, automatic TestCase promotion, review bypass,
  automation execution, business source modification, artifact upload/mutation,
  cloud storage, RBAC, tenants, permissions, scheduling, PR comments, deploy,
  release, merge, or push behavior.

## Slice Boundary

- Add runtime prompt seeds:
  - `knowledge_card_extraction:v1`
  - `requirement_understanding:v1`
  - `risk_analysis:v1`
  - `coverage_analysis:v1`
  - `test_design:v1`
  - `evidence_case_generation:v1`
  - `evidence_case_review:v1`
  - `case_dedup:v1`
  - `automation_readiness:v1`
  - `knowledge_feedback:v1`
- Add runtime skill seeds:
  - `knowledge-ingestion-skill:v1`
  - `risk-analysis-skill:v1`
  - `coverage-analysis-skill:v1`
  - `test-design-skill:v1`
  - `knowledge-feedback-skill:v1`
- Add fixture documentation describing the seed set and boundaries.
- Update the prompt/skill contract and existing seed fixture so built-in
  registry discovery remains aligned with documentation.
- Add a focused smoke test proving seed files exist, follow the contract
  sections, reference `TestKnowledgeCard` / `KnowledgeEvidence`, and preserve
  no-runtime boundaries.
- Update registry-loader tests only for expected built-in seed counts.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add knowledge Prompt/Skill seeds | done | `/Users/yanchen/VscodeProject/Chtest/backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_knowledge_prompt_skill_seeds.py -q && git diff --check` | pending | seed files only |
| Update prompt/skill registry count smoke | done | `/Users/yanchen/VscodeProject/Chtest/backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_registry_loader.py backend/app/tests/prompt_skill/test_skill_files.py backend/app/tests/prompt_skill/test_knowledge_prompt_skill_seeds.py -q && git diff --check` | pending | registry discovery only |
| Slice 31 completion gate | done | `/Users/yanchen/VscodeProject/Chtest/backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_registry_loader.py backend/app/tests/prompt_skill/test_skill_files.py backend/app/tests/prompt_skill/test_knowledge_prompt_skill_seeds.py -q && git diff --check` | pending | docs and handoff |

## Verification Command

```bash
/Users/yanchen/VscodeProject/Chtest/backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_registry_loader.py backend/app/tests/prompt_skill/test_skill_files.py backend/app/tests/prompt_skill/test_knowledge_prompt_skill_seeds.py -q
git diff --check
```

Expected result: prompt/skill seed files are discoverable, parseable, contract
aligned, and no whitespace errors exist.

## Acceptance

- Knowledge-driven prompt seeds exist and include Agent, Purpose, Input Schema,
  Output Schema, Instructions, and Failure Output.
- Knowledge-driven skill seeds exist and include Applies To, Methodology, Input
  Contract, Output Contract, Quality Gates, Forbidden Actions, and Tool
  Permissions.
- Seed content uses `TestKnowledgeCard` and normalized `KnowledgeEvidence`
  terminology.
- Seed content explicitly forbids external provider calls, vector indexes, MCP
  runtime, and generated-case promotion.
- Registry loader discovery remains deterministic after adding the new seed
  files.
- `docs/contracts/05-prompt-skill-contract.md` and
  `docs/fixtures/05-minimal-prompt-skill-seeds.md` list the new seeds.
- The slice does not add runtime retrieval, provider integration, frontend,
  API, database, migration, runner, or MCP behavior.

## Commit Message

```text
docs(prompt-skill): add knowledge agent seed prompts
```

## Next Task

Slice 32 candidate: Agent workflow contract for requirement-to-reviewed-case.
