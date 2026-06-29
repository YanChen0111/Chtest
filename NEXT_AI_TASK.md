# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 05: Prompt And Skill Registry.

## Current Task

Task 4: Add registry loader and hash logic.

## Product Value Answer

After this task, Chtest can idempotently load built-in PromptVersion and
SkillVersion records from runtime markdown files with stable content hashes, so
AI tasks can trace exact prompt and skill versions.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-05-prompt-skill-registry.md`
3. `docs/contracts/05-prompt-skill-contract.md`
4. `docs/contracts/07-seed-data-contract.md`
5. `docs/fixtures/05-minimal-prompt-skill-seeds.md`
6. `docs/implementation/04-ai-vibecoding-governance.md`

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
backend/app/modules/prompt_skill/registry_loader.py
backend/app/modules/prompt_skill/service.py
backend/app/tests/prompt_skill/test_registry_loader.py
```

Read existing prompt/skill contracts and runtime `prompts/` and `skills/` files
only to align parsing and hash behavior.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_registry_loader.py -q
```

Expected result: the registry loader focused test passes.

## Acceptance

- Loader discovers all built-in prompt and skill runtime markdown files.
- Loader computes stable `sha256:` content hashes.
- Loader creates PromptVersion and SkillVersion records idempotently.
- Loader does not overwrite an already existing name/version with different
  active content.
- Parsed prompt schemas and skill gates/permissions follow
  `docs/contracts/05-prompt-skill-contract.md`.
- No prompt/skill markdown content changes, API, frontend, real provider,
  vector index, RAG storage, or MCP runtime is added in this task.
- `git status --short` shows only expected loader/service/test files and
  required task docs before commit.

## Commit Message

```text
feat(prompt-skill): add registry loader
```

## Next Task

Slice 05 Task 5: Add mock-provider eval bench.
