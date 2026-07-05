# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 53: KnowledgeAdapter Provider Evaluation Review Audit Handoff Contract.

## Current Task

Slice 53 Task 2: Define KnowledgeAdapter provider evaluation review audit
handoff contracts.

## Product Value Answer

After this task, Chtest has data, API, state-machine, artifact, and
prompt/skill contracts for handing provider evaluation review summary export
evidence into one audit handoff bundle. Future planning can trace the summary
export back to the review decision, provider evaluation plan, provider
metadata, license/reference evidence, KnowledgeEvidence normalization,
provider_state, fallback behavior, disabled-by-default decision, source
hashes, and ReviewHistory without enabling providers or changing runtime
behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md`
5. `docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md`
6. `backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_summary_export_contract_golden.py`
7. `docs/fixtures/40-knowledge-adapter-provider-evaluation-review-summary-export-golden.md`
8. `memory/08-session-handoff.md`
9. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  runtime retrieval docs, and provider SDK docs unless a concrete blocker
  requires them.

## Expected Files

Update only these files for the current task:

```text
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/contracts/05-prompt-skill-contract.md
docs/implementation/10-v2-scope-options.md
docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract-only. Do not add frontend code, backend runtime feature code, report
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
rg -n "KnowledgeAdapter Provider Evaluation Review Audit Handoff|knowledge_adapter_provider_evaluation_review_audit_handoff|build_knowledge_adapter_provider_evaluation_review_audit_handoff|provider evaluation review summary export artifact|provider evaluation review decision artifact|provider evaluation plan artifact|evidence chain status|included artifact ids|excluded artifact reasons|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md
git diff --check
```

Expected result: required terms are present in contracts and plan, and diff
check passes.

## Acceptance

- Contracts define provider evaluation review audit handoff inputs, outputs,
  evidence chain status labels, summary export artifact linkage, review
  decision artifact linkage, provider evaluation plan artifact linkage,
  included/excluded artifact handling, unresolved follow-up flags,
  ReviewHistory, failure behavior, and forbidden side effects.
- Contracts exclude provider enablement, provider integration, provider SDKs,
  external calls, vector database, embeddings, reranking, runtime retrieval,
  UI, export/download endpoints, RBAC, tenants, permissions, and package
  upgrades.
- `NEXT_AI_TASK.md` points to Slice 53 Task 3.

## Commit Message

```text
docs(v2): define knowledge adapter provider evaluation review audit handoff contracts
```

## Next Task

Slice 53 Task 3: Add KnowledgeAdapter provider evaluation review audit handoff
golden smoke.
