# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 31: Knowledge Prompt/Skill Seeds.

## Current Task

Slice 31 Completion Gate.

## Product Value Answer

After this task, Chtest has committed the final knowledge-agent prompt and skill
seed set with focused verification evidence.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/05-prompt-skill-contract.md`
4. `docs/implementation/04-ai-vibecoding-governance.md`
5. `docs/implementation/10-v2-scope-options.md`
6. `docs/implementation/11-final-rag-agent-strategy.md`
7. `docs/implementation/slices/slice-31-knowledge-prompt-skill-seeds.md`
8. `docs/fixtures/19-knowledge-prompt-skill-seeds.md`
9. `memory/08-session-handoff.md`
10. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, and provider implementation
  docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/tests/prompt_skill/test_registry_loader.py
backend/app/tests/prompt_skill/test_skill_files.py
backend/app/tests/prompt_skill/test_knowledge_prompt_skill_seeds.py
docs/implementation/slices/slice-31-knowledge-prompt-skill-seeds.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Seed registry task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, external provider integrations, vector database,
embeddings, reranking, background indexing, graph runtime, MCP runtime,
artifact upload/mutation/delete, generated-case auto-approval, runner behavior
changes, report generation behavior changes, remote CI provider behavior, RBAC,
tenants, or permissions.

## Verification Command

```bash
/Users/yanchen/VscodeProject/Chtest/backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_registry_loader.py backend/app/tests/prompt_skill/test_skill_files.py backend/app/tests/prompt_skill/test_knowledge_prompt_skill_seeds.py -q
git diff --check
```

Expected result: registry loader and skill-file smokes account for the complete
knowledge-agent prompt/skill seed set, and diff check passes.

## Acceptance

- Registry loader discovery count is updated for the complete prompt and skill
  seed set.
- Skill-file contract smoke includes the new skills and their expected agents.
- Knowledge prompt/skill seed smoke stays green.
- Slice 31 task table records completion.
- No RAG runtime, MCP runtime, provider, vector, graph, frontend, API,
  migration, runner, or report behavior is added.

## Commit Message

```text
docs(prompt-skill): add knowledge agent seed prompts
```

## Next Task

Select and plan the next narrow V2 task after Slice 31 completion.
