# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

V1 Completion Review.

## Current Task

Task 1: Audit V1 completion evidence and remaining gaps.

## Product Value Answer

After this task, Chtest has a clear V1 completion audit: which evidence loops
are implemented, which verification commands pass, which gaps remain, and what
the next release-acceptance task should be.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`
9. `docs/implementation/00-v0.1-walking-skeleton.md`
10. `docs/fixtures/00-v1-demo-path.md`
11. `docs/implementation/slices/slice-17-extension-surface.md`

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/06-v1-completion-audit.md
```

Audit-only task. Do not add product code, RAG runtime, MCP runtime, RBAC,
tenants, permissions, marketplace, cloud sync, release automation, or remote CI
provider integration.

## Verification Command

```bash
test -f docs/implementation/06-v1-completion-audit.md && rg -n "Implemented|Remaining gaps|Verification|Next task" docs/implementation/06-v1-completion-audit.md
```

Expected result: V1 completion audit exists and names evidence, gaps,
verification, and next task.

## Acceptance

- Audits implemented V1 evidence loops against `docs/fixtures/00-v1-demo-path.md`.
- Lists passing verification commands already available.
- Lists remaining gaps without implementing them.
- Names one next release-acceptance task.
- Keeps V1 non-goals out of scope.

## Commit Message

```text
docs(v1): add completion audit
```

## Next Task

V1 release acceptance or gap closure task named by the audit.
