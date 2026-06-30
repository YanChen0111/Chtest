# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Post-V1 Planning.

## Current Task

Post-V1 Task 2: Create V1 release package skeleton.

## Product Value Answer

After this task, the V1 release package has a stable documentation skeleton for
release notes, acceptance evidence, and manual walkthrough content.

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
12. `docs/implementation/06-v1-completion-audit.md`
13. `docs/implementation/07-v1-release-acceptance.md`
14. `docs/implementation/08-v1-final-acceptance-handoff.md`
15. `docs/implementation/09-post-v1-release-packaging-plan.md`

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/08-v1-final-acceptance-handoff.md
docs/implementation/09-post-v1-release-packaging-plan.md
docs/release/v1/README.md
docs/release/v1/acceptance-evidence.md
docs/release/v1/manual-walkthrough.md
```

Documentation-only release packaging task. Do not add product code, RAG
runtime, MCP runtime, RBAC, tenants, permissions, marketplace, cloud sync,
release automation, or remote CI provider integration.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py backend/app/tests/golden/test_extension_surface_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: all V1 golden smokes, frontend tests, and diff check pass.

## Acceptance

- Creates `docs/release/v1/README.md`.
- Creates `docs/release/v1/acceptance-evidence.md`.
- Creates `docs/release/v1/manual-walkthrough.md`.
- Keeps current V1 acceptance evidence linked.
- Keeps V1 non-goals out of scope.

## Commit Message

```text
docs(release): add v1 release package skeleton
```

## Next Task

Write the V1 manual walkthrough and acceptance evidence details.
