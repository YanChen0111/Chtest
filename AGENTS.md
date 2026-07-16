# Chtest AI Coding Rules

Chtest V1 is a local-first AI testing evidence workbench for individual test
engineers and automation test engineers. AI coding sessions must optimize for
small verified changes, not broad exploration.

## Start Here

Before development work, read:

1. `START_HERE_FOR_AI.md`
2. `NEXT_AI_TASK.md`

Then follow the fast path named by `NEXT_AI_TASK.md`:

1. current Slice task file
2. task-specific contracts
3. task-specific fixtures only when needed

Do not read broad architecture, reference, roadmap, or migration documents
unless the active task or a concrete blocker requires them.

## Current Task Boundary

- Work only on the current task named in `NEXT_AI_TASK.md`.
- `Must Read` files are required.
- `Do Not Read Unless Needed` files should stay out of context unless needed to
  resolve a failure, conflict, or missing definition.
- `Expected Files` is the default write boundary. Read nearby files when needed
  to understand symbols or local patterns, but explain any write outside the
  expected set before making it.
- Prefer the exact `Verification Command` from `NEXT_AI_TASK.md`.

## Source Of Truth

When documents, code, memory, or chat context disagree, use this order:

1. `docs/product/01-positioning-and-scope.md`
2. `docs/contracts/*`
3. `docs/implementation/04-ai-vibecoding-governance.md`
4. `docs/implementation/01-v1-delivery-plan.md`
5. `memory/13-ai-readable-project-brief.md`
6. `docs/fixtures/*`
7. `docs/architecture/*`
8. `docs/reference/*`, `docs/reviews/*`, and `docs/superpowers/*`

Chat history and temporary memory never override contracts. If behavior is not
covered by contracts, update or flag the contract before treating the behavior
as implemented truth.

## Engineering Loop

Every task should be:

- small enough to explain in one sentence;
- tied to one product value answer;
- verified with one focused command;
- self-reviewed with `git diff --check` and `git diff --name-only`;
- committed only after scope and verification are clear, unless the user asks
  not to commit;
- handed off in `NEXT_AI_TASK.md` or `memory/08-session-handoff.md` only when
  task state, slice state, risk, blocker, or priority changes.

Git records code history. Memory records session continuity. Contracts record
implementation truth.

## Do Not Expand Scope

Do not add RBAC, tenants, enterprise collaboration, RAG runtime, MCP runtime
dependency, dashboards, marketplace features, broad CI/CD/cloud CI work, or
unrequested refactors unless the active task explicitly calls for them.
