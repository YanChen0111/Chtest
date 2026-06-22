# Chtest Memory Index

This directory is the long-term memory for Chtest. Read it before every new AI development session and update it at the end of each session.

The purpose is to let long-running vibe coding continue from stable project facts instead of transient chat context.

## One-Sentence Product Definition

Chtest V1 is an AI testing evidence workbench for individual test engineers and automation test engineers.

It uses ideas from WHartTest's AI testing workflow and MeterSphere's case review, test asset, and report experience. It helps one engineer turn requirements and local code changes into reviewed, sandbox-executed, evidence-backed, and quality-measured testing assets.

Chtest is not an enterprise collaboration test management platform. V1 focuses on personal testing design and automation productivity. The long-term direction is a small-team AI testing workbench plus Agent/Skill/MCP testing tool ecosystem.

## V1 Loops

The first release spine is `docs/fixtures/00-v1-demo-path.md`: Requirement -> AI review -> candidate case -> human review -> AutomationDraft -> approval -> runner execution -> artifacts -> evidence report.

1. Requirement to cases: Requirement -> AI requirement review -> AI case generation -> human review -> case library.
2. Case to automation: Requirement/TestCase -> AI AutomationDraft -> approval -> pytest/Playwright execution -> report.
3. Code to quality: Local Git diff -> AI UnitTestPatch -> approval -> pytest regression -> quality conclusion.

The first and second loops are mainlines. The third loop is a support workflow.

## V1 Hard Constraints

- Single-user mode: one default user and one default workspace.
- PostgreSQL + Redis are the default infrastructure.
- Frozen stack: FastAPI, SQLAlchemy 2, Pydantic v2, Alembic, Vue 3, Arco Design Vue, Redis + RQ, Docker Compose.
- RAG is not built in; only KnowledgeAdapter is provided.
- Lightweight ContextArtifact inputs come before full RAG; AI tasks must record used context artifact ids or an explicit empty list.
- AI-generated cases must enter a review window before becoming TestCase records.
- AutomationDraft must be approved before execution and cannot directly write target repositories.
- Approved AutomationDraft execution uses Chtest artifact runtime copies, not direct writes into the target repository.
- Runner sandbox is a V1 safety boundary: TestRun must record runtime manifest, dependency snapshot, environment snapshot, network setting, and artifact trace.
- `docker_runner` is the preferred product acceptance runner when available; `local_subprocess` is a development fallback.
- Failed AutomationDraft execution can enter an evidence-driven repair loop, but repair candidates remain review-gated.
- UnitTestPatch must be approved before application and can only write test directories.
- AI cannot automatically modify business source files.
- AI quality metrics must track generation count, acceptance rate, rejection rate, edit rate, execution pass rate, and failure reason distribution.
- Mock-provider eval bench must track schema_valid_rate, evidence_complete_rate, unsafe_output_rate, usefulness, first-run pass, manual edit, and repair success signals.
- Git Quality Center is a support page for local diff, unit test generation, regression execution, and quality reports.
- Agent orchestrates workflows; Prompt constrains output; Skill stores testing methods; Tool Adapter/MCP handles tool calls.
- Reference framework source is local study material and is excluded from the Chtest repository commit set.

## Required Reading Before Development

Full order:

1. `README.md`
2. `00-ai-session-protocol.md`
3. `13-ai-readable-project-brief.md`
4. `01-product-prd.md`
5. `02-platform-spec.md`
6. `03-tech-stack.md`
7. `04-project-constraints.md`
8. `05-roadmap.md`
9. `06-architecture-decisions.md`
10. `07-dev-log.md`
11. `08-session-handoff.md`
12. `09-reference-framework-review.md`
13. `10-superpowers-review.md`
14. `11-implementation-slices.md`
15. `12-agent-mcp-skill-design.md`

Required docs:

1. `docs/product/01-positioning-and-scope.md`
2. `docs/contracts/01-data-model-contract.md`
3. `docs/contracts/02-api-contract.md`
4. `docs/contracts/03-state-machines.md`
5. `docs/contracts/04-artifact-contract.md`
6. `docs/contracts/05-prompt-skill-contract.md`
7. `docs/contracts/06-error-code-contract.md`
8. `docs/contracts/07-seed-data-contract.md`
9. `docs/contracts/08-mock-provider-contract.md`
10. `docs/implementation/01-v1-development-process.md`
11. `docs/implementation/02-v1-slice-plan.md`
12. `docs/implementation/04-ai-vibecoding-governance.md`
13. `docs/product/07-ai-testing-evidence-workbench-optimization.md`
14. `docs/product/06-frontend-ui-guidelines.md` when implementing frontend views

