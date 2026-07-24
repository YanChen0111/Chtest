# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. Docker runtime work remains intentionally skipped because the local
Docker Desktop/WSL engine is unavailable.

## Current Slice

Slice 48: Agent Reliability and EvalOps.

## Current Task

Task 48.2 is complete: ground every generated case in immutable requirement,
risk, or approved evidence claims.

Verified behavior:

1. `case_generation:v2` persists a deterministic, hashed
   `requirement_claim_snapshot` on AITask input.
2. Every candidate must cite real snapshot claim ids with semantically matching
   evidence; risk and knowledge citations must also link their persisted ids.
3. Validation is per candidate and fails the complete batch closed with
   `CASE_GENERATION_GROUNDING_INVALID` before any candidate is persisted.
4. V1 remains available for replay, while the frontend defaults new generation
   to v2 and recovers the latest reviewed requirement without browser-local ids.
5. Verification is backend `462 passed`, frontend `25 files / 54 tests`, and a
   successful production build.

## Previous Tasks Verified

- Added optional Alembic `20260714_0013`: PostgreSQL full-text GIN is always
  emitted; pgvector extension/native column/HNSW setup is capability-gated and
  does not block SQLite or PostgreSQL without extension privileges.
- Added safe `postgres_hybrid` configuration, capability snapshots, native
  embedding synchronization, full-text/vector candidate SQL, provider-neutral
  score normalization, dimension/freshness checks, and deterministic keyword
  fallback with `vector_score=null`.
- Added PostgreSQL dialect/offline DDL tests, fake capability/native-result
  tests, SQLite no-op migration/fallback tests, and existing consumer regressions.
- Post-implementation review split full-text and vector candidate CTEs, applies
  dimension-matched casts/filters, keeps the similarity threshold outside the
  HNSW-ordered pool, and prevents vector-only mode from admitting text-only
  candidates. Focused Task 47.4/47.5 verification is now `76 passed`.
- Online acceptance completed on isolated PostgreSQL 16.14 databases at
  `127.0.0.1:55432`: the plain database upgraded to head with GIN full-text
  only, while the pgvector database upgraded to head with native vector storage
  and the HNSW index. The application adapter returned a real hybrid match with
  `vector_score=1.0`; the limited database correctly reported no vector
  capability and never fabricated a vector score.
- Added dependency-free optional Qdrant/Haystack/LlamaIndex fake-client
  contracts, safe configuration validation, provider-visible routing, and
  deterministic no-client/failure/invalid-candidate fallback. Focused suite is
  `46 passed`.
- Added Alembic `20260715_0014` and evidence-backed GeneratedCaseCandidate
  fields for covered requirement/risk ids, case type, generation reason, gap
  notes, automation readiness, and quality assessment. Existing model output
  remains backward compatible through deterministic defaults. CaseGeneration
  and migration verification is `13 passed`.
- Added deterministic `CaseReviewAgent` and `CoverageGapAgent` quality
  functions plus automation readiness assessment. Candidate persistence now
  writes provider-neutral findings and blockers. Focused quality/CaseGeneration
  verification is `12 passed`.
- Added Alembic `20260715_0015`, typed same-project knowledge relationships,
  creation API validation, and persisted relationship edges in the graph
  response. Migration/API verification is `28 passed`.
- Added Alembic `20260715_0016` and reviewed feedback APIs. Approval creates an
  extracted card only; card approval remains separate. Migration/API
  verification is `29 passed`.
- Built the final RAG workbench at `/extension/knowledge-workbench` with KPI
  cards, next-action links, provider health/degraded state, retrieval log
  filters, evidence/trace columns, coverage summary, and responsive layouts.
- Added focused `RagWorkbenchView` coverage and preserved HTTP status codes in
  API errors so tester-facing diagnostics retain failures such as `502`.
- Frontend verification: `25 test files / 50 tests passed`; production build
  passed with the existing chunk-size warning; desktop and 390px mobile browser
  smoke confirmed reachable controls and no visible overlap.
- Added the contract-backed `GET /api/projects/{project_id}/evidence-trace`
  endpoint with bounded `q` search, project isolation, safe artifact refs, and
  retrieval diagnostics. The focused knowledge API suite is `27 passed`.
- Added global evidence trace search and a details drawer to the workbench,
  preserving source locators, evidence ids, provider/mode, fallback, latency,
  and safe artifact links. Full frontend verification remains `25 files / 50
  tests` after the trace integration; desktop and 390px mobile smoke passed.
- Added consistent recent-run resume actions, named `data-test` selectors,
  loading/empty/error/stale states, and safe downstream-state clearing across
  knowledge, case review/library, pytest/Playwright/Newman/JMeter execution,
  reporting, automation, and CI/CD pages.
- Frontend verification after the multi-page refactor: `26 test files / 53
  tests passed`; production build passed with the existing chunk-size warning;
  desktop and `390x844` multi-page smoke found no horizontal overflow.
- Added the final provider-neutral RAG eval fixture with two required cards, a
  distractor, an unsafe same-project card, and a cross-project card. Fixture
  metrics are recall `1.0`, precision `1.0`, and exclusion `1.0`; optional
  provider unavailability remains visible as degraded fallback.
- Final focused backend acceptance is `69 passed`; frontend remains `26 files /
  53 tests`; source DB SHA256 remains unchanged.

## Task 47.5 Acceptance Evidence

The temporary PostgreSQL acceptance environment is outside the repository and
uses empty test databases only:

- `chtest_plain_test` is owned by a limited role and has no pgvector extension;
- `chtest_vector_test` has pgvector `0.8.3`, native `embedding_vector`, and
  `ix_test_knowledge_embedding_vector_hnsw_64`;
- online migration, extension privilege behavior, native `<=>`, HNSW index
  planning, and native/fallback capability behavior were verified;
- the blocked `storage/chtest-dev.db` was not used for migration or smoke data.

Docker Desktop/WSL remains unavailable, but it no longer blocks this task.

## Product Value Answer

Test engineers can ingest, review, retrieve, diagnose, trace, and improve
knowledge from one efficient operational surface.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/04-ai-vibecoding-governance.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/slices/slice-47-final-test-knowledge-rag-system.md`
9. `memory/08-session-handoff.md`
10. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Docker Desktop/WSL repair, provider runtime installation/deployment guides,
  graph/feedback, enterprise collaboration, marketplace, cloud CI, RBAC,
  tenants, permissions, unrelated frontend pages, or broad roadmap documents.

## Expected Files

Default write boundary:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
frontend/src/** knowledge workbench routes/components/services only
frontend/tests/** knowledge workbench only
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
docs/implementation/slices/slice-47-final-test-knowledge-rag-system.md
```

Explain any write outside this set before editing it.

## Verification Commands

Run backend and frontend regression plus the production build:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend/app/tests -q
npm --prefix frontend test -- --run
npm --prefix frontend run build
git diff --check
```

The source `storage/chtest-dev.db` remains blocked and read-only. Do not run
upgrade, stamp, bootstrap, or registry mutation against it.

## Acceptance

- Every v2 candidate is validated against immutable source claims before
  persistence.
- Empty/stale browser workflow context recovers the latest reviewed project
  requirement instead of submitting blank ids.
- `git diff --check` passes.

## Commit Message

```text
feat(case-generation): enforce immutable claim grounding
```

## Next Task

Task 48.3: add a fixed claim-grounding evaluation corpus that measures valid
citation recall, unsupported-case rejection, and requirement coverage drift
across Prompt/Skill versions. Do not begin it without an explicit
implementation request.
