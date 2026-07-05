# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 53: KnowledgeAdapter Provider Evaluation Review Audit Handoff Contract.

## Current Task

Slice 53 Task 1: Add KnowledgeAdapter Provider Evaluation Review Audit Handoff task plan.

## Product Value Answer

After this task, Chtest has a narrow plan for handing provider evaluation
review summary export evidence into one audit handoff bundle. Future planning
can trace the summary export back to the review decision, provider evaluation
plan, provider metadata, license/reference evidence, KnowledgeEvidence
normalization, provider_state, fallback behavior, disabled-by-default decision,
source hashes, and ReviewHistory without enabling providers or changing
runtime behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md`
5. `backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_summary_export_contract_golden.py`
6. `docs/fixtures/40-knowledge-adapter-provider-evaluation-review-summary-export-golden.md`
7. `memory/08-session-handoff.md`
8. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  runtime retrieval docs, and provider SDK docs unless a concrete blocker
  requires them.

## Expected Files

Update only these files for the current task:

```text
docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Planning only. Do not add frontend code, backend runtime feature code, report
generation behavior changes, export/download endpoints, migrations, package
upgrades, broad KnowledgeAdapter CRUD implementation, backend feature API,
frontend page, automatic prompt eligibility, prompt assembly implementation,
prompt runtime execution, provider calls, deterministic retrieval behavior
change, automatic knowledge ingestion, external provider integrations, vector
database, embeddings, reranking, graph runtime, MCP runtime, provider SDK,
credentials, provider enablement, runtime retrieval, provider-backed prompt
context evidence, artifact upload/mutation/delete, historical evidence
mutation, provider evaluation review summary export mutation, provider
evaluation review decision mutation, provider evaluation plan mutation,
generated-case auto-approval, runner behavior changes, remote CI provider
behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
test -f docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md
rg -n "KnowledgeAdapter Provider Evaluation Review Audit Handoff|provider evaluation review audit handoff|knowledge_adapter_provider_evaluation_review_audit_handoff|provider evaluation review summary export artifact|provider evaluation review decision artifact|provider evaluation plan artifact|evidence chain status|included artifact ids|excluded artifact reasons|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Expected result: plan file exists, required terms are present, and diff check
passes.

## Acceptance

- Slice 53 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit message.
- The plan names audit handoff inputs and outputs, summary export artifact
  linkage, review decision artifact linkage, provider evaluation plan artifact
  linkage, evidence chain status, included/excluded artifact handling,
  ReviewHistory, failure behavior, and forbidden side effects.
- The plan excludes provider enablement, provider integration, provider SDKs,
  external calls, vector database, embeddings, reranking, runtime retrieval,
  UI, export/download endpoints, RBAC, tenants, permissions, and package
  upgrades.
- `NEXT_AI_TASK.md` points to Slice 53 Task 2.

## Commit Message

```text
docs(v2): add knowledge adapter provider evaluation review audit handoff plan
```

## Next Task

Slice 53 Task 2: Define KnowledgeAdapter provider evaluation review audit
handoff contracts.
