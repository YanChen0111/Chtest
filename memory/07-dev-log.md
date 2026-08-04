# Development Log

## 2026-07-13 Case Generation Decision Gate And Coverage Dimensions

### Completed

- Completed the P0/P1 case-generation review hardening requested for chtest.
- Added a required decision-table acknowledgement gate before final case
  generation and enforced it in the backend with
  `CASE_GENERATION_DECISION_TABLE_REQUIRED`.
- Added persisted `coverage_dimensions_json` on GeneratedCaseCandidate and
  removed frontend text heuristics from the coverage matrix.
- Tightened CaseGenerationAgent schema validation so candidates without legal
  coverage dimensions and evidence fail without persisting candidates.
- Reset the frontend decision-table acknowledgement when the requirement source
  changes.
- Synced Prompt/Skill files, fixture seeds, contracts, mock provider, OpenAI
  provider instructions, golden fixture, tests, and `NEXT_AI_TASK.md`.
- Docker/compose runtime work remains skipped per user instruction.

### Verification

- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_automation_plan.py backend/app/tests/api/test_test_knowledge_cards.py -q`
  - Result: `20 passed in 3.05s`.
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_test_knowledge_cards.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_model_connection_config.py backend/app/tests/api/test_extension_surface.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_automation_plan.py backend/app/tests/db/test_case_generation_models.py -q`
  - Result: `57 passed in 5.19s`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/settings/ProjectSettingsView.spec.ts src/views/extension/KnowledgeBaseView.spec.ts src/views/requirements/RequirementReviewView.spec.ts src/views/cases/CaseGenerationReviewView.spec.ts src/views/automation/AutomationDraftReviewView.spec.ts`
  - Result: `5` files passed, `16` tests passed.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run build`
  - Result: passed with existing Vite large chunk warning.
- `git diff --check`
  - Result: no output.

### Next Step

- Browser-smoke the non-Docker reviewer workflow and automation-draft execution
  type selection for Playwright/API/JMeter.

## 2026-07-08 Slice 46 Completion Gate

### Completed

- Completed Slice 46: AI Workbench Evidence Table Empty States.
- Selected-task artifact summary now shows an explicit empty state when no
  artifact evidence is recorded.
- Selected-task LLM call log now shows an explicit empty state when no LLM call
  logs are recorded.
- Existing populated artifact and LLM call tables still render as before.
- Raw prompt, raw request, and raw LLM output remain metadata-only; no backend,
  provider, prompt, skill, contract, fixture, execution page, package, RAG
  runtime, or MCP runtime behavior changed.
- Updated `NEXT_AI_TASK.md` to select the next narrow V2 task.

### Verification

- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `4` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Select another narrow V2 task outside broad refactors and unrelated
  dirty-worktree scope.

## 2026-07-08 Slice 46 AI Workbench Evidence Table Empty States Plan

### Completed

- Selected `Slice 46: AI Workbench Evidence Table Empty States` after Slice 45
  completion.
- The slice adds explicit selected-task empty states for missing artifact
  evidence and missing LLM call logs.
- Added the Slice 46 task plan.
- Updated `NEXT_AI_TASK.md` to Slice 46 Task 2.

### Verification

- Planning verification will be covered by the Slice 46 focused frontend gate.

### Next Step

- Add focused AI Workbench coverage for a selected task with empty artifacts
  and empty LLM call logs, then render the explicit empty states.

## 2026-07-08 Slice 45 Completion Gate

### Completed

- Completed Slice 45: AI Workbench Token Usage Empty State.
- Empty task-level and LLM-call token usage metadata now renders as not
  recorded instead of a blank AI Workbench value.
- Non-empty token usage metadata still renders formatted token labels.
- Raw prompt, raw request, and raw LLM output remain metadata-only; no backend,
  provider, prompt, skill, contract, fixture, execution page, package, RAG
  runtime, or MCP runtime behavior changed.
- Updated `NEXT_AI_TASK.md` to select the next narrow V2 task.

### Verification

- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Select another narrow V2 task outside broad refactors and unrelated
  dirty-worktree scope.

## 2026-07-08 Slice 45 AI Workbench Token Usage Empty State Plan

### Completed

- Selected `Slice 45: AI Workbench Token Usage Empty State` after Slice 44
  completion.
- The slice renders empty token usage metadata as not recorded instead of a
  blank AI Workbench task detail or LLM call cell.
- Added the Slice 45 task plan.
- Updated `NEXT_AI_TASK.md` to Slice 45 Task 2.

### Verification

- Planning verification will be covered by the Slice 45 focused frontend gate.

### Next Step

- Add focused AI Workbench coverage for empty token usage and update the shared
  token usage display helper.

## 2026-07-08 Slice 44 Completion Gate

### Completed

- Completed Slice 44: AI Workbench Request Evidence Visibility.
- AI Workbench LLM call rows now show request evidence as recorded or not
  recorded.
- Local open links render only when the request artifact id matches an existing
  selected-task Artifact with `safe_to_show=true`.
- Focused coverage now includes the safe request link path, an unsafe artifact
  negative path, and a missing request artifact row.
- Raw prompt, raw request, and raw LLM output remain metadata-only; no backend,
  provider, prompt, skill, contract, fixture, execution page, package, RAG
  runtime, or MCP runtime behavior changed.
- Updated `NEXT_AI_TASK.md` to select the next narrow V2 task.

### Verification

- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Select another narrow V2 task outside broad refactors and unrelated
  dirty-worktree scope.

## 2026-07-08 Slice 43 Completion Gate

### Completed

- Completed Slice 43: AI Workbench Parsed Output Evidence Visibility.
- AI Workbench LLM call rows now show parsed output evidence as recorded or not
  recorded.
- Local open links render only when the parsed output artifact id matches an
  existing selected-task Artifact with `safe_to_show=true`.
- Raw LLM output remains metadata-only; no backend, provider, prompt, skill,
  contract, fixture, execution page, package, RAG runtime, or MCP runtime
  behavior changed.
- Updated `NEXT_AI_TASK.md` to select the next narrow V2 task.

### Verification

- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Select another narrow V2 task outside broad refactors and unrelated
  dirty-worktree scope.

## 2026-07-08 Slice 43 AI Workbench Parsed Output Evidence Visibility Plan

### Completed

- Selected `Slice 43: AI Workbench Parsed Output Evidence Visibility` after
  Slice 42 completion.
- The slice shows whether each LLM call has parsed output evidence, with a
  local open link only for safe persisted artifacts.
- Added the Slice 43 task plan.
- Updated `NEXT_AI_TASK.md` to Slice 43 Task 2.

### Verification

- Planning verification will be covered by the Slice 43 focused frontend gate.

### Next Step

- Show parsed output evidence status in the AI Workbench LLM call log.

## 2026-07-08 Slice 42 Completion Gate

### Completed

- Completed Slice 42: AI Workbench Context Manifest Evidence Visibility.
- AI Workbench task details now show context manifest evidence as recorded or
  not generated.
- Local open links render only when the context manifest artifact id matches an
  existing selected-task Artifact with `safe_to_show=true`.
- Raw LLM output remains metadata-only; no backend, provider, prompt, skill,
  contract, fixture, execution page, package, RAG runtime, or MCP runtime
  behavior changed.
- Updated `NEXT_AI_TASK.md` to select the next narrow V2 task.

### Verification

- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Select another narrow V2 task outside broad refactors and unrelated
  dirty-worktree scope.

## 2026-07-08 Slice 42 AI Workbench Context Manifest Evidence Visibility Plan

### Completed

- Selected `Slice 42: AI Workbench Context Manifest Evidence Visibility` after
  Slice 41 completion.
- The slice shows whether AI task context manifest evidence was recorded, with
  a local open link only for safe persisted artifacts.
- Added the Slice 42 task plan.
- Updated `NEXT_AI_TASK.md` to Slice 42 Task 2.

### Verification

- Planning verification will be covered by the Slice 42 focused frontend gate.

### Next Step

- Show context manifest evidence status in the AI Workbench task detail.

## 2026-07-08 Slice 41 Completion Gate

### Completed

- Completed Slice 41: AI Workbench Artifact Link Accessibility.
- AI Workbench artifact summary links now expose row-specific `aria-label` and
  `title` attributes while preserving visible `打开` text.
- Safe-to-show link conditions and artifact URLs remain unchanged.
- No backend, provider, prompt, skill, contract, fixture, execution page,
  package, RAG runtime, or MCP runtime behavior changed.
- Updated `NEXT_AI_TASK.md` to select the next narrow V2 task.

### Verification

- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Select another narrow V2 task outside execution shell/form refactor and
  unrelated dirty-worktree scope.

## 2026-07-08 Slice 41 AI Workbench Artifact Link Accessibility Plan

### Completed

- Selected `Slice 41: AI Workbench Artifact Link Accessibility` after Slice 40
  completion.
- The slice adds row-specific accessible labels to AI Workbench artifact summary
  links while preserving visible text, href generation, and safe-to-show link
  conditions.
- Added the Slice 41 task plan.
- Updated `NEXT_AI_TASK.md` to Slice 41 Task 2.

### Verification

- Planning verification will be covered by the Slice 41 focused frontend gate.

### Next Step

- Add `aria-label` and `title` to AI Workbench artifact summary open links.

## 2026-07-08 Slice 40 Completion Gate

### Completed

- Completed Slice 40: AI Task Schema Validation Evidence Visibility.
- AI Workbench LLM call rows now expose schema-validation evidence as recorded
  or not recorded.
- Local open links render only when the schema-validation artifact id matches
  an existing selected-task Artifact with `safe_to_show=true`.
- Raw LLM output remains metadata-only; no backend, provider, prompt, skill,
  contract, fixture, execution page, package, RAG runtime, or MCP runtime
  behavior changed.
- Updated `NEXT_AI_TASK.md` to select the next narrow V2 task.

### Verification

- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Select another narrow V2 task outside execution shell/form refactor and
  unrelated dirty-worktree scope.

## 2026-07-08 Slice 40 AI Task Schema Validation Evidence Visibility Plan

### Completed

- Selected `Slice 40: AI Task Schema Validation Evidence Visibility` as the
  next narrow V2 task outside automatic execution-page cleanup.
- Added the Slice 40 task plan.
- Updated `NEXT_AI_TASK.md` to Slice 40 Task 2.
- Recorded that Slice 39 remains verified but uncommitted because shared
  docs/memory files contain large unrelated dirty-worktree changes; do not use
  broad staging.

### Verification

- Planning verification will be covered by the Slice 40 focused frontend gate.

### Next Step

- Show schema-validation evidence status in the AI Workbench LLM call log.

## 2026-07-08 Slice 39 Completion Gate

### Completed

- Completed Slice 39: Execution Evidence Link Accessibility.
- Added row-specific `aria-label` and `title` attributes to
  `ExecutionRunManifestPanel.vue` open links.
- Updated focused component coverage to assert accessible labels while
  preserving visible `打开` text and existing artifact URL behavior.
- Preserved run manifest row availability rules, output definitions, display
  helpers, result tables, metrics, artifact tables, and start/refresh behavior.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionOutputArtifacts.spec.ts src/views/execution/executionDisplay.spec.ts src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `12` files passed, `20` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Before new product-code work, path-limit review/stage/commit the Slice 39
  implementation and handoff files, or explicitly document why Slice 39 remains
  uncommitted.
- Stop automatic execution-page cleanup here. Remaining execution-page changes
  should be selected as a fresh product-value task or explicitly promoted as a
  broader shell/form refactor.

## 2026-07-08 Slice 39 Execution Evidence Link Accessibility Plan

### Completed

- Selected `Slice 39: Execution Evidence Link Accessibility` as the next narrow
  V2 task after Slice 38 completion.
- The slice adds row-specific accessible labels to run manifest evidence links
  while preserving visible text, href generation, and availability rules.
- Added `docs/implementation/slices/slice-39-execution-evidence-link-accessibility.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 38 completion
  and the Slice 39 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 39 planning.

### Verification

- `rg -n "Slice 39|Execution Evidence Link Accessibility|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-39-execution-evidence-link-accessibility.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md`
- Result: planning references present.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 39 Task 2: Add accessible labels to manifest evidence links.

## 2026-07-08 Slice 38 Completion Gate

### Completed

- Completed Slice 38: Execution Output Artifact Definitions.
- Added `frontend/src/views/execution/executionOutputArtifacts.ts`.
- Added focused definition coverage for pytest, Playwright, Newman, and JMeter
  manifest output artifact ordering and labels.
- Replaced page-local manifest output artifact arrays in pytest, Playwright,
  Newman, and JMeter execution pages with shared constants.
- Preserved manifest row semantics, artifact filters, artifact links, metrics,
  result tables, display helpers, and start/refresh behavior.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/executionOutputArtifacts.spec.ts src/views/execution/executionDisplay.spec.ts src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `12` files passed, `20` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Stop automatic execution-page cleanup here. Remaining duplication is mostly
  page shell/layout and entry forms, which should be planned explicitly before
  editing because the blast radius is broader than Slices 33-38.

## 2026-07-08 Slice 38 Execution Output Artifact Definitions Plan

### Completed

- Selected `Slice 38: Execution Output Artifact Definitions` as the next safe
  V2 slice after Slice 37 completion.
- The slice extracts duplicated manifest output artifact definition arrays while
  keeping artifact lookup, artifact filtering, manifest row-building semantics,
  and runner behavior unchanged.
- Added `docs/implementation/slices/slice-38-execution-output-artifact-definitions.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 37 completion
  and the Slice 38 recommendation.
- `NEXT_AI_TASK.md` already points to Slice 38 planning.

### Verification

- `rg -n "Slice 38|Execution Output Artifact Definitions|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-38-execution-output-artifact-definitions.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md`
- Result: planning references present.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 38 Task 2: Add shared execution output artifact definitions.

## 2026-07-07 Slice 37 Completion Gate

### Completed

- Completed Slice 37: Execution Display Helpers.
- Added `frontend/src/views/execution/executionDisplay.ts`.
- Added focused helper coverage for run status labels and run duration labels.
- Replaced page-local status label and run duration display logic in pytest,
  Playwright, Newman, and JMeter execution pages with the shared helper.
- Preserved page layout, forms, JMeter parsed JTL duration formatting, result
  row shaping, run manifest, metrics panel, artifact table, result table, and
  start/refresh behavior.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/executionDisplay.spec.ts src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `11` files passed, `16` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Pause broad automatic extraction. Remaining duplication is mostly execution
  page shell/layout and entry forms, which should be planned only if explicitly
  promoted because the blast radius is larger than Slices 33-37.

## 2026-07-07 Slice 37 Execution Display Helpers Plan

### Completed

- Selected `Slice 37: Execution Display Helpers` as the next safe V2 slice
  after Slice 36 completion.
- The slice extracts pure status and run-duration display helpers while keeping
  page layout, forms, result data, and runner-specific JMeter formatting in the
  pages.
- Added `docs/implementation/slices/slice-37-execution-display-helpers.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 36 completion
  and the Slice 37 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 37 Task 1: Add Execution Display Helpers
  task plan.

### Verification

- `rg -n "Slice 37|Execution Display Helpers|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-37-execution-display-helpers.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md`
- Result: planning references present.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 37 Task 2: Add shared execution display helpers.

## 2026-07-07 Slice 36 Completion Gate

### Completed

- Completed Slice 36: Execution Result Table Panel.
- Added `frontend/src/views/execution/ExecutionResultTable.vue`.
- Added focused component coverage for page-owned columns and rows.
- Replaced duplicated result table section markup in pytest, Playwright,
  Newman, and JMeter execution pages with the shared component.
- Preserved page-owned runner-specific result columns, JMeter result row
  shaping, run manifest, metrics panel, artifact table, and start/refresh
  behavior.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `10` files passed, `14` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Select the next narrow V2 task after Slice 36 completion.

## 2026-07-07 Slice 36 Execution Result Table Panel Plan

### Completed

- Selected `Slice 36: Execution Result Table Panel` as the next safe V2 slice
  after Slice 35 completion.
- The slice extracts duplicated result table section display while keeping
  runner-specific result columns and row shaping on each execution page.
- Added `docs/implementation/slices/slice-36-execution-result-table-panel.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 35 completion
  and the Slice 36 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 36 Task 1: Add Execution Result Table
  Panel task plan.

### Verification

- `rg -n "Slice 36|Execution Result Table Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-36-execution-result-table-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md`
- Result: planning references present.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 36 Task 2: Add shared execution result table component.

## 2026-07-07 Slice 35 Completion Gate

### Completed

- Completed Slice 35: Execution Metrics Panel.
- Added `frontend/src/views/execution/ExecutionMetricsPanel.vue`.
- Added focused component coverage for numeric and string metric values.
- Replaced duplicated metric tile markup and scoped CSS in pytest,
  Playwright, Newman, and JMeter execution pages with the shared component.
- Preserved page-owned runner-specific metric item computation, result tables,
  artifact filters, start/refresh behavior, and evidence links.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `9` files passed, `13` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Plan Slice 36: Execution Result Table Panel.

## 2026-07-07 Slice 35 Execution Metrics Panel Plan

### Completed

- Selected `Slice 35: Execution Metrics Panel` as the next safe V2 slice after
  Slice 34 completion.
- The slice extracts duplicated metric tile display while keeping
  runner-specific metric item computation on each execution page.
- Added `docs/implementation/slices/slice-35-execution-metrics-panel.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 34 completion
  and the Slice 35 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 35 Task 1: Add Execution Metrics Panel
  task plan.

### Verification

- `rg -n "Slice 35|Execution Metrics Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-35-execution-metrics-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md`
- Result: planning references present.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 35 Task 2: Add shared execution metrics panel component.

## 2026-07-07 Slice 34 Completion Gate

### Completed

- Completed Slice 34: Execution Artifact Table Panel.
- Added `frontend/src/views/execution/ExecutionArtifactTable.vue`.
- Added focused component coverage for artifact metadata, local open links, and
  accessible open-link labels.
- Replaced duplicated artifact table markup in pytest, Playwright, Newman, and
  JMeter execution pages with the shared component.
- Preserved page-owned runner-specific artifact filtering, metrics, result
  tables, start/refresh behavior, and read-only local artifact semantics.
- Updated `NEXT_AI_TASK.md` to plan Slice 35: Execution Metrics Panel.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `8` files passed, `12` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Plan Slice 35: Execution Metrics Panel.

## 2026-07-07 Slice 34 Execution Artifact Table Panel Plan

### Completed

- Selected `Slice 34: Execution Artifact Table Panel` as the next safe V2 slice
  after Slice 33 completion.
- The slice extracts duplicated artifact table display while keeping
  runner-specific artifact filters on each execution page.
- Added `docs/implementation/slices/slice-34-execution-artifact-table-panel.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 33 completion
  and the Slice 34 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 34 Task 2: Add shared execution artifact
  table component.

### Verification

- `rg -n "Slice 34|Execution Artifact Table Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-34-execution-artifact-table-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md`
- Result: planning references present.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 34 Task 2: Add shared execution artifact table component.

## 2026-07-07 Slice 33 Completion Gate

### Completed

- Completed Slice 33: Execution Run Manifest Panel.
- Execution pages now render the run manifest through one shared
  `ExecutionRunManifestPanel.vue` component.
- Pytest, Playwright, Newman, and JMeter pages preserve runner-specific metrics,
  output artifact definitions, start/refresh behavior, local link rules, and
  missing evidence visibility.
- Updated `NEXT_AI_TASK.md` to select and plan the next narrow V2 task.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `7` files passed, `11` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Select and plan the next narrow V2 task after Slice 33 completion.

## 2026-07-07 Slice 33 Execution Run Manifest Panel Implementation

### Completed

- Added `frontend/src/views/execution/ExecutionRunManifestPanel.vue`.
- Added focused component coverage.
- Replaced duplicated run manifest panel markup in pytest, Playwright, Newman,
  and JMeter execution pages with the shared component.
- Removed page-local manifest table columns and scoped manifest CSS.
- Updated `NEXT_AI_TASK.md` to Slice 33 Completion Gate.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `5` files passed, `5` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Run Slice 33 Completion Gate.

## 2026-07-07 Slice 33 Execution Run Manifest Panel Plan

### Completed

- Selected `Slice 33: Execution Run Manifest Panel` as the next safe V2 slice
  after Slice 32 completion.
- The slice extracts the remaining duplicated manifest display block while
  keeping helper semantics and runner-specific evidence unchanged.
- Added `docs/implementation/slices/slice-33-execution-run-manifest-panel.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 32 completion
  and the Slice 33 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 33 Task 2: Add shared execution run
  manifest panel component.

### Verification

- `rg -n "Slice 33|Execution Run Manifest Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-33-execution-run-manifest-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md`
- Result: planning references present.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 33 Task 2: Add shared execution run manifest panel component.

## 2026-07-07 Slice 32 Completion Gate

### Completed

- Completed Slice 32: Execution Run Manifest Helper.
- `buildExecutionRunManifestRows` now centralizes runtime, snapshot, and output
  artifact row construction for execution run manifests.
- Pytest, Playwright, Newman, and JMeter execution pages reuse the helper while
  keeping runner-specific output artifact definitions.
- Updated `NEXT_AI_TASK.md` to select and plan the next narrow V2 task.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `6` files passed, `10` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Select and plan the next narrow V2 task after Slice 32 completion.

## 2026-07-07 Slice 32 Execution Run Manifest Helper Implementation

