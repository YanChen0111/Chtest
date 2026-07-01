# Slice 27: AI Task Evidence Artifact Links Task Plan

## Goal

Make AI task evidence artifacts easier to inspect from the AI Workbench without
showing unsafe raw model content inline.

Slice 24 made local TestRun artifacts openable. Slice 25 explained report
evidence. Slice 26 clarified external CI artifact references. This slice
applies the same local evidence access pattern to AI task artifacts such as
`context_manifest.json`, `parsed_output.json`, `schema_validation.json`, and
safe retrieval evidence.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- Recent evidence slices:
  - `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`
  - `docs/implementation/slices/slice-24-local-artifact-access-links.md`
  - `docs/implementation/slices/slice-25-execution-evidence-summary.md`
  - `docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md`

## Product Value Answer

After this slice, a user reviewing an AI task can open safe local evidence
artifacts from the AI Workbench and understand why some artifacts, such as raw
LLM output, are not directly openable in the UI.

## Preconditions

- AI task detail APIs already return artifact metadata for the selected task.
- Artifact rows already include `safe_to_show` and `redaction_applied`
  metadata for AI evidence.
- Local artifact access already supports persisted local Artifact rows.
- AI Workbench already renders AI task artifacts and LLM call logs.

## Non-goals

- No inline raw LLM output display.
- No prompt editor, prompt replay, AI task rerun, model/provider integration,
  streaming logs, or schema editor.
- No RAG runtime, vector database, embeddings, reranking, MCP runtime,
  marketplace, remote CI provider integration, RBAC, tenants, or permissions.
- No artifact upload, mutation, delete, sharing, signed URL, cloud storage,
  broad artifact browser, indexing, search, dashboard, report generation,
  FailureAnalysis, QualityGateDecision, or runner behavior changes.

## Slice Boundary

- Define a read-only AI task evidence artifact link contract.
- Add AI Workbench links only for persisted local Artifact ids that are safe to
  open from the UI.
- Keep unsafe artifacts visible as metadata but not directly openable.
- Keep raw LLM output content out of the page even when its metadata is shown.
- Add focused frontend coverage and one golden/API smoke proving the safe local
  evidence boundary.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add AI Task Evidence Artifact Links task plan | done | `test -f docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md && rg -n "AI Task Evidence Artifact Links|Product Value Answer|Non-goals|Task Table|safe_to_show|raw LLM|artifact" docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md && git diff --check` | `add4adc` | planning-only scope |
| Define AI task evidence artifact link contract | done | `rg -n "AI task evidence artifact|safe_to_show|raw LLM|local artifact" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md && git diff --check` | pending | contract-only |
| Add AI Workbench artifact links | planned | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | AI Workbench only |
| Add AI task artifact link golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ai_task_evidence_artifact_links_golden.py -q && git diff --check` | pending | safe evidence proof |
| Slice 27 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ai_task_evidence_artifact_links_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q && npm --prefix frontend run build && npm --prefix frontend run test -- --run && git diff --check` | pending | docs and handoff |

## Task 1: Add AI Task Evidence Artifact Links Task Plan

Goal: Define the smallest AI task evidence artifact link slice before contracts
or frontend changes.

Expected files:

- `docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md
rg -n "AI Task Evidence Artifact Links|Product Value Answer|Non-goals|Task Table|safe_to_show|raw LLM|artifact" docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Creates the Slice 27 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to AI task artifact evidence readability and safe local
  links.
- Does not add product code, backend code, frontend code, migrations, package
  upgrades, or tests.

Commit message:

```text
docs(v2): add ai task artifact link plan
```

## Task 2: Define AI Task Evidence Artifact Link Contract

Goal: Clarify which AI task artifacts can receive local open links and which
remain metadata-only.

Expected files:

- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "AI task evidence artifact|safe_to_show|raw LLM|local artifact" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md
git diff --check
```

Acceptance:

- API contract defines AI task artifact links as read-only local Artifact links
  derived from existing artifact metadata.
- Artifact contract states `safe_to_show=false` artifacts remain visible as
  metadata but do not receive direct UI open links.
- Contract preserves the no raw LLM inline display, no rerun, no provider
  integration, and no artifact mutation boundary.

Commit message:

```text
docs(v2): define ai task artifact link contract
```

## Task 3: Add AI Workbench Artifact Links

Goal: Let users open safe local AI task evidence artifacts from AI Workbench.

Expected files:

- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Safe local AI task artifacts show an "打开" link.
- Unsafe artifacts such as raw LLM output remain visible as metadata and show a
  not-openable status.
- LLM call logs still cite request/response/parsed artifact ids without
  inlining artifact contents.
- Page still excludes rerun, provider control, prompt editing, raw content, and
  remote runtime controls.

Commit message:

```text
feat(frontend): link safe ai task artifacts
```

## Task 4: Add AI Task Artifact Link Golden Smoke

Goal: Prove safe AI task artifact links use persisted local evidence and unsafe
AI artifacts stay metadata-only.

Expected files:

- `backend/app/tests/golden/test_ai_task_evidence_artifact_links_golden.py`
- `docs/fixtures/15-ai-task-evidence-artifact-links-golden.md`
- `docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ai_task_evidence_artifact_links_golden.py -q
git diff --check
```

Acceptance:

- Golden proves a safe AI task artifact can be opened through local artifact
  access.
- Golden proves an unsafe raw LLM artifact remains metadata-only for UI link
  purposes.
- Golden proves no AI task rerun, provider call, Report, FailureAnalysis,
  QualityGateDecision, artifact mutation, RAG runtime, or MCP runtime behavior
  is created by artifact link display.

Commit message:

```text
test(golden): add ai task artifact link smoke
```

## Slice 27 Completion Gate

Goal: Validate AI task evidence artifact links end to end and hand off the next
V2 task.

Expected files:

- `docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ai_task_evidence_artifact_links_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- All Slice 27 task rows are marked done with commit ids.
- Completion evidence records frontend build/test, golden checks, and diff
  verification.
- Non-goals remain excluded.
- Handoff names the next V2 slice or planning task.

Commit message:

```text
docs(v2): complete ai task artifact link slice
```
