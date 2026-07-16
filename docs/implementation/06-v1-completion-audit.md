# V1 Completion Audit

## Purpose

This audit summarizes Chtest V1 completion evidence after Slice 17. It does not
add product behavior. It identifies implemented evidence loops, known remaining
gaps, available verification commands, and the next release-acceptance task.

## Implemented

### Requirement To Case

Implemented:

- Project, module, requirement, ContextArtifact, PromptVersion, SkillVersion,
  AITask, RequirementReview, RiskItem, CaseGenerationTask,
  GeneratedCaseCandidate, review actions, TestCase promotion, and case metrics.
- Golden smoke: `backend/app/tests/golden/test_requirement_to_case.py`.
- Metrics golden smoke:
  `backend/app/tests/golden/test_requirement_to_case_metrics.py`.
- Test case library golden smoke:
  `backend/app/tests/golden/test_test_case_library_golden.py`.

Evidence against `docs/fixtures/00-v1-demo-path.md`:

- Steps 1, 2, 6, 7, 8, 9, and 10 are covered by backend golden tests.
- RequirementReview and CaseGeneration task context references are covered by
  API/golden paths.

### Case To Automation Evidence

Implemented:

- AutomationDraft generation, edit, approve, pytest TestRun execution,
  Playwright minimal execution, failure analysis, automation execution Report,
  and evidence manifest generation.
- Golden smoke:
  `backend/app/tests/golden/test_automation_draft_golden.py`.
- Pytest golden smoke:
  `backend/app/tests/golden/test_testrunner_pytest_golden.py`.
- Playwright golden smoke:
  `backend/app/tests/golden/test_playwright_minimal_loop_golden.py`.
- Report/failure analysis golden smoke:
  `backend/app/tests/golden/test_report_failure_analysis_golden.py`.

Evidence against `docs/fixtures/00-v1-demo-path.md`:

- Steps 11, 12, 13, 14, and 15 are implemented across slice-level golden
  tests.
- Report evidence manifests are required before passed conclusions.

### CI/CD Quality Center

Implemented:

- Local diff CICDRun, changed file parsing, risk analysis artifact,
  UnitTestPatch, PatchScopeGate, human review, patch apply, new-test TestRun,
  regression selection/run, QualityGateDecision, and CI/CD quality Report.
- Foundation golden smoke:
  `backend/app/tests/golden/test_cicd_quality_center_golden.py`.
- Full UnitTestPatch/regression golden smoke:
  `backend/app/tests/golden/test_unit_test_patch_regression_golden.py`.

Evidence:

- Local-first CI/CD support workflow is covered from diff to quality gate and
  evidence report.
- Merge, push, release, deployment, remote CI provider, and PR comment actions
  remain out of scope.

### Extension Surface

Implemented:

- RAG 知识库 page surface backed by ContextArtifact.
- Empty KnowledgeAdapter state.
- MCP-ready ToolDefinition schema metadata.
- Frontend RAG 知识库 shell.
- Golden smoke:
  `backend/app/tests/golden/test_extension_surface_golden.py`.

Evidence:

- KnowledgeAdapter remains configuration-only with `used_knowledge=false`.
- ToolDefinition is MCP-ready through schema/readiness only.
- No vector/RAG/MCP runtime tables or dependencies are introduced.

### Frontend Shells

Implemented:

- Vue 3, Vite, Arco Design Vue workbench layout and navigation.
- Pages for AI 工作台、需求评审、用例生成评审、用例库、自动化草稿中心、
  执行中心、Playwright 执行、CI/CD 质量中心、报告中心、提示词 / 技能中心、
  RAG 知识库、项目设置.
- Visual review adjustment: AI 工作台 recent-task list and task detail now use a
  vertical layout, and key labels are Chinese-facing.

## Verification

Current focused commands:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_extension_surface_golden.py -q
npm --prefix frontend run test -- --run
```

Most recent results:

- Extension Surface API + golden smoke: `6 passed`.
- Frontend shell tests: `14 passed`, `17 tests passed`.

Recommended V1 release-acceptance command set:

```bash
backend/.venv/bin/python -m pytest \
  backend/app/tests/golden/test_requirement_to_case.py \
  backend/app/tests/golden/test_requirement_to_case_metrics.py \
  backend/app/tests/golden/test_test_case_library_golden.py \
  backend/app/tests/golden/test_automation_draft_golden.py \
  backend/app/tests/golden/test_testrunner_pytest_golden.py \
  backend/app/tests/golden/test_playwright_minimal_loop_golden.py \
  backend/app/tests/golden/test_report_failure_analysis_golden.py \
  backend/app/tests/golden/test_cicd_quality_center_golden.py \
  backend/app/tests/golden/test_unit_test_patch_regression_golden.py \
  backend/app/tests/golden/test_extension_surface_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Expected outcome:

- All golden smoke tests pass.
- All frontend tests pass.
- `git diff --check` is clean.

## Remaining gaps

The following gaps should be handled or explicitly accepted before declaring V1
release-ready:

- Run and record the full V1 release-acceptance command set above in a single
  session.
- Confirm whether `docs/fixtures/00-v1-demo-path.md` requires one single
  end-to-end V1 demo test, or whether the existing slice-level golden smokes are
  acceptable as composable evidence.
- Verify `ToolInvocation` linkage in the pytest runner path against the V1
  minimum demo requirement.
- Verify runtime artifact expectations for the V1 demo:
  `runtime_manifest.json`, dependency snapshot, environment snapshot,
  stdout/stderr/JUnit artifacts, and sandbox metadata.
- Review older slice task tables for stale `pending commit` entries, especially
  Slice 5 and earlier completion-gate rows, and either update documentation or
  record why historical commit ids are unavailable.
- Decide whether V1 needs an explicit release acceptance report document that
  summarizes golden test output and frontend screenshots.

Non-goals remain out of scope:

- RAG runtime, vector indexing, embeddings, reranking.
- MCP server/client runtime, remote MCP calls, plugin marketplace.
- RBAC, tenants, permissions, enterprise approval workflows.
- Remote CI provider integration, release automation, deployment orchestration.

## Next task

Run V1 release acceptance and create the acceptance report.

Recommended task name:

```text
V1 Completion Review Task 2: Run V1 release acceptance
```

Expected files:

- `docs/implementation/07-v1-release-acceptance.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

Recommended verification:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py backend/app/tests/golden/test_extension_surface_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```
