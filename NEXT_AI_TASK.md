# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 05: Prompt And Skill Registry.

## Current Task

Task 2: Add built-in prompt files.

## Product Value Answer

After this task, Chtest has deterministic built-in prompt markdown files with
machine-readable input/output schemas, so later registry loading and AI task
execution can trace prompt content by version and hash.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-05-prompt-skill-registry.md`
3. `docs/contracts/05-prompt-skill-contract.md`
4. `docs/contracts/07-seed-data-contract.md`
5. `docs/contracts/08-mock-provider-contract.md`
6. `docs/fixtures/05-minimal-prompt-skill-seeds.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement review or case generation product pages.
- Prompt editing, optimization, A/B testing, and real provider integration docs.
- CI/CD Quality Center implementation docs beyond artifact owner references.
- RAG runtime, vector index, embedding, chunking, or reranking docs.
- MCP runtime integration docs.

## Expected Files

Create or update only these files for the current task:

```text
prompts/requirement_review/v1.md
prompts/risk_matrix/v1.md
prompts/case_generation/v1.md
prompts/case_review/v1.md
prompts/automation_draft_generation/v1.md
prompts/cicd_change_analysis/v1.md
prompts/unit_test_generation/v1.md
prompts/regression_selection/v1.md
prompts/tool_execution/v1.md
prompts/failure_analysis/v1.md
prompts/report_generation/v1.md
backend/app/tests/prompt_skill/test_prompt_files.py
```

Read existing prompt/skill contracts and mock provider outputs only to align schemas.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_prompt_files.py -q
```

Expected result: the built-in prompt file focused test passes.

## Acceptance

- Every required prompt file exists with Agent, Purpose, Input Schema, Output Schema, Instructions, and Failure Output sections.
- Input Schema and Output Schema blocks parse as JSON objects.
- Prompt output instructions require JSON-only responses and no markdown fences.
- Prompt files contain no secrets and no customer data.
- No skill markdown files, registry loader, API, frontend, real provider, vector index, RAG storage, or MCP runtime is added in this task.
- `git status --short` shows only expected prompt files and required task docs before commit.

## Commit Message

```text
feat(prompt): add built-in v1 prompts
```

## Next Task

Slice 05 Task 3: Add built-in skill files.
