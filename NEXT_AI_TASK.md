# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 52: KnowledgeAdapter Provider Evaluation Review Summary Export Contract.

## Current Task

Slice 52 Task 1: Add KnowledgeAdapter Provider Evaluation Review Summary Export
task plan.

## Product Value Answer

After this task, Chtest will have a narrow plan for exporting a local
KnowledgeAdapter provider evaluation review summary as audit evidence for
future planning. The plan must stay contract-only and must not enable a
provider, install a provider SDK, fetch remote URLs, run retrieval, create
vector infrastructure, change prompt context behavior, add a frontend page,
or add RBAC, tenants, or permissions.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md`
5. `backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_decision_contract_golden.py`
6. `docs/fixtures/39-knowledge-adapter-provider-evaluation-review-decision-golden.md`
7. `memory/08-session-handoff.md`
8. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  and runtime retrieval docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Planning-only task. Do not add frontend code, backend runtime feature code,
report generation behavior changes, export/download endpoints, migrations,
package upgrades, broad KnowledgeAdapter CRUD implementation, backend feature
API, frontend page, automatic prompt eligibility, prompt assembly
implementation, prompt runtime execution, provider calls, deterministic
retrieval behavior change, automatic knowledge ingestion, external provider
integrations, vector database, embeddings, reranking, graph runtime, MCP
runtime, provider SDK, credentials, provider enablement, runtime retrieval,
provider-backed prompt context evidence, artifact upload/mutation/delete,
historical evidence mutation, generated-case auto-approval, runner behavior
changes, remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
test -f docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md
rg -n "KnowledgeAdapter Provider Evaluation Review Summary Export|provider evaluation review summary export|export_knowledge_adapter_provider_evaluation_review_summary|knowledge_adapter_provider_evaluation_review_summary_export|provider evaluation review decision artifact|accepted_for_planning|accepted_with_constraints|blocked|needs_revision|unsupported|KnowledgeEvidence|provider_state|fallback behavior|license review|reference intake|disabled by default|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Expected result: plan file exists, required planning terms are present, and
diff check passes.

## Acceptance

- Slice 52 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names provider evaluation review summary export inputs and outputs,
  review decision artifact linkage, accepted/blocked/unsupported/revision
  decision groups, license/reference intake, KnowledgeEvidence normalization,
  provider_state, fallback behavior, disabled by default policy,
  ReviewHistory, failure behavior, and forbidden side effects.
- The plan excludes provider enablement, provider integration, provider SDKs,
  external calls, vector database, embeddings, reranking, background indexing,
  runtime retrieval, UI, RBAC, tenants, permissions, and package upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

## Commit Message

```text
docs(v2): add knowledge adapter provider evaluation review summary export plan
```

## Next Task

Slice 52 Task 2: Define KnowledgeAdapter provider evaluation review summary
export contracts.
