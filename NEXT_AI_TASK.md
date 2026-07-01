# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 31: Generated Case Knowledge Evidence Persistence.

## Current Task

Slice 31 Task 2: Confirm Persistence Contract Boundary.

## Product Value Answer

After this task, contracts explicitly state how generated-case knowledge
evidence fields are persisted and returned before backend implementation starts.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md`
9. `docs/fixtures/18-test-knowledge-card-contract-golden.md`
10. `memory/08-session-handoff.md`
11. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, and provider implementation
  docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract clarification task. Do not add frontend code, backend runtime feature
code, tests, migrations, package upgrades, external provider integrations,
vector database, embeddings, reranking, background indexing, graph runtime, MCP
runtime, artifact upload/mutation/delete, generated-case auto-approval, runner
behavior changes, report generation behavior changes, remote CI provider
behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
rg -n "source_knowledge_evidence_ids|knowledge_evidence_refs_json|review_findings_json|coverage_gap_notes|RAG runtime|MCP runtime" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md
git diff --check
```

Expected result: contracts describe persistence and API display behavior for
generated-case knowledge evidence fields and preserve runtime non-goals; diff
check passes.

## Acceptance

- Contracts state the fields are persisted on GeneratedCaseCandidate when
  present in normalized AI output.
- Contracts state list API returns the fields with safe defaults.
- Contracts state absent evidence remains backward-compatible.
- Contracts preserve no RAG runtime, MCP runtime, vector, embedding, reranking,
  external provider, graph runtime, auto-approval, runner, report, RBAC, tenant,
  permission, and remote CI provider boundaries.

## Commit Message

```text
docs(v2): clarify generated case knowledge evidence persistence
```

## Next Task

Slice 31 Task 3: Persist Generated-Case Knowledge Evidence Fields.
