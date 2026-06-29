# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 05: Prompt And Skill Registry.

## Current Task

Task 3: Add built-in skill files.

## Product Value Answer

After this task, Chtest has deterministic built-in skill markdown files with
methodology, quality gates, forbidden actions, and tool permissions, so later
registry loading and AI task execution can trace skill content by version and
hash.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-05-prompt-skill-registry.md`
3. `docs/contracts/05-prompt-skill-contract.md`
4. `docs/contracts/07-seed-data-contract.md`
5. `docs/fixtures/05-minimal-prompt-skill-seeds.md`
6. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement review or case generation product pages.
- Skill marketplace, plugin import, prompt editing, optimization, A/B testing,
  and real provider integration docs.
- CI/CD Quality Center implementation docs beyond artifact owner references.
- RAG runtime, vector index, embedding, chunking, or reranking docs.
- MCP runtime integration docs.

## Expected Files

Create or update only these files for the current task:

```text
skills/requirement-review-skill/v1.md
skills/test-case-generation-skill/v1.md
skills/testcase-review-skill/v1.md
skills/automation-draft-skill/v1.md
skills/unit-test-generation-skill/v1.md
skills/regression-selection-skill/v1.md
skills/tool-execution-skill/v1.md
skills/failure-analysis-skill/v1.md
skills/report-generation-skill/v1.md
backend/app/tests/prompt_skill/test_skill_files.py
```

Read existing prompt/skill contracts and seed skill files only to align contract
sections.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_skill_files.py -q
```

Expected result: the built-in skill file focused test passes.

## Acceptance

- Every required skill file exists with Applies To, Methodology, Input Contract,
  Output Contract, Quality Gates, Forbidden Actions, and Tool Permissions
  sections.
- Applies To maps each skill to the expected V1 Agent.
- Quality Gates and Forbidden Actions are non-empty.
- Skill files contain no secrets and no customer data.
- No prompt markdown changes, registry loader, API, frontend, real provider,
  vector index, RAG storage, or MCP runtime is added in this task.
- `git status --short` shows only expected skill files and required task docs
  before commit.

## Commit Message

```text
feat(skill): add built-in v1 skills
```

## Next Task

Slice 05 Task 4: Add registry loader and hash logic.