Task-specific fixtures:

- V1 minimum demo: `docs/fixtures/00-v1-demo-path.md`
- Requirement to cases: `docs/fixtures/01-golden-requirement-to-case.md`
- Case to automation: `docs/fixtures/02-golden-case-to-playwright.md`
- Git quality: `docs/fixtures/03-golden-git-quality.md`

Minimum reading set under tight context:

1. `README.md`
2. `13-ai-readable-project-brief.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `11-implementation-slices.md`
8. `08-session-handoff.md`

## Canonical Source Of Truth

When documents disagree, follow this order:

1. `docs/product/01-positioning-and-scope.md`.
2. `docs/contracts/*`.
3. `docs/implementation/04-ai-vibecoding-governance.md`.
4. `docs/implementation/01-v1-delivery-plan.md`.
5. `memory/13-ai-readable-project-brief.md`.
6. `docs/fixtures/*`.
7. `docs/architecture/*`.
8. `docs/reference/*`, `docs/reviews/*`, and `docs/superpowers/*`.

## Update Rules After Development

Always update:

- `07-dev-log.md`: completed work, verification, open items, risk/blocker.
- `08-session-handoff.md`: next session reading order, current state, next step, user confirmations.

Update related files when scope changes:

- Product target or scope: `01-product-prd.md` and `docs/product/*`.
- Architecture or modules: `02-platform-spec.md` and `docs/architecture/*`.
- Technology stack: `03-tech-stack.md` and `docs/architecture/03-implementation-technology.md`.
- Hard constraints: `04-project-constraints.md`.
- Roadmap: `05-roadmap.md`, `docs/implementation/01-v1-delivery-plan.md`, `docs/implementation/02-v1-slice-plan.md`.
- Data/API/state changes: `docs/contracts/*`.
- Golden Path changes: `docs/fixtures/*`.
- Agent/MCP/Skill/Prompt changes: `12-agent-mcp-skill-design.md` and `docs/contracts/05-prompt-skill-contract.md`.
- Evidence-loop strategy changes: `docs/product/07-ai-testing-evidence-workbench-optimization.md`.

## Memory File Roles

| File | Role |
|---|---|
| `00-ai-session-protocol.md` | AI start/finish protocol |
| `01-product-prd.md` | Product goal, users, scenarios, scope, acceptance |
| `02-platform-spec.md` | Platform architecture, modules, flows, data model |
| `03-tech-stack.md` | Technical stack and replacement choices |
| `04-project-constraints.md` | Safety, scope, environment, AI generation, RAG constraints |
| `05-roadmap.md` | V1 plan and later roadmap |
| `06-architecture-decisions.md` | Architecture decision records |
| `07-dev-log.md` | Development log |
| `08-session-handoff.md` | Continuation note for next session |
| `09-reference-framework-review.md` | WHartTest and MeterSphere reference review |
| `10-superpowers-review.md` | Feasibility and delivery strategy review |
| `11-implementation-slices.md` | Implementation slices for AI-assisted development |
| `12-agent-mcp-skill-design.md` | Agent/MCP/Skill/Prompt/RAG adapter design |
| `13-ai-readable-project-brief.md` | Compact project brief for AI context recovery |

## Official Docs

- Docs entry: `docs/README.md`
- Positioning: `docs/product/01-positioning-and-scope.md`
- Product PRD: `docs/product/02-v1-product-prd.md`
- Page PRD: `docs/product/03-user-journey-and-page-prd.md`
- AI metrics: `docs/product/04-ai-quality-metrics.md`
- Version boundaries: `docs/product/05-non-goals-and-version-boundaries.md`
- Frontend UI guidelines: `docs/product/06-frontend-ui-guidelines.md`
- Evidence workbench optimization: `docs/product/07-ai-testing-evidence-workbench-optimization.md`
- Data model contract: `docs/contracts/01-data-model-contract.md`
- API contract: `docs/contracts/02-api-contract.md`
- State machines: `docs/contracts/03-state-machines.md`
- Artifact contract: `docs/contracts/04-artifact-contract.md`
- Prompt/Skill contract: `docs/contracts/05-prompt-skill-contract.md`
- Error code contract: `docs/contracts/06-error-code-contract.md`
- Seed data contract: `docs/contracts/07-seed-data-contract.md`
- Mock provider contract: `docs/contracts/08-mock-provider-contract.md`
- Golden Path 0: `docs/fixtures/00-v1-demo-path.md`
- Golden Path 1: `docs/fixtures/01-golden-requirement-to-case.md`
- Golden Path 2: `docs/fixtures/02-golden-case-to-playwright.md`
- Golden Path 3: `docs/fixtures/03-golden-git-quality.md`
- Platform architecture: `docs/architecture/01-platform-architecture.md`
- Agent summary: `docs/architecture/02-agent-mcp-skill-prompt.md`
- Technical guide: `docs/architecture/03-implementation-technology.md`
- Agent workflow: `docs/architecture/04-agent-workflow-design.md`
- Git Quality design: `docs/architecture/05-git-quality-center-design.md`
- Development process: `docs/implementation/01-v1-development-process.md`
- Delivery plan: `docs/implementation/01-v1-delivery-plan.md`
- Slice plan: `docs/implementation/02-v1-slice-plan.md`
- Slice 1 Task plan: `docs/implementation/slices/slice-01-platform-foundation.md`
- Slice 2 Task plan: `docs/implementation/slices/slice-02-backend-core.md`
- Slice 2.5 Task plan: `docs/implementation/slices/slice-02-frontend-foundation.md`
- Slice 3 Task plan: `docs/implementation/slices/slice-03-project-core.md`
- Slice 4 Task plan: `docs/implementation/slices/slice-04-ai-runtime-core.md`
- Slice 5 Task plan: `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- Testing acceptance: `docs/implementation/03-testing-and-acceptance.md`
- AI vibecoding governance: `docs/implementation/04-ai-vibecoding-governance.md`
- Docker environment: `docs/deployment/01-docker-environment.md`
- Roadmap: `docs/roadmap/01-implementation-roadmap.md`
- Project review: `docs/reviews/2026-06-18-project-review.md`

## Repositories And References

- Target repo: `https://github.com/2696437448-cmyk/Chtest`
- Local project directory: `/Users/yanchen/VscodeProject/Chtest`
- Reference directory: `/Users/yanchen/VscodeProject/Chtest/参考框架/`
- WHartTest source: `/Users/yanchen/VscodeProject/Chtest/参考框架/WHartTest`, reference commit `927bff2`
- MeterSphere source: `/Users/yanchen/VscodeProject/Chtest/参考框架/metersphere`, reference commit `5dc6df5`

## Current State

- Phase: V1 implementation-ready documentation, contracts, Golden Paths, and Slice 1-5 Task plans are complete, including Slice 2.5 Frontend Foundation.
- Focus: start Slice 1 Task 1, then proceed through Slice 1, Slice 2, Slice 2.5, and Slice 3 with Task-level verification and commits.
- Principle: real, maintainable, extensible implementation; no throwaway demo and no enterprise collaboration platform.
- Latest P0 optimization: Strategy B evidence-loop-first delivery, runner sandbox, ContextArtifact trace, mock-provider eval bench, AutomationDraft repair loop, AutomationQualityMetric, and Golden Path product value checks are now part of the current docs.

## Implementation Principles

- Use WHartTest AI/MCP/Skills/Agent, generated case modal, review status, optimization review, and executor ideas as primary references.
- Use MeterSphere case review, pass-rate progress, test asset governance, and report views as supporting references.
- Use a modular monolith with Redis queue and PostgreSQL storage.
- Keep RAG as an adapter until an external RAG service is available.
- Use Internal Git Tool Adapter first; GitHub MCP is a later integration.
- Each module must be runnable, verifiable, committed, and easy to roll back. Update memory after every iteration.
- Every completed Task follows `docs/implementation/04-ai-vibecoding-governance.md`: focused verification, git diff self-review, and commit.
- Memory update policy: Task-level progress is mainly recorded by git; Slice completion and major context changes must update memory.
- Git records code history. Memory records session continuity. Contracts record implementation truth.
