# Chtest Frontend UI Guidelines

## 1. Purpose

This document gives V1 frontend implementation guidance so vibe coding produces a serious testing workbench instead of a generic enterprise admin template.

Chtest is a personal AI testing design and automation workbench. The UI should help one tester quickly review AI output, approve safe actions, inspect evidence, and continue the three product loops.

## 1.1 User-Facing Language

- All visible page titles, navigation labels, buttons, empty states, table headers, and helper copy should be Chinese-first.
- Keep technical English only when the term is a product contract, code symbol, or industry term that would be more precise in English, such as `Prompt`, `Skill`, `Playwright`, `MCP`, or `TestCommand`.
- The following user-facing contract names must be rendered in Chinese in the UI:
  - `ContextArtifact` -> `上下文工件`
  - `AITask` -> `AI 任务`
  - `LLMCallLog` -> `大模型调用日志`
  - `Artifact` -> `工件`
- Technical identifiers can remain in code, API payloads, and logs, but visible labels must prefer Chinese text.

## 2. Design Direction

- Workbench-first, not landing-page-first.
- Dense but readable, not decorative.
- Workflow and evidence centered, not organization-management centered.
- Tables, drawers, split panes, status strips, and reports are the default primitives.
- Cards are only for repeated summary items or focused panels, not for wrapping every section.

## 3. Navigation

Primary navigation should follow V1 work:

1. AI 工作台.
2. 需求评审.
3. 用例生成评审.
4. 用例库和测试套件.
5. 自动化草稿中心.
6. 执行中心.
7. CI/CD 质量中心.
8. 报告中心.
9. RAG 知识库.
10. Prompt / Skill 中心.
11. 工具适配器 / MCP 中心.
12. 设置.

`CI/CD 质量中心` is the user-facing page name for the local diff, UnitTestPatch, regression, and quality report workflow. Current technical contract names are `CICDRun`, `CICDChangedFile`, `CICDChangeAnalysisAgent`, and `UnitTestPatch`.

`RAG 知识库` is a ContextArtifact and KnowledgeAdapter management surface. It must not imply that V1 has built-in vector indexing, embeddings, chunking, or reranking.

Do not add enterprise navigation such as departments, members, roles, permissions, SSO, audit center, or tenant management in V1.

## 4. Page Layout Rules

- Use a persistent left navigation and a compact top status/action bar.
- Use tables for scan-heavy lists: tasks, candidates, cases, drafts, runs, reports.
- Use drawers for detail review: candidate case detail, AutomationDraft detail, patch detail, TestRun artifacts.
- Use split panes when comparing source and AI output: requirement vs review, case vs draft, diff vs patch.
- Keep primary actions close to review surfaces: approve, edit, reject, request optimization, run, generate report.
- Long-running tasks must show status, stage, elapsed time, Agent, Prompt/Skill, and model.

## 5. Review Surfaces

AI-generated content must be visually reviewable before promotion:

- GeneratedCaseCandidate review shows steps, expected results, requirement references, risk references, AI reason, and duplicate warning.
- AutomationDraft review shows code, suggested file path, execution notes, risk notes, Prompt/Skill version, and approval state.
- CI/CD 质量中心中的 UnitTestPatch review shows unified diff, affected paths, PatchScopeGate result, test intent, and coverage target.

Use explicit state tags for pending review, approved, edited, rejected, needs optimization, approval required, running, passed, failed, error, timeout.

## 6. Evidence Display

Reports and failed executions must show evidence before AI explanation:

- TestRun aggregate counts.
- stdout/stderr links.
- JUnit/coverage/trace/screenshot artifacts.
- FailureAnalysis classification and confidence.
- Evidence manifest and missing evidence.

If evidence is missing, the page should show `insufficient_evidence` or `needs_attention`, not a confident pass/fail story.

## 7. Visual Style

- Use Arco Design Vue components as the baseline.
- Use the approved A direction: shallow light page background, white content surfaces, compact spacing, and clear status colors.
- Prefer `#f5f7fa` / `#f7f8fa` page backgrounds, `#ffffff` surfaces, `#e5e6eb` borders, `#165dff` primary actions, `#00b42a` evidence/pass/safe states, `#f53f3f` fail/reject states, and `#ff7d00` pending/warning states.
- Avoid marketing heroes, oversized illustrations, decorative gradients, and dashboard vanity charts.
- Use icons for common actions when available: run, approve, reject, edit, report, artifact, refresh.
- Keep typography practical: page headings modest, table content scannable, code blocks readable.
- Reference WHartTest for Vue/Arco generation and review patterns, and MeterSphere for dense test asset management patterns. Do not migrate V1 away from Vue 3 + Arco Design Vue.

## 8. V1 Frontend Non-Goals

- No team management UI.
- No RBAC/permission pages.
- No plugin marketplace UI.
- No full low-code UI automation designer.
- No marketing home page.
- No large analytics cockpit before the three Golden Paths work.
- No built-in RAG/vector/rerank UI beyond the RAG 知识库 management surface.

## 9. Acceptance Check

A V1 frontend screen is acceptable when a single tester can answer:

- What needs my review?
- What did AI generate?
- What evidence supports this result?
- What can I safely approve or run next?
- Which Prompt/Skill/model produced this output?
