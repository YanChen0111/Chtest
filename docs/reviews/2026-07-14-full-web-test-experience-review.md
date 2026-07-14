# Full Web Test Experience Review

Date: 2026-07-14

## Review Goal

Review every current Chtest web route from the perspective of an individual
test engineer. The review prioritizes test throughput, test quality, logs,
evidence traceability, and daily operational clarity over decorative redesign.

## Cross-Product Findings

### P0: No Unified Run And Evidence Trace

Evidence exists in AITask, LLMCallLog, ReviewHistory, Artifact, TestRun,
FailureAnalysis, Report, and knowledge retrieval records, but users cannot start
from one business entity and traverse the complete chain.

Required change:

- Add a unified evidence trace drawer/page available from requirement, generated
  case, TestCase, automation draft, TestRun, failure, report, and knowledge card.
- Show stage, status, time, correlation id, safe summary, and Artifact links.
- Add global search for entity id, requirement number, case title, TestRun id,
  error code, and artifact sha256.

Why: log storage without correlation does not reduce diagnosis time or prove why
a test conclusion is trustworthy.

### P0: Pages Cannot Reliably Resume Previous Work

Most workflow pages start from a new form or default id. Recent runs, filters,
saved selections, and incomplete work are missing or scattered.

Required change:

- Each operational page needs a compact recent-run list with status filters,
  updated time, owner/source, and resume action.
- Replace remaining raw UUID inputs with searchable entity selectors.
- Persist view filters and selected records per project.

Why: testers repeat the same navigation and id-copy work many times per day;
resume-first design directly improves throughput and reduces wrong-asset errors.

### P0: Local Runtime And Database Health Is Not Actionable

The running backend can be older than the frontend, and the local database can
have prompt-registry drift or missing migration state. Pages show generic red
alerts such as Internal Server Error or an empty alert bar.

Required change:

- Add a startup/readiness diagnostic surface: API version, schema revision,
  registry status, Artifact store path, provider health, runner availability.
- Convert backend errors into stable error code, safe explanation, affected
  capability, evidence link, and next action.

Why: a local-first tool must help the tester repair local state without reading
server logs or guessing which component is stale.

### P1: Navigation Reflects Features, Not Tester Workflow

The sidebar is a flat list and every item shows a low-value `就绪` tag. The main
path and support tools are not visually separated.

Required change:

- Group navigation into Test Design, Automation And Execution, Evidence And
  Quality, and Configuration.
- Replace repeated `就绪` tags with meaningful running/failed/review-needed
  badges only when counts are non-zero.
- Add a project-scoped command/search entry and recent entities.

Why: navigation should reduce decision time and surface outstanding work rather
than repeat static readiness text.

### P1: Page Density And Visual Hierarchy Are Inconsistent

Operational pages use large cards and empty states, while evidence-rich pages
can exceed several screen heights. The RAG page is over 3,000 px tall at first
load and Prompt/Skill exceeds 9,000 px.

Required change:

- Use tabs for distinct views, split panels for list/detail review, sticky
  action bars, compact status summaries, and pagination/virtualization.
- Keep raw code, manifests, schemas, and long evidence collapsed by default.
- Use semantic status colors consistently: neutral, running, review, blocked,
  failed, passed.

Why: testers scan and compare repeatedly; excessive vertical travel and equal
visual weight hide blockers and slow review.

## Page Findings

### AI Workbench

Keep: backend/model health, task counts, Artifact and LLM call tables.

Change:

- Add task search, agent/status/date filters, pagination, duration and error-code
  columns, and failure-first default sorting.
- Make every task row open a task detail drawer with request, context manifest,
  schema validation, response Artifact, related business entity, and retry link.
- Add correlation links from LLMCallLog and Artifact ids to unified trace.

Why: this should be the main AI execution log console, not a long static task
table.

### Requirement Review

Change:

- Add recent requirements/reviews and draft persistence.
- Replace ContextArtifact id text with searchable approved knowledge/context
  selection.
- Present findings in severity groups with resolve/defer decisions and a visible
  unresolved-risk count before document generation.
- Link each finding to its source evidence and later generated cases.

Why: RequirementReview is the first quality gate; unresolved ambiguity must be
managed, not only displayed.

### Case Generation Review

Keep: decision-table acknowledgement, task status, persisted coverage dimensions,
candidate list/detail separation.

Change:

- Hide advanced ids by default and expose them in trace details.
- Add candidate bulk triage, duplicate grouping, evidence completeness,
  CaseReviewAgent findings, coverage-gap summary, and automation-readiness
  filters.
- Add retry/cancel and generation comparison across prompt/model/knowledge
  versions.

