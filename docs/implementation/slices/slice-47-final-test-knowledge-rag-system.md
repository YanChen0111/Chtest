# Slice 47: Final Test Knowledge RAG System

## Goal

Promote and deliver Chtest's final evidence-backed test knowledge system without
allowing vector/RAG provider schemas to replace Chtest contracts.

## Product Value Answer

After this slice family, test engineers can import project knowledge as
observable runs, review structured testing knowledge, retrieve semantically
related evidence, understand why generated cases exist, find uncovered risks,
trace failures back to knowledge and cases, and review proposed learning from
accepted/rejected work.

## Architecture Decisions And Reasons

| Major capability | Design | Why |
|---|---|---|
| Ingestion | KnowledgeIngestionRun with artifacts and idempotency | Large imports fail partially; a run gives progress, retry, counts, and exact evidence |
| Structured knowledge | Chtest-owned TestKnowledgeCard types and review state | Test concepts are auditable and stable across parser/provider changes |
| Safety | Separate extracted and approved states; prompt eligibility is server-computed | Retrieval confidence cannot replace human trust and secret/staleness gates |
| Hybrid retrieval | Metadata + PostgreSQL full-text + pgvector by default | Keeps business rows, joins, transactions, and vectors in one local-first database |
| Scale adapter | Optional Qdrant behind KnowledgeAdapter | Dedicated vector search is useful only when measured corpus/latency requires another service |
| Orchestration adapters | Optional Haystack/LlamaIndex providers behind KnowledgeAdapter | Their pipeline/connectors accelerate implementation while Chtest evidence remains stable |
| Retrieval output | Persist normalized KnowledgeEvidence and KnowledgeRetrievalRun | Case/report consumers need provider-neutral scores, source locators, latency, and errors |
| Quality agents | CaseReviewAgent and CoverageGapAgent produce structured findings | Automates mechanical checks and focuses human review on product judgment |
| Relationship graph | Typed PostgreSQL relationships first; external graph acceleration later | Impact/coverage queries need auditable edges and do not initially require a graph database |
| Feedback | Proposed KnowledgeFeedbackEvent with two review gates | The system learns from use without automatically poisoning approved knowledge |
| Observability | Unified evidence trace and retrieval/ingestion log APIs | Local failures and quality regressions must be diagnosable without server-log access |

## Provider Boundary

```text
Haystack / LlamaIndex / pgvector / Qdrant
  -> KnowledgeAdapter provider implementation
  -> Chtest KnowledgeRetrievalRun + KnowledgeEvidence
  -> CaseGeneration / Review / Report / Trace
```

Provider documents, nodes, payloads, collection schemas, and scores never become
Chtest API or ORM contracts.

## Task Table

| Task | Status | Value | Verification |
|---|---|---|---|
| 47.1 Promote product/contracts and add full-web review | done | Stable scope and reasons before code | contract keyword/self-check + `git diff --check` |
| 47.2 Add local DB preflight and safe baseline migration diagnostics | done | Current local data can upgrade without hidden destructive action | 11 focused preflight/migration/registry tests + live read-only/copy diagnostics |
| 47.3 Add KnowledgeIngestionRun and enhanced TestKnowledgeCard | done | Observable imports and reviewable knowledge | 19 ingestion/migration/retrieval tests + 44 related API tests + 30 DB tests |
| 47.4 Add KnowledgeRetrievalRun and normalized KnowledgeEvidence | done | Queryable retrieval logs and stable evidence | 64 focused API/golden/DB tests + 398 full-backend passes |
| 47.5 Add PostgreSQL full-text + pgvector KnowledgeAdapter | done | Local-first semantic recall | Isolated PostgreSQL/pgvector online smoke + deterministic fallback tests |
| 47.6 Add optional Qdrant and Haystack/LlamaIndex provider contracts | done | Scale/provider choice without schema leakage | provider contract tests with fake clients |
| 47.7 Add evidence-backed CaseGeneration fields | done | Every case explains why it exists | case generation contract/golden tests |
| 47.8 Add CaseReviewAgent and CoverageGapAgent | pending | Automatic domain/evidence/coverage quality gate | agent mock/eval tests |
| 47.9 Add typed relationships and graph queries | pending | Impact, gaps, and regression recommendation | relationship API/golden tests |
| 47.10 Add reviewed feedback loop | pending | Accepted/rejected/failure knowledge improves the project | feedback state/API tests |
| 47.11 Build final RAG workbench | pending | Efficient ingestion, review, retrieval, graph, feedback, provider UX | focused frontend tests + build + browser smoke |
| 47.12 Add unified trace and global evidence search | pending | Logs and evidence are discoverable across pages | trace API/frontend tests + browser smoke |
| 47.13 Refactor all pages around recent runs and named selectors | pending | Daily test throughput and workflow resumption | per-page focused tests + responsive browser smoke |
| 47.14 Final eval and acceptance | pending | Prove quality gains and provider fallback | full focused suites + RAG eval fixture + `git diff --check` |

## First Implementation Boundary

The first code task after contract promotion is Task 47.2, not pgvector. The
current local database is unversioned and missing current columns; adding new
tables before a safe preflight would make final RAG impossible to accept on the
actual local-first upgrade path.

Task 47.2 expected files:

```text
backend/app/db or backend/app/bootstrap.py
backend/app/tests/db/*preflight*
backend/app/tests/api/test_local_bootstrap.py
backend/alembic/* only when the diagnostic contract proves the baseline
docs/contracts/* when implementation evidence refines the upgrade contract
```

Task 47.2 command:

```powershell
backend\.venv\Scripts\python.exe -m backend.app.db_preflight --database-path storage/chtest-dev.db --json
```

The command opens the source with SQLite read-only/query-only settings, reports
the current Alembic heads, required GeneratedCaseCandidate columns, and built-in
PromptVersion drift, and records source fingerprints before and after the run.
`--copy-to <new-path>` creates a consistent SQLite backup at an explicit path,
refuses overwrite, inspects only that copy, and recommends `alembic current`
instead of an upgrade when the baseline is unknown.

## Non-Goals

- No generic chat knowledge base.
- No unreviewed knowledge or feedback entering CaseGeneration.
- No hidden indexing on synchronous case generation requests.
- No automatic source database mutation without backup/preflight evidence.
- No provider-specific schema in Chtest public APIs or core models.
- No Qdrant service requirement for the local-first default.
- No automatic approval based only on vector score or model confidence.

## Acceptance Metrics

- Ingestion completion/partial-failure rate and retry success.
- Knowledge evidence precision and required-card recall.
- Required, boundary, exception, permission, state, channel, and historical-risk
  case coverage.
- Duplicate/hallucination rate and evidence completeness.
- Human acceptance/edit/rejection rates.
- Automation readiness and first-run pass rate.
- Retrieval latency, fallback rate, stale-index rate, and provider failure rate.
- Median clicks/time to resume a run and trace a failed conclusion to artifacts.
