# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Select next V2 small slice.

## Current Task

Select and plan the next narrow V2 task after Slice 27 completion.

## Product Value Answer

After this task, the next V2 slice is selected with a small task boundary,
clear product value, expected files, non-goals, verification, and commit scope.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-24-local-artifact-access-links.md`
9. `docs/implementation/10-v2-scope-options.md`
10. `docs/implementation/slices/slice-25-execution-evidence-summary.md`
11. `docs/implementation/10-v2-scope-options.md`
12. `docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md`
13. `docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md`
14. `memory/08-session-handoff.md`
15. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, and frontend redesign docs unless a concrete blocker
  requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-22-jmeter-local-execution.md
docs/implementation/10-v2-scope-options.md
docs/implementation/slices/slice-23-frontend-build-baseline.md
docs/implementation/slices/slice-24-local-artifact-access-links.md
docs/implementation/slices/slice-25-execution-evidence-summary.md
docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md
docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
backend/app/tests/golden/test_artifact_access_golden.py
docs/fixtures/12-local-artifact-access-golden.md
backend/app/tests/golden/test_execution_evidence_summary_golden.py
docs/fixtures/13-execution-evidence-summary-golden.md
backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py
docs/fixtures/14-ci-imported-artifact-reference-clarity-golden.md
```

Planning task. Do not add frontend or backend feature code, migrations, package
upgrades, artifact upload/mutation/delete, cloud storage, external provider
integration, RBAC, tenants, permissions, broad redesign work, report generation
behavior, runner behavior changes, AI task rerun, prompt editing, raw LLM inline
display, RAG runtime, or MCP runtime.

## Verification Command

```bash
rg -n "Slice 27|AI Task Evidence Artifact Links|f9bebbe|c14fa57|57cf570|add4adc" docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

Expected result: Slice 27 completion evidence is discoverable and diff check
passes before selecting the next slice.

## Acceptance

- Slice 27 is recorded as complete in slice docs and memory.
- Next V2 slice is selected from existing V2 scope docs or current local
  evidence gaps.
- New task boundary names product value, expected files, verification command,
  non-goals, and commit message.
- Scope stays local-first and avoids remote provider, RBAC, tenant, cloud, RAG
  runtime, MCP runtime, and broad redesign expansion.

## Commit Message

```text
docs(v2): add next v2 slice plan
```

## Next Task

To be selected after Slice 27 completion.