### Completed

- Added `frontend/src/views/execution/executionRunManifest.ts`.
- Added focused helper tests for runtime, dependency snapshot, environment
  snapshot, and output artifact rows.
- Replaced duplicated manifest row-building code in pytest, Playwright, Newman,
  and JMeter execution pages with the shared helper.
- Preserved runner-specific output artifact lists and existing page layouts.
- Updated `NEXT_AI_TASK.md` to Slice 32 Completion Gate.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/executionRunManifest.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `5` files passed, `8` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Run Slice 32 Completion Gate.

## 2026-07-07 Slice 32 Execution Run Manifest Helper Plan

### Completed

- Selected `Slice 32: Execution Run Manifest Helper` as the next safe V2 slice
  after Slice 31 completion.
- The slice removes real duplication in execution run manifest row-building
  while avoiding backend, contracts, fixtures, prompts, skills, and deleted
  knowledge-card scope.
- Added `docs/implementation/slices/slice-32-execution-run-manifest-helper.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 31 completion
  and the Slice 32 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 32 Task 2: Add execution run manifest
  helper.

### Verification

- `rg -n "Slice 32|Execution Run Manifest Helper|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-32-execution-run-manifest-helper.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md`
- Result: planning references present.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 32 Task 2: Add execution run manifest helper.

## 2026-07-07 Slice 31 Completion Gate

### Completed

- Completed Slice 31: Execution Evidence Availability Labels.
- The execution evidence availability helper now standardizes labels for
  local-openable, unavailable, external-reference, and metadata-only states.
- Pytest, Playwright, Newman, and JMeter execution run manifest rows now use the
  helper while preserving local link rules and runner-specific evidence tables.
- Updated `NEXT_AI_TASK.md` to select and plan the next narrow V2 task.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `5` files passed, `6` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Select and plan the next narrow V2 task after Slice 31 completion.

## 2026-07-07 Slice 31 Task 3 Execution Manifest Availability Labels

### Completed

- Applied the shared evidence availability label helper to pytest,
  Playwright, Newman, and JMeter execution run manifest rows.
- Preserved local link rules: links still require a persisted local Artifact id
  in `TestRunRead.artifacts`.
- Preserved runner-specific metrics and artifact tables.
- Updated `NEXT_AI_TASK.md` to Slice 31 Completion Gate.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `4` files passed, `4` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Run Slice 31 Completion Gate.

## 2026-07-07 Slice 31 Task 2 Evidence Availability Label Helper

### Completed

- Added `frontend/src/views/execution/evidenceAvailability.ts`.
- Added focused helper tests for local-openable, unavailable, external
  reference, and metadata-only evidence states.
- The helper returns labels only; it does not create URLs, inspect files, fetch
  remote data, mutate artifacts, or depend on backend changes.
- Updated `NEXT_AI_TASK.md` to Slice 31 Task 3: Apply availability labels to
  execution run manifests.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/evidenceAvailability.spec.ts`
- Result: `1` file passed, `2` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 31 Task 3: Apply availability labels to execution run
  manifests.

## 2026-07-07 Slice 31 Execution Evidence Availability Labels Plan

### Completed

- Selected `Slice 31: Execution Evidence Availability Labels` as the next safe
  V2 slice after Slice 30 completion.
- The slice continues the evidence-readability thread while avoiding the
  current dirty worktree's deleted knowledge-card, prompt, skill, contract, and
  fixture scope.
- Added `docs/implementation/slices/slice-31-execution-evidence-availability-labels.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 30 completion
  and the Slice 31 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 31 Task 2: Add execution evidence
  availability label helper.

### Verification

- `rg -n "Slice 31|Execution Evidence Availability Labels|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-31-execution-evidence-availability-labels.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md`
- Result: planning references present.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 31 Task 2: Add execution evidence availability label helper.

## 2026-07-07 Slice 30 Completion Gate

### Completed

- Completed Slice 30: Execution Run Manifest Parity.
- Playwright, Newman, and JMeter execution pages now all show the compact
  read-only run manifest panel established by Slice 29.
- The panels preserve runner-specific evidence sections while adding common
  command/workspace/safety-policy/snapshot/output availability cues.
- Updated `NEXT_AI_TASK.md` to select and plan the next narrow V2 task.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts`
- Result: `3` files passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Select and plan the next narrow V2 task after Slice 30 completion.

## 2026-07-07 Slice 30 Task 4 JMeter Run Manifest Panel

### Completed

- Added the read-only `执行运行清单` panel to the JMeter execution page.
- The panel shows command, working directory, runner mode, run workspace,
  repository read-only policy, network policy, runtime files, snapshots, and
  JMeter output artifact availability.
- Local download links render only when an id matches a persisted local
  `TestRunRead.artifacts` row.
- Focused JMeter coverage now includes persisted runtime/dependency/stdout/
  JTL/parsed-output artifacts plus missing runtime, environment snapshot, and
  stderr rows.
- Updated `NEXT_AI_TASK.md` to Slice 30 Completion Gate.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/JMeterExecutionView.spec.ts`
- Result: `1` file passed, `1` test passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Run Slice 30 Completion Gate.

## 2026-07-07 Slice 30 Task 3 Newman Run Manifest Panel

### Completed

- Added the read-only `执行运行清单` panel to the Newman execution page.
- The panel shows command, working directory, runner mode, run workspace,
  repository read-only policy, network policy, runtime files, snapshots, and
  Newman output artifact availability.
- Local download links render only when an id matches a persisted local
  `TestRunRead.artifacts` row.
- Focused Newman coverage now includes persisted runtime/dependency/stdout/
  newman-json/parsed-output artifacts plus missing runtime, environment
  snapshot, stderr, and JUnit rows.
- Updated `NEXT_AI_TASK.md` to Slice 30 Task 4: Add JMeter run manifest panel.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/NewmanExecutionView.spec.ts`
- Result: `1` file passed, `1` test passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 30 Task 4: Add JMeter run manifest panel.

## 2026-07-07 Slice 30 Task 2 Playwright Run Manifest Panel

### Completed

- Added the read-only `执行运行清单` panel to the Playwright execution page.
- The panel shows command, working directory, runner mode, run workspace,
  repository read-only policy, network policy, runtime files, snapshots, and
  output artifact availability.
- Local download links render only when an id matches a persisted local
  `TestRunRead.artifacts` row.
- Focused Playwright coverage now includes persisted runtime/dependency/stdout/
  trace/screenshot artifacts plus missing runtime, environment snapshot,
  stderr, parsed output, and JUnit rows.
- Updated `NEXT_AI_TASK.md` to Slice 30 Task 3: Add Newman run manifest panel.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts`
- Result: `1` file passed, `1` test passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 30 Task 3: Add Newman run manifest panel.

## 2026-07-07 Slice 30 Execution Run Manifest Parity Plan

### Completed

- Used three parallel subagents to evaluate the next V2 slice after Slice 29:
  V2 priority, Git/worktree risk, and contracts/fixtures readiness.
- Selected `Slice 30: Execution Run Manifest Parity` as the safest next slice.
- Added `docs/implementation/slices/slice-30-execution-run-manifest-parity.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 29 completion
  and the Slice 30 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 30 Task 1.

### Rationale

- Slice 29 proved the run manifest contract and pytest page implementation.
- Playwright, Newman, and JMeter pages can reuse the same existing `TestRunRead`
  evidence without backend/API changes.
- The current worktree has large unrelated unstaged changes and deletions, so
  this planning task avoided backend, frontend, contracts, fixtures, prompt, and
  skill files.

### Verification

- `rg -n "Execution Run Manifest Parity|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-30-execution-run-manifest-parity.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md`
- Result: planning references present.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 30 Task 2: Add Playwright run manifest panel.

## 2026-07-07 Slice 29 Completion Gate

### Completed

- Completed Slice 29: Execution Run Manifest.
- Recorded Task 4 verification and Slice 29 completion evidence.
- Updated `NEXT_AI_TASK.md` to select and plan the next narrow V2 task.

### Verification

- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q`
- Result: `2 passed`.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `npm --prefix frontend run test -- --run`
- Result: `16` files passed, `21` tests passed.
- `git diff --check`
- Result: no output.

### Notes

- Workspace-local `uv` and MinGit live under `.tmp/tools`, which is ignored.
- Current Git status still includes broad unrelated working tree changes and
  deletions outside Slice 29; they were not reverted or staged.

### Next Step

- Select and plan the next narrow V2 slice from `NEXT_AI_TASK.md`.


## 2026-07-07 Slice 29 Execution Run Manifest Golden Smoke Verified

### Completed

- Restored workspace-local tooling under `.tmp/tools`: portable `uv` and
  portable MinGit.
- Created `backend/.venv` with `uv --project backend sync --dev`.
- Restored Git metadata for `origin/docs/preflight-vibecoding-fixes` without
  overwriting working tree files.
- Updated `NEXT_AI_TASK.md` to Slice 29 Completion Gate.

### Verification

- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Notes

- Current Git status includes many unrelated pre-existing working tree changes
  and deletions outside Slice 29 Task 4; they were not reverted or staged.

### Next Step

- Run Slice 29 Completion Gate from `NEXT_AI_TASK.md`.


## 2026-07-06 Slice 29 Execution Run Manifest Golden Smoke

### Completed

- Added `backend/app/tests/golden/test_execution_run_manifest_golden.py`.
- Added `docs/fixtures/17-execution-run-manifest-golden.md`.
- Golden seed covers existing TestRun manifest fields, persisted local Artifact
  rows and metadata, missing snapshot id visibility, missing runtime Artifact
  id visibility, and local artifact access only for persisted Artifact ids.
- Golden asserts read/display inputs do not create or mutate Report,
  FailureAnalysis, QualityGateDecision, AutomationRepairTask, AutomationDraft,
  AITask, TestRun, or Artifact rows.

### Verification

- Scoped whitespace/conflict-marker check passed.
- Backend golden pytest could not run because `backend/.venv` is missing and
  system `python.exe` is an unusable WindowsApps stub.
- Attempts to install/download missing Git/Python tooling were blocked by the
  escalation auto-review, even after user allowed environment setup.

### Next Step

- Restore backend Python 3.12/uv or `backend/.venv`, restore usable git checkout,
  then run the Slice 29 Task 4 golden smoke and `git diff --check`.

## 2026-07-06 Slice 29 Frontend Run Manifest Panel

### Completed

- Added the pytest execution page `执行运行清单` panel.
- The panel derives command, working directory, runner mode, run workspace,
  repository-readonly policy, network policy, runtime files, dependency
  snapshot, environment snapshot, and output artifact availability from
  existing `TestRunRead` fields and Artifact metadata.
- Local open links are rendered only when an id matches a persisted Artifact row
  returned in `TestRunRead.artifacts`.
- Missing snapshots and missing output artifacts remain visible as unavailable
  evidence.
- Added focused frontend coverage for persisted local Artifact links and missing
  snapshot rows.
- Used parallel subagents for read-only implementation mapping and scoped Vue /
  spec drafts; main thread integrated and verified the final changes.
- Updated `NEXT_AI_TASK.md` to Slice 29 Task 4: Add execution run manifest
  golden smoke.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/PytestExecutionView.spec.ts`
- Result: `1` file passed, `1` test passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- Scoped whitespace/conflict-marker check on the two changed frontend files:
  no output.

### Notes

- Standard `git status`, `git diff --check`, and commit were blocked because
  this workspace has an empty `.git/` directory and no `git` executable on PATH.
- GitHub remote state for `YanChen0111/Chtest` could not be confirmed because
  the network request failed and the escalation request was rejected.

## 2026-07-01 Slice 29 Execution Run Manifest Contract

### Completed

- Defined execution run manifest as read-only presentation derived from
  existing TestRun fields and Artifact metadata.
- Required command, working directory, runner mode, workspace,
  repository-readonly policy, network policy, parsed result, and artifact
  availability to remain visible.
- Required missing runtime/dependency/environment snapshots to stay visible as
  unavailable evidence.
- Preserved the no runner behavior, report generation, FailureAnalysis,
  QualityGateDecision, remote provider, RAG runtime, or MCP runtime boundary.
- Updated `NEXT_AI_TASK.md` to Slice 29 Task 3: Add frontend run manifest panel.

### Next Step

- Commit `docs(v2): define execution run manifest contract`.
- Continue Slice 29 Task 3 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 29 Execution Run Manifest Plan

### Completed

- Selected Slice 29: Execution Run Manifest.
- Added `docs/implementation/slices/slice-29-execution-run-manifest.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 28 completion
  and Slice 29 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 29 Task 2: Define execution run manifest
  contract.

### Rationale

- Slices 24-28 made artifacts openable and evidence summaries readable across
  reports, AI Workbench, imported CI evidence, and quality gates.
- The remaining execution-level gap is explaining the TestRun itself: command,
  working directory, runner mode, workspace, repository/network policy,
  snapshots, and output artifacts.
- Slice 29 stays small by defining and displaying a read-only manifest from
  existing TestRun fields and Artifact metadata without changing runner
  behavior.

### Next Step

- Commit `docs(v2): add execution run manifest plan`.
- Continue Slice 29 Task 2 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 28 Completion Gate

### Completed

- Completed Slice 28: CI/CD Quality Gate Evidence Summary.
- Recorded Task 4 commit `2c0bd91`.
- Verified CI/CD Quality Center quality gate summaries remain readable,
  evidence-only, and local-artifact-limited.
- Confirmed missing UnitTestPatch, new-test, or regression evidence remains
  visible and returns `needs_review`, not `passed`.
- Updated `NEXT_AI_TASK.md` to select and plan the next narrow V2 slice.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_gate_evidence_summary_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q`
- Result: `2` passed.
- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.
- `npm --prefix frontend run test -- --run`
- Result: `16` files passed, `21` tests passed.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `docs(v2): complete quality gate evidence summary slice`.
- Continue with `NEXT_AI_TASK.md` to select and plan the next narrow V2 slice.

## 2026-07-01 Slice 28 Quality Gate Evidence Summary Golden Smoke

### Completed

- Added a Slice 28 golden smoke for CI/CD quality gate evidence summary inputs.
- Golden covers a passed quality gate with UnitTestPatch/PatchScopeGate,
  new-test, and regression evidence.
- Golden covers a missing-evidence quality gate returning `needs_review`.
- Golden asserts summary inputs do not create Report, FailureAnalysis,
  AutomationDraft, new Artifact rows, existing Artifact mutation, or
  remote-provider side effects.
- Added fixture documentation:
  `docs/fixtures/16-cicd-quality-gate-evidence-summary-golden.md`.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_gate_evidence_summary_golden.py -q`
- Result: `1` passed.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `test(golden): add quality gate evidence summary smoke`.
- Continue Slice 28 Completion Gate.

## 2026-07-01 Slice 28 CI/CD Quality Gate Frontend Summary

### Completed

- CI/CD Quality Center quality gate panel now shows a compact evidence summary.
- Summary includes UnitTestPatch/PatchScopeGate, new-test, and regression
  required evidence rows.
- Blocking reasons are visible in readable Chinese labels.
- Only the UnitTestPatch persisted Artifact id receives a local open link;
  new-test and regression rows remain structured evidence.
- Updated `NEXT_AI_TASK.md` to Slice 28 Task 4: Add quality gate evidence
  summary golden smoke.

### Verification

- `npm --prefix frontend run test -- --run src/views/cicd/CicdQualityCenterView.spec.ts`
- Result: `1` file passed, `2` tests passed.
- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `feat(frontend): summarize quality gate evidence`.
- Continue Slice 28 Task 4 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 28 Quality Gate Evidence Summary Contract

### Completed

- Defined quality gate evidence summary as read-only presentation derived from
  existing QualityGateDecision fields and Artifact metadata.
- Required UnitTestPatch/PatchScopeGate, new-test, and regression evidence rows
  to remain visible.
- Required blocking reasons and missing evidence to remain visible and not be
  treated as passing or downloadable evidence.
- Preserved the no quality gate computation, report generation, runner, remote
  provider, RBAC, tenant, RAG runtime, or MCP runtime boundary.
- Updated `NEXT_AI_TASK.md` to Slice 28 Task 3: Add CI/CD quality gate frontend
  summary.

### Next Step

- Commit `docs(v2): define quality gate evidence summary contract`.
- Continue Slice 28 Task 3 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 28 CI/CD Quality Gate Evidence Summary Plan

### Completed

- Selected Slice 28: CI/CD Quality Gate Evidence Summary.
- Added `docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 27 completion
  and Slice 28 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 28 Task 2: Define quality gate evidence
  summary contract.

### Rationale

- QualityGateDecision already stores status, summary, blocking reasons,
  `status_detail`, and evidence Artifact ids.
- The CI/CD Quality Center currently exposes the gate result but not enough
  readable evidence detail for required evidence and missing blockers.
- Slice 28 stays small by adding read-only summary clarity without changing
  quality gate computation, report generation, runner behavior, or remote CI
  provider integration.

### Next Step

- Commit `docs(v2): add quality gate evidence summary plan`.
- Continue Slice 28 Task 2 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 27 Completion Gate

### Completed

- Completed Slice 27: AI Task Evidence Artifact Links.
- Recorded Task 4 commit `f9bebbe`.
- Confirmed safe AI task artifacts can use local open links in AI Workbench.
- Confirmed unsafe raw LLM artifacts remain metadata-only, not inlined, and not
  directly openable in the UI.
- Confirmed no AI task rerun, provider call, Report, FailureAnalysis,
  QualityGateDecision, TestRun, artifact mutation, RAG runtime, or MCP runtime
  behavior was added.
- Updated `NEXT_AI_TASK.md` to select the next narrow V2 slice.

### Verification

- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.
- `npm --prefix frontend run test -- --run`
- Result: `16` files passed, `21` tests passed.
- `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ai_task_evidence_artifact_links_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q`
- Result: `2 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `docs(v2): complete ai task artifact link slice`.
- Select and plan the next V2 small slice.

## 2026-07-01 Slice 27 AI Task Artifact Link Golden Smoke

### Completed

- Added `backend/app/tests/golden/test_ai_task_evidence_artifact_links_golden.py`.
- Added `docs/fixtures/15-ai-task-evidence-artifact-links-golden.md`.
- Golden proves a safe `parsed_output` AI task artifact can be opened through
  local artifact access.
- Golden proves unsafe `raw_llm_output` remains metadata-only for UI link
  purposes and is not inlined by AI task detail.
- Golden proves artifact link display creates no AI task rerun, provider call,
  Report, FailureAnalysis, QualityGateDecision, TestRun, artifact mutation, RAG
  runtime, or MCP runtime behavior.
- Updated `NEXT_AI_TASK.md` to Slice 27 Completion Gate.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ai_task_evidence_artifact_links_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `test(golden): add ai task artifact link smoke`.
- Continue Slice 27 Completion Gate from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 27 AI Workbench Artifact Links

### Completed

- AI Workbench safe AI task artifacts now show a local "打开" link.
- `safe_to_show=false` artifacts, including raw LLM output, remain visible as
  metadata and show `不可直接打开`.
- LLM call logs continue to cite artifact ids without inlining content.
- Updated `NEXT_AI_TASK.md` to Slice 27 Task 4: Add AI task artifact link
  golden smoke.

### Verification

- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.

### Next Step

- Commit `feat(frontend): link safe ai task artifacts`.
- Continue Slice 27 Task 4 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 27 AI Task Artifact Link Contract

### Completed

- Defined AI task evidence artifact links as read-only local Artifact links.
- Required `safe_to_show=true` before AI Workbench may render a direct open
  link.
- Clarified `safe_to_show=false` artifacts, including raw LLM output, remain
  visible as metadata but not directly openable.
- Preserved the no raw LLM inline display, rerun, provider integration,
  artifact mutation, RAG runtime, and MCP runtime boundary.
- Updated `NEXT_AI_TASK.md` to Slice 27 Task 3: Add AI Workbench artifact
  links.

### Next Step

- Commit `docs(v2): define ai task artifact link contract`.
- Continue Slice 27 Task 3 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 27 AI Task Evidence Artifact Links Plan

### Completed

- Selected Slice 27: AI Task Evidence Artifact Links.
- Added `docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 26 completion
  and Slice 27 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 27 Task 2: Define AI task evidence
  artifact link contract.

### Rationale

- AI Workbench already shows AI task artifact metadata and safe display flags.
- Slice 24 already added read-only local artifact access.
- Slice 27 stays small by adding safe local artifact links for AI task evidence
  without showing raw LLM content inline, rerunning AI tasks, mutating
  artifacts, or adding provider/RAG/MCP runtime behavior.

### Next Step

- Commit `docs(v2): add ai task artifact link plan`.
- Continue Slice 27 Task 2 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 26 Completion Gate

### Completed

- Completed Slice 26: CI Imported Artifact Reference Clarity.
- Recorded Task 4 commit `d67b40e`.
- Confirmed imported external artifact references remain:
  - display-only inert metadata;
  - not locally openable;
  - not remotely fetched;
  - free of TestRun, Report, FailureAnalysis, QualityGateDecision, UnitTestPatch,
    AutomationDraft, or remote-provider side effects.
- Updated `NEXT_AI_TASK.md` to select the next narrow V2 slice.

### Verification

- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.
- `npm --prefix frontend run test -- --run`
- Result: `16` files passed, `21` tests passed.
- `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q`
- Result: `2 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `docs(v2): complete ci imported reference clarity slice`.
- Select and plan the next V2 small slice.

## 2026-07-01 Slice 26 Imported Reference Inert Golden Smoke

### Completed

- Added `backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py`.
- Added `docs/fixtures/14-ci-imported-artifact-reference-clarity-golden.md`.
- Golden proves imported external artifact references remain inert metadata.
- Golden proves local artifact access rejects the external reference with
  `ARTIFACT_NOT_LOCAL`.
- Golden proves local `ci_run_metadata.json` remains readable as local
  evidence.
- Golden proves imported reference metadata does not create TestRun, Report,
  FailureAnalysis, QualityGateDecision, UnitTestPatch, or AutomationDraft rows.
- Updated `NEXT_AI_TASK.md` to Slice 26 Completion Gate.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `test(golden): add ci imported reference clarity smoke`.
- Continue Slice 26 Completion Gate from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 26 CI Imported Reference Frontend Clarity

### Completed

- CI/CD Quality Center imported reference rows now show:
  - inert reference status;
  - `不可本地打开`;
  - `未远程拉取`;
  - external URL as reference text.
- Focused frontend test confirms no local artifact download link is rendered
  for imported external references.
- Updated `NEXT_AI_TASK.md` to Slice 26 Task 4: Add imported reference inert
  golden smoke.

### Verification

- `npm --prefix frontend run test -- --run src/views/cicd/CicdQualityCenterView.spec.ts`
- Result: `2 passed`.
- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `feat(frontend): clarify ci imported artifact references`.
- Continue Slice 26 Task 4 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 26 Imported Reference Display Contract

### Completed

- Defined imported artifact reference display as read-only external metadata.
- Clarified imported references are not local Artifact files and are not locally
  openable.
- Required display of inert status and `remote_fetch_performed=false`.
- Preserved the no remote fetch/provider integration boundary.
- Updated `NEXT_AI_TASK.md` to Slice 26 Task 3: Add CI imported reference
  frontend clarity.

### Next Step

- Commit `docs(v2): define imported reference clarity contract`.
- Continue Slice 26 Task 3 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 26 CI Imported Artifact Reference Clarity Plan

### Completed

- Selected Slice 26: CI Imported Artifact Reference Clarity.
- Added `docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 25 completion
  and Slice 26 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 26 Task 2: Define imported artifact
  reference display contract.

### Rationale

- CI import already stores external artifact references as inert evidence.
- The CI/CD Quality Center shows these references, but the local/non-local
  boundary can be clearer for users.
- The slice stays small by improving display clarity and preserving
  `remote_fetch_performed=false`, with no remote provider calls or downloads.

### Next Step

- Commit `docs(v2): add ci imported reference clarity plan`.
- Continue Slice 26 Task 2 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 25 Completion Gate

### Completed

- Completed Slice 25: Execution Evidence Summary.
- Recorded Task 4 commit `41c8f46`.
- Confirmed Slice 25 remains read-only and local-first:
  - no report generation behavior changes;
  - no automatic Report, FailureAnalysis, QualityGateDecision, or repair task;
  - no runner behavior changes;
  - no artifact upload, mutation, delete, sharing, cloud storage, signed URL,
    broad artifact browser, RAG runtime, MCP runtime, RBAC, tenants, or
    permissions expansion.
- Updated `NEXT_AI_TASK.md` to select and plan the next narrow V2 slice.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_evidence_summary_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q`
- Result: `2 passed`.
- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.
- `npm --prefix frontend run test -- --run`
- Result: `16` files passed, `21` tests passed.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `docs(v2): complete execution evidence summary slice`.
- Select and plan the next V2 small slice.

## 2026-07-01 Slice 25 Execution Evidence Summary Golden Smoke

### Completed

- Added `backend/app/tests/golden/test_execution_evidence_summary_golden.py`.
- Added `docs/fixtures/13-execution-evidence-summary-golden.md`.
- Golden proves a summary row can cite a persisted local Artifact and open it
  through the artifact access endpoint.
- Golden verifies downloaded bytes match persisted `sha256` and `size_bytes`.
- Golden keeps structured metric evidence non-downloadable, missing evidence
  explicit, and external imported artifact references inert.
- Updated `NEXT_AI_TASK.md` to Slice 25 Completion Gate.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_evidence_summary_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `test(golden): add execution evidence summary smoke`.
- Continue Slice 25 Completion Gate from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 25 Report Evidence Summary Frontend

### Completed

- Added local Artifact open links to report evidence summary rows.
- Added local Artifact open links to report artifact rows.
- Missing evidence rows now remain visible as `缺失不可打开`.
- Metric/TestResult evidence remains structured evidence rather than
  downloadable artifact evidence.
- Updated `NEXT_AI_TASK.md` to Slice 25 Task 4: Add execution evidence summary
  golden smoke.

### Verification

- `npm --prefix frontend run test -- --run src/views/reporting/ReportFailureAnalysisView.spec.ts`
- Result: `1 passed`.
- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `feat(frontend): summarize execution evidence`.
- Continue Slice 25 Task 4 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 25 Execution Evidence Summary Contract

### Completed

- Defined execution evidence summary as a read-only presentation concept in the
  API contract.
- Documented summary row derivation from `ReportRead.evidence_manifest`,
  Artifact metadata, local downloadability, and missing evidence.
- Added artifact contract rules for local-only evidence summary links.
- Updated `NEXT_AI_TASK.md` to Slice 25 Task 3: Add report evidence summary
  frontend.

### Next Step

- Commit `docs(v2): define execution evidence summary contract`.
- Continue Slice 25 Task 3 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 25 Execution Evidence Summary Plan

### Completed

- Selected Slice 25: Execution Evidence Summary.
- Added `docs/implementation/slices/slice-25-execution-evidence-summary.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 24 completion
  and Slice 25 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 25 Task 2: Define execution evidence
  summary contract.

### Rationale

- Slice 24 made execution artifacts openable.
- The next evidence-loop value is showing what those artifacts prove: required
  evidence, supporting claims, missing evidence, and local downloadability.
- The slice stays small by deriving summary rows from existing Report/TestRun
  evidence and not changing report generation, FailureAnalysis, runner behavior,
  or QualityGateDecision behavior.

### Next Step

- Commit `docs(v2): add execution evidence summary plan`.
- Continue Slice 25 Task 2 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 24 Completion Gate

### Completed

- Completed Slice 24: Local Artifact Access Links.
- Recorded Task 5 commit `0f27919`.
- Confirmed Slice 24 remains read-only and local-first:
  - no artifact upload, mutation, delete, sharing, cloud storage, or signed URL;
  - no external artifact fetch or remote provider behavior;
  - no runner behavior changes, Report, FailureAnalysis, QualityGateDecision,
    RAG runtime, MCP runtime, RBAC, tenants, or permissions expansion.
- Updated `NEXT_AI_TASK.md` to select and plan the next narrow V2 slice.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py backend/app/tests/golden/test_artifact_access_golden.py -q`
- Result: `5 passed`.
- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.
- `npm --prefix frontend run test -- --run`
- Result: `16` files passed, `21` tests passed.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `docs(v2): complete local artifact access slice`.
- Select and plan the next V2 small slice.

## 2026-07-01 Slice 24 Artifact Access Golden Smoke

### Completed

- Added `backend/app/tests/golden/test_artifact_access_golden.py`.
- Added `docs/fixtures/12-local-artifact-access-golden.md`.
- Golden proves a persisted local `TestRun` stdout artifact can be downloaded
  through `GET /api/artifacts/{artifact_id}/download`.
- Golden verifies downloaded bytes match persisted `sha256` and `size_bytes`.
- Golden verifies external imported artifact references remain inert with
  `ARTIFACT_NOT_LOCAL`.
- Updated `NEXT_AI_TASK.md` to Slice 24 Completion Gate.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_artifact_access_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `test(golden): add local artifact access smoke`.
- Continue Slice 24 Completion Gate from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 24 Frontend Artifact Links

### Completed

- Added `artifactDownloadUrl` helper.
- Added local Artifact access links to pytest, Playwright, Newman, and JMeter
  execution artifact tables.
- Preserved existing artifact metadata table display.
- Updated `NEXT_AI_TASK.md` to Slice 24 Task 5: Add artifact access golden
  smoke.

### Verification

- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.
- `npm --prefix frontend run test -- --run src/views/execution/JMeterExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts`
- Result: `4 passed`.
- `npm --prefix frontend run test -- --run`
- Result: `16 files passed, 21 tests passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `feat(frontend): link local execution artifacts`.
- Continue Slice 24 Task 5 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 24 Artifact Access Backend API

### Completed

- Added `GET /api/artifacts/{artifact_id}/download`.
- Added local file read through `LocalArtifactStore`.
- Added safe content-disposition filename handling.
- Added contract error paths for missing, unsafe, and non-local artifacts.
- Added `backend/app/tests/api/test_artifact_access.py`.
- Updated `NEXT_AI_TASK.md` to Slice 24 Task 4: Add frontend artifact links.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py -q`
- Result: `4 passed`.
- `backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py backend/app/tests/api/test_context_artifacts.py -q`
- Result: `13 passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `feat(artifact): add local artifact access api`.
- Continue Slice 24 Task 4 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 24 Artifact Access Contract

### Completed

- Defined `GET /api/artifacts/{artifact_id}/download` in the API contract.
- Added local artifact access rules to the artifact contract.
- Kept external CI imported artifact references inert.
- Updated `NEXT_AI_TASK.md` to Slice 24 Task 3: Add backend artifact download
  API.

### Next Step

- Commit `docs(v2): define artifact access contract`.
- Continue Slice 24 Task 3 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 24 Local Artifact Access Plan

### Completed

- Selected Slice 24: Local Artifact Access Links.
- Added `docs/implementation/slices/slice-24-local-artifact-access-links.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 23 completion
  and Slice 24 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 24 Task 2: Define local artifact access
  contract.

### Rationale

- Execution pages expose artifact paths, but local evidence artifacts should be
  directly accessible from the workbench.
- The slice stays small as read-only local Artifact access with no cloud
  storage, sharing, RBAC, tenants, permissions, or provider fetches.

### Next Step

- Commit `docs(v2): add local artifact access plan`.
- Continue Slice 24 Task 2 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 22 JMeter Local Runner Backend

### Completed

- Completed Slice 22 Task 4: Add JMeter runner backend.
- Extended `backend/app/modules/execution/jmeter_runner.py` with:
  - `JMeterRunner`;
  - allowlisted command validation;
  - non-GUI `jmeter -n -t <plan.jmx> -l <result.jtl>` command normalization;
  - JTL output path validation;
  - fake-executable-friendly subprocess execution.
- Extended project command allowlist for `command_type=jmeter`.
- Extended execution service with `runner_mode=jmeter_local` from configured
  active TestCommand.
- Persisted JMeter stdout/stderr, `jmeter_jtl`, parsed_result artifacts, and
  JMeter TestResult rows.
- Added API tests for successful fake JMeter execution and forbidden shell
  operator rejection.
- Updated Slice 22 table with Task 3 commit `0d1a666` and Task 4 done pending
  commit.
- Updated `NEXT_AI_TASK.md` to Slice 22 Task 5: Add JMeter execution frontend
  shell.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py backend/app/tests/api/test_newman_execution.py backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/api/test_playwright_minimal_loop.py -q
git diff --check
```

Results:

- JMeter runner/API tests: `5 passed`.
- JMeter + Newman + pytest + Playwright execution tests: `27 passed`.
- `git diff --check` clean.

### Next Step

- Commit with `feat(execution): add jmeter local runner`.
- Continue Slice 22 Task 5: add JMeter execution frontend shell.

## 2026-07-01 Slice 22 JMeter Parser

### Completed

- Completed Slice 22 Task 3: Add JMeter parser and backend API tests.
- Added `backend/app/modules/execution/jmeter_runner.py` with deterministic JTL
  parser support for:
  - CSV JTL rows;
  - XML `sample` / `httpSample` rows;
  - missing or empty JTL error handling.
- Added `backend/app/tests/api/test_jmeter_execution.py` covering parsed result
  counts, failure details, latency metadata, XML parsing, and missing/empty JTL
  errors.
- Parser returns JMeter TestResult candidates without invoking a local JMeter
  binary.
- Updated Slice 22 table with Task 2 commit `10fa27d` and Task 3 done pending
  commit.
- Updated `NEXT_AI_TASK.md` to Slice 22 Task 4: Add JMeter runner backend.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py backend/app/tests/api/test_newman_execution.py -q
git diff --check
```

Results:

- JMeter parser/API tests: `3 passed`.
- JMeter + Newman execution tests: `7 passed`.
- `git diff --check` clean.

### Next Step

- Commit with `feat(execution): parse jmeter evidence`.
- Continue Slice 22 Task 4: add JMeter runner backend.

## 2026-07-01 Slice 22 JMeter Execution Contract Boundary

### Completed

- Completed Slice 22 Task 2: Define JMeter execution contract boundary.
- Updated data contract to include:
  - `TestCommand.command_type=jmeter` boundary;
  - `TestRun.runner_mode=jmeter_local`;
  - JMeter TestRun parsed result expectations;
  - JMeter ToolDefinition allowlist rules.
- Updated API contract to keep JMeter under `POST /api/test-runs` with
  `runner_mode=jmeter_local` and no JMX editing or performance dashboard APIs.
- Updated state-machine contract to map sampler/assertion failure to `failed`
  and runtime/parser/allowlist issues to `error`.
- Updated artifact contract with `jmeter_jtl` and parsed JMeter evidence rules.
- Updated Slice 22 task table with Task 1 commit `59d3918` and Task 2 done
  pending commit.
- Updated `NEXT_AI_TASK.md` to Slice 22 Task 3: Add JMeter parser and backend
  API tests.

### Verification

```bash
rg -n "JMeter|jmeter|jmeter_local|jmeter_jtl|ToolDefinition|command_type" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-22-jmeter-local-execution.md
git diff --check
```

Results:

- JMeter contract keywords found across data/API/state/artifact contracts and
  Slice 22 plan.
- `git diff --check` clean.

### Next Step

- Commit with `docs(v2): define jmeter execution contract`.
- Continue Slice 22 Task 3: add JMeter parser and backend API tests.

## 2026-07-01 Slice 22 JMeter Local Execution Plan

### Completed

- Completed the planning task to select the next V2 small slice after Slice 21.
- User selected option A: JMeter local execution evidence.
- Incorporated read-only subagent review from `Pascal`, which recommended
  JMeter as Slice 22 while keeping Task 1 planning-only and Task 2
  contract-first.
- Added `docs/implementation/slices/slice-22-jmeter-local-execution.md`.
- Updated `docs/implementation/10-v2-scope-options.md`:
  - records Slice 21 completion;
  - recommends Slice 22 JMeter local execution evidence;
  - keeps JMeter scoped to local non-GUI runner evidence.
- Updated `NEXT_AI_TASK.md` to Slice 22 Task 2: Define JMeter execution
  contract boundary.
- Explicitly kept out JMX editing, performance dashboards, distributed JMeter,
  cloud load testing, arbitrary shell execution, secrets management, CI
  provider controls, RAG runtime, MCP runtime, RBAC, tenants, and permissions.

### Verification

```bash
test -f docs/implementation/slices/slice-22-jmeter-local-execution.md
rg -n "JMeter|jmeter|jmeter_local|Product Value Answer|Non-goals|Task Table|Task 2" docs/implementation/slices/slice-22-jmeter-local-execution.md docs/implementation/10-v2-scope-options.md
git diff --check
```

Results:

- Slice 22 plan file exists.
- JMeter planning keywords found in Slice 22 plan and V2 scope options.
- `git diff --check` clean.

### Next Step

- Commit with `docs(v2): add jmeter execution slice plan`.
- Continue Slice 22 Task 2: define JMeter execution contract boundary.

## 2026-07-01 Slice 21 Completion Gate

### Completed

- Completed Slice 21: Local Review Attribution History.
- Recorded all Slice 21 task rows as done through Task 6.
- Confirmed ReviewHistory remains local append-only attribution evidence:
  - no public generic ReviewHistory create/update/delete endpoint;
  - no RBAC, roles, permissions, tenants, assignment, notification, team inbox,
    remote provider governance, RAG runtime, or MCP runtime expansion.
- Updated `NEXT_AI_TASK.md` to select the next V2 small slice after Slice 21
  completion.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/golden/test_review_history_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- ReviewHistory API + golden: `6 passed`.
- Full frontend suite: `15` files passed, `20` tests passed.
- `git diff --check` clean.

### Next Step

- Commit with `docs(v2): complete local review history slice`.
- Select the next V2 small slice.

## 2026-07-01 Slice 21 Review History Golden Smoke

### Completed

- Completed Slice 21 Task 6: Add review history golden smoke.
- Added fixture `docs/fixtures/10-local-review-history-golden.md`.
- Added golden test
  `backend/app/tests/golden/test_review_history_golden.py`.
- Golden exercises existing review-gated evidence actions:
  - creates a local CICDRun from static diff evidence;
  - generates and approves a test-only UnitTestPatch;
  - applies the approved patch so new-test evidence can run;
  - records new-test and regression evidence;
  - computes a QualityGateDecision.
- Golden confirms ReviewHistory records:
  - UnitTestPatch `approve`, `scope_validated -> approved`, comment, reviewer,
    timestamp, and related CICDRun;
  - QualityGateDecision `compute_quality_gate`, `pending -> passed`, reviewer,
    timestamp, evidence ids, and related CICDRun;
  - related CICDRun history returns both events.
- Guardrails confirm no roles, permissions, or tenants table is introduced.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_review_history_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/golden/test_review_history_golden.py -q
git diff --check
```

Results:

- ReviewHistory golden smoke: `1 passed`.
- ReviewHistory API + golden: `6 passed`.
- `git diff --check` clean.

### Next Step

- Commit with `test(golden): add local review history smoke`.
- Continue Slice 21 Completion Gate.

## 2026-07-01 Slice 21 Frontend Review History Panels

### Completed

- Completed Slice 21 Task 5: Add frontend review history panels.
- Added frontend ReviewHistory API typing/helper for `GET /api/review-history`.
- Added local review history state and load actions to:
  - case generation review;
  - AutomationDraft review;
  - CI/CD UnitTestPatch and QualityGateDecision flows.
- Added compact secondary history panels in existing review surfaces:
  - TestCase candidate review;
  - AutomationDraft review;
  - UnitTestPatch review;
  - QualityGateDecision compute.
- Panels show action, reviewer, status transition, timestamp, comment, and
  evidence count with Chinese-facing labels while preserving product terms such
  as TestCase, AutomationDraft, UnitTestPatch, and QualityGateDecision.
- Added focused frontend assertions for local history display and
  review-history API reads.

### Verification

```bash
npm --prefix frontend run test -- --run src/views/cases/CaseGenerationReviewView.spec.ts src/views/automation/AutomationDraftReviewView.spec.ts src/views/cicd/CicdQualityCenterView.spec.ts
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- Focused review surface tests: `3` files passed, `4` tests passed.
- Full frontend suite: `15` files passed, `20` tests passed.
- `git diff --check` clean.

### Next Step

- Commit with `feat(frontend): show local review history`.
- Continue Slice 21 Task 6: add review history golden smoke.

## 2026-07-01 Slice 21 Review History Action Hooks

### Completed

- Completed Slice 21 Task 4: Attach history to existing review actions.
- Hooked ReviewHistory append side effects into successful existing actions:
  - GeneratedCaseCandidate approve / approve_after_edit / reject.
  - AutomationDraft edit / approve.
  - UnitTestPatch approve / reject.
  - QualityGateDecision compute / recompute.
- Preserved existing state-machine validation. Invalid actions still fail before
  history is appended.
- QualityGateDecision history records the created decision as the primary
  entity and the CICDRun as related entity.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_unit_test_patch_regression.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_unit_test_patch_regression.py backend/app/tests/api/test_ci_run_metadata_import.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q
git diff --check
```

Results:

- Task 4 focused tests: `37 passed`.
- Related backend + golden regression: `91 passed`.
- `git diff --check` clean.

### Next Step

- Commit with `feat(review): record review history events`.
- Continue Slice 21 Task 5: add frontend review history panels.

## 2026-07-01 Slice 21 Review History Model And Service

### Completed

- Completed Slice 21 Task 3: Add review history model and service.
- Added backend ReviewHistory module:
  - SQLAlchemy model for local append-only events;
  - schemas for read/list responses;
  - service helpers for append and focused list queries;
  - `GET /api/review-history` router;
  - FastAPI router registration.
- Added Alembic migration `20260701_0006_review_history.py`.
- Added focused tests for:
  - default `Default User` attribution;
  - append-only persistence through service helper;
  - same-project evidence Artifact validation;
  - entity and related-entity filtered API reads;
  - no generic public `POST /api/review-history`;
  - migration table creation.
- Kept Task 3 scoped to persistence/read surface only. Existing review actions
  are not hooked yet; that remains Slice 21 Task 4.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/api/test_projects.py backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/db/test_case_generation_models.py -q
