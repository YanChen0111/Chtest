# Chtest Documentation

Chtest V1 is an AI Testing Workbench for individual test engineers and automation test engineers. It improves testing efficiency and quality across requirement review, case generation, case review, automation draft generation, controlled execution, failure analysis, and report generation.

V1 focuses on three loops:

1. Requirement -> AI requirement review -> AI case generation -> human review -> case library.
2. Requirement/TestCase -> AI AutomationDraft -> approval -> pytest/Playwright execution -> report.
3. Local Git diff -> AI UnitTestPatch -> approval -> pytest regression -> quality conclusion.

The first and second loops are the product mainlines. The Git loop is a support workflow.

## Canonical Source Of Truth

When documents disagree, follow this order:

1. `product/01-positioning-and-scope.md`.
2. `contracts/*`.
3. `implementation/04-ai-vibecoding-governance.md`.
4. `implementation/01-v1-delivery-plan.md`.
4. `../memory/13-ai-readable-project-brief.md`.
5. `fixtures/*`.
6. `architecture/*`.
7. `reference/*`, `reviews/*`, and `superpowers/*`.

## Documentation Entry Points

| Directory | Purpose |
|---|---|
| `product/` | Product positioning, PRD, page PRD, AI metrics, version boundaries |
| `architecture/` | Platform architecture, Agent/MCP/Skill/Prompt design, Git Quality design |
| `contracts/` | Data model, API, state machine, artifact, Prompt/Skill contracts |
| `fixtures/` | Golden Path standard inputs and expected outputs |
| `implementation/` | V1 delivery plan, development process, slice plan, acceptance |
| `deployment/` | Docker, environment, startup, and operation constraints |
| `reference/` | WHartTest and MeterSphere migration map |
| `roadmap/` | Phase roadmap and agile slices |
| `reviews/` | Architecture, feasibility, and risk review |
| `superpowers/` | Design, plan, and review docs for structured AI development |
| `../memory/` | Long-term AI context and session handoff |

## Recommended Reading Order

1. `../memory/README.md`
2. `../memory/13-ai-readable-project-brief.md`
3. `product/01-positioning-and-scope.md`
4. `product/02-v1-product-prd.md`
5. `contracts/01-data-model-contract.md`
6. `contracts/02-api-contract.md`
7. `contracts/03-state-machines.md`
8. `contracts/04-artifact-contract.md`
9. `contracts/05-prompt-skill-contract.md`
10. `contracts/06-error-code-contract.md`
11. `contracts/07-seed-data-contract.md`
12. `contracts/08-mock-provider-contract.md`
13. `fixtures/00-v1-demo-path.md`
14. `fixtures/01-golden-requirement-to-case.md`
15. `fixtures/02-golden-case-to-playwright.md`
16. `fixtures/03-golden-git-quality.md`
17. `implementation/01-v1-development-process.md`
18. `implementation/02-v1-slice-plan.md`
19. `implementation/03-testing-and-acceptance.md`
20. `implementation/04-ai-vibecoding-governance.md`

## V1 Hard Constraints

- Single-user mode; no RBAC, multi-tenant, or enterprise collaboration.
- PostgreSQL + Redis + Docker Compose from the first release.
- Frozen V1 stack: FastAPI, SQLAlchemy 2, Pydantic v2, Alembic, Vue 3, Arco Design Vue, Redis + RQ.
- RAG is not built in; only KnowledgeAdapter is provided.
- MCP is not a V1 dependency; Internal Tool Adapter comes first.
- Git Quality Center is a support workflow and must not overtake the requirement-to-automation mainlines.
- V1 priority tools: TestRunner/pytest and Playwright minimal loop.
- Newman after V1 core loop; JMeter after execution/report parsing is stable; Appium and traffic capture are roadmap capabilities.
- AI-generated cases require review before entering the case library.
- AI-generated AutomationDraft requires approval before execution.
- AI-generated UnitTestPatch requires approval and can only write test directories.

## Document List

### Product

- `product/01-positioning-and-scope.md`: Positioning, scope, and main workflows.
- `product/02-v1-product-prd.md`: Detailed product PRD.
- `product/03-user-journey-and-page-prd.md`: User journey and page-level PRD.
- `product/04-ai-quality-metrics.md`: AI quality metrics.
- `product/05-non-goals-and-version-boundaries.md`: Non-goals and version boundaries.

### Contracts

- `contracts/01-data-model-contract.md`: Field-level data model contract.
- `contracts/02-api-contract.md`: Core API request/response contract.
- `contracts/03-state-machines.md`: State machines and allowed transitions.
- `contracts/04-artifact-contract.md`: Artifact path, type, metadata, and evidence manifest.
- `contracts/05-prompt-skill-contract.md`: Prompt/Skill file format, versioning, and output rules.
- `contracts/06-error-code-contract.md`: Stable API error codes.
- `contracts/07-seed-data-contract.md`: Required deterministic seed data.
- `contracts/08-mock-provider-contract.md`: Deterministic mock provider behavior.

### Fixtures

- `fixtures/00-v1-demo-path.md`: V1 minimum demo path.
- `fixtures/01-golden-requirement-to-case.md`: Requirement to cases.
- `fixtures/02-golden-case-to-playwright.md`: TestCase to pytest/Playwright.
- `fixtures/03-golden-git-quality.md`: Git diff to quality report.

### Architecture

- `architecture/01-platform-architecture.md`: Platform architecture.
- `architecture/02-agent-mcp-skill-prompt.md`: Agent/MCP/Skill/Prompt summary.
- `architecture/03-implementation-technology.md`: Technical implementation guide.
- `architecture/04-agent-workflow-design.md`: Detailed Agent workflow design.
- `architecture/05-git-quality-center-design.md`: Git Quality Center design.

### Implementation And Operation

- `implementation/01-v1-development-process.md`: V1 development process.
- `implementation/01-v1-delivery-plan.md`: V1 delivery plan.
- `implementation/02-v1-slice-plan.md`: V1 slice plan.
- `implementation/slices/slice-01-platform-foundation.md`: Slice 1 Task plan.
- `implementation/slices/slice-02-backend-core.md`: Slice 2 Task plan.
- `implementation/03-testing-and-acceptance.md`: Testing and acceptance.
- `implementation/04-ai-vibecoding-governance.md`: AI development governance, Task loop, testing, commit, rollback, and handoff rules.
- `deployment/01-docker-environment.md`: Docker and environment control.
- `roadmap/01-implementation-roadmap.md`: Implementation roadmap.
- `reference/01-open-source-migration-map.md`: Open-source reference migration map.

## Next Step

Start Slice 1 Task 1: initialize platform directories according to `implementation/slices/slice-01-platform-foundation.md`.
