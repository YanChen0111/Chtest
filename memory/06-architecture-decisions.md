# Architecture Decisions

## Purpose

This document records the current architecture decisions for Chtest V1. It is written as implementation guidance for future AI sessions and developers.

## ADR-0001: Use A Modular Monolith For V1

Decision: Chtest V1 uses a modular monolith backend with FastAPI, PostgreSQL, Redis, and worker processes.

Reason: The product needs fast iteration, clear module boundaries, and low operational complexity. A modular monolith is easier to build and maintain than microservices for a single-user local-first tool.

Implementation:

- Backend modules: project, requirement, case, automation, execution, git_quality, ai_runtime, report, artifact.
- Module boundaries are enforced by service interfaces and database contracts.
- Workers handle AI tasks and tool execution.

## ADR-0002: Use Single-User Mode First

Decision: V1 runs in single-user mode with default workspace and default user.

Reason: The first product value is personal testing productivity. Multi-user collaboration adds permission, audit, notification, and organization complexity that does not improve V1 learning speed.

Implementation:

- Tables keep `created_by` and `updated_by` fields.
- API uses default user internally.
- No login or RBAC in V1.

## ADR-0003: Use PostgreSQL And Redis From Day One

Decision: V1 uses PostgreSQL for persistent data and Redis for queue/cache/runtime coordination.

Reason: The data model includes review states, execution records, artifacts, AI tasks, and reports. PostgreSQL gives reliable relational contracts; Redis keeps async execution simple.

Implementation:

- Docker Compose starts PostgreSQL and Redis.
- Local development uses migrations.
- Worker queue defaults to RQ or equivalent lightweight Redis queue.

## ADR-0004: Keep RAG As An Adapter Interface

Decision: V1 does not build RAG indexing, vector storage, chunking, or reranking. It only defines KnowledgeAdapter.

Reason: Requirement review and case generation must work without a knowledge base. RAG can be connected later without changing Agent contracts.

Implementation:

- `KnowledgeAdapter.search_context()` returns evidence list.
- Default provider returns `used_knowledge=false` and empty evidence.
- AI output schema always records whether evidence was used.

## ADR-0005: Human Review Is Mandatory For AI Assets

Decision: GeneratedCaseCandidate, AutomationDraft, and UnitTestPatch must pass human review before becoming official assets or being applied.

Reason: The product relies on AI for speed, but test quality depends on human control at key checkpoints.

Implementation:

- Candidate cases cannot directly become TestCase.
- AutomationDraft cannot execute until approved.
- UnitTestPatch cannot apply until approved and scope-validated.

## ADR-0006: AI Quality Metrics Are First-Class

Decision: Chtest records acceptance rate, edit rate, rejection reason, first-run pass rate, schema validation pass rate, failure classifications, prompt version, and skill version.

Reason: The product goal is not just generating content. It must prove whether AI improves quality and efficiency.

Implementation:

- Every AITask binds PromptVersion and SkillVersion.
- Review actions update metrics.
- Reports expose AI effectiveness data.

## ADR-0007: Reference Frameworks Are Design Inputs Only

Decision: WHartTest and MeterSphere are used as design references. Chtest does not depend on their runtime code in V1.

Reason: Chtest needs a smaller, single-user, AI-first architecture. Directly mixing large external platform code would raise maintenance cost.

Implementation:

- Reference source remains under `参考框架/` locally.
- `.gitignore` excludes `参考框架/`.
- Migration decisions are recorded in `docs/reference/01-open-source-migration-map.md`.

## ADR-0008: Use Vue 3 + Arco Design For Frontend

Decision: Frontend uses Vue 3, TypeScript, Vite, Pinia, Vue Router, and Arco Design Vue.

Reason: This stack is productive for data-heavy workbench screens and matches the requested platform-style UI.

Implementation:

- No marketing landing page.
- First screen is the actual workbench.
- UI centers on review queues, structured editors, execution status, and reports.

## ADR-0009: Use Controlled Tool Adapter Before MCP

Decision: V1 implements internal ToolDefinition and ToolInvocation first. MCP is connected later through the same contract.

Reason: Local test execution and artifact parsing need strict allowlists, timeouts, and approval gates. Internal adapters are easier to harden before exposing MCP servers.

Implementation:

- ToolDefinition describes risk, approval, timeout, allowlist, and schemas.
- ToolInvocation records every call and artifact.
- Future MCP tools map into ToolDefinition.

## ADR-0010: Final Product Positioning

Decision: Chtest V1 is an AI Testing Workbench for individual test engineers and automation test engineers.

Reason: This positioning keeps the first release focused on the highest-value personal testing loops and avoids unnecessary enterprise collaboration complexity.

Implementation:

- Mainline A: requirement review to reviewed test cases.
- Mainline B: reviewed case to automation draft, execution, failure analysis, and report.
- Support workflow: local Git diff to scoped unit test patch and regression conclusion.

## ADR-0011: Tool Priority For V1

Decision: V1 implements pytest TestRunner first, then Playwright smoke execution. Newman and JMeter are later tool adapters using the same ToolDefinition and artifact contracts.

Reason: pytest gives the fastest real execution loop for unit/API/service tests. Playwright covers practical UI automation. Newman and JMeter add value after the execution/report foundation is stable.

Implementation:

- P0: pytest TestRunner, JUnit parsing, stdout/stderr artifacts.
- P0: Git diff reader and patch scope validator.
- P1: Playwright smoke execution with screenshot and trace artifacts.
- Later: Newman and JMeter adapters.

## ADR-0012: AutomationDraft Is A Core Entity

Decision: AutomationDraft is a core V1 entity, not an optional report field.

Reason: The product must bridge manual/AI-designed cases and executable automation. A dedicated entity gives review, versioning, approval, execution, and quality metrics a stable home.

Implementation:

- AutomationDraft can be created from TestCase or Requirement.
- AutomationDraft stores draft code, framework, suggested path, execution notes, and risk notes.
- AutomationDraft requires review before execution.

## ADR-0013: Git Quality Is A Support Workflow

Decision: Git Quality is included in V1 as a support workflow, not the main product path.

Reason: The user wants push/diff-driven unit test generation and regression support, but the core product value is AI-assisted testing lifecycle work.

Implementation:

- Git diff analysis generates GitChangeSet and GitChangedFile.
- UnitTestPatch is approval-gated and test-directory scoped.
- RegressionAgent recommends commands and explains selection.

## ADR-0014: Final Documentation Priority

Decision: Future implementation follows the documentation priority declared in `docs/product/01-positioning-and-scope.md`.

Reason: Long-running AI development needs stable source-of-truth ordering.

Implementation:

- Product positioning defines scope.
- Contracts define data/API/state names.
- Implementation plan defines delivery order.
- Memory documents preserve active context for the next AI session.
