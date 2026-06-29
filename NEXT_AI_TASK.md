# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 05: Prompt And Skill Registry.

## Current Task

Task 5: Add mock-provider eval bench.

## Product Value Answer

After this task, Chtest has a deterministic mock-provider evaluation baseline
for built-in prompts and skills, so schema validity, evidence completeness, and
unsafe output rates can be measured before real provider integration.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-05-prompt-skill-registry.md`
3. `docs/contracts/05-prompt-skill-contract.md`
4. `docs/contracts/07-seed-data-contract.md`
5. `docs/contracts/08-mock-provider-contract.md`
6. `docs/fixtures/05-minimal-prompt-skill-seeds.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement review or case generation product pages.
- Skill marketplace, plugin import, prompt editing UI, optimization, A/B testing,
  and real provider integration docs.
- CI/CD Quality Center implementation docs beyond artifact owner references.
- RAG runtime, vector index, embedding, chunking, or reranking docs.
- MCP runtime integration docs.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/prompt_skill/eval_bench.py
backend/app/modules/prompt_skill/eval_samples.py
backend/app/tests/prompt_skill/test_eval_bench.py
docs/fixtures/eval-bench/requirements.md
docs/fixtures/eval-bench/code-changes.md
docs/fixtures/eval-bench/failed-runs.md
docs/fixtures/eval-bench/bug-history.md
```

Read existing mock provider outputs only to align deterministic sample metrics.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_eval_bench.py -q
```

Expected result: the mock-provider eval bench focused test passes.

## Acceptance

- Eval bench runs deterministic samples without external network.
- Metrics include `schema_valid_rate`, `evidence_complete_rate`,
  `unsafe_output_rate`, `manual_edit_rate`, `first_run_pass_rate`, and
  `repair_success_rate`.
- Built-in prompt output schemas are used to validate mock outputs where
  applicable.
- Eval fixture files contain no real secrets or customer data.
- No public leaderboard, API, frontend, real provider, vector index, RAG
  storage, or MCP runtime is added in this task.
- `git status --short` shows only expected eval bench files and required task
  docs before commit.

## Commit Message

```text
feat(prompt-skill): add mock provider eval bench
```

## Next Task

Slice 05 Task 6: Add Prompt/Skill API.