Why: the main review question is which risks are still uncovered and which
candidates need human judgment, not which UUID was submitted.

### Test Case Library

Change:

- Add server-side filter/sort/pagination for module, priority, test type, risk,
  source, review status, automation readiness, and last execution result.
- Show requirement/risk coverage and evidence count in the list.
- Add bulk tag/module/automation-plan actions and compare versions.
- Add direct trace to source candidate, review history, executions, failures,
  and reports.

Why: the library should be the reusable testing asset catalog and regression
selection surface, not only a list/detail viewer.

### Automation Draft Center

Keep: named TestCase/TestCommand selection and four-stage workflow.

Change:

- Add recent plans/drafts and restore incomplete review.
- Replace hard-coded edit behavior with a real code editor/diff and structured
  review fields.
- Show automation-readiness blockers before generation, quality findings beside
  code, and execution evidence in a resizable lower panel.
- Add direct logs/trace links for plan AITask, draft AITask, review, and TestRun.

Why: automation review needs comparison and evidence, not a one-way generated
code display.

### Execution Pages

Change:

- Make Automation Draft the primary entry; keep standalone pages as run-history
  and diagnostics views.
- Replace remaining id fields with searchable approved drafts/commands.
- Add TestRun list with status, runner, duration, branch/commit, started time,
  failure class, report availability, and rerun action.
- Stream or poll run state automatically; expose stdout/stderr search and copy,
  artifact filters, and failure-result navigation.

Why: testers need fast rerun, comparison, and log diagnosis more often than a
blank launch form.

### CI/CD Quality Center

Change:

- Replace the tall card sequence with a stepper and sticky gate summary.
- Replace project/repository ids with configured selectors and local Git status.
- Show changed-file risk coverage, missing evidence, patch review, new-test and
  regression results in a single evidence matrix.
- Add run history, imported/local source distinction, recompute history, and
  unified trace.

Why: a gate is a decision surface; blockers and evidence completeness must be
visible without scrolling through every stage.

### Report And Failure Analysis

Change:

- Replace raw TestRun id with recent failed/run selector.
- Add report/failure history, failure filters, root-cause confidence, evidence
  completeness, and links to test result/log lines/artifacts.
- Add compare-runs and create BugPattern feedback proposal.

Why: failure analysis is primarily a diagnosis and learning workflow, not two
independent generation buttons.

### RAG Knowledge Workbench

Current problem: import, deterministic retrieval, card review, index, graph,
adapter, and MCP/tool information are mixed into one very long page. Metric
cards stack vertically and the first-screen alert can be visually empty.

Required final layout:

```text
Overview | Ingestion | Knowledge Cards | Retrieval Lab | Relationships | Feedback | Provider
```

- Overview: trusted-card count, pending review, stale/unsafe, index freshness,
  retrieval precision/latency, uncovered risk count, failed ingestion count.
- Ingestion: source-type chooser, run list, progress, parser result, retry, and
  evidence artifacts.
- Knowledge Cards: filterable list/detail review with source locator, diff,
  safety, duplicate target, confidence, and usage.
- Retrieval Lab: query/filter controls, score breakdown, source preview,
  provider/fallback state, and saved retrieval run.
- Relationships: impact/coverage query presets and evidence-backed graph/table.
- Feedback: proposed learning queue and two-stage review.
- Provider: KnowledgeAdapter capabilities, health, version, pgvector/Qdrant or
  Haystack/LlamaIndex configuration without secret display.

Why: these are different tester jobs and must not compete in one vertical page.

### Prompt / Skill Center

Change:

- Use tabs and version list/detail instead of rendering all content at once.
- Add agent/status search, schema diff, activation/deprecation history, eval
  result, and linked AI tasks.
- Collapse prompt/skill bodies and forbid raw secret-bearing examples.

Why: a 9,000 px page makes version comparison and governance unreliable.

### Project Settings

Change:

- Add setup checklist and readiness summary.
- Use CRUD dialogs/selectors for modules, repositories, environments, and test
  commands; empty tables need create actions.
- Separate model/provider secrets from project assets and expose test evidence
  for connection checks.
- Show schema/registry/runtime version diagnostics.

Why: configuration errors currently surface later as workflow failures; setup
should prevent them before testing starts.

## Delivery Priority

1. Local database/runtime diagnostic and safe migration path.
2. Unified run history, global search, and evidence trace.
3. Final RAG ingestion/cards/retrieval evidence contract and workbench.
4. Case review quality agents and coverage-gap workflow.
5. Execution/report run history and searchable logs.
6. Navigation and responsive density refactor across all pages.

