# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 05: Prompt And Skill Registry.

## Current Task

Task 1: Add PromptVersion and SkillVersion models.

## Product Value Answer

After this task, Chtest can persist versioned PromptVersion and SkillVersion
records so every AI task can trace which prompt and skill contract produced its
output.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-05-prompt-skill-registry.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/05-prompt-skill-contract.md`
5. `docs/contracts/07-seed-data-contract.md`
6. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement review or case generation product pages.
- Prompt file content details beyond model fields and version/hash constraints.
- CI/CD Quality Center implementation docs beyond artifact owner references.
- RAG runtime, vector index, embedding, chunking, or reranking docs.
- MCP runtime integration docs.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/prompt_skill/models.py
backend/app/modules/prompt_skill/schemas.py
backend/alembic/versions/<revision>_prompt_skill_registry.py
backend/app/tests/db/test_prompt_skill_models.py
```

Read existing AI Runtime and Project Core model tests only to follow SQLAlchemy, Alembic, and SQLite/PostgreSQL compatibility patterns.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_prompt_skill_models.py -q
```

Expected result: the Prompt/Skill model focused test passes.

## Acceptance

- PromptVersion and SkillVersion tables match the data and Prompt/Skill contracts.
- Records carry stable identifiers, semantic version fields, lifecycle status, content hash, schema/config JSON, and timestamps.
- Uniqueness constraints prevent duplicate active logical versions.
- SQLite tests and PostgreSQL migration remain compatible with existing project patterns.
- No built-in prompt markdown files, skill markdown files, registry loader, API, frontend, real provider, vector index, RAG storage, or MCP runtime is added in this task.
- `git status --short` shows only expected Prompt/Skill model files and required task docs before commit.

## Commit Message

```text
feat(prompt-skill): add prompt and skill models
```

## Next Task

Slice 05 Task 2: Add built-in prompt files.
