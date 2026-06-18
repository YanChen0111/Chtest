# Chtest Planning Review

## Verdict

Chtest V1 is feasible and worth building if implementation stays focused on an AI Testing Workbench for individual test engineers and automation test engineers.

The product should proceed to implementation. The next milestone is not more strategy writing; it is a runnable Docker + FastAPI + PostgreSQL + Redis + worker + Vue foundation.

## Strengths

- Scope is single-user and local-first.
- Infrastructure is realistic: PostgreSQL, Redis, Docker Compose, FastAPI, Vue, worker.
- AI output is controlled by review windows, schema validation, artifacts, and quality metrics.
- AutomationDraft gives the product a clear bridge from test design to execution.
- Tool Adapter first and MCP later is the right safety boundary.
- RAG is limited to KnowledgeAdapter, avoiding early infrastructure drag.
- WHartTest and MeterSphere are used as capability references, not runtime dependencies.

## Required Implementation Focus

### P0: Build Runnable Infrastructure First

Create the platform skeleton before adding AI complexity: Docker Compose, backend health/ready, database migration, worker ping, frontend shell, and default user/workspace.

### P0: Implement Contracts Before Screens Grow

Data model, API, state machines, artifacts, Prompt/Skill contracts, and ToolDefinition must be implemented early so screens do not invent incompatible fields.

### P0: Make AutomationDraft A First-Class Path

Requirement/case to automation is a main product path. AutomationDraft must include generation, review, edit, approval, execution, TestRun/TestResult, FailureAnalysis, and Report.

### P1: Keep Git Quality As Support Workflow

Git Quality is valuable, but it should not block the main requirement-to-automation loop. Build it after AI runtime, case review, and pytest execution are stable.

### P1: Keep Tool Execution Safe

Before broad execution, implement allowlists, timeouts, approval policy, artifact capture, and ToolInvocation logs.

## Risk Review

| Risk | Control |
|---|---|
| Scope expands into enterprise test management | Keep V1 single-user and workbench-focused |
| AI output quality is unstable | Require schema validation, human review, quality metrics, and Prompt/Skill versioning |
| Tool execution creates safety risk | Use ToolDefinition allowlist, risk level, timeout, approval, and artifact logs |
| Automation draft cannot run in real projects | Store execution notes, fixture assumptions, risk notes, and require review |
| Unit test patch modifies source code | Enforce PatchScopeGate and approval before apply |
| RAG delays delivery | Keep KnowledgeAdapter empty until external RAG exists |
| MCP delays delivery | Build Internal Tool Adapter first |

## Recommendation

Proceed with Batch 1 and Batch 2 immediately. After the platform skeleton and Project Settings are working, implement AI Runtime, Requirement Review, Case Generation Review, AutomationDraft, pytest execution, FailureAnalysis, and reports in that order.
