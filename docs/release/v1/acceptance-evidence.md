# V1 Acceptance Evidence

Date: 2026-06-30

## Automated Gate

Run from repository root:

```text
/Users/yanchen/VscodeProject/Chtest
```

Backend golden release-acceptance command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py backend/app/tests/golden/test_extension_surface_golden.py -q
```

Recorded result:

- `10 passed`
- Covers every V1 golden smoke in one full model-registry run.
- Source report:
  `docs/implementation/07-v1-release-acceptance.md`

Frontend workbench command:

```bash
npm --prefix frontend run test -- --run
```

Recorded result:

- `14` test files passed.
- `17 tests passed`.
- Covers the workbench shell pages used by V1 release workflows.

Diff hygiene command:

```bash
git diff --check
```

Recorded result:

- Clean.
- Confirms the release documentation changes contain no whitespace errors.

## Release Status

Recommendation:

- `GO` for V1 acceptance based on the automated evidence above.

Known release blocker status:

- Resolved: historical golden smokes no longer depend on later-slice table
  absence in a complete model registry.

Remaining non-blocking release choices:

- Optional screenshots for release notes.
- Optional manual walkthrough capture.
- Optional cleanup of older historical slice task tables if those tables are
  used in public release notes.

## Evidence Reports

- Completion audit:
  `docs/implementation/06-v1-completion-audit.md`
- Release acceptance report:
  `docs/implementation/07-v1-release-acceptance.md`
- Final acceptance handoff:
  `docs/implementation/08-v1-final-acceptance-handoff.md`
- Release packaging decision:
  `docs/implementation/09-post-v1-release-packaging-plan.md`

## Evidence Coverage

The automated gate covers:

| Area | Evidence |
|---|---|
| Requirement review | `test_requirement_to_case.py` |
| Requirement/case metrics | `test_requirement_to_case_metrics.py` |
| Test case library | `test_test_case_library_golden.py` |
| AutomationDraft review | `test_automation_draft_golden.py` |
| pytest execution | `test_testrunner_pytest_golden.py` |
| Playwright execution | `test_playwright_minimal_loop_golden.py` |
| Failure analysis and report | `test_report_failure_analysis_golden.py` |
| CI/CD Quality Center | `test_cicd_quality_center_golden.py` |
| UnitTestPatch and regression | `test_unit_test_patch_regression_golden.py` |
| Extension surfaces | `test_extension_surface_golden.py` |

## Evidence Chain

The V1 automated evidence demonstrates:

1. Requirement and ContextArtifact records can feed AI review/case generation.
2. Generated cases require human review before entering the library.
3. AutomationDraft requires review before execution.
4. TestRun and TestResult records capture runner output and artifacts.
5. Reports require evidence manifests before conclusions are accepted.
6. Local diff CI/CD support can analyze risk, generate scoped patches, run
   evidence, and produce a QualityGateDecision.
7. RAG 知识库 and MCP-ready ToolDefinition surfaces exist without adding V1
   runtime dependencies.

## Out Of Scope Confirmed

The V1 acceptance gate does not require or include:

- Real LLM provider calls.
- RAG runtime, vector index, embeddings, or reranking.
- MCP runtime, remote MCP calls, or plugin marketplace.
- RBAC, tenants, permissions, or enterprise collaboration.
- Remote CI provider integration, deployment automation, or release automation.
- Unapproved AI changes to business source files.
