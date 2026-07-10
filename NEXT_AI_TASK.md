# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. The current focus is no longer a narrow AI Workbench empty-state slice;
the platform has moved into V2 acceptance stabilization.

## Current Slice

V2 acceptance stabilization: verify that the local-first AI testing workbench
can run the main reviewer workflow with model configuration, RAG knowledge
cards, local vector index coverage, case generation, automation planning, and
execution evidence surfaces.

## Current Task

Continue V2 acceptance stabilization without Docker runtime work. The user
explicitly asked to skip Docker because the local engine cannot be repaired in
this session.

Current local follow-up:

1. keep the already-passing local dev/browser workflow as the acceptance path;
2. harden only concrete local evidence risks found during acceptance;
3. do not spend more time on Docker Desktop, WSL, or container runtime recovery;
4. preserve Docker Compose config as a known-valid but externally blocked path.

## Product Value Answer

The user needs to know whether the current platform can be accepted as a
runnable testing workbench, not just a collection of implemented slices.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/04-ai-vibecoding-governance.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `memory/08-session-handoff.md`
7. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad roadmap, migration, enterprise collaboration, marketplace, distributed
  execution, cloud storage, cloud CI/provider integration, RBAC, tenants,
  permissions, or unrelated deleted golden-chain files unless a concrete
  verification failure requires them.

## Expected Files

Default write boundary:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
backend/alembic/*
backend/app/modules/*
backend/app/tests/*
frontend/src/api/*
frontend/src/stores/*
frontend/src/views/*
frontend/vite.config.ts
deploy/docker-compose.yml
```

Only edit files that are directly required to fix a verification blocker. Do
not revert unrelated dirty-worktree changes.

## Verification Commands

Use focused verification first:

```bash
backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_automation_plan.py -q
```

```bash
npm --prefix frontend run test -- --run src/views/automation/AutomationDraftReviewView.spec.ts
```

```bash
backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_test_knowledge_cards.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_model_connection_config.py backend/app/tests/api/test_extension_surface.py -q
```

```bash
npm --prefix frontend run test -- --run src/views/settings/ProjectSettingsView.spec.ts src/views/extension/KnowledgeBaseView.spec.ts src/views/requirements/RequirementReviewView.spec.ts src/views/cases/CaseGenerationReviewView.spec.ts
```

```bash
npm --prefix frontend run build
git diff --check
```

Docker/compose runtime verification is intentionally skipped until the machine's
Docker Desktop Linux Engine is repaired outside this repo.

## Acceptance

- Local code acceptance is complete: backend tests, frontend tests/build,
  migration, real-model RequirementReview, RAG evidence flow, AutomationPlan,
  and AutomationDraft smoke all pass.
- Browser acceptance against the local dev stack is complete after fixing the
  Vite `/api` proxy target. With `VITE_API_BASE_URL=http://127.0.0.1:8010/api`,
  the RAG page renders `测试知识卡3`, `知识覆盖率67%`, `Vector Index3`, and
  `Vector Coverage100%`.
- Docker Compose syntax and image configuration are verified.
- Docker runtime acceptance is skipped by current user direction. Docker
  Desktop currently returns HTTP 500 from both `desktop-linux` and `default`
  engine API contexts.
- AutomationDraft approval now has a local quality gate: placeholder-only
  drafts such as `assert True` cannot be approved and the UI surfaces the
  quality-gate failure.

## Commit Message

```text
TBD after acceptance stabilization scope is clean
```

## Next Task

Continue non-Docker V2 acceptance stabilization. Prefer the next smallest local
evidence risk, such as making fake/stub automation adapter evidence impossible
to mistake for a real product regression pass, then run the focused verification
commands above.
