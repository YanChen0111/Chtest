# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 05: Prompt And Skill Registry.

## Current Task

Task 7: Add Prompt/Skill frontend shell.

## Product Value Answer

After this task, Chtest has a Prompt/Skill Center frontend shell where users can
inspect built-in prompt and skill versions, hashes, applicable agents, and
contract metadata.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-05-prompt-skill-registry.md`
3. `docs/product/06-frontend-ui-guidelines.md`
4. `docs/contracts/05-prompt-skill-contract.md`
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
frontend/src/views/prompt-skill/PromptSkillCenterView.vue
frontend/src/api/promptSkill.ts
frontend/src/stores/promptSkill.ts
frontend/src/router/index.ts
frontend/src/views/prompt-skill/PromptSkillCenterView.spec.ts
```

Precondition: Slice 02.5 Frontend Foundation is complete. Read existing frontend
route/API/store/test patterns only to align the shell.

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: the frontend test suite passes with Prompt/Skill Center shell
coverage.

## Acceptance

- Prompt/Skill Center route renders a read-only shell.
- Frontend API client can load prompt and skill version lists.
- Store tracks loading, error, prompts, and skills.
- View displays version identity, hash, status, applicable Agent(s), and
  schema/gate metadata at shell level.
- No prompt editing, marketplace, real provider, vector index, RAG storage, or
  MCP runtime is added in this task.
- `git status --short` shows only expected frontend files and required task docs
  before commit.

## Commit Message

```text
feat(frontend): add prompt skill center shell
```

## Next Task

Slice 06: Requirement To Case mainline.
