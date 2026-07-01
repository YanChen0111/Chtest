# V1 Release Acceptance Report

Date: 2026-06-30

## Scope

This report records the V1 release-acceptance run after Slice 17 Extension
Surface completion and the follow-up fix for historical golden isolation
assertions.

The run is acceptance-only. It does not add product code, RAG runtime, MCP
runtime, RBAC, tenants, permissions, marketplace, cloud sync, release
automation, deployment automation, or remote CI provider integration.

## Verification Commands

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py backend/app/tests/golden/test_extension_surface_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

## Results

Backend golden release-acceptance suite, first run:

- Result: `5 failed, 5 passed`.
- Passing coverage remains present for the earlier and later accepted flows.
- Failing checks are isolation assertions in historical slice golden smokes,
  not flow execution failures.

Backend golden release-acceptance suite, after Task 3 fix:

- Result: passed.
- Pytest reported `10 passed`.
- The five failing historical golden smokes now assert that no later-slice rows
  or behavior were created by the current flow, instead of asserting table
  absence in the complete model registry.

Frontend suite:

- Result: passed.
- Vitest reported `14` test files passed and `17` tests passed.

Diff hygiene:

- Result: passed.
- `git diff --check` reported no whitespace errors.

## Backend Failures

The backend failures are:

- `test_automation_draft_golden.py`: expected `test_runs` table to be absent.
- `test_testrunner_pytest_golden.py`: expected `reports` table to be absent.
- `test_playwright_minimal_loop_golden.py`: expected `reports` table to be
  absent.
- `test_report_failure_analysis_golden.py`: expected
  `quality_gate_decisions` table to be absent.
- `test_cicd_quality_center_golden.py`: expected `quality_gate_decisions` table
  to be absent.

Root cause:

- The historical slice golden smokes used table absence as a proxy for
  "later-slice behavior is not involved".
- In the complete V1 application, all SQLAlchemy models are imported before
  `Base.metadata.create_all`, so later-slice tables exist during a full release
  acceptance run.
- The product intent is still valid, but the assertion should verify absence of
  rows or behavior created by that flow, not absence of the table itself.

## Fix Applied

Task 3 updated only golden smoke assertions:

- Automation draft golden now checks no `TestRun`, `TestResult`, or `Report`
  rows were created.
- Pytest runner golden now checks no `Report` or `QualityGateDecision` rows
  were created.
- Playwright runner golden now checks no `Report`, `FailureAnalysis`, or
  `QualityGateDecision` rows were created.
- Report/failure-analysis golden now checks no `QualityGateDecision` rows were
  created.
- CI/CD quality center golden now checks no `QualityGateDecision` rows were
  created.

This preserves each slice's original non-goal intent while allowing full V1
release acceptance to run with every model registered.

## Recommendation

GO for V1 release acceptance based on the current automated evidence set.

Residual release risk remains around whether the team wants a single narrative
end-to-end V1 demo in addition to composable golden smokes. The automated
release-acceptance gate itself is passing.

## Release Blocker

Resolved.

## Next Task

Prepare final V1 acceptance handoff and clean stale historical planning entries
that still describe completed slices as pending.
