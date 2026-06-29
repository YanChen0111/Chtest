# Slice 05: Prompt And Skill Registry Task Plan

## Goal

Load, validate, version, expose, and benchmark built-in PromptVersion and SkillVersion records for AI workflows.

## Source Documents

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/contracts/07-seed-data-contract.md`
- `docs/contracts/08-mock-provider-contract.md`
- `docs/architecture/02-agent-mcp-skill-prompt.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-02-frontend-foundation.md`
- `docs/product/06-frontend-ui-guidelines.md`

## Preconditions

- Slice 01, Slice 02, Slice 02.5, and Slice 04 AI Runtime Core are complete.
- If Slice 02.5 is not complete, skip Task 7 and record it as blocked in handoff instead of hand-writing an ad hoc frontend structure.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add PromptVersion and SkillVersion models | done | `pytest backend/app/tests/db/test_prompt_skill_models.py -q` | pending commit | Migration included |
| Add built-in prompt files | done | `backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_prompt_files.py -q` | pending commit | JSON output schema required |
| Add built-in skill files | done | `backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_skill_files.py -q` | pending commit | Quality gates and forbidden actions |
| Add registry loader and hash logic | done | `backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_registry_loader.py -q` | pending commit | Idempotent seed |
| Add mock-provider eval bench | planned | `pytest backend/app/tests/prompt_skill/test_eval_bench.py -q` | - | Deterministic schema/evidence/unsafe metrics |
| Add Prompt/Skill API | planned | `pytest backend/app/tests/api/test_prompt_skill_registry.py -q` | - | List and detail only |
| Add Prompt/Skill frontend shell | planned | `npm --prefix frontend run test -- --run` | - | Version list and detail smoke |

## Task 1: Add PromptVersion And SkillVersion Models

Goal: Add PromptVersion and SkillVersion models, schemas, migration, and uniqueness constraints.

Expected files:

- `backend/app/modules/prompt_skill/models.py`
- `backend/app/modules/prompt_skill/schemas.py`
- `backend/alembic/versions/<revision>_prompt_skill_registry.py`
- `backend/app/tests/db/test_prompt_skill_models.py`

Verification command:

```bash
pytest backend/app/tests/db/test_prompt_skill_models.py -q
```

Non-goals:

- Do not implement prompt editing UI.
- Do not overwrite active versions in place.

Commit message:

```text
feat(prompt-skill): add prompt and skill models
```

## Task 2: Add Built-In Prompt Files

Goal: Add V1 built-in prompt markdown files with Agent, Purpose, Input Schema, Output Schema, Instructions, and Failure Output sections.

Expected files:

- `prompts/requirement_review/v1.md`
- `prompts/risk_matrix/v1.md`
- `prompts/case_generation/v1.md`
- `prompts/case_review/v1.md`
- `prompts/automation_draft_generation/v1.md`
- `prompts/cicd_change_analysis/v1.md`
- `prompts/unit_test_generation/v1.md`
- `prompts/regression_selection/v1.md`
- `prompts/tool_execution/v1.md`
- `prompts/failure_analysis/v1.md`
- `prompts/report_generation/v1.md`
- `backend/app/tests/prompt_skill/test_prompt_files.py`

Verification command:

```bash
pytest backend/app/tests/prompt_skill/test_prompt_files.py -q
```

Non-goals:

- Do not optimize prompt quality beyond contract compliance.
- Do not include real secrets or customer data.

Commit message:

```text
feat(prompt): add built-in v1 prompts
```

## Task 3: Add Built-In Skill Files

Goal: Add V1 built-in skill markdown files with methodology, input/output contract, quality gates, forbidden actions, and tool permissions.

Expected files:

- `skills/requirement-review-skill/v1.md`
- `skills/test-case-generation-skill/v1.md`
- `skills/testcase-review-skill/v1.md`
- `skills/automation-draft-skill/v1.md`
- `skills/unit-test-generation-skill/v1.md`
- `skills/regression-selection-skill/v1.md`
- `skills/tool-execution-skill/v1.md`
- `skills/failure-analysis-skill/v1.md`
- `skills/report-generation-skill/v1.md`
- `backend/app/tests/prompt_skill/test_skill_files.py`

Verification command:

```bash
pytest backend/app/tests/prompt_skill/test_skill_files.py -q
```

Non-goals:

- Do not build plugin import.
- Do not create a skill marketplace.

Commit message:

```text
feat(skill): add built-in v1 skills
```

## Task 4: Add Registry Loader And Hash Logic

Goal: Load prompt and skill files into database idempotently and compute stable content hash.

Expected files:

- `backend/app/modules/prompt_skill/registry_loader.py`
- `backend/app/modules/prompt_skill/service.py`
- `backend/app/tests/prompt_skill/test_registry_loader.py`

Verification command:

```bash
pytest backend/app/tests/prompt_skill/test_registry_loader.py -q
```

Non-goals:

- Do not overwrite already published active content.
- Do not implement A/B testing.

Commit message:

```text
feat(prompt-skill): add registry loader
```

## Task 5: Add Mock-Provider Eval Bench

Goal: Add a deterministic eval bench that can run built-in prompts and skills against mock provider samples and produce schema, evidence, and safety metrics.

Expected files:

- `backend/app/modules/prompt_skill/eval_bench.py`
- `backend/app/modules/prompt_skill/eval_samples.py`
- `backend/app/tests/prompt_skill/test_eval_bench.py`
- `docs/fixtures/eval-bench/requirements.md`
- `docs/fixtures/eval-bench/code-changes.md`
- `docs/fixtures/eval-bench/failed-runs.md`
- `docs/fixtures/eval-bench/bug-history.md`

Verification command:

```bash
pytest backend/app/tests/prompt_skill/test_eval_bench.py -q
```

Expected metrics:

- `schema_valid_rate`
- `evidence_complete_rate`
- `unsafe_output_rate`
- `manual_edit_rate`
- `first_run_pass_rate`
- `repair_success_rate`

Non-goals:

- Do not build a public model leaderboard.
- Do not call a real LLM provider.
- Do not block V1 on perfect metric thresholds; this bench is the deterministic baseline.

Commit message:

```text
feat(prompt-skill): add mock provider eval bench
```

## Task 6: Add Prompt/Skill API

Goal: Add list/detail APIs for PromptVersion and SkillVersion so AI tasks and UI can trace versions.

Expected files:

- `backend/app/modules/prompt_skill/router.py`
- `backend/app/modules/prompt_skill/service.py`
- `backend/app/modules/prompt_skill/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_prompt_skill_registry.py`

Verification command:

```bash
pytest backend/app/tests/api/test_prompt_skill_registry.py -q
```

Non-goals:

- Do not add write/edit endpoints.
- Do not allow deleting versions used by AITask.

Commit message:

```text
feat(prompt-skill): add registry api
```

## Task 7: Add Prompt/Skill Frontend Shell

Goal: Add version list/detail views for Prompt and Skill Center.

Precondition: Slice 02.5 Frontend Foundation is complete.

Expected files:

- `frontend/src/views/prompt-skill/PromptSkillCenterView.vue`
- `frontend/src/api/promptSkill.ts`
- `frontend/src/stores/promptSkill.ts`
- `frontend/src/router/index.ts`
- `frontend/src/views/prompt-skill/PromptSkillCenterView.spec.ts`

Verification command:

```bash
npm --prefix frontend run test -- --run
```

Non-goals:

- Do not implement prompt editing.
- Do not implement metric comparison charts yet.

Commit message:

```text
feat(frontend): add prompt skill center shell
```

## Slice Completion Gate

- Built-in PromptVersion and SkillVersion records load idempotently.
- Hash changes when file content changes.
- Prompt files include valid JSON schemas.
- Skill files include quality gates and forbidden actions.
- Mock-provider eval bench outputs schema_valid_rate, evidence_complete_rate, and unsafe_output_rate.
- AI task creation can reference active prompt and skill versions.
- Prompt/Skill API returns version trace data for AI tasks.
- `memory/07-dev-log.md` and `memory/08-session-handoff.md` are updated.
- Next Slice is set to Slice 06 Requirement Review.