git diff --check
```

Results:

- ReviewHistory focused tests: `5 passed`.
- Related backend regression: `23 passed`.
- `git diff --check` clean.

### Next Step

- Completed in commit `31bb8cc`.

## 2026-07-01 Slice 21 Review History Contract Boundary

### Completed

- Completed Slice 21 Task 2: Define review history contract boundary.
- Added `ReviewHistory` data contract as local append-only evidence.
- Defined deterministic local `Default User` reviewer attribution as a display
  label, not an auth principal.
- Added API contract for `GET /api/review-history` as a read-only local review
  history surface.
- Defined state-machine side effects for:
  - GeneratedCaseCandidate review.
  - AutomationDraft edit/approval/rejection.
  - UnitTestPatch approval/rejection.
  - QualityGateDecision compute/recompute.
- Defined artifact boundary: ReviewHistory references existing Artifact ids and
  does not add a dedicated artifact type in Slice 21.
- Incorporated subagent review guidance:
  - Generated case approval history is written to GeneratedCaseCandidate and
    displayed by TestCase through `source_candidate_id`.
  - QualityGateDecision history records the CICDRun `quality_gate_status`
    transition via related entity fields.
- Updated `NEXT_AI_TASK.md` to Slice 21 Task 3: Add review history model and
  service.

### Verification

```bash
rg -n "ReviewHistory|review history|review attribution|Default User|RBAC|permissions" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-21-local-review-attribution-history.md
git diff --check
```

Results:

- ReviewHistory contract keywords found in data/API/state/artifact contracts
  and Slice 21 plan.
- `git diff --check` clean.

### Next Step

- Completed in commit `b77262b`.

## 2026-07-01 V2 Next Slice Selection After Slice 20

### Completed

- Completed the planning task to select the next V2 small slice after Slice 20.
- Ran parallel subagent reviews for:
  - Candidate Direction B follow-up: JMeter local execution evidence.
  - Candidate Direction C: local review attribution/history.
- Selected Candidate Direction C, renamed and narrowed to:
  `Slice 21: Local Review Attribution History`.
- Rationale:
  - Slice 18, Slice 19, and Slice 20 added more evidence sources.
  - The next highest value is making the human review side of the evidence loop
    more traceable.
  - Local review history strengthens Chtest's human-reviewed, evidence-backed
    positioning without requiring external tools.
  - JMeter local execution evidence remains a strong follow-up candidate, but it
    depends on another runner/tool path.
- Added `docs/implementation/slices/slice-21-local-review-attribution-history.md`.
- Updated `docs/implementation/10-v2-scope-options.md`:
  - records Slice 20 completion;
  - recommends Slice 21 local review attribution/history;
  - keeps JMeter local execution evidence as a future candidate.
- Updated `NEXT_AI_TASK.md` to Slice 21 Task 2: define review history contract
  boundary.

### Verification

```bash
test -f docs/implementation/slices/slice-21-local-review-attribution-history.md
rg -n "Local Review Attribution History|Product Value Answer|Non-goals|Task Table|append-only|RBAC|permissions" docs/implementation/slices/slice-21-local-review-attribution-history.md docs/implementation/10-v2-scope-options.md
git diff --check
```

Results:

- Slice 21 plan file exists.
- Scope keywords found in Slice 21 plan and V2 scope options.
- `git diff --check` clean.

### Next Step

- Completed in commit `f121483`.

## 2026-07-01 Slice 20 Completion Gate

### Completed

- Completed Slice 20: CI Run Metadata Import.
- Ran completion verification:
  - CI import API tests;
  - CI import golden smoke;
  - full frontend suite;
  - diff whitespace check.
- Confirmed Slice 20 remains import-only and evidence-first:
  - no remote CI provider calls;
  - no webhook receiver;
  - no pipeline trigger/rerun/cancel/schedule;
  - no PR comment, deploy, release, credential, RBAC, tenant, permission,
    marketplace, RAG runtime, or MCP runtime expansion.
- Updated Slice 20 task table:
  - Task 6 commit recorded as `499ec1d`;
  - completion gate marked done pending commit.
- Updated `NEXT_AI_TASK.md` to select the next V2 small slice after Slice 20.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py backend/app/tests/golden/test_ci_run_metadata_import_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- Slice 20 API + golden tests: `54 passed`.
- Frontend suite: `15` files passed, `20` tests passed.
- `git diff --check` clean.

### Next Step

- Commit completion gate with `docs(v2): complete ci metadata import slice`.
- Select the next V2 small slice.

## 2026-07-01 Slice 20 CI Import Golden Smoke

### Completed

- Completed Slice 20 Task 6: Add CI import golden smoke.
- Added golden fixture:
  `docs/fixtures/09-ci-run-metadata-import-golden.md`.
- Added golden smoke:
  `backend/app/tests/golden/test_ci_run_metadata_import_golden.py`.
- Golden proves static CI metadata import creates:
  - `CICDRun(source_type=ci_import, trigger_type=imported, status=imported)`;
  - deterministic `CICDChangedFile` rows;
  - `ci_run_metadata` evidence artifact;
  - compatible `changed_files` evidence artifact;
  - frontend-readable `ci_run_metadata` in `GET /api/cicd/runs/{id}`.
- Golden confirms imported CI conclusion remains evidence only:
  - `quality_gate_status=pending`;
  - no QualityGateDecision, UnitTestPatch, AutomationDraft, TestRun, or Report;
  - `remote_fetch_performed=false`;
  - imported artifact references are inert references.
- Updated Slice 20 task table:
  - Task 5 commit recorded as `6aedab0`;
  - Task 6 marked done pending commit.
- Updated `NEXT_AI_TASK.md` to Slice 20 Completion Gate.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_run_metadata_import_golden.py -q
```

Results:

- CI import golden smoke: `1 passed`.

### Next Step

- Run related backend/frontend/diff checks.
- Commit Task 6 with `test(golden): add ci metadata import smoke`.
- Continue Slice 20 Completion Gate.

## 2026-07-01 Slice 20 CI Import Frontend Evidence

### Completed

- Completed Slice 20 Task 5: Add CI import frontend evidence display.
- Added CI import evidence rendering in `CI/CD 质量中心`:
  - provider inert label;
  - import status;
  - CI conclusion;
  - QualityGateDecision pending/local gate separation;
  - job/external run id;
  - inert imported artifact references.
- Kept risk analysis evidence table focused on `risk_analysis`.
- Extended the narrow CICDRun read evidence surface so
  `analysis_artifacts` includes `ci_run_metadata` as frontend-readable import
  evidence. This stayed under `/api/cicd/runs/{id}` and did not use the RAG
  extension surface.
- Added frontend API types for CI import evidence content and artifact
  references.
- Added a view test proving imported CI evidence renders and remote provider
  control labels are absent.
- Updated Slice 20 task table:
  - Task 4 commit recorded as `554e74c`;
  - Task 5 marked done pending commit.
- Updated `NEXT_AI_TASK.md` to Slice 20 Task 6: CI import golden smoke.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/api/test_ci_run_metadata_import.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- CI metadata import API tests: `53 passed`.
- Existing CI/CD quality center + import API tests: `60 passed`.
- Frontend suite: `15` files passed, `20` tests passed.
- `git diff --check` clean.

### Next Step

- Commit Task 5 with `feat(frontend): show ci import evidence`.
- Continue Slice 20 Task 6: Add CI import golden smoke.

## 2026-07-01 Slice 20 CI Import API

### Completed

- Completed Slice 20 Task 4: Add CI run import API.
- Added `POST /api/cicd/runs/import`.
- Added import response schemas for created artifacts and import status.
- Persisted imported CI metadata as evidence-only records:
  - `CICDRun` with `source_type=ci_import`, `trigger_type=imported`, inert
    provider label, refs, pipeline name, `status=imported`, and
    `quality_gate_status=pending`;
  - `CICDChangedFile` rows created from deterministic parser output;
  - `ci_run_metadata.json` Artifact metadata/content;
  - compatible `changed_files.json` Artifact manifest.
- Added duplicate import rejection by project/repository/provider/external run
  id using `CI_IMPORT_DUPLICATE_EXTERNAL_RUN`.
- Mapped CI import parser errors through API error codes without adding remote
  provider behavior.
- Confirmed import does not create `QualityGateDecision`, `UnitTestPatch`,
  `AutomationDraft`, `TestRun`, or `Report`.
- Updated Slice 20 task table:
  - Task 3 commit recorded as `21ce127`;
  - Task 4 marked done pending commit.
- Updated `NEXT_AI_TASK.md` to Slice 20 Task 5: frontend evidence display.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/api/test_ci_run_metadata_import.py -q
git diff --check
```

Results:

- CI metadata import API tests: `53 passed`.
- Existing CI/CD quality center + import API tests: `60 passed`.
- `git diff --check` clean.

### Next Step

- Commit Task 4 with `feat(cicd): add ci metadata import api`.
- Continue Slice 20 Task 5: frontend evidence display.

## 2026-07-01 Slice 20 CI Metadata Parser

### Completed

- Completed Slice 20 Task 3: Add deterministic CI metadata parser.
- Added parser-only CI import schemas:
  - changed file import items;
  - inert artifact reference items;
  - CI run metadata import request shape.
- Added deterministic parser service:
  - parses static CI metadata JSON into an internal parsed import model;
  - normalizes changed files through existing `classify_file_role`,
    `detect_language`, and `classify_risk` rules;
  - emits `ci_run_metadata.json`-ready content and metadata with
    `provider_is_inert_label=true`, `remote_fetch_performed=false`, and
    `quality_gate_auto_decision=false`;
  - preserves imported artifact references as inert references only.
- Added CI import error classes with contract error codes for invalid payloads,
  remote control fields, credentials, unsupported provider operations, and
  external fetch requests.
- Added parser tests covering:
  - provider label, pipeline/job, conclusion, refs, timestamps, duration,
    changed files, and artifact references;
  - source/test changed-file role and risk normalization;
  - remote-control fields, credentials, external fetch requests, provider
    operations, malformed changed files, and invalid artifact references.
- Updated Slice 20 task table:
  - Task 2 commit recorded as `2201b94`;
  - Task 3 marked done pending commit.
- Updated `NEXT_AI_TASK.md` to Slice 20 Task 4: Add CI run import API.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/api/test_ci_run_metadata_import.py -q
```

Results:

- CI metadata import parser tests: `46 passed`.
- Existing CI/CD quality center + import parser tests: `53 passed`.

### Next Step

- Run final `git diff --check`.
- Commit Task 3 with `feat(cicd): add ci metadata import parser`.
- Continue Slice 20 Task 4: Add CI run import API.

## 2026-06-30 Slice 20 CI Import Contract Boundary

### Completed

- Completed Slice 20 Task 2: Define CI import contract boundary.
- Updated data contract:
  - allows `source_type=ci_import`;
  - keeps provider values as inert source labels;
  - records imported CI conclusion as evidence only;
  - keeps QualityGateDecision from auto-passing based on imported status.
- Updated API contract:
  - adds `POST /api/cicd/runs/import` contract;
  - defines request/response shape for static CI metadata import;
  - rejects control fields, webhook/trigger/rerun/deploy/release behavior,
    credentials, external fetches, and provider operations.
- Updated state-machine contract:
  - defines import status as local evidence import state;
  - keeps `quality_gate_status=pending` until explicit gate recompute.
- Updated artifact contract:
  - adds `ci_run_metadata.json`;
  - defines inert artifact references and `remote_fetch_performed=false`.
- Updated error-code contract:
  - defines CI import payload/control/credential/provider/fetch/duplicate
    rejection codes.
- Addressed document review findings:
  - added `imported` and `import_failed` CICDRun statuses to the data contract;
  - added `ci_run_metadata` to the data-model Artifact type list;
  - made provider label lists consistent;
  - made `trigger_type=imported` explicit in the API contract;
  - clarified imported CI run details live in `ci_run_metadata.json`, not
    CICDRun columns.
- Updated Slice 20 task table with Task 1 commit `b1acde6` and Task 2 pending
  commit.
- User approved continuing development on 2026-07-01.
- Updated `NEXT_AI_TASK.md` to Slice 20 Task 3: deterministic CI metadata
  parser.

### Verification

```bash
rg -n "ci_import|CI import|imported CI|ci_run_metadata|remote CI provider|QualityGateDecision|CI_IMPORT_" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/06-error-code-contract.md docs/implementation/slices/slice-20-ci-run-metadata-import.md
git diff --check
```

Results:

- Contract boundary keywords found across data, API, state-machine, artifact,
  error-code, and Slice 20 docs.
- `git diff --check` clean.

### Next Step

- Commit Task 2 with `docs(cicd): define ci metadata import boundary`.
- Continue Slice 20 Task 3: deterministic CI metadata parser.

## 2026-06-30 V2 Next Slice Selection

### Completed

- Completed the planning task to select the next V2 small slice after Slice 19.
- Ran parallel subagent reviews for:
  - Candidate Direction B: runner expansion. Recommendation was JMeter local
    execution evidence, not Appium or traffic capture.
  - Candidate Direction C: local review attribution/history, explicitly not
    RBAC or permissions.
  - Candidate Direction D: import-only CI evidence bridge.
- Selected Candidate Direction D as the next slice:
  `Slice 20: CI Run Metadata Import`.
- Rationale:
  - It directly extends the existing CI/CD 管理 evidence workflow from Slice 15
    and Slice 16.
  - It imports external CI facts into Chtest without controlling remote
    providers.
  - It keeps imported status as evidence, not authority for
    QualityGateDecision.
- Added `docs/implementation/slices/slice-20-ci-run-metadata-import.md`.
- Updated `docs/implementation/10-v2-scope-options.md`:
  - records Slice 19 completion;
  - marks deterministic retrieval as delivered;
  - recommends Slice 20 import-only CI metadata evidence.
- Updated `NEXT_AI_TASK.md` to Slice 20 Task 1.

### Verification

```bash
test -f docs/implementation/slices/slice-20-ci-run-metadata-import.md
rg -n "CI Run Metadata Import|Product Value Answer|Non-goals|Task Table|import-only|remote CI provider" docs/implementation/slices/slice-20-ci-run-metadata-import.md docs/implementation/10-v2-scope-options.md
git diff --check
```

Results:

- Slice 20 plan file exists.
- Scope keywords found in Slice 20 plan and V2 scope options.
- `git diff --check` clean.

### Next Step

- Commit with `docs(v2): add ci run metadata import slice plan`.
- Continue Slice 20 Task 2: define CI import contract boundary.

## 2026-06-30 Slice 19 Completion Gate

### Completed

- Completed Slice 19: Deterministic Knowledge Retrieval Stub.
- Updated Slice 19 task table:
  - Task 5 commit recorded as `b578fac`.
  - Task 6 commit recorded as `ebd67af`.
  - Completion gate marked done pending commit.
- Confirmed deterministic retrieval remains local and evidence-first:
  - no vector database;
  - no embeddings;
  - no reranking;
  - no external RAG provider runtime;
  - no MCP runtime dependency;
  - no RBAC, tenants, permissions, marketplace, cloud sync, or remote CI
    provider integration.
- Updated `NEXT_AI_TASK.md` to select the next V2 small slice.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- Backend deterministic retrieval + requirement review + extension surface +
  golden smoke: `23 passed`.
- Frontend suite: `15` files passed, `19` tests passed.
- `git diff --check` clean.

### Next Step

- Commit completion gate with `docs(v2): complete deterministic knowledge retrieval slice`.
- Then select the next V2 small slice from `NEXT_AI_TASK.md`.

## 2026-06-30 Slice 19 Deterministic Retrieval Golden Smoke

### Completed

- Added deterministic retrieval golden fixture:
  `docs/fixtures/08-deterministic-knowledge-retrieval-golden.md`.
- Added golden smoke:
  `backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py`.
- Golden flow proves:
  - safe `coupon-api-notes.md` ContextArtifact creation;
  - deterministic local KnowledgeAdapter configuration;
  - requirement review with `use_knowledge=true`;
  - exact retrieved ContextArtifact ids in review response and AITask output;
  - persisted `knowledge_retrieval` evidence Artifact metadata;
  - persisted `knowledge_retrieval.json` content with query terms, matched
    terms, score, snippet, SHA256, prompt eligibility, and redaction state;
  - RAG 知识库 `/knowledge-base` latest retrieval evidence display surface.
- Golden asserts no vector index, embedding, MCP runtime, tenant, role, or
  permission dependency is introduced.
- Fixed the narrow evidence-surface gap exposed by the golden smoke:
  requirement review now stores bounded retrieval result summaries in
  `knowledge_retrieval` Artifact metadata, so `/knowledge-base` can derive
  latest snippets/scores/matched terms from metadata.
- Updated Slice 19 task table so Task 5 records commit `b578fac` and Task 6 is
  done pending commit.
- Updated `NEXT_AI_TASK.md` to Slice 19 Completion Gate.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
git diff --check
```

Results:

- Golden smoke: `1 passed`.
- Related backend deterministic retrieval, requirement review, extension
  surface, and golden tests: `23 passed`.
- `git diff --check` clean.

### Next Step

- Commit Task 6 with `test(golden): add deterministic knowledge retrieval smoke`.
- Then run Slice 19 Completion Gate verification and close the slice.

## 2026-06-30 Slice 19 Retrieval Evidence Frontend Display

### Completed

- RAG 知识库 frontend now displays deterministic retrieval evidence.
- Added latest retrieval summary types in the frontend extension API.
- Added store getter for latest retrievals.
- KnowledgeBaseView now shows:
  - retrieval evidence count;
  - KnowledgeAdapter retrieval mode;
  - ContextArtifact retrieved count and latest retrieved time;
  - latest retrieval query terms, matched terms, scores, snippets, and source
    ContextArtifact titles.
- Added empty state for pages without retrieval evidence.
- Added a narrow backend extension surface derivation so `/knowledge-base`
  returns `retrieved_count`, `latest_retrieved_at`, and `latest_retrievals`
  from `knowledge_retrieval` artifacts.

### Verification

```bash
npm --prefix frontend run test -- --run
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py backend/app/tests/api/test_deterministic_knowledge_retrieval.py -q
git diff --check
```

Results:

- Frontend suite: `15` files passed, `19` tests passed.
- Extension + deterministic retrieval API tests: `12 passed`.
- `git diff --check` clean.

### Next Step

- Add deterministic retrieval golden smoke fixture and test.

## 2026-06-30 Slice 19 Retrieval Evidence On Requirement Review

### Completed

- Attached deterministic local retrieval to requirement review when
  `use_knowledge=true`.
- Requirement review now injects retrieved ContextArtifact ids into the AI task
  context manifest only when snippets are actually retrieved.
- Added `knowledge_retrieval.json` evidence artifacts owned by AITask with
  query terms, matched terms, scores, snippets, ContextArtifact ids, SHA256,
  and redaction/prompt eligibility metadata.
- AITask output now records `used_knowledge=true`,
  `used_context_artifact_ids`, and `retrieval_evidence_artifact_id` only when
  retrieval evidence exists.
- Preserved `use_knowledge=false` behavior, including explicit
  `context_artifact_ids`.
- Added regression coverage for configured-but-disabled retrieval paths,
  adapter-not-configured paths, mixed explicit/retrieved context ids, and
  persisted evidence artifact content.
- Updated `NEXT_AI_TASK.md` to Slice 19 Task 5: retrieval evidence frontend
  display.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py -q
git diff --check
```

Results:

- Deterministic retrieval + requirement review tests: `16 passed`.
- `git diff --check` clean.

### Next Step

- Display latest deterministic retrieval evidence on the RAG 知识库 frontend
  without adding vector search, external provider config, MCP runtime, RBAC,
  tenants, permissions, marketplace, cloud sync, or remote CI provider controls.

## 2026-06-30 Slice 19 Deterministic Retrieval Service

### Completed

- Added deterministic local retrieval service in the extension module.
- Added `POST /api/projects/{project_id}/knowledge-adapter/retrieve`.
- Allowed `provider_type=deterministic_local` for the V2 local stub while
  keeping config updates from setting `used_knowledge=true`.
- Retrieval reads only same-project ContextArtifacts with `safe_to_show=true`
  and `allowed_for_prompt=true`.
- Retrieval returns bounded snippets, deterministic scores, matched terms,
  ContextArtifact ids, SHA256, and prompt eligibility metadata.
- Added focused TDD coverage for service matching, API ordering/limits,
  disabled/not configured adapters, deterministic local config, and Chinese
  query terms.
- Updated `NEXT_AI_TASK.md` to Slice 19 Task 4: attach retrieval evidence to
  requirement review AI task flows.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py -q
