# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 04: AI Runtime Core.

## Current Task

Task 2: Add Artifact store service.

## Product Value Answer

After this task, Chtest can write and read local artifact files safely, calculate
sha256 and size metadata, and give later ContextArtifact, mock-provider, worker,
and report tasks one shared evidence storage path.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-04-ai-runtime-core.md`
3. `docs/contracts/04-artifact-contract.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement review or case generation product pages.
- CI/CD Quality Center implementation docs beyond artifact owner references.
- Frontend page polish docs.
- RAG runtime, vector index, embedding, chunking, or reranking docs.
- MCP runtime integration docs.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/ai_runtime/artifact_store.py
backend/app/modules/ai_runtime/schemas.py
backend/app/tests/artifacts/test_artifact_store.py
```

Read nearby AI Runtime model/schema files only to follow existing patterns.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/artifacts/test_artifact_store.py -q
```

Expected result: the artifact store focused test passes.

## Acceptance

- Artifact store writes through a temporary file and atomically renames into place.
- Artifact store calculates `sha256` and `size_bytes` from bytes written.
- Artifact store rejects path traversal and absolute paths outside the configured artifact root.
- Artifact store can read an artifact-relative path back from the local root.
- No S3/MinIO, download API, database writes, ContextArtifact API, mock provider, worker handler, frontend, vector index, RAG storage, or MCP runtime is added in this task.
- `git status --short` shows only the expected Artifact store files before commit.

## Commit Message

```text
feat(artifact): add local artifact store
```

## Next Task

Slice 04 Task 3: Add ContextArtifact API.
