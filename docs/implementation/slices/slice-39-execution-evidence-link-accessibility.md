# Slice 39: Execution Evidence Link Accessibility

## Goal

Add accessible labels to execution run manifest evidence links.

Slice 34 added accessible open-link labels to the shared artifact table. The run
manifest panel still renders multiple identical `打开` links without row-specific
labels, making them harder to distinguish for assistive technology.

## Product Value Answer

After this slice, execution run manifest evidence links remain visually compact
while exposing row-specific accessible labels, so reviewers can distinguish
which local evidence artifact each link opens.

## Preconditions

- Slice 33 extracts the shared execution run manifest panel.
- Slice 34 extracts the shared execution artifact table panel with accessible
  open-link labels.
- Slice 38 centralizes output artifact definitions.

## Non-goals

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No artifact lookup changes, artifact filtering changes, artifact link URL
  changes, run manifest row-building semantics changes, result data changes,
  metric calculation changes, report generation, FailureAnalysis,
  QualityGateDecision, or AutomationDraft behavior.
- No page shell/form refactor, frontend redesign, TestKnowledgeCard, generated
  case knowledge evidence, prompt, skill, contract, fixture, RAG runtime, MCP
  runtime, marketplace, RBAC, tenants, permissions, or package upgrades.

## Slice Boundary

- Update `ExecutionRunManifestPanel.vue` link attributes only.
- Add focused component assertions for `aria-label` and `title`.
- Preserve visible link text, URLs, table rows, and open-link conditions.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Evidence Link Accessibility task plan | done | `rg -n "Slice 39|Execution Evidence Link Accessibility|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-39-execution-evidence-link-accessibility.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md && git diff --check` | pending | planning verification passed; `git diff --check` clean |
| Add accessible labels to manifest evidence links | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; visual link text and URLs unchanged |
| Slice 39 completion gate | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionOutputArtifacts.spec.ts src/views/execution/executionDisplay.spec.ts src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q && git diff --check` | pending | verification passed; no backend changes made |

## Verification Command

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts
npm --prefix frontend run build
git diff --check
```

## Acceptance

- Run manifest local evidence links include row-specific `aria-label` and
  `title` attributes.
- Visible link text remains `打开`.
- Links still render only when a row has `artifactId` and is available.
- No execution page behavior, runner behavior, or artifact URL behavior changes.

Commit message:

```text
fix(frontend): label execution manifest evidence links
```