git diff --check
```

### Next Step

- Attach retrieval evidence to requirement review AITask output and artifact
  records without adding external RAG, MCP runtime, vector search, embeddings,
  reranking, RBAC, tenants, or permissions.

## 2026-06-30 Slice 19 Deterministic Retrieval Contract Boundary

### Completed

- Updated data, API, state-machine, and artifact contracts for deterministic
  local knowledge retrieval.
- Added `provider_type=deterministic_local` as a V2 KnowledgeAdapter stub mode.
- Added `knowledge_retrieval` artifact contract and evidence shape.
- Clarified when `used_knowledge=true` is valid.
- Updated `NEXT_AI_TASK.md` to Slice 19 Task 3: add local retrieval service.

### Verification

```bash
rg -n "Deterministic|KnowledgeAdapter|ContextArtifact|used_knowledge|retrieval|retrieved" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
git diff --check
```

### Next Step

- Implement deterministic local retrieval service with focused backend tests.

## 2026-06-30 Slice 19 Deterministic Knowledge Retrieval Plan

### Completed

- Added
  `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`.
- Scoped Slice 19 to deterministic local ContextArtifact retrieval evidence.
- Defined task table, expected files, verification commands, and non-goals.
- Updated `NEXT_AI_TASK.md` to Slice 19 Task 2: define deterministic retrieval
  contract boundary.

### Verification

```bash
test -f docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
rg -n "Product Value Answer|Non-goals|Task Table|Deterministic|ContextArtifact|KnowledgeAdapter" docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
git diff --check
```

### Next Step

- Update contracts for deterministic retrieval evidence before implementation.

## 2026-06-30 V2 Next Slice Selection

### Completed

- Updated `docs/implementation/10-v2-scope-options.md` with Slice 18 completion
  status.
- Selected `Slice 19: Deterministic Knowledge Retrieval Stub` as the next small
  V2 slice.
- Kept the next slice scoped to local ContextArtifact retrieval evidence, not a
  full RAG platform.
- Updated `NEXT_AI_TASK.md` to V2 Task 4: draft the Slice 19 plan.

### Verification

```bash
rg -n "V2 Progress|Recommended Next V2 Slice|Slice 19|Still Out Of Scope" docs/implementation/10-v2-scope-options.md
git diff --check
```

### Next Step

- Draft `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`.

## 2026-06-30 Slice 18 Completion Gate

### Completed

- Completed Slice 18: Newman API Execution.
- Recorded completion evidence in
  `docs/implementation/slices/slice-18-newman-api-execution.md`.
- Updated `NEXT_AI_TASK.md` to V2 Task 3: select the next small V2 slice.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_newman_execution.py backend/app/tests/golden/test_newman_api_execution_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- Newman API + golden tests: `5 passed`.
- Frontend suite: `15` test files passed, `18` tests passed.
- `git diff --check` clean.

### Next Step

- Select the next small V2 slice from current product priorities.

## 2026-06-30 Slice 18 Newman Golden Smoke

### Completed

- Added `backend/app/tests/golden/test_newman_api_execution_golden.py`.
- Added `docs/fixtures/07-newman-api-execution-golden.md`.
- Proved configured Newman TestCommand -> TestRun -> artifacts -> TestResult
  evidence chain.
- Updated `NEXT_AI_TASK.md` to Slice 18 completion gate.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_newman_api_execution_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_newman_execution.py backend/app/tests/golden/test_newman_api_execution_golden.py -q
git diff --check
```

Results:

- Newman golden smoke: `1 passed`.
- Newman API + golden: `5 passed`.
- `git diff --check` clean.

### Next Step

- Run Slice 18 completion gate and record final evidence.

## 2026-06-30 Slice 18 Newman Frontend Shell

### Completed

- Added `frontend/src/views/execution/NewmanExecutionView.vue`.
- Added focused Newman frontend test.
- Added `/execution/newman` route and `API 执行` navigation item.
- Reused execution store with `runner_mode=newman_local` and TestCommand-only
  source.
- Updated `NEXT_AI_TASK.md` to Slice 18 Task 5: add Newman golden smoke.

### Verification

```bash
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- Frontend suite: `15` test files passed, `18` tests passed.
- `git diff --check` clean.

### Next Step

- Add Newman API execution golden smoke and fixture documentation.

## 2026-06-30 Slice 18 Newman Backend Runner

### Completed

- Added Newman runner/parser backend.
- Added `command_type=newman` allowlist support.
- Added `runner_mode=newman_local` service branch.
- Persisted Newman stdout/stderr, `newman_json`, `parsed_output`, TestRun, and
  assertion-level TestResult evidence.
- Added deterministic API tests with a fake `npx` executable.
- Updated `NEXT_AI_TASK.md` to Slice 18 Task 4: add Newman frontend shell.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_newman_execution.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/api/test_playwright_minimal_loop.py backend/app/tests/api/test_test_commands.py -q
git diff --check
```

Results:

- Newman focused API tests: `4 passed`.
- Adjacent execution/project tests: `27 passed`.
- `git diff --check` clean.

### Next Step

- Add the Newman API execution frontend shell.

## 2026-06-30 Slice 18 Newman Contract Boundary

### Completed

- Updated data, API, state-machine, and artifact contracts for Newman API
  execution.
- Added `command_type=newman`, `runner_mode=newman_local`, Newman parsed result
  expectations, and `newman_json` artifact rules.
- Kept Newman under TestCommand/ToolDefinition allowlists and `/api/test-runs`.
- Updated `NEXT_AI_TASK.md` to Slice 18 Task 3: add the Newman backend
  runner/parser.

### Verification

```bash
rg -n "Newman|newman|newman_json|command_type|ToolDefinition" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-18-newman-api-execution.md
git diff --check
```

### Next Step

- Implement the backend Newman runner/parser with deterministic API tests.

## 2026-06-30 Slice 18 Newman API Execution Plan

### Completed

- Added `docs/implementation/slices/slice-18-newman-api-execution.md`.
- Scoped the first V2 slice to local Newman API execution evidence.
- Defined task table, expected files, verification commands, and non-goals.
- Updated `NEXT_AI_TASK.md` to Slice 18 Task 2: define the Newman contract
  boundary.

### Verification

```bash
test -f docs/implementation/slices/slice-18-newman-api-execution.md
rg -n "Product Value Answer|Non-goals|Task Table|Task 2" docs/implementation/slices/slice-18-newman-api-execution.md
git diff --check
```

### Next Step

- Update contracts for `command_type=newman`, Newman artifacts, parsed result
  expectations, and ToolDefinition allowlist boundaries before implementation.

## 2026-06-30 Frontend Chinese Copy Review

### Completed

- Localized ordinary English UI copy across V1 frontend pages.
- Preserved product/domain terms such as Prompt, Skill, AutomationDraft,
  TestCommand, TestRun, ContextArtifact, ToolDefinition, and MCP-ready.
- Added display-only Chinese labels for common backend enums and statuses.
- Updated affected frontend tests.

### Verification

```bash
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- Frontend suite: `14` test files passed, `17` tests passed.
- `git diff --check` clean.

### Next Step

- Continue with V2 Task 2: draft the Slice 18 Newman API Execution plan.

## 2026-06-30 V2 Scope Options

### Completed

- Added `docs/implementation/10-v2-scope-options.md`.
- Listed V2 candidate directions for RAG runtime, runner expansion, review
  governance, and CI/CD import bridge.
- Recommended `Slice 18: Newman API Execution` as the first V2 slice.
- Updated `NEXT_AI_TASK.md` to V2 Task 2.

### Verification

```bash
rg -n "Candidate Direction|Recommended First V2 Slice|Still Out Of Scope|Next Task" docs/implementation/10-v2-scope-options.md
git diff --check
```

### Next Step

- Draft the Slice 18 Newman API Execution plan before implementation.

## 2026-06-30 V1 Release Screenshots

### Completed

- Captured release screenshots from `http://localhost:5174/`.
- Added screenshots for AI 工作台, CI/CD 质量中心, 报告中心, and RAG 知识库.
- Linked screenshots from `docs/release/v1/README.md`.
- Updated `NEXT_AI_TASK.md` to V2 Task 1.

### Verification

```bash
file docs/release/v1/screenshots/*.png
git diff --check
```

### Next Step

- Draft V2 scope options.

## 2026-06-30 V1 Release Manual Walkthrough

### Completed

- Expanded `docs/release/v1/manual-walkthrough.md` into a release-ready manual
  checklist.
- Expanded `docs/release/v1/acceptance-evidence.md` with command evidence,
  release status, coverage mapping, evidence chain, and explicit non-goals.
- Updated `docs/release/v1/README.md`.
- Updated `NEXT_AI_TASK.md` to Post-V1 Task 4.

### Verification

```bash
rg -n "Requirement|AutomationDraft|TestRun|Report|CI/CD|RAG" docs/release/v1/manual-walkthrough.md
rg -n "10 passed|17 tests|completion-audit|release-acceptance|final-acceptance" docs/release/v1/acceptance-evidence.md
git diff --check
```

### Next Step

- Decide whether to capture optional frontend screenshots or move directly to
  V2 planning.

## 2026-06-30 V1 Release Package Skeleton

### Completed

- Added `docs/release/v1/README.md`.
- Added `docs/release/v1/acceptance-evidence.md`.
- Added `docs/release/v1/manual-walkthrough.md`.
- Added `docs/release/v1/screenshots/.gitkeep` for optional screenshots.
- Updated `NEXT_AI_TASK.md` to Post-V1 Task 3.

### Verification

```bash
test -f docs/release/v1/README.md
test -f docs/release/v1/acceptance-evidence.md
test -f docs/release/v1/manual-walkthrough.md
git diff --check
```

### Next Step

- Expand the V1 manual walkthrough and acceptance evidence into release-ready
  content.

## 2026-06-30 Post-V1 Release Packaging Decision

### Completed

- Added `docs/implementation/09-post-v1-release-packaging-plan.md`.
- Decided to use the current composable golden suite as V1 automated acceptance
  evidence.
- Deferred any new narrative automated E2E test until after V1 packaging.
- Planned a lightweight release package with release notes, manual walkthrough,
  acceptance evidence, and optional frontend screenshots.
- Updated final acceptance handoff and `NEXT_AI_TASK.md`.

### Verification

```bash
rg -n "Decision|Release Package Contents|Implementation Plan|Next Task" docs/implementation/09-post-v1-release-packaging-plan.md
git diff --check
```

### Next Step

- Create the `docs/release/v1/` release package skeleton.

## 2026-06-30 V1 Final Acceptance Handoff

### Completed

- Added `docs/implementation/08-v1-final-acceptance-handoff.md`.
- Recorded V1 acceptance recommendation as `GO`.
- Linked the completion audit, release acceptance report, product scope, and V1
  release spine.
- Recorded remaining non-blocking decisions for release packaging.
- Switched `NEXT_AI_TASK.md` to Post-V1 Task 1.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py backend/app/tests/golden/test_extension_surface_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- Backend V1 golden release-acceptance suite: `10 passed`.
- Frontend workbench suite: `14` test files passed, `17` tests passed.
- `git diff --check` clean.

### Next Step

- Decide release packaging and demo artifact strategy for Post-V1.

## 2026-06-30 V1 Release Acceptance Golden Isolation Fix

### Completed

- Fixed the V1 release-acceptance blocker from the first full golden run.
- Updated five historical golden smokes to assert absence of rows or behavior
  instead of absence of later-slice tables.
- Preserved the original slice non-goal intent without product-code changes.
- Updated `docs/implementation/07-v1-release-acceptance.md` with GO status.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py backend/app/tests/golden/test_extension_surface_golden.py -q
```

Results:

- Focused failing golden set: `5 passed`.
- Full V1 golden release-acceptance suite: `10 passed`.

### Next Step

- Prepare the final V1 acceptance handoff and decide whether release packaging
  needs an additional narrative E2E demo artifact.

## 2026-06-30 V1 Release Acceptance First Run

### Completed

- Ran the first V1 release-acceptance verification set after Slice 17
  completion.
- Added `docs/implementation/07-v1-release-acceptance.md`.
- Recorded release recommendation as `NO-GO`.
- Identified release blocker: five historical golden smokes assert later-slice
  table absence, but full V1 acceptance registers all models before table
  creation.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py backend/app/tests/golden/test_extension_surface_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- Backend golden release-acceptance suite: `5 failed`, `5 passed`.
- Frontend shell tests: `14` test files passed, `17` tests passed.
- `git diff --check` clean.

### Next Step

- Fix the five golden isolation assertions by checking absence of rows or
  behavior instead of absence of complete tables.
- Re-run the full V1 release-acceptance command set.

## 2026-06-30 Slice 17 Extension Surface Completion

### Completed

- Completed Slice 17 Extension Surface.
- Added contract boundary for RAG 知识库 as ContextArtifact management and usage
  display, not internal RAG runtime.
- Added empty KnowledgeAdapter shell with `not_configured`, `disabled`, and
  `configured_stub` states.
- Added RAG 知识库 backend API backed by ContextArtifact and AITask usage.
- Added MCP-ready ToolDefinition schema/readiness metadata without MCP runtime.
- Added frontend RAG 知识库 shell using the light Chtest workbench style.
- Adjusted AI 工作台 based on visual review: recent tasks and task details are
  now vertically stacked, and key visible labels were translated into Chinese.
- Added Extension Surface golden smoke and fixture.
- Kept vector index, embeddings, reranking, external RAG provider calls, MCP
  runtime, RBAC, tenants, permissions, marketplace, cloud sync, release, and
  deployment out of this slice.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_extension_surface_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- Extension Surface API + golden smoke: `6 passed`.
- Frontend shell tests: `14 passed`, `17 tests passed`.
- `git diff --check` clean.

### Next Step

- Start V1 completion review / acceptance planning, since Slice 17 is the last
  item in `docs/implementation/02-v1-slice-plan.md`.
  The next task should verify the full V1 evidence spine and document any
  remaining gaps before release acceptance.

## 2026-06-30 Slice 16 UnitTestPatch And Regression Completion

### Completed

- Completed Slice 16 UnitTestPatch And Regression.
- Added UnitTestPatch and QualityGateDecision model/schema.
- Added PatchScopeGate and blocked source/config/migration/generated/unknown
  non-test path changes.
- Added UnitTestPatch generation/review/apply APIs with review-gated lifecycle.
- Added new-test and regression APIs that create CICD-linked TestRun evidence
  from allowlisted TestCommand records.
- Added QualityGateDecision API with passed/failed/needs_review evidence rules.
- Added CI/CD quality Report API backed by latest QualityGateDecision and
  evidence artifacts.
- Added frontend CI/CD Quality Center shell for patch review, scope gate,
  new-test/regression evidence, quality gate, and report references.
- Added golden smoke for local diff -> UnitTestPatch -> tests/regression ->
  quality gate -> report evidence.
- Kept merge, push, release, deployment, remote CI provider integration, PR
  comments, RAG runtime, MCP runtime, RBAC, tenants, and permissions out of
  this slice.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- UnitTestPatch regression API + golden smoke: `23 passed`.
- Frontend shell tests: `13 passed`, `16 tests passed`.
- `git diff --check` clean.

### Next Step

- Start Slice 17 Extension Surface by creating a scoped task plan for the RAG
  知识库 surface, empty KnowledgeAdapter, and MCP-ready Tool schema without
  building RAG runtime, MCP runtime, RBAC, tenants, or permissions.

## 2026-06-30 Slice 15 CI/CD Quality Center Foundation Completion

### Completed

- Completed Slice 15 CI/CD Quality Center Foundation.
- Added CICDRun and CICDChangedFile model/schema, local diff parser, CI/CD run
  create/list/get API, mock change analysis API, and risk_analysis artifact
  evidence.
- Added frontend CI/CD Quality Center shell for local diff input, changed files,
  file role/risk display, and analysis artifact references.
- Added golden smoke for local diff -> CICDRun -> changed files -> risk
  analysis evidence.
- Kept UnitTestPatch, QualityGateDecision, TestRun, Report, merge/release
  decisions, remote CI provider integration, RAG runtime, MCP runtime, RBAC,
  tenants, and permissions out of this slice.
- Updated `NEXT_AI_TASK.md` to Slice 16 Task 1: Add UnitTestPatch And Regression
  task plan.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/golden/test_cicd_quality_center_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- CI/CD Quality API + golden smoke: `8 passed`.
- Frontend shell tests: `13 passed`, `16 tests passed`.
- `git diff --check` clean.

### Next Step

- Start Slice 16 by creating
  `docs/implementation/slices/slice-16-unit-test-patch-regression.md` with
  small, verifiable tasks for UnitTestPatch, PatchScopeGate, pytest regression,
  and QualityGateDecision evidence.

## 2026-06-30 Slice 14 Report And Failure Analysis Completion

### Completed

- Completed Slice 14 Report And Failure Analysis.
- Added FailureAnalysis and Report model/schema, deterministic mock
  FailureAnalysis API, automation_execution Report API, report artifacts, and
  evidence_manifest metadata.
- Added frontend Report/FailureAnalysis workbench shell with evidence shown
  before AI explanation.
- Added golden smoke for failed TestRun -> FailureAnalysis -> Report evidence.
- Kept CI/CD quality gates, merge/release decisions, RAG runtime, MCP runtime,
  RBAC, tenants, permissions, and broad report analytics out of this slice.
- Updated `NEXT_AI_TASK.md` to Slice 15 Task 1: Add CI/CD Quality Center task
  plan.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py backend/app/tests/golden/test_report_failure_analysis_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- Report/FailureAnalysis API + golden smoke: `9 passed`.
- Frontend shell tests: `12 passed`, `15 tests passed`.
- `git diff --check` clean.

### Next Step

- Start Slice 15 by creating
  `docs/implementation/slices/slice-15-cicd-quality-center.md` with small,
  verifiable tasks for local-first CI/CD quality evidence.

## 2026-06-29 Slice 06 Requirement To Case Mainline Completion

### Completed

- Completed Slice 06 Requirement To Case Mainline.
- Added backend requirement creation, deterministic RequirementReviewAgent mock
  flow, CaseGenerationAgent mock flow, candidate review actions, and official
  TestCase promotion for approved candidates.
- Added fixture-aligned golden smoke for the coupon checkout requirement path.
- Added frontend Requirement Review and Case Generation Review workbench shells
  using Vue 3 + Arco Design Vue.
- Kept AutomationDraft, execution, Playwright, CI/CD quality, report center, real
  provider, RAG runtime, MCP runtime, RBAC, tenants, and permissions out of this
  slice.
- Updated `NEXT_AI_TASK.md` to Slice 09 Task 1: Add Case Metrics task plan.

### Verification

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/golden/test_requirement_to_case.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Results:

- Backend Slice 06 chain: `15 passed`.
- Frontend shell tests: `7 passed`, `10 tests passed`.
- `git diff --check` clean.

### Next Step

- Start Slice 09 by creating `docs/implementation/slices/slice-09-case-metrics.md`
  with small, verifiable tasks for case quality metrics.

## 2026-06-18 Documentation Foundation

### Completed

- Created Chtest under `/Users/yanchen/VscodeProject/Chtest`.
- Initialized Chtest as an independent Git repository on branch `main`.
- Configured remote `origin` as `https://github.com/2696437448-cmyk/Chtest.git`.
- Added `.gitignore` and excluded reference framework source, secrets, caches, and runtime artifacts.
- Downloaded reference frameworks into `参考框架/`: WHartTest and MeterSphere.
- Reviewed WHartTest capabilities: MCP tools, Skill packaging, generated case modal, review status, optimization review, and actuator execution.
- Reviewed MeterSphere capabilities: case review pages, pass-rate progress, test asset management, test plan/report views.
- Built the long-term `memory/` documentation system for AI-assisted development.
- Built the formal `docs/` documentation system for product, architecture, contracts, fixtures, implementation, deployment, reference, review, roadmap, and superpowers docs.

### Final V1 Scope Captured

- Chtest V1 is an AI Testing Workbench for individual test engineers and automation test engineers.
- V1 is single-user and local-first.
- V1 uses PostgreSQL, Redis, Docker Compose, FastAPI, worker, Vue 3, and Arco Design Vue.
- Mainline A: requirement review to reviewed test cases.
- Mainline B: reviewed test cases to AutomationDraft, execution, failure analysis, and report.
- Support workflow: local Git diff to UnitTestPatch, regression execution, and quality report.
- RAG is exposed only through KnowledgeAdapter.
- Tool execution uses Internal Tool Adapter first and remains MCP-ready.
- pytest is the P0 execution path; Playwright minimal loop is P1; Newman/JMeter/Appium/traffic capture are later capabilities.

### Contracts Completed

- Data model contract includes Project, Module, Repository, Environment, TestCommand, Requirement, RequirementReview, RiskItem, GeneratedCaseCandidate, TestCase, AutomationDraft, CICDRun, CICDChangedFile, UnitTestPatch, TestRun, TestResult, FailureAnalysis, Report, AITask, PromptVersion, SkillVersion, ToolDefinition, ToolInvocation, and Artifact.
- API contract includes Project Settings, Requirement Review, Case Generation, Case Review, AutomationDraft, CI/CD Quality, TestRun, FailureAnalysis, Report, and AITask APIs.
- State machines define AITask, GeneratedCaseCandidate, AutomationDraft, UnitTestPatch, ToolInvocation, TestRun, Report, PromptVersion, and SkillVersion transitions.
- Golden Paths define requirement-to-case, case-to-automation, and Git-quality expected behavior.

### Verification

- Documentation entry points are aligned in `docs/README.md` and `memory/README.md`.
- Product scope, contracts, Agent workflow, fixture actions, and implementation order are consistent.
- Reference framework source remains local-only and ignored by Git.

### Next Step

Start V1 Slice 1 and Slice 2: create platform skeleton, Docker Compose, FastAPI health/ready, PostgreSQL, Redis, worker ping, Vue + Arco shell, default workspace/user, and Project Settings APIs.

## 2026-06-18 AI Vibecoding Governance

### Completed

- Added `docs/implementation/04-ai-vibecoding-governance.md` as the mandatory AI development governance document.
- Defined Slice / Task / Commit relationship, Task Definition Of Ready, mandatory Task loop, testing gates, commit rules, workspace protection, DB migration rules, Prompt/Skill rules, dependency rules, failure handling, rollback, and handoff requirements.
- Updated development process and slice plan to require focused verification, git diff self-review, commit per completed Task, and handoff updates.
- Updated docs and memory indexes so future AI sessions read the governance document before coding.

### Verification

