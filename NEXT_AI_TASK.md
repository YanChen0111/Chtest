# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 04: AI Runtime Core.

## Current Task

Task 4: Add Mock LLM Provider.

## Product Value Answer

After this task, Chtest can produce deterministic mock LLM outputs for AI runtime
tests without external network, paid API keys, or real provider dependencies.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-04-ai-runtime-core.md`
3. `docs/contracts/08-mock-provider-contract.md`
4. `docs/contracts/05-prompt-skill-contract.md`
5. `docs/contracts/04-artifact-contract.md`
6. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement review or case generation product pages.
- CI/CD Quality Center implementation docs beyond artifact owner references.
- Frontend page polish docs.
- RAG runtime, vector index, embedding, chunking, or reranking docs.
- MCP runtime integration docs.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/ai_runtime/providers/base.py
backend/app/modules/ai_runtime/providers/mock_provider.py
backend/app/modules/ai_runtime/schemas.py
backend/app/tests/ai_runtime/test_mock_provider.py
```

Read fixtures only when needed for deterministic mock output shape.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_mock_provider.py -q
```

Expected result: the deterministic mock provider focused test passes.

## Acceptance

- Mock provider never calls external network.
- Mock provider supports success, provider_error, schema_invalid, and timeout test modes.
- Success output is deterministic and echoes `used_context_artifact_ids` when context is provided.
- Mock provider can create raw, parsed, schema validation, and error artifact payloads through the local artifact store interface if tests require artifact capture.
- No OpenAI-compatible provider, worker handler, AI Task API, business agent endpoint, frontend, vector index, RAG storage, or MCP runtime is added in this task.
- `git status --short` shows only expected mock-provider files before commit.

## Commit Message

```text
feat(ai-runtime): add deterministic mock provider
```

## Next Task

Slice 04 Task 5: Add AI Task Enqueue And Worker Handler.
