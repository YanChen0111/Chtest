# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 05: Prompt And Skill Registry.

## Current Task

Task 6: Add Prompt/Skill API.

## Product Value Answer

After this task, Chtest exposes read-only PromptVersion and SkillVersion APIs so
AI tasks and the UI can trace active prompt and skill versions.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-05-prompt-skill-registry.md`
3. `docs/contracts/05-prompt-skill-contract.md`
4. `docs/contracts/07-seed-data-contract.md`
5. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement review or case generation product pages.
- Skill marketplace, plugin import, prompt editing UI, optimization, A/B testing,
  and real provider integration docs.
- CI/CD Quality Center implementation docs beyond artifact owner references.
- RAG runtime, vector index, embedding, chunking, or reranking docs.
- MCP runtime integration docs.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/prompt_skill/router.py
backend/app/modules/prompt_skill/service.py
backend/app/modules/prompt_skill/schemas.py
backend/app/main.py
backend/app/tests/api/test_prompt_skill_registry.py
```

Read existing PromptVersion/SkillVersion schemas and router patterns only to
align list/detail responses.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_prompt_skill_registry.py -q
```

Expected result: the Prompt/Skill registry API focused test passes.

## Acceptance

- API exposes list and detail endpoints for PromptVersion.
- API exposes list and detail endpoints for SkillVersion.
- Responses include version identity, hash, status, applicable Agent(s), and
  schema/gate metadata.
- Endpoints are read-only; no create/update/delete endpoints are added.
- No frontend, real provider, vector index, RAG storage, or MCP runtime is
  added in this task.
- `git status --short` shows only expected registry API files and required task
  docs before commit.

## Commit Message

```text
feat(prompt-skill): add registry api
```

## Next Task

Slice 05 Task 7: Add Prompt/Skill frontend shell.