- Documentation-only change.
- Path and keyword consistency checks should verify the governance document is referenced from docs, memory, session protocol, slice plan, and handoff.

### Next Step

- Start Slice 1 with the governance protocol: define Task DoR, create focused verification, implement minimal foundation, run checks, commit, and update handoff.

## 2026-06-18 Memory Update Policy

### Completed

- Added Chinese Memory Update Policy to `docs/implementation/04-ai-vibecoding-governance.md`.
- Clarified that Git records code history, Memory records session continuity, and Contracts record implementation truth.
- Updated session protocol, memory index, and handoff template so Task-level progress relies on git commits, while Slice completion and major context changes update memory.

### Verification

- Documentation-only change.
- Check references with `rg "Memory Update Policy|Git 记录代码历史|每个 Slice" docs memory`.

## 2026-06-18 Final Pre-Coding Closure

### Completed

- Fixed AutomationDraft approval wording in page PRD: AutomationDraft uses `edit`, `approve`, and `reject`; `approve_after_edit` remains only for GeneratedCaseCandidate.
- Aligned Memory update policy across brief, session protocol, development process, and governance.
- Added V1 Minimum Demo Golden Path fixture.
- Added Slice 1 and Slice 2 Task Plans for small-step coding.
- Added Error Code, Seed Data, and Mock Provider contracts.
- Updated docs and memory indexes for the new fixture, contracts, and Slice Task Plans.

### Verification

- Documentation-only change.
- Required checks: AutomationDraft action grep, Memory policy grep, new file references, and docs consistency checks.

### Next Step

- Continue from `NEXT_AI_TASK.md`; Slice 1 Task 1 is complete.

## 2026-06-22 ContextArtifact Contract Closure

### Completed

- Defined V1 ContextArtifact as an API-level use of the Artifact table, not a new table.
- Fixed owner rule: project-level ContextArtifact uses `owner_entity_type=Project` and `owner_entity_id=project_id`.
- Clarified that `use_knowledge=false` disables external RAG/KnowledgeAdapter only; provided `context_artifact_ids` are still injected into prompts.
- Added ContextArtifact usage to V1 Minimum Demo, seed data, mock provider behavior, prompt/skill contract, testing acceptance, and AI-readable project brief.
- Expanded Artifact redaction and safety rules to cover context documents, logs, OpenAPI snippets, and fixtures.

### Verification

- Documentation-only change.
- Required checks: ContextArtifact grep, `use_knowledge=false` semantics grep, owner rule grep, docs whitespace check.

## 2026-06-23 Slice 1 Start

### Completed

- Tightened execution-readiness documentation after product and market review.
- Created branch `codex/chtest-vibecoding-foundation` for implementation work.
- Completed Slice 1 Task 1: initialized platform directories with `.gitkeep`.
- Completed Slice 1 Task 2: added PostgreSQL and Redis Docker Compose services plus `.env.example`.
- Completed Slice 1 Task 3: added backend Dockerfile, README, and backend Compose placeholder.

### Verification

- `find backend frontend worker deploy prompts skills mcp_tools artifacts -maxdepth 1 -type f -name .gitkeep`
- `docker compose -f deploy/docker-compose.yml config`

### Next Step

- Continue Slice 1 Task 4 from `NEXT_AI_TASK.md`: add worker container placeholder.

## 2026-06-25 Frontend Chinese UI Alignment

### Completed

- Reconciled frontend design docs to Chinese-first visible copy.
- Added explicit UI naming rules:
  - `ContextArtifact` -> `上下文工件`
  - `AITask` -> `AI 任务`
  - `LLMCallLog` -> `大模型调用日志`
  - `Artifact` -> `工件`
- Updated page PRD section names and user-facing entities so future frontend coding uses Chinese labels by default.
- Updated Slice 02.5 frontend task plan and `NEXT_AI_TASK.md` so the next AI coding session starts from frontend scaffold work instead of the stale Slice 1 worker placeholder.

### Verification

- Documentation-only change.
- Required checks: `git diff --check`, `git diff --name-only`, and readback of `NEXT_AI_TASK.md`.

### Next Step

- Slice 02.5 Task 1 completed in commit `daf5b7c`: scaffolded Vue 3 + TypeScript + Vite frontend app.
- Verification: `npm --prefix frontend run build`, `npm --prefix frontend run test -- --run`, and `git diff --check`.
- Slice 02.5 Task 2 completed in commit `2ec1c7c`: added Arco Design Vue, Vue Router, Pinia, API client shell, Chinese-first workbench layout, and AI 工作台页面。
- Verification: `npm --prefix frontend run test -- --run`, `npm --prefix frontend run build`, and `git diff --check`.
- Residual note: the Vite build passes but warns that the current Arco-based bundle is large; optimization can happen later and does not block Slice 02.5 Task 2 acceptance.
- Slice 02.5 Task 3 completed in commit `6526a2b`: added frontend Dockerfile, frontend README, and Docker Compose frontend service for the Vite dev server。
- Verification: `docker compose -f deploy/docker-compose.yml config`, `npm --prefix frontend run test -- --run`, `npm --prefix frontend run build`, and `git diff --check`.
- Slice 02.5 Task 4 completed in commit `de1f5fd`: added typed frontend `/health` helper plus AI 工作台 success/failure smoke tests。
- Verification: `npm --prefix frontend run test -- --run`, `npm --prefix frontend run build`, and `git diff --check`.
- Slice 02.5 Frontend Foundation is now complete.
- Continue from `NEXT_AI_TASK.md`: Slice 03 Task 1, add project core models and migration.

## 2026-06-26 Final Frontend Design Documentation

### Completed

- Captured the approved A direction as the final V1 frontend design: light palette, Chinese-first copy, Vue 3 + Arco Design Vue, workbench density, tables, split panes, drawers, and evidence-first reports.
- Added `docs/product/08-frontend-design-spec.md` as the implementation-facing frontend design source.
- Added `docs/superpowers/specs/2026-06-26-chtest-final-frontend-design.md` as the approved brainstorming spec archive.
- Standardized the user-facing local diff quality page name to `CI/CD 质量中心` across current product, architecture, implementation, and memory docs.
- Aligned CI/CD quality contracts and fixtures to `CICDRun`, `CICDChangedFile`, `CICDChangeAnalysisAgent`, `/api/cicd/*`, and `docs/fixtures/03-golden-cicd-quality.md`.
- Added `RAG 知识库` as a user-facing page for ContextArtifact, KnowledgeAdapter configuration state, safety metadata, and evidence usage display.
- Clarified that V1 does not build internal RAG runtime, vector indexing, chunking, embedding, or reranking.
- Clarified that V1 CI/CD Quality Center remains local-first and does not include GitHub Actions, GitLab CI, webhook ingestion, or PR comments.
- Documented open-source UI reference boundaries: keep Arco Design Vue; WHartTest MIT patterns may be adapted with attribution; MeterSphere, shadcn/ui, Nuxt UI, and Creative Tim are design references only.

### Verification

- Documentation-only change.
- Required checks: `git diff --check`, `git diff --name-only`, and targeted grep for old user-facing names in current docs.

### Next Step

- Continue from `NEXT_AI_TASK.md`: Slice 03 Task 1, add project core models and migration.

## 2026-06-26 Slice 03 Project Core Backend Migration

### Completed

- Completed Slice 03 Task 1: added SQLAlchemy Project Core models for `Workspace`, `User`, `Project`, `Module`, `Repository`, `Environment`, and `TestCommand`.
- Added the first Alembic migration for project core tables and constraints.
- Added a focused DB test covering migration smoke, project context persistence, module tree relationship, and project-name uniqueness.
- Added backend package/dependency foundation with `backend/pyproject.toml` so local verification can run through an isolated Python environment.
- Updated `docs/reference/01-open-source-migration-map.md` with the WHartTest reference code used for the migration and the capabilities intentionally not migrated.
- Updated Slice 03 task tracking and moved `NEXT_AI_TASK.md` to Slice 03 Task 2: Add Project CRUD API.

### Verification

- `UV_CACHE_DIR=.tmp/uv-cache uv --project backend run pytest backend/app/tests/db/test_project_core_models.py -q`
- Result: `4 passed in 0.32s`

### Next Step

- Continue from `NEXT_AI_TASK.md`: Slice 03 Task 2, add Project CRUD API.

## 2026-07-01 Slice 23 Completion Gate

### Completed

- Completed Slice 23: Frontend Build Baseline.
- Recorded Task 2 commit `07b1442` and marked the completion gate done pending
  commit.
- Updated `NEXT_AI_TASK.md` to select the next V2 small slice.

### Verification

- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.
- `npm --prefix frontend run test -- --run`
- Result: `16 files passed, 21 tests passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `docs(v2): complete frontend build baseline slice`.
- Select the next V2 small slice.

## 2026-07-01 Slice 23 Task 2 Frontend Build Baseline

### Completed

- Restored `npm --prefix frontend run build`.
- Relaxed `ApiClient.postJson` / `patchJson` body constraints from
  `Record<string, unknown>` to `object` so typed request interfaces compile.
- Replaced ES2021 `replaceAll` calls with ES2020-compatible `replace` calls.
- Added a fallback for optional CI/CD `risk_level`.
- Updated `NEXT_AI_TASK.md` to Slice 23 Completion Gate.

### Verification

- `npm --prefix frontend run build`
- Result: passed with Vite large chunk warning.
- `npm --prefix frontend run test -- --run`
- Result: `16 files passed, 21 tests passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `fix(frontend): restore build baseline`.
- Continue Slice 23 Completion Gate.

## 2026-07-01 Next V2 Slice Selection

### Completed

- Selected Slice 23: Frontend Build Baseline.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 22 completion
  and the Slice 23 recommendation.
- Added `docs/implementation/slices/slice-23-frontend-build-baseline.md`.
- Updated `NEXT_AI_TASK.md` to Slice 23 Task 2: Fix frontend build TypeScript
  baseline.

### Rationale

- Slice 22 frontend tests passed, but extra frontend build verification exposed
  existing TypeScript baseline errors.
- The next small slice should restore the build gate without changing product
  behavior or redesigning the frontend.

### Verification

- `npm --prefix frontend run build`
- Result: failed as expected with the documented TypeScript baseline errors.

### Next Step

- Commit `docs(v2): add frontend build baseline plan`.
- Continue Slice 23 Task 2 from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 22 JMeter Completion Gate

### Completed

- Completed Slice 22: JMeter Local Execution Evidence.
- Recorded Task 6 commit `a2fc879` and marked the completion gate done pending commit.
- Confirmed JMeter remains a local, allowlisted, non-GUI execution evidence slice.
- Updated `NEXT_AI_TASK.md` to select the next V2 small slice.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py backend/app/tests/golden/test_jmeter_local_execution_golden.py -q`
- Result: `6 passed`.
- `npm --prefix frontend run test -- --run`
- Result: `16 files passed, 21 tests passed`.
- `git diff --check`
- Result: no output.

### Next Step

- Commit `docs(v2): complete jmeter execution slice`.
- Select the next V2 small slice.

## 2026-07-01 Slice 22 Task 6 JMeter Golden Smoke

### Completed

- Added `backend/app/tests/golden/test_jmeter_local_execution_golden.py`.
- Added `docs/fixtures/11-jmeter-local-execution-golden.md`.
- Proved configured `TestCommand(command_type=jmeter)` can create a local
  `TestRun(runner_mode=jmeter_local)` with stdout/stderr, `jmeter_jtl`,
  `parsed_output`, parsed sampler evidence, and TestResult rows.
- Kept the golden deterministic by using a fake JMeter executable.
- Updated `NEXT_AI_TASK.md` to Slice 22 Completion Gate.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_jmeter_local_execution_golden.py -q`
- Result: `1 passed`.

### Next Step

- Commit `test(golden): add jmeter local execution smoke`.
- Continue Slice 22 Completion Gate from `NEXT_AI_TASK.md`.

## 2026-07-01 Slice 22 Task 5 JMeter Frontend Shell

### Completed

- Added the JMeter execution frontend shell at `/execution/jmeter`.
- Added a TestCommand-only JMeter launch form using `runner_mode=jmeter_local`.
- Added Chinese evidence display for TestRun status, duration, total/passed/failed/error counts, Sampler count, assertion count, average latency, JTL artifacts, parsed output, and Sampler TestResult rows.
- Added navigation for `JMeter 执行`.
- Generalized execution refresh error copy so it is not pytest-specific.
- Updated `NEXT_AI_TASK.md` to Slice 22 Task 6: Add JMeter local execution golden smoke.

### Verification

- `npm --prefix frontend run test -- --run src/views/execution/JMeterExecutionView.spec.ts src/layouts/WorkbenchLayout.spec.ts`
- Result: `3 passed`.
- `npm --prefix frontend run test -- --run`
- Result: `16 files passed, 21 tests passed`.
- `git diff --check`
- Result: no output.

### Extra Notes

- Frontend dev server started at `http://127.0.0.1:5174/`; JMeter preview path:
  `http://127.0.0.1:5174/execution/jmeter`.
- `curl -I http://127.0.0.1:5174/execution/jmeter` returned `200 OK`.
- Extra `npm --prefix frontend run build` is currently blocked by existing
  TypeScript baseline errors outside this task's verification scope.

### Next Step

- Commit `feat(frontend): show jmeter execution evidence`.
- Continue Slice 22 Task 6 from `NEXT_AI_TASK.md`.

## 2026-06-29 Slice 03 Project Core Completion

### Completed

- Completed Slice 03 Task 2: Project create/read/update APIs and Project Settings bootstrap API.
- Completed Slice 03 Task 3: Module tree create/list/update API with five-level validation and descendant path refresh.
- Completed Slice 03 Task 4: Repository and Environment APIs with repository path allowlist and environment secret-reference guard.
- Completed Slice 03 Task 5: TestCommand create/list/update/validate APIs with allowlist, working-directory, shell-operator, and same-project environment checks.
- Completed Slice 03 Task 6: Project Settings frontend shell with typed API helper, Pinia store, route, and Chinese-first workbench view.
- Updated `NEXT_AI_TASK.md` to Slice 04 Task 1: Add AI Runtime models and migration.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py backend/app/tests/api/test_modules.py backend/app/tests/api/test_repository_environment.py backend/app/tests/api/test_test_commands.py backend/app/tests/db/test_project_core_models.py -q`
- Result: `39 passed in 2.61s`
- `npm --prefix frontend run test -- --run`
- Result: `4 passed (4), 6 passed (6)`
- `npm --prefix frontend run build`
- Result: passed with existing Arco bundle size warning.
- `git diff --check`
- Result: no output.

### Commits

- `6c12d64 feat(projects): add project settings api`
- `57e64f4 feat(projects): add module tree api`
- `7c8471f feat(projects): add repository and environment api`
- `47f6724 feat(projects): add test command validation`
- `524b7c7 feat(frontend): add project settings shell`

### Next Step

- Continue Slice 04 Task 1 from `NEXT_AI_TASK.md`: add AI Runtime models and migration.

## 2026-06-29 Slice 04 AI Runtime Backend Progress

### Completed

- Completed Slice 04 Task 1: AI Runtime models and migration for `AITask`, `Artifact`, `LLMCallLog`, and `context_artifact_ids`.
- Completed Slice 04 Task 2: local `LocalArtifactStore` with path safety, atomic write, sha256, size, and read helpers.
- Completed Slice 04 Task 3: ContextArtifact create/list API with owner enforcement, MIME/type guard, size limit, and conservative secret scan.
- Completed Slice 04 Task 4: deterministic Mock LLM Provider with success, provider error, schema invalid, timeout, and all V1 mock contract models.
- Completed Slice 04 Task 5: fake queue and AI task worker handler with status progression, Artifact rows, LLMCallLog rows, failure artifacts, and cancelled-task guard.
- Completed Slice 04 Task 6: AI Task detail/list API for status views, LLM call logs, context usage, artifact summaries, and safe artifact metadata.
- Completed Slice 04 Task 7: AI Workbench frontend status shell with recent AI tasks, selected task details, context usage, artifact summaries, and LLM call logs.
- Updated `NEXT_AI_TASK.md` to Slice 04 Completion Gate.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q`
- Result: `49 passed in 0.94s`
- `npm --prefix frontend run test -- --run`
- Result: `7 passed (7)`
- `npm --prefix frontend run build`
- Result: passed with existing Arco bundle size warning.
- `git diff --check`
- Result: no output.

### Commits

- `11bb6cc feat(ai-runtime): add ai task artifact and llm call models`
- `5b17d26 feat(artifact): add local artifact store`
- `d7570ba feat(ai-runtime): add context artifact api`
- `693e171 feat(ai-runtime): add deterministic mock provider`
- `63efbc6 feat(ai-runtime): add ai task worker handler`
- `f006cb2 feat(ai-runtime): add ai task api`
- `31ce363 feat(frontend): add ai task status shell`

### Next Step

- Slice 04 completion gate completed after Task 7.
- Continue Slice 05 Task 1 from `NEXT_AI_TASK.md`: add PromptVersion and SkillVersion models.

## 2026-06-29 Slice 04 AI Runtime Completion Gate

### Completed

- Verified Slice 04 AI Runtime Core end to end.
- Confirmed Slice 04 task table records Task 1-7 as done with commit ids.
- Confirmed `NEXT_AI_TASK.md` now points to Slice 05 Task 1: Add PromptVersion and SkillVersion models.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q`
- Result: `49 passed in 1.58s`
- `npm --prefix frontend run test -- --run`
- Result: `7 passed (7)`
- `npm --prefix frontend run build`
- Result: passed with existing Arco bundle size warning.
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 05 Task 1 from `NEXT_AI_TASK.md`.

## 2026-06-29 Slice 05 Prompt And Skill Registry Models

### Completed

- Completed Slice 05 Task 1: added `PromptVersion` and `SkillVersion` SQLAlchemy models, Pydantic read schemas, Alembic migration, and DB tests.
- PromptVersion persists `name`, `version`, `hash`, `agent_name`, `content`, input/output schema JSON, status, and timestamp fields.
- SkillVersion persists `name`, `version`, `hash`, applicable agents, content, quality gates, forbidden actions, tool permissions, status, and timestamp fields.
- Added uniqueness constraints for `name + version` on both version tables.
- Updated `NEXT_AI_TASK.md` to Slice 05 Task 2: Add built-in prompt files.

### Verification

- `backend/.venv/bin/python -m pytest backend/app/tests/db/test_prompt_skill_models.py -q`
- Result: `5 passed in 0.36s`
- `backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/db/test_prompt_skill_models.py -q`
- Result: `15 passed in 0.38s`
- `git diff --check`
- Result: no output.

### Next Step

- Continue Slice 05 Task 2 from `NEXT_AI_TASK.md`: add built-in prompt files.

## 2026-07-10 V2 Acceptance Stabilization

### Completed

- Repaired Alembic bootstrap and verified an empty database upgrades to head.
- Added automatic Prompt/Skill registry bootstrap for new local databases.
- Added AutomationPlan prompt/skill contracts and active-version traceability.
- Connected approved TestKnowledgeCard evidence to RequirementReview,
  CaseGeneration, and AutomationPlan.
- Added OpenAI-compatible Responses-to-Chat-Completions fallback for gateways
  that return reasoning-only Responses payloads.
- Fixed the Docker image/runtime configuration so migrations, registry files,
  and model connection persistence are present in containers.
- Ran a fresh local HTTP acceptance path and a real-model RequirementReview.

### Verification

- Backend related suite: `84 passed`.
- Frontend focused suite: `10 passed`.
- Frontend build: passed, existing Vite chunk-size warning remains.
- Alembic empty database: passed.
- Compose config and `git diff --check`: passed.
- Real model RequirementReview: passed through
  `openai_chat_completions_fallback`, score `78`, `used_knowledge=true`.

### Blocker

- Docker Desktop `desktop-linux` engine returns HTTP 500 for `/v1.55/version`.
  Project compose configuration is valid, but container startup cannot be
  accepted until the local Docker engine recovers.

### Follow-up Fix

- Fixed `frontend/vite.config.ts` so the local dev `/api` proxy uses
  `VITE_API_PROXY_TARGET` or `VITE_API_BASE_URL` before falling back to
  `http://127.0.0.1:8000`.
- Restarted Vite with `VITE_API_BASE_URL=http://127.0.0.1:8010/api`.
- Verified the browser RAG page now renders the acceptance data:
  `ContextArtifact1`, `测试知识卡3`, `知识覆盖率67%`,
  `Vector Index3`, `Vector Coverage100%`.
- Verification:
  - Frontend focused suite: `5 passed`.
  - Frontend build: passed with the existing Vite chunk-size warning.

## 2026-07-13 AutomationDraft Evidence Quality Gate

### Completed

- Added computed AutomationDraft `quality_gate` read data for approval blockers
  and evidence warnings.
- Blocked approval for fake/stub/demo adapter-style draft code so demo evidence
  cannot be mistaken for a real regression pass.
- Updated the AutomationDraft review page to render blockers/warnings and
  disable approval when blockers exist.
- Synced AutomationDraft data/API/error-code contracts and golden test coverage.

### Verification

- Automation focused backend + golden suite: `17 passed`.
- AutomationDraft frontend spec: `3 passed`.
- Related backend acceptance suite: `43 passed`.
- Related frontend acceptance suite: `9 passed`.
- Frontend build: passed with existing Vite chunk-size warning.
- `git diff --check`: no output.

