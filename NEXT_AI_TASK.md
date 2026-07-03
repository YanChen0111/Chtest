# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 34: Knowledge Feedback Contract.

## Current Task

Slice 34 Task 1: Add Knowledge Feedback Contract task plan.

## Product Value Answer

After this task, Chtest has a narrow plan for KnowledgeFeedbackAgent feedback
contracts before any feedback runtime, TestKnowledgeCard CRUD, or prompt
eligibility automation exists.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/02-api-contract.md`
4. `docs/contracts/03-state-machines.md`
5. `docs/contracts/05-prompt-skill-contract.md`
6. `prompts/knowledge_feedback/v1.md`
7. `skills/knowledge-feedback-skill/v1.md`
8. `docs/implementation/11-final-rag-agent-strategy.md`
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
docs/implementation/slices/slice-34-knowledge-feedback-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Planning-only task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, KnowledgeFeedbackAgent runtime,
TestKnowledgeCard CRUD, prompt-eligible auto-marking, automatic knowledge
ingestion, external provider integrations, vector database, embeddings,
reranking, graph runtime, MCP runtime, provider SDK, credentials, artifact
upload/mutation/delete, historical review/failure/report/TestCase mutation,
generated-case auto-approval, runner behavior changes, report generation
behavior changes, remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
test -f docs/implementation/slices/slice-34-knowledge-feedback-contract.md
rg -n "Knowledge Feedback Contract|KnowledgeFeedbackAgent|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-34-knowledge-feedback-contract.md NEXT_AI_TASK.md
git diff --check
```

Expected result: Slice 34 plan file exists, required plan terms are present,
and diff check passes.

## Acceptance

- Slice 34 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names KnowledgeFeedbackAgent, accepted/rejected cases,
  ReviewHistory, FailureAnalysis, Report, KnowledgeEvidence, draft feedback,
  human review, prompt eligibility, and feedback fallback boundaries.
- `NEXT_AI_TASK.md` points to Task 2.

## Commit Message

```text
docs(v2): add knowledge feedback contract plan
```

## Next Task

Slice 34 Task 2: Define KnowledgeFeedbackAgent draft feedback contracts.
