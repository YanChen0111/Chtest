# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 53: KnowledgeAdapter Provider Evaluation Review Audit Handoff Contract.

## Current Task

Slice 53 Task 3: Add KnowledgeAdapter provider evaluation review audit handoff
golden smoke.

## Product Value Answer

After this task, Chtest has a contract-level fixture and golden smoke proving
KnowledgeAdapter provider evaluation review audit handoff remains evidence
packaging only. Future planning can trace summary export, review decision,
provider evaluation plan, source hashes, and ReviewHistory without enabling
providers, mutating provider state, or creating runtime retrieval behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md`
5. `backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_audit_handoff_contract_golden.py`
6. `docs/fixtures/41-knowledge-adapter-provider-evaluation-review-audit-handoff-golden.md`
7. `backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_summary_export_contract_golden.py`
8. `docs/fixtures/40-knowledge-adapter-provider-evaluation-review-summary-export-golden.md`
9. `memory/08-session-handoff.md`
10. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  runtime retrieval docs, and provider SDK docs unless a concrete blocker
  requires them.

## Expected Files

Update only these files for the current task:

```text
backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_audit_handoff_contract_golden.py
docs/fixtures/41-knowledge-adapter-provider-evaluation-review-audit-handoff-golden.md
docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden smoke only. Do not add frontend code, backend runtime feature code,
report generation behavior changes, export/download endpoints, migrations,
package upgrades, broad KnowledgeAdapter CRUD implementation, backend feature
API, frontend page, automatic prompt eligibility, prompt assembly
implementation, prompt runtime execution, provider calls, deterministic
retrieval behavior change, automatic knowledge ingestion, external provider
integrations, vector database, embeddings, reranking, graph runtime, MCP
runtime, provider SDK, credentials, provider enablement, runtime retrieval,
provider-backed prompt context evidence, artifact upload/mutation/delete,
historical evidence mutation, provider evaluation review summary export
mutation, provider evaluation review decision mutation, provider evaluation
plan mutation, generated-case auto-approval, runner behavior changes, remote
CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_audit_handoff_contract_golden.py -q
git diff --check
```

Expected result: focused golden smoke passes and diff check passes.

## Acceptance

- Golden names KnowledgeAdapter Provider Evaluation Review Audit Handoff,
  provider evaluation review audit handoff, provider evaluation review summary
  export artifact, provider evaluation review decision artifact, provider
  evaluation plan artifact, evidence chain status, included artifact ids,
  excluded artifact reasons, provider review decision group summary,
  unresolved blocker summary, unresolved safety question summary,
  KnowledgeEvidence, provider_state, fallback behavior, disabled by default
  policy, ReviewHistory, failure behavior, and forbidden side effects.
- Golden proves no provider SDK, external call, vector database, embedding,
  reranking, background indexing, runtime retrieval, provider-backed prompt
  context evidence, UI, export/download endpoint, RBAC, tenants, permissions,
  package upgrade, or provider-state mutation is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 53 Completion Gate.

## Commit Message

```text
test(golden): add knowledge adapter provider evaluation review audit handoff smoke
```

## Next Task

Slice 53 Completion Gate.