### Next Step

- Continue non-Docker V2 acceptance with real project-local fixtures,
  selectors, or API hooks when a target app integration path is available.

## 2026-07-13 AutomationDraft Embedded Execution Types

### Completed

- Embedded pytest, Playwright, API/Newman, and JMeter execution entry points in
  the AutomationDraft review page so execution evidence is part of the
  automation draft workflow instead of scattered sidebar pages.
- Kept backend safety semantics: pytest and Playwright execute from approved
  AutomationDraft records, while API/Newman and JMeter use configured
  TestCommand records.
- Removed standalone Playwright/API/JMeter execution links from the primary
  workbench navigation while preserving their routes for deep links.
- Added frontend coverage for starting pytest from an approved draft and
  starting API/Newman and JMeter runs from embedded TestCommand execution
  types.

### Verification

- AutomationDraft focused backend suite: `16 passed`.
- AutomationDraft frontend spec: `4 passed`.
- Related frontend execution/navigation suite: `10 passed`.
- Frontend build: passed with existing Vite chunk-size warning.

### Remaining Risk

- The broader backend execution runner suite still fails on this Windows
  machine when fake `npx`, `newman`, or `jmeter` scripts are launched directly
  by `subprocess` (`WinError 193`). This is outside the frontend integration
  change and should be handled as a separate Windows runner-test compatibility
  follow-up.

## 2026-07-13 Case Generation Flow UX Review

### Completed

- Preserved senior-test-engineer feedback for the reservation charging
  scenario.
- Inspected the complete Chtest flow from RequirementReview to formal
  requirement document, CaseGeneration, candidate review, and TestCase library
  promotion.
- Confirmed RequirementReview produced useful ambiguity/risk findings for the
  reservation charging requirement.
- Confirmed formal requirement document creation and generation-source handoff
  work structurally.
- Confirmed candidate review actions and `approve_after_edit` TestCase
  promotion work structurally.

### Observations

- Real-model CaseGeneration failed with recoverable HTTP 524 after a long
  wait, while the UI only showed loading and did not surface task progress or
  failure evidence.
- Mock-model CaseGeneration succeeded structurally but generated coupon cases
  for the reservation charging input, so mock output must not be used as
  domain-quality evidence.
- The next product risk is not whether the endpoints exist; it is whether a
  test engineer can see generation progress, understand failures, and verify
  risk-dimension coverage before approving cases.

## 2026-07-13 Case Generation P0/P1 Optimization

### Completed

- Implemented visible CaseGeneration task lifecycle for the requirement-to-case
  flow. Case generation now creates a pending task, runs in a background task,
  and exposes task status through `GET /api/case-generation/tasks/{id}`.
- Added failed-task error visibility with `error_code` and `error_message` so
  provider failures, schema failures, and quality gates can be shown in the UI.
- Added a domain-alignment gate that fails wrong-domain output with
  `CASE_GENERATION_DOMAIN_MISMATCH` and prevents candidate persistence.
- Updated the case generation review page to poll task status before loading
  candidates and to show CaseGenerationTask/AITask ids, AI status, error code,
  and error message.
- Added a lightweight test-dimension coverage matrix for generated candidates
  covering main flow, negative path, boundary, state, permission, channel,
  device/current condition, and risk references.
- Kept prompt-ready knowledge index coverage honest by marking indexes stale
  when reviewed knowledge cards are no longer prompt-eligible.
- Updated API/data/state contracts for asynchronous CaseGeneration tasks and
  knowledge index coverage semantics.

### Verification

- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_case_generation.py -q`
  - Result: `6 passed`.
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_test_knowledge_cards.py -q`
  - Result: `25 passed`.
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_test_knowledge_cards.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_model_connection_config.py backend/app/tests/api/test_extension_surface.py -q`
  - Result: `44 passed`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/cases/CaseGenerationReviewView.spec.ts src/views/requirements/RequirementReviewView.spec.ts`
  - Result: `6 passed`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/settings/ProjectSettingsView.spec.ts src/views/extension/KnowledgeBaseView.spec.ts src/views/requirements/RequirementReviewView.spec.ts src/views/cases/CaseGenerationReviewView.spec.ts`
  - Result: `11 passed`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run build`
  - Result: passed with existing Vite chunk-size warning.
- `git diff --check`
  - Result: no output.

## 2026-07-13 Automation Reviewer Asset Selection UX

### Completed

- Replaced AutomationDraft TestCase/TestCommand UUID inputs with searchable,
  business-labeled asset selectors.
- Filtered API/Newman and JMeter commands by compatible active command type.
- Added explicit case-selection, plan-approval, draft-review, and
  execution-evidence stages with responsive layout.
- Removed the fake default TestCase id and disabled generation until explicit
  selection or restored reviewed-case context.

### Verification

- Focused AutomationDraft spec: `5 passed`.
- Related frontend workflow suite: `6 files passed, 11 tests passed`.
- Frontend build passed with the existing Vite chunk-size warning.
- Browser selection smoke passed against 5 real TestCases.

### Blocker

- Full browser plan generation is blocked by an unversioned local database,
  missing current GeneratedCaseCandidate columns, and PromptVersion registry
  content drift. A copied-database Alembic upgrade starts at the first migration
  and fails because tables already exist. No migration was applied to the
  original database.

## 2026-07-14 Final RAG Scope Promotion And Full Web Review

### Completed

- Reviewed all current web routes for test efficiency, quality, logs,
  traceability, and visual hierarchy.
- Promoted Final Test Knowledge RAG into product scope.
- Added final data/API/state/artifact contracts and Slice 47 task plan.
- Preserved KnowledgeAdapter as the boundary for pgvector/PostgreSQL, Qdrant,
  Haystack, and LlamaIndex implementations.

### Verification

- Contract keyword/self-check passed.
- `git diff --check`: no output.

### Next

- Add safe local database preflight before final RAG migrations.

## 2026-07-14 Knowledge Retrieval Run And Evidence Boundary

### Completed

- Added persisted KnowledgeRetrievalRun and normalized KnowledgeEvidence with
  Alembic `20260714_0012`.
- Added provider-neutral retrieval-log create/list/read APIs, paging, filters,
  latency/count/error evidence, and successful empty-result Artifacts.
- Routed RequirementReview, CaseGeneration, and AutomationPlan knowledge use
  through canonical evidence ids and safe reference manifests.
- Closed retrieval trace/safety gaps for unsafe lifecycle changes, historical
  raw copies, mixed/multi-run evidence, legacy adapter bypass, candidate display
  payloads, Artifact download gates, and cross-project AITask correlation.
- Added current card lifecycle/prompt eligibility to retrieval responses while
  retaining the original evidence snapshots.

### Verification

- Focused Task 47.4 suite: `64 passed`.
- Full backend: `398 passed, 13 failed`; remaining failures are the known
  Windows fake-runner `WinError 193` cases and stale golden decision-table
  acknowledgement fixtures.
- `compileall`: passed.
- `git diff --check`: passed.
- Read-only local DB preflight confirmed the source fingerprint is unchanged and
  `source_mutation_performed=false`.

### Next

- Task 47.5: PostgreSQL full-text + pgvector KnowledgeAdapter with deterministic
  fallback, no Qdrant/orchestration/frontend expansion.

## 2026-07-14 PostgreSQL Hybrid Adapter Offline Implementation

### Implemented

- Added capability-gated PostgreSQL full-text/pgvector migration and Python
  adapter without mapping the optional native column into the core ORM.
- Added HNSW-compatible vector candidate SQL, dimension/model/freshness gates,
  native embedding synchronization, safe config validation, provider-neutral
  evidence normalization, and explicit SQLite/pgvector-unavailable fallback.
- Added pgvector Python dependency and PostgreSQL dialect/offline DDL tests.

### Verification

- Focused 47.4/47.5 retrieval, consumer, golden, migration, and SQL suite:
  `74 passed`.
- Full backend checkpoint: `406 passed, 13 failed`, with only known unrelated
  Windows runner and stale golden fixture failures.
- `compileall` and `git diff --check`: passed.

### Blocker

- No local PostgreSQL server/test URL exists, and Docker Desktop's engine
  returns HTTP 500. Real online PostgreSQL/pgvector migration, query, HNSW plan,
  and recall smoke cannot be performed. Task 47.5 remains in progress.

## 2026-07-15 PostgreSQL Candidate Query Review

### Completed

- Corrected native vector retrieval to use a dimension-matched, HNSW-orderable
  candidate pool before threshold filtering and full-text merging.
- Kept vector-only retrieval free of text-only candidates and improved fallback
  reasons for missing native capability versus missing fresh candidates.
- Added fake-native provider-neutral evidence and PostgreSQL SQL-shape coverage.

### Verification

- Focused Task 47.4/47.5 suite: `76 passed`.
- Full backend: `410 passed, 13 known unrelated failures`.
- `compileall`, `git diff --check`, and read-only DB fingerprint checks passed.

### Blocker

- Task 47.5 still requires dedicated PostgreSQL test URLs for online migration,
  full-text, pgvector ordering, HNSW plan, and recall acceptance.

## 2026-07-15 PostgreSQL Hybrid Online Acceptance

### Completed

- Created an isolated PostgreSQL 16.14 + pgvector 0.8.3 environment outside
  the repository and ran the temporary server under `NetworkService`.
- Ran Alembic online to head `20260714_0013` against both an unprivileged
  no-vector database and a pgvector-enabled database.
- Verified GIN full-text-only capability and deterministic no-vector fallback
  in the plain database.
- Verified native `vector(64)` storage, the default HNSW index, native `<=>`
  ordering, and an application adapter hybrid result with `vector_score=1.0`
  in the vector database.
- Confirmed the source acceptance SQLite database was not used or mutated.

### Verification

- Focused Task 47.4/47.5 suite: `76 passed`.
- Online migration: both temporary databases reached `20260714_0013`.
- Adapter capability probe: plain `{vector_extension: false}` and vector
  `{vector_extension: true, vector_column: true, vector_index: true}`.
- `compileall` and `git diff --check`: passed before this handoff update.

### Next

- Task 47.6: optional Qdrant and Haystack/LlamaIndex provider contracts using
  fake clients only.

## 2026-07-15 Evidence-Backed CaseGeneration Fields

### Implemented

- Added Alembic `20260715_0014` for explicit requirement/risk coverage ids,
  case type, generation reason, coverage gap notes, automation readiness, and
  quality assessment on `GeneratedCaseCandidate`.
- Extended CaseGeneration validation, persistence, and candidate list output.
  Legacy model responses receive deterministic defaults (`ai_reason`,
  `test_type`, and requirement/risk refs) so existing fixtures remain valid.
- Updated the data contract to make the evidence-backed fields explicit.

### Verification

- CaseGeneration and migration suite: `13 passed`.
- `compileall` and `git diff --check`: passed before final commit check.

### Next

- Task 47.8: CaseReviewAgent and CoverageGapAgent quality gates.

## 2026-07-15 Case Quality Agents

### Implemented

- Added dependency-free deterministic `CaseReviewAgent` and `CoverageGapAgent`
  evaluators plus automation readiness assessment.
- Candidate persistence now writes provider-neutral quality findings,
  coverage-gap summaries, evidence ids, automation framework, blockers, and
  confidence without copying provider payloads.

### Verification

- Quality agent and CaseGeneration suite: `12 passed`.
- Full golden collection still contains the pre-existing missing-fixture and
  stale decision-table acknowledgement failures; no new failure is attributed
  to the quality agent change.

### Next

- Task 47.9: typed relationships and graph queries.

## 2026-07-15 Typed Knowledge Relationships

### Implemented

- Added Alembic `20260715_0015` and `TestKnowledgeRelationship` with typed
  source/target entities, evidence artifact ids, confidence, status, metadata,
  and unique edge identity.
- Added same-project entity validation and an idempotent relationship creation
  endpoint.
- Existing graph output now includes persisted relationship edges beside the
  deterministic derived coverage graph.

### Verification

- Knowledge migration/API suite: `28 passed`.
- No graph database or external runtime was added.

### Next

- Task 47.10: reviewed knowledge feedback loop.

## 2026-07-15 Reviewed Knowledge Feedback

### Implemented

- Added Alembic `20260715_0016` and KnowledgeFeedbackEvent persistence.
- Added proposal and review APIs with same-project source validation and secret
  rejection.
- Approved feedback creates only an `extracted` TestKnowledgeCard; trusted card
  approval remains a separate human action. Rejected feedback creates no card.

### Verification

- Feedback/knowledge migration API suite: `29 passed`.

### Next

- Task 47.11: final RAG workbench frontend.

## 2026-07-15 Optional Provider Contracts

### Implemented

- Added dependency-free `optional_providers` contracts for Qdrant, Haystack,
  and LlamaIndex-shaped fake clients. Provider point/document/node ids,
  payloads, and raw scores are discarded at normalization time.
- Added bounded score normalization, safe source locators, stable capability
  snapshots, and deterministic `provider_unavailable`,
  `provider_search_failed`, and `provider_candidate_unavailable` reasons.
- Extended KnowledgeAdapter configuration validation and retrieval routing so
  optional providers remain visible as the configured provider and degrade to
  keyword evidence when no client is installed.
- Clarified the contract boundary between pre-final stub rules and promoted
  Final Test Knowledge provider rules.

### Verification

- Focused provider/extension/retrieval/PostgreSQL suite: `46 passed`.
- `compileall` and `git diff --check`: passed.

## 2026-07-15 Final RAG Workbench Frontend

### Implemented

- Added `/extension/knowledge-workbench` as a tester-first operational surface
  for ingestion/review entry points, retrieval logs, graph coverage, feedback,
  and provider health.
- Added dense KPI/next-action sections, provider degraded-state visibility,
  retrieval filtering, evidence/trace context, and responsive desktop/mobile
  layouts.
- Preserved HTTP status codes in API error messages so diagnostics retain the
  original failure code.

### Verification

- Frontend suite: `25 test files / 50 tests passed`.
- Production build passed; Vite emitted only the existing chunk-size warning.
- Browser smoke passed on desktop and a `390x844` mobile viewport with no
  visible overlap or unreachable workbench controls.

## 2026-07-15 Unified Evidence Trace Search

### Implemented

- Added the contract-backed project-scoped evidence trace endpoint with bounded
  global `q` search and entity-root tracing for ingestion, retrieval, evidence,
  cards, feedback, and generated case candidates.
- Safe artifact references, source locators, normalized evidence ids, provider
  mode, fallback, degraded state, and latency are preserved without exposing raw
  prompts, provider payloads, or unsafe artifacts.
- Added workbench global trace search, stage filtering, responsive result rows,
  and a details drawer before navigating to the originating record.

### Verification

- Focused backend knowledge API suite: `27 passed`.
- Frontend suite: `25 test files / 50 tests passed`; production build passed
  with the known chunk-size warning.
- Browser smoke passed on desktop and `390x844` mobile; trace search controls
  remained reachable and the responsive layout avoided overlap.

## 2026-07-15 Recent Run Navigation And Selectors

### Implemented

- Added a shared recent execution-run panel with local session persistence,
  refresh-before-resume behavior, stale indicators, and bounded history.
- Added resume actions and stable selectors across knowledge, case generation,
  case library, four execution surfaces, reporting, automation, and CI/CD.
- Error retries preserve useful prior data; resume actions clear downstream
  state that belongs to a different selected run.

### Verification

- Frontend suite: `26 test files / 53 tests passed`.
- Production build passed with the existing chunk-size warning.
- Desktop and `390x844` browser smoke across the affected workflows found no
  horizontal overflow and confirmed reachable recent-run/empty-state controls.

## 2026-07-15 Slice 47 Final Acceptance

### Implemented

- Added a provider-neutral final RAG eval fixture with two required items, one
  distractor, one unsafe same-project item, and one cross-project item.
- The fixture records deterministic recall, precision, safety exclusion, and
  optional-provider fallback visibility without provider-native payloads.

### Verification

- Final focused backend acceptance: `69 passed`.
- Frontend acceptance: `26 test files / 53 tests passed`; production build and
  desktop/`390x844` browser smoke passed.
- Fixture metrics: recall `1.0`, precision `1.0`, unsafe/cross-project
  exclusion `1.0`; `provider_unavailable` fallback is degraded and visible.
- Source DB hash remains
  `d8fb34dc054cffc69675c92351ebfbdf6620e82dc76b31bcf7ee759f357a7e01`.
- Slice 47 is complete. Known Windows runner and stale pre-Slice-47 golden
  failures remain unrelated baseline issues.

## 2026-07-24 Slice 48.2 Immutable Case Grounding

### Implemented

- Added hashed requirement/risk/knowledge claim snapshots and Prompt/Skill v2.
- Replaced batch-only alignment for v2 with per-case, fail-closed grounding
  validation and persisted grounding quality evidence.
- Added automatic reviewed-requirement recovery for new browsers and rejected
  stale cross-requirement document selections.

### Verification

- Backend: `462 passed`.
- Frontend: `25 test files / 54 tests passed`.
- Production build passed with the existing large-chunk warning.

## 2026-07-28 Slice 49.2 Workflow-Control Persistence

### Implemented

- Added project-scoped persistent workflow runs, immutable stage snapshots,
  append-only human decisions, and append-only transition events.
- Added server-side position reconstruction, stage-scoped canonical hashing,
  secret/size/integrity checks, and optimistic compare-and-swap.
- Added exact approval-decision consumption with database uniqueness and ABA
  coverage; fingerprints remain correlation/integrity metadata only.
- Added Alembic metadata registration and upgraded the migration-head contract
  to revision `20260728_0019`.
- Kept public APIs, frontend, and existing domain-service migration out of this
  task.

### Verification

- Focused policy, persistence, and migration suite: `44 passed`.
- Backend: `511 passed, 1 deselected`; the deselected symlink escape test needs
  a Windows privilege unavailable to the current process.
- Frontend: `25 test files / 54 tests passed`.
- Production build passed with the existing large-chunk warning.
- Runtime DB acceptance: v2 task succeeded with 11 claims, 5 candidates, and
  grounding status `pass` for every candidate.

## 2026-07-24 Slice 48.3 Claim Grounding EvalOps

### Implemented

- Added a fixed, provider-neutral Claim Grounding corpus for explicit v1/v2
  Prompt/Skill pairs.
- Added fail-closed offline metrics for citation recall, unsupported rejection,
  requirement coverage, coverage drift, and per-case Claim diagnostics.
- Documented the EvalOps metric and corpus contract.

### Verification

- Focused grounding/API suite: `23 passed`.
- Backend: `471 passed, 1 deselected`; the deselected symlink security test
  requires a Windows privilege unavailable to the current process.
- Frontend: `25 files / 54 tests`; production build passed with the existing
  chunk-size warning.

## 2026-07-24 Slice 49.1 Human-Controlled Transition Policy

### Implemented

- Added persistence-free workflow positions and scoped human approval grants.
- Added requirement-to-execution and CI/CD patch stage sequences with exact
  predecessor-prefix validation.
- Restricted AI to candidate submission and deterministic system code to
  adjacent-stage advancement after matching human approval.
- Added stale/cross-workflow/cross-subject grant rejection, new-snapshot rules,
  separate automation plan/draft gates, and CI/CD patch gate coverage.
- Documented the policy boundary without claiming integration into current
  domain services.

### Verification

- Focused workflow policy: `29 passed`.
- Backend: `500 passed, 1 deselected`; the deselected symlink escape test needs
  a Windows privilege unavailable to the current process.
- Frontend: `25 test files / 54 tests passed`.
- Production build passed with the existing large-chunk warning.

## 2026-07-29 Slice 49.3 RequirementReview Workflow Integration

### Implemented

- Integrated RequirementReview with authoritative WorkflowRun snapshots and
  project-scoped complete, edit, reject, approve, continue, selected revision,
  and atomic approve-and-continue actions.
- Required exact approval evidence before formal RequirementDocument creation.
- Replaced direct frontend navigation with server-driven `can_*` actions,
  candidate editing, stale-state refresh, controlled advance, and formal-asset
  blocking before approval.

### Verification

- Focused backend workflow/requirements suite: `68 passed`.
- Full backend: `515 passed`.
- Frontend: `25 test files / 55 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed; the protected source database was not used.

### Next

- Task 49.4: integrate the adjacent RiskReview stage without migrating later
  domains in the same task.

## 2026-07-29 Slice 49.4 RiskReview Workflow Integration

### Implemented

- Bound the RiskReview draft to the exact consumed RequirementReview snapshot
  id and hash.
- Added project-scoped submit, complete, edit, approve, reject, continue, and
  atomic approve-and-continue actions with server-owned state and optimistic
  compare-and-swap.
- Made current risk candidates come from the authoritative immutable workflow
  snapshot, so edited candidates and the approval target cannot diverge.
- Added frontend RiskReview stage switching, candidate editing, server-driven
  actions, stale-state refresh, and controlled advance to TestPlanReview.

### Verification

- Focused backend workflow/requirements suite: `60 passed`.
- Full backend: `516 passed`.
- Frontend: `25 test files / 55 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed; the protected source database was not used.

### Next

- Task 49.5: integrate TestPlanReview without migrating later domains in the
  same task.

## 2026-07-29 Slice 49.5 TestPlanReview Workflow Integration

### Implemented

- Added project-scoped TestPlanReview backend actions on the existing
  RequirementReview-owned WorkflowRun: submit, complete, edit, approve, reject,
  continue, and atomic approve-and-continue.
