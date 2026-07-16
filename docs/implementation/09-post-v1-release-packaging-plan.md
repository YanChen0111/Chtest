# Post-V1 Release Packaging Plan

Date: 2026-06-30

## Decision

Use the current composable golden suite as the V1 automated acceptance evidence.

Do not add a new narrative end-to-end automated test before V1 packaging. The
current suite already covers the V1 evidence spine across focused golden smokes,
and `docs/implementation/07-v1-release-acceptance.md` records a passing full
release-acceptance run.

Add a lightweight release packaging artifact instead:

- one short release note;
- one manual walkthrough checklist;
- optional frontend screenshots captured from the running local workbench.

## Rationale

The V1 product proof is not broad feature count. It is the evidence-backed loop:

```text
Requirement or local code change
  -> AI risk and test analysis
  -> reviewed test cases or test patches
  -> approved AutomationDraft or UnitTestPatch
  -> controlled runner execution
  -> runtime artifacts and evidence
  -> failure analysis or repair candidate
  -> report
  -> AI quality metrics
```

The current golden suite verifies that loop in composable parts:

- requirement review and case generation;
- case library and metrics;
- AutomationDraft review;
- pytest and Playwright execution evidence;
- failure analysis and reporting;
- CI/CD Quality Center local diff analysis;
- UnitTestPatch, regression, and QualityGateDecision;
- extension surface boundaries for RAG 知识库 and MCP-ready ToolDefinition.

A single narrative automated E2E test would be useful later, but it is not
required to accept V1 because the release gate now runs all V1 golden smokes
together.

## Release Package Contents

Create a small package under a future docs/release area:

```text
docs/release/v1/
  README.md
  manual-walkthrough.md
  acceptance-evidence.md
  screenshots/
```

Recommended contents:

- `README.md`: V1 positioning, scope, non-goals, and quick start.
- `manual-walkthrough.md`: human-readable walkthrough based on
  `docs/fixtures/00-v1-demo-path.md`.
- `acceptance-evidence.md`: links to `06-v1-completion-audit.md`,
  `07-v1-release-acceptance.md`, and `08-v1-final-acceptance-handoff.md`.
- `screenshots/`: optional local screenshots for AI 工作台, requirement/case
  flow, execution center, CI/CD 质量中心, 报告中心, and RAG 知识库.

## Implementation Plan

### Task 1: Create Release Package Skeleton

Files:

- Create `docs/release/v1/README.md`.
- Create `docs/release/v1/acceptance-evidence.md`.
- Create `docs/release/v1/manual-walkthrough.md`.
- Create directory `docs/release/v1/screenshots/`.

Verification:

```bash
test -f docs/release/v1/README.md
test -f docs/release/v1/acceptance-evidence.md
test -f docs/release/v1/manual-walkthrough.md
git diff --check
```

Commit:

```text
docs(release): add v1 release package skeleton
```

### Task 2: Write Manual Walkthrough

Files:

- Modify `docs/release/v1/manual-walkthrough.md`.

Walkthrough sections:

- Project and context setup.
- Requirement review and context usage.
- Candidate case generation and human approval.
- AutomationDraft review and approval.
- pytest execution evidence.
- failure analysis and report evidence.
- CI/CD Quality Center support workflow.
- Extension surfaces and explicit non-goals.

Verification:

```bash
rg -n "Requirement|AutomationDraft|TestRun|Report|CI/CD|RAG" docs/release/v1/manual-walkthrough.md
git diff --check
```

Commit:

```text
docs(release): add v1 manual walkthrough
```

### Task 3: Record Acceptance Evidence

Files:

- Modify `docs/release/v1/acceptance-evidence.md`.

Required evidence:

- Backend release acceptance command and `10 passed` result.
- Frontend Vitest command and `14` test files / `17` tests result.
- `git diff --check` clean result.
- Links to completion audit, release acceptance report, and final handoff.

Verification:

```bash
rg -n "10 passed|17 tests|completion-audit|release-acceptance|final-acceptance" docs/release/v1/acceptance-evidence.md
git diff --check
```

Commit:

```text
docs(release): record v1 acceptance evidence
```

### Task 4: Capture Optional Frontend Screenshots

Files:

- Add image files under `docs/release/v1/screenshots/` only if the local web
  workbench is running and visual capture is requested.
- Modify `docs/release/v1/README.md` to link screenshots if captured.

Suggested pages:

- AI 工作台.
- 需求评审.
- 用例库.
- 执行中心.
- CI/CD 质量中心.
- 报告中心.
- RAG 知识库.

Verification:

```bash
git diff --check
```

Commit:

```text
docs(release): add v1 workbench screenshots
```

## Non-Goals

Do not add these during release packaging:

- New product flows.
- New backend APIs.
- New frontend pages.
- RAG runtime, vector indexing, embeddings, reranking.
- MCP runtime or remote MCP calls.
- RBAC, tenants, permissions, or enterprise collaboration.
- Remote CI provider integration, deployment automation, or release
  automation.

## Next Task

Create the V1 release package skeleton.