- Bound TestPlanReview input to the exact approved RiskReview snapshot id and
  hash, and bound the adjacent CaseReview draft to the exact approved
  TestPlanReview snapshot id and hash without migrating Case workflow behavior.
- Required an explicit non-empty test strategy before approving or advancing a
  plan that contains high or critical approved risk items.
- Documented the TestPlanReview API/state-machine contract.
- Wired the RequirementReview frontend store/API/view to switch TestPlanReview
  submit, complete, edit, approve, reject, and continue actions by authoritative
  workflow stage.

### Verification

- Focused backend requirement API suite: `21 passed`.
- Focused backend requirement/workflow suite: `61 passed`.
- Full backend: `517 passed`.
- Focused frontend RequirementReview suite with temporary Node `v24.18.0`:
  `1 file / 2 tests passed`.
- Full frontend with temporary Node `v24.18.0`: `25 files / 55 tests passed`.
- Production build with temporary Node `v24.18.0` passed with the existing
  large-chunk warning.
- `git diff --check` passed.
- The temporary Node runtime was restored only for this shell under
  `%TEMP%\chtest-task49-node`; it was not committed and did not change system
  PATH.

### Next

- Task 49.6: integrate CaseReview into persisted workflow control using the
  exact approved TestPlanReview snapshot as input.

## 2026-07-29 Slice 49.6 CaseReview Workflow Integration

### Implemented

- Added project-scoped CaseReview backend actions on the existing
  RequirementReview-owned WorkflowRun: read, submit, complete, edit, approve,
  reject, continue, and atomic approve-and-continue.
- Bound CaseReview input to the exact approved TestPlanReview snapshot id and
  hash, and bound the adjacent AutomationPlanReview draft to the exact approved
  CaseReview snapshot id/hash plus approved candidate/test-case evidence.
- Preserved existing GeneratedCaseCandidate review rules: AI generation alone
  cannot approve candidates or create formal TestCase rows; CaseReview approval
  requires all same-review candidates to reach final human-reviewed states and
  at least one approved candidate to have a TestCase.
- Made CaseReview edits create a JSON-safe immutable snapshot and invalidate old
  approval before re-entering human review.
- Documented the CaseReview API/state-machine contract.
- Wired the CaseGenerationReview frontend store/API/view to load the
  authoritative CaseReview gate and invoke submit, complete, edit, approve,
  reject, continue, and approve-and-continue actions with server-owned lock
  versions.

### Verification

- Focused backend CaseReview/workflow suite: `46 passed`.
- Full backend: `518 passed`.
- Focused frontend CaseGenerationReview suite with temporary Node `v24.18.0`:
  `1 file / 8 tests passed`.
- Full frontend with temporary Node `v24.18.0`: `25 files / 56 tests passed`.
- Production build with temporary Node `v24.18.0` passed with the existing
  large-chunk warning.
- `git diff --check` passed.
- The temporary Node runtime remains isolated under `%TEMP%\chtest-task49-node`;
  it was not committed and did not change system PATH.

### Next

- Task 49.7: integrate AutomationPlanReview into persisted workflow control
  using the exact approved CaseReview snapshot as input.

## 2026-07-29 Slice 49.7 AutomationPlanReview Workflow Integration

### Implemented

- Added project-scoped AutomationPlanReview backend actions on the existing
  RequirementReview-owned WorkflowRun: read, submit, complete, edit, approve,
  reject, continue, and atomic approve-and-continue.
- Bound AutomationPlanReview input to the exact approved CaseReview snapshot id
  and hash, and bound the adjacent AutomationDraftReview draft to the exact
  approved AutomationPlanReview snapshot id/hash plus approved plan/test-case
  evidence.
- Preserved existing AutomationPlan review rules: AI plan output alone cannot
  generate draft code, approve draft code, or execute tests; AutomationPlanReview
  approval requires at least one approved AutomationPlan for an approved
  TestCase from the CaseReview snapshot.
- Made AutomationPlanReview edits create a JSON-safe immutable snapshot and
  invalidate old approval before re-entering human review.
- Documented the AutomationPlanReview API/state-machine contract.
- Wired the AutomationDraftReview frontend store/API/view to load the
  authoritative AutomationPlanReview gate after plan generation and invoke
  submit, complete, edit, approve, reject, continue, and approve-and-continue
  actions with server-owned lock versions.

### Verification

- Focused backend AutomationPlanReview/CaseReview/workflow suite: `49 passed`.
- Full backend: `519 passed`.
- Focused frontend AutomationDraftReview suite with temporary Node `v24.18.0`:
  `1 file / 6 tests passed`.
- Full frontend with temporary Node `v24.18.0`: `25 files / 57 tests passed`.
- Production build with temporary Node `v24.18.0` passed with the existing
  large-chunk warning.
- `git diff --check` passed.
- The temporary Node runtime remains isolated under `%TEMP%\chtest-task49-node`;
  it was not committed and did not change system PATH.

### Next

- Task 49.8: integrate AutomationDraftReview into persisted workflow control
  using the exact approved AutomationPlanReview snapshot as input.

## 2026-07-29 Slice 49.8 AutomationDraftReview Workflow Integration

### Implemented

- Added project-scoped AutomationDraftReview backend actions on the existing
  RequirementReview-owned WorkflowRun: read, submit, complete, edit, approve,
  reject, continue, and atomic approve-and-continue.
- Bound AutomationDraftReview input to the exact approved AutomationPlanReview
  snapshot id and hash, and bound the adjacent ExecutionApproval draft to the
  exact approved AutomationDraftReview snapshot id/hash plus approved
  AutomationPlan, AutomationDraft, and TestCase evidence.
- Preserved existing AutomationDraft review rules: AI draft output alone cannot
  approve code or execute tests; AutomationDraftReview approval requires at
  least one approved AutomationDraft for an approved AutomationPlan from the
  AutomationPlanReview snapshot.
- Made AutomationDraftReview edits create a JSON-safe immutable snapshot and
  invalidate old approval before re-entering human review.
- Documented the AutomationDraftReview API/state-machine contract.
- Wired the AutomationDraftReview frontend store/API/view to load the
  authoritative AutomationDraftReview gate after draft creation and invoke
  submit, complete, edit, approve, reject, continue, and approve-and-continue
  actions with server-owned lock versions.

### Verification

- Focused backend AutomationDraftReview/workflow suite: `44 passed`.
- Full backend: `520 passed`.
- Focused frontend AutomationDraftReview suite with temporary Node `v24.18.0`:
  `1 file / 7 tests passed`.
- Full frontend with temporary Node `v24.18.0`: `25 files / 58 tests passed`.
- Production build with temporary Node `v24.18.0` passed with the existing
  large-chunk warning.
- `git diff --check` passed.
- The temporary Node runtime remains isolated under `%TEMP%\chtest-task49-node`;
  it was not committed and did not change system PATH.

### Next

- Task 49.9: integrate ExecutionApproval into persisted workflow control using
  the exact approved AutomationDraftReview snapshot as input.

## 2026-07-29 Slice 49.9 ExecutionApproval Workflow Integration

### Implemented

- Added project-scoped ExecutionApproval backend actions on the existing
  RequirementReview-owned WorkflowRun: read, submit, complete, edit, approve,
  reject, continue, and atomic approve-and-continue.
- Bound ExecutionApproval input to the exact approved AutomationDraftReview
  snapshot id and hash, and bound the adjacent ExecutionResultReview draft to
  the exact approved ExecutionApproval snapshot id/hash plus upstream snapshot
  evidence, approved AutomationDraft ids, execution decisions, and generated
  TestRun ids.
- Required workflow-backed AutomationDraft execution to include the current
  ExecutionApproval approval decision id; stale approval decisions are rejected
  after edits create a new snapshot.
- Preserved deterministic draft blocking reasons before execution while moving
  demo/unverified evidence warnings into the explicit ExecutionApproval human
  gate instead of requiring pre-existing execution evidence for a first run.
- Documented the ExecutionApproval API/state-machine contract.
- Wired the pytest execution frontend store/API/view to load the authoritative
  ExecutionApproval gate and send the approved decision id when starting a
  draft-backed run.

### Verification

- Focused backend ExecutionApproval/pytest/workflow suite: `55 passed`.
- Full backend: `521 passed`.
- Focused frontend PytestExecutionView suite with temporary Node `v24.18.0`:
  `1 file / 3 tests passed`.
- Full frontend with temporary Node `v24.18.0`: `25 files / 59 tests passed`.
- Production build with temporary Node `v24.18.0` passed with the existing
  large-chunk warning.
- `git diff --check` passed.
- The temporary Node runtime remains isolated under `%TEMP%\chtest-task49-node`;
  it was not committed and did not change system PATH.

### Next

- Task 49.10: integrate ExecutionResultReview into persisted workflow control
  using the exact approved ExecutionApproval snapshot as input.

## 2026-07-29 Slice 49.10 ExecutionResultReview Workflow Integration

### Implemented

- Added project-scoped ExecutionResultReview backend actions on the existing
  RequirementReview-owned WorkflowRun: read, submit, complete, edit, approve,
  reject, continue, and atomic approve-and-continue.
- Bound ExecutionResultReview input to the exact approved ExecutionApproval
  snapshot id and hash, generated TestRun ids, execution Artifact ids, and
  upstream AutomationDraftReview/AutomationPlanReview/CaseReview snapshot
  evidence.
- Required ExecutionResultReview approval and advancement to have generated
  TestRun evidence plus at least one persisted same-project execution Artifact.
- Required workflow-backed failure analysis and automation execution report
  generation to include the current ExecutionResultReview approval decision id,
  or the same approval already consumed by a successful advance to ReportReview.
- Made ExecutionResultReview edits create a JSON-safe immutable result-decision
  snapshot and invalidate old approval before re-entering human review.
- Documented the ExecutionResultReview API/state-machine contract.
- Wired the reporting frontend API/store/view to load the authoritative
  ExecutionResultReview gate, block report/failure-analysis actions before
  approval, and send the approved decision id in both request payloads.

### Verification

- Focused backend ExecutionResultReview/reporting/pytest/workflow suite:
  `63 passed`.
- Full backend: `521 passed`.
- Focused frontend reporting + PytestExecutionView suite with temporary Node
  `v24.18.0`: `2 files / 6 tests passed`.
- Full frontend with temporary Node `v24.18.0`: `25 files / 60 tests passed`.
- Production build with temporary Node `v24.18.0` passed with the existing
  large-chunk warning.
- `git diff --check` passed.
- The temporary Node runtime remains isolated under `%TEMP%\chtest-task49-node`;
  it was not committed and did not change system PATH.

### Next

- Task 49.11: integrate ReportReview into persisted workflow control using the
  exact approved ExecutionResultReview snapshot as input.

## 2026-07-30 Slice 49.11 ReportReview Workflow Integration

### Implemented

- Added ReportReview controlled actions on the existing RequirementReview-owned
  WorkflowRun: read, submit, complete, edit, approve, reject, continue, and
  approve-and-continue.
- Bound ReportReview to the exact approved ExecutionResultReview snapshot and
  preserved source ExecutionApproval snapshot id/hash, generated TestRun ids,
  execution Artifact evidence, generated Report ids, and Report Artifact ids.
- Changed workflow-backed automation execution report generation to create
  editable `draft` report candidates instead of formal `ready` reports.
- Required ReportReview approval to capture current generated report and report
  artifact evidence in the immutable ReportReview snapshot; edits invalidate
  old approval.
- Implemented terminal ReportReview publish by consuming the exact current
  approval once, marking generated reports `ready`, returning the authoritative
  lock version, and rejecting replay.
- Wired the reporting frontend API/store/view to load ReportReview, save report
  snapshots, approve/reject, publish, and refresh the report after publish.
- Updated API, state-machine, and artifact contracts for ReportReview.

### Verification

- Focused backend reporting workflow suite:
  `backend\\.venv\\Scripts\\python.exe -m pytest backend/app/tests/api/test_report_failure_analysis.py backend/app/tests/api/test_automation_plan.py::test_execution_approval_workflow_gates_test_run_and_preserves_draft_snapshot -q` => `9 passed`.
- Full backend: `backend\\.venv\\Scripts\\python.exe -m pytest backend/app/tests -q` => `521 passed`.
- Full frontend with Node `v24.18.0` from `D:\\Downloads\\Chtest-env\\node-v24.18.0-win-x64`:
  `npm.cmd --prefix frontend run test -- --run` => `25 files / 60 tests passed`.
- Production build with the same Node runtime:
  `npm.cmd --prefix frontend run build` => passed with the existing large-chunk warning.
- `git diff --check` passed.

### Next

- Task 49.12: add an AI Workbench workflow queue for pending review, pending
  approval, and continuable WorkflowRun tasks without adding RBAC, dashboards,
  or cross-user collaboration.

## 2026-08-03 Slice 49.12 AI Workbench Workflow Queue

### Implemented

- Added project-scoped read-only workflow queue API:
  `GET /api/projects/{project_id}/workflow-runs`.
- Queue returns only active actionable WorkflowRun rows grouped as
  `waiting_review`, `waiting_approval`, and `can_continue`; it excludes draft,
  rejected, inactive, cross-project, and consumed terminal approval records.
- Queue items include workflow kind, subject ref, stage/state, lock version,
  snapshot id/hash, current unconsumed approval id, and a nullable route hint.
  Route hints remain null until a destination can restore the exact run instead
  of falling back to recent browser context.
- Added the AI Workbench workflow queue panel with grouped read-only lists and
  explicit unavailable-route state. It intentionally exposes no review,
  approval, reject, continue, report publish, artifact mutation, or domain
  creation action.
- Updated the API contract and added backend/frontend queue coverage.

### Verification

- Focused backend:
  `backend\\.venv\\Scripts\\python.exe -m pytest backend/app/tests/workflow_control/test_workflow_queue.py -q` => `1 passed`.
- Backend regression excluding the existing symlink-capability test:
  `backend\\.venv\\Scripts\\python.exe -m pytest backend/app/tests -q -k "not test_rejects_symlink_escape_inside_artifact_root" --basetemp .t49/q` => `521 passed, 1 deselected`.
- The excluded test reached its Windows `symlink_to` setup and was blocked by
  current-process privilege (`WinError 1314`); no product assertion failed.
- Focused frontend:
  `npm.cmd --prefix frontend run test -- AiWorkbenchView.spec.ts --run` => `1 file / 5 tests passed`.
- Full frontend with Node `v24.18.0` from
  `D:\\Downloads\\Chtest-env\\node-v24.18.0-win-x64`:
  `npm.cmd --prefix frontend run test -- --run` => `25 files / 61 tests passed`.
- Production build with the same Node runtime passed with the existing
  large-chunk warning. `git diff --check` passed.

### Next

- Task 49.13: add a lightweight TestCampaign and coverage matrix entry with
  explicit scope and exit conditions; keep it local-first and review-gated.

## 2026-08-03 Slice 49.13 Controlled TestCampaign Scope

### Implemented

- Added Alembic `20260803_0020`, TestCampaign persistence, project-scoped
  schemas/service/router, and app router registration.
- Persisted explicit scope statement, same-project target Environment, version
  reference, normalized exit conditions, selected requirement/risk/test-plan/
  approved-case ids, and deterministic coverage rows.
- Reused the existing WorkflowRun Scope gate. Create writes an immutable first
  snapshot; edit revises to a new immutable snapshot; submit/review/approve/
  reject/continue retain server-owned compare-and-swap and exact approval
  consumption.
- Requirement/risk coverage requires explicit GeneratedCaseCandidate links from
  selected approved cases. Test-plan coverage requires approval evidence on the
  exact immutable snapshot. Missing relationships remain visible gaps.
- Added API tests for evidence-backed coverage, gap reporting, project
  isolation, stale approval invalidation, one-time approval consumption, and
  absence of execution/report side effects.
- Updated data, API, and state-machine contracts plus the Alembic head
  regression expectation.

### Verification

- Focused API and migration:
  `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_test_campaigns.py backend/app/tests/db/test_alembic_upgrade_head.py -q` => `6 passed`.
- Full backend:
  `backend\.venv\Scripts\python.exe -m pytest backend/app/tests -q --basetemp .t49/campaign-full` => `524 passed`.
- Full frontend with Node `v24.18.0` from
  `D:\Downloads\Chtest-env\node-v24.18.0-win-x64`:
  `npm.cmd --prefix frontend test -- --run` => `25 files / 61 tests passed`.
- Production build with the same Node runtime passed with the existing
  large-chunk warning.
- `git diff --check` passed.

### Next

- Task 49.14: add the focused frontend TestCampaign Scope page using only the
  authoritative campaign API and workflow projection.

## 2026-08-03 Slice 49.14 Controlled TestCampaign Scope Frontend

### Implemented

- Added the focused `/campaigns/scope` page with project environment, version,
  exit-condition, and evidence-id inputs; editable candidate scope; persisted
  deterministic coverage rows; snapshot and approval audit data; and the
  fixed human review action bar.
- Added typed TestCampaign API calls and a Pinia store that always sends the
  current server lock version and exact approval decision id.
- Stale `409` responses fail closed, display an explicit refresh requirement,
  and disable candidate and gate mutations.
- Continue waits for the authoritative `requirement_review` response before
  navigating. The page never recomputes coverage from displayed text.
- Added responsive navigation and mobile action layout without introducing a
  dashboard or execution/report orchestration.

### Verification

- Focused frontend: `npm.cmd --prefix frontend run test -- TestCampaignScopeView.spec.ts --run` => `1 file / 3 tests passed`.
- Full backend: `backend\.venv\Scripts\python.exe -m pytest backend/app/tests -q --basetemp .t49/campaign-ui-final` => `524 passed`.
- Full frontend: `npm.cmd --prefix frontend test -- --run` => `26 files / 64 tests passed`.
- Production build passed with the existing large-chunk warning.
- Real browser QA verified create, persisted requirement/risk gaps, submit,
  complete review, approve, and server-backed continue. Desktop and `390x844`
  views had no horizontal overflow or overlapping controls.
- `git diff --check` passed. The protected source database was not used.

### Next

- Task 49.15: expose a route only for Scope queue items that can restore the
  exact same-project TestCampaign, and fail closed on invalid explicit ids.

## 2026-08-04 Slice 49.15 Exact TestCampaign Scope Resume

### Implemented

- Added deterministic same-project Scope route resolution to the read-only
  WorkflowRun queue.
- Required the TestCampaign Scope page to load an explicit campaign id directly
  and fail closed on malformed, missing, inactive, or otherwise unavailable
  subjects without falling back to a recent campaign.
- Preserved server-owned lock versions and approval ids for every mutation; the
  queue route remains a navigation hint rather than authorization.
- Added backend and frontend coverage for the exact route and fail-closed
  branches, and updated the API contract.

### Verification

- Focused backend queue suite: `2 passed`.
- Full backend: `525 passed`.
- Focused Scope + AI Workbench frontend suite: `2 files / 10 tests passed`.
- Full frontend: `26 files / 66 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.
- Historical pytest scratch directories and the protected source database were
  not modified.

### Next

- Task 49.16: expose an exact route only for standard same-project
  RequirementReview subjects and make the RequirementReview page fail closed
  on explicit restore failure. Do not route TestCampaign-origin
  RequirementReview runs until their adjacent-stage domain contract exists.

## 2026-08-04 Slice 49.16 Exact RequirementReview Resume

### Implemented

- Added deterministic RequirementReview route resolution for active
  same-project Requirement subjects in the read-only WorkflowRun queue.
- Included exact Requirement, RequirementReview, and WorkflowRun ids in the
  navigation hint and verified all three in the RequirementReview page.
- Added direct Requirement loading while preserving project and relationship
  validation in the store.
- Locked new review creation and cleared review state whenever explicit restore
  parameters are incomplete, invalid, cross-project, or mismatched. Explicit
  mode never falls back to local storage or recent records.
- Kept TestCampaign-origin RequirementReview runs null until they own a
  contract-backed RequirementReview row.

### Verification

- Focused backend queue suite: `3 passed`.
- Full backend: `526 passed`.
- Focused RequirementReview + AI Workbench frontend suite: `2 files / 10 tests
  passed`.
- Full frontend: `26 files / 69 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

### Next

- Task 49.17: expose and restore the exact standard RiskReview queue subject
  through the existing project-scoped API. Do not add later stages or route
  TestCampaign-origin RequirementReview runs.

## 2026-08-04 Slice 49.17 Exact RiskReview Resume

### Implemented

- Added deterministic RiskReview route resolution for active same-project
  RequirementReview subjects in the read-only WorkflowRun queue.
- Added `workflow_stage=risk_review` to the exact Requirement,
  RequirementReview, and WorkflowRun navigation hint.
- Routed explicit RiskReview restoration through the existing project-scoped
  RiskReview API and verified the returned stage and run before exposing the
  server-owned controls.
- Preserved the old RequirementReview route and fail-closed behavior for
  unsupported stages, invalid ids, stale browser context, and mismatched runs.

### Verification

- Focused backend queue suite: `4 passed`.
- Full backend: `527 passed`.
- Focused RequirementReview + AI Workbench frontend suite: `2 files / 12 tests
  passed`.
- Full frontend: `26 files / 71 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

### Next

- Task 49.18: expose and restore the exact standard TestPlanReview queue subject
  through the existing project-scoped API. Keep CaseReview and
  TestCampaign-origin RequirementReview runs out of scope.
