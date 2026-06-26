# Chtest Final Frontend Design Spec

## 1. Status

This document is the approved V1 frontend design spec as of 2026-06-26. It turns the final A direction into implementation guidance for later AI coding sessions.

It complements:

- `docs/product/03-user-journey-and-page-prd.md`
- `docs/product/06-frontend-ui-guidelines.md`
- `docs/reference/01-open-source-migration-map.md`

When implementing frontend pages, use this document for layout, visual language, page composition, and component behavior. Product behavior and data contracts still come from `docs/product/01-positioning-and-scope.md` and `docs/contracts/*`.

## 2. Design Read

Chtest V1 should feel like a light, professional AI testing evidence workbench for one test engineer or automation test engineer.

The UI is not a landing page, data wall, enterprise admin console, or decorative AI dashboard. It is a daily production tool for reviewing AI output, approving safe actions, inspecting evidence, and continuing test work.

Target visual direction:

- Arco Design Vue baseline.
- Light neutral surfaces.
- Compact workbench density.
- Tables, split panes, drawers, and status strips as the primary structure.
- Clear review states and evidence-first reporting.
- Chinese-first visible copy.

## 3. References And Migration Boundary

### 3.1 Libraries To Keep

V1 keeps the existing frontend stack:

- Vue 3.
- TypeScript.
- Vite.
- Arco Design Vue.
- Pinia.
- Vue Router.

Do not migrate V1 to shadcn/ui, Nuxt UI, Creative Tim, React, Next.js, Tailwind-only UI, or a new design system unless a later task explicitly changes the stack contract.

### 3.2 Open-Source UI References

Use these projects as references, not as a reason to change the stack:

| Reference | Use For | Boundary |
|---|---|---|
| WHartTest / WHartTest_Vue | AI case generation modal structure, test case review flow, knowledge selector, Arco-style Vue implementation patterns | MIT reference. Small adapted code patterns can be migrated with license notice and local refactor. |
| MeterSphere | Test asset management density, case table behavior, report organization, execution result surfaces | Do not copy source into Chtest because the license is not compatible for direct migration into this V1 codebase. Recreate interaction patterns only. |
| shadcn-ui/ui | Clean component rhythm, predictable form/table/dialog composition | Reference only. Do not introduce React/shadcn into V1. |
| nuxt/ui | Light application shell, command density, restrained tokens | Reference only. Do not migrate to Nuxt. |
| Creative Tim UI templates | Admin layout conventions and page composition examples | Reference only. Avoid marketing-card visuals. |

## 4. Visual Tokens

Use a shallow light palette. The UI should read as calm and technical, with restrained color and strong state clarity.

| Token | Value | Use |
|---|---|---|
| Page background | `#f5f7fa` or `#f7f8fa` | App background and outer shell |
| Surface | `#ffffff` | Main content surfaces, tables, forms, drawers |
| Soft surface | `#f2f3f5` | Toolbar background, selected nav, subtle grouping |
| Border | `#e5e6eb` | Dividers, table borders, panel borders |
| Text primary | `#1d2129` | Main readable text |
| Text secondary | `#4e5969` | Descriptions and metadata |
| Text tertiary | `#86909c` | Hints and less important timestamps |
| Disabled | `#c9cdd4` | Disabled actions and unreviewed secondary state |
| Primary blue | `#165dff` | Main actions, links, active navigation |
| Evidence green | `#00b42a` | Passed, approved, safe evidence, available knowledge |
| Risk red | `#f53f3f` | Failed, rejected, blocking risk |
| Pending amber | `#ff7d00` | Pending approval, needs optimization, warning |
| Info cyan | `#14c9c9` | Optional secondary technical status |

Rules:

- Use Arco status colors where possible, then map them to the tokens above.
- Green should mean evidence, pass, safety, or available knowledge. Do not use it as generic decoration.
- Avoid purple-blue AI gradients, beige/brown palettes, dark slate dashboards, and decorative orbs.
- Keep border radius at 4 to 8 px for panels, tables, inputs, drawers, and repeated cards.
- Prefer dividers and density over heavy shadows.

## 5. Global Shell

### 5.1 Desktop Layout

Desktop uses a persistent workbench shell:

```text
Left navigation
  + compact top status/action bar
  + page content area
```

Left navigation:

- Fixed width around 220 to 248 px.
- Chinese labels.
- Active item uses light blue background, blue text, and a small left accent.
- Icons can be used when an icon library is already present. Do not hand-draw icons.

Top status/action bar:

- Current project.
- Environment.
- Repository or branch when relevant.
- Knowledge source availability.
- Refresh action.
- Primary task action when the page has one.

Content area:

- Max readable width should fit a workbench table, not a marketing page.
- Use page title, short metadata row, and then the active work surface.
- Avoid page hero sections.

### 5.2 Mobile Layout

Mobile uses:

- Top bar with project, current page, and nav drawer trigger.
- Drawer navigation.
- Single-column stacked sections.
- Full-screen detail drawer for review surfaces.
- Tables become compact list rows or internally scrollable containers.

No page should create body-level horizontal scrolling.

## 6. Final Navigation

Primary navigation order:

1. AI 工作台
2. 需求评审
3. 用例生成评审
4. 用例库和测试套件
5. 自动化草稿中心
6. 执行中心
7. CI/CD 管理
8. 报告中心
9. RAG 知识库
10. Prompt / Skill 中心
11. 工具适配器 / MCP 中心
12. 设置

Rules:

- User-facing page name is `CI/CD 管理`, not `CI/CD 质量中心`.
- Current V1 data names are `CICDRun`, `CICDChangedFile`, and `UnitTestPatch`.
- `RAG 知识库` is a user-facing knowledge and context management page. V1 still does not build vector indexing, embeddings, reranking, or an internal RAG runtime.

## 7. Page Templates

Use a small set of repeatable templates so future AI coding stays consistent.

### 7.1 Workbench Overview

Used by:

- AI 工作台.
- 报告中心 summary states.

Structure:

- Compact metric strip.
- Pending work table.
- Recent task table.
- Right side detail or activity drawer when needed.

### 7.2 Review Split Pane

Used by:

- 需求评审.
- 用例生成评审.
- 自动化草稿中心.
- CI/CD 管理 patch review.

Structure:

- Left source/context pane.
- Middle AI output or candidate list.
- Right detail/review/action pane.
- Bottom evidence, risk, or history panel when needed.

### 7.3 Asset Library

Used by:

- 用例库和测试套件.
- RAG 知识库.
- Prompt / Skill 中心.
- 工具适配器 / MCP 中心.

Structure:

- Left tree or filter column.
- Main table.
- Detail drawer.
- Toolbar with create/import/search/filter actions.

### 7.4 Execution And Evidence

Used by:

- 执行中心.
- 报告中心.
- CI/CD 管理 execution section.

Structure:

- Execution configuration form.
- Queue or run list.
- Artifact panel.
- Evidence-first report details.

## 8. Page Designs

### 8.1 AI 工作台

Purpose: show what the tester should handle next and provide fast entry into the three V1 loops.

Layout:

- Top action group: 新建需求评审, 新建用例生成, 新建自动化草稿, 新建 CI/CD 任务.
- Metric strip: 待评审用例, 待审批草稿, 执行失败, 可用知识证据, 今日报告.
- Pending work table sorted by risk and blocker state.
- Recent AI task table with Agent, status, elapsed time, Prompt/Skill, model, and result link.
- Evidence status strip showing missing artifacts or failing jobs.

Primary rule: the first screen must answer "what needs my review now".

### 8.2 需求评审

Purpose: let AI find requirement issues before test design starts.

Layout:

- Left pane: requirement text/file input, module, requirement source, target test type, `上下文工件` selector, `use_knowledge` switch.
- Middle pane: six-dimension score, total score, risk level, requirement quality trend for the current item.
- Right pane: issue list, clarification questions, conflicts, untestable statements, rewrite suggestions, used context artifacts.
- Bottom panel: risk matrix with impact, probability, suggested test strategy, and evidence references.

Actions:

- 开始评审.
- 编辑评分.
- 保存评审.
- 生成用例.

Safety:

- Show `used_context_artifact_ids` even when `use_knowledge=false`.
- Show schema validation errors with raw output artifact link.

### 8.3 用例生成评审

Purpose: make AI-generated cases reviewable before they enter the official library.

Layout:

- Left pane: module tree, requirement selector, generation batch list.
- Main table: candidate title, type, priority, status, duplicate warning, requirement reference, review owner state.
- Right drawer: steps, expected result, input data, AI reason, requirement references, risk references, editable fields.
- Top metric strip: generated count, adoption rate, rejection rate, edit rate, duplicate rate, review progress.

Actions:

- 接受.
- 编辑后接受.
- 驳回.
- 要求优化.
- 批量评审.

Reference migration:

- WHartTest `GenerateCasesModal` can guide generation configuration: generation mode, test type, requirement document, requirement module, prompt, knowledge selector, save module, and case selection.

### 8.4 用例库和测试套件

Purpose: manage reviewed testing assets and provide the automation draft entry.

Layout:

- Left module tree up to five levels.
- Tabs: 用例, 测试套件.
- Case table: title, type, priority, source, review status, latest run result, automation status.
- Suite table: suite name, selected cases, execution strategy, linked command.
- Detail drawer: steps, expected results, test data, requirement links, versions, automation entry.

Actions:

- 新建用例.
- 编辑用例.
- 生成 pytest 草稿.
- 生成 Playwright 草稿.
- 加入测试套件.

### 8.5 自动化草稿中心

Purpose: keep generated automation code in a review-gated draft state.

Layout:

- Left draft list grouped by status and source case.
- Center code/diff viewer with suggested file path and framework.
- Right review panel with execution notes, risk notes, Prompt/Skill version, model, validation result, and approval actions.
- Bottom execution entry appears only for approved drafts.

Actions:

- 编辑.
- 审批通过.
- 驳回.
- 执行.

Rules:

- Unapproved AutomationDraft cannot execute.
- AutomationDraft does not support `approve_after_edit`; that action belongs to GeneratedCaseCandidate.

### 8.6 执行中心

Purpose: run approved commands and inspect structured evidence.

Layout:

- Tool list: TestRunner / pytest and Playwright first; Newman and JMeter later.
- Execution form: project, environment, command, parameters, artifact strategy.
- Execution queue: queued, running, passed, failed, error, timeout, cancelled.
- Artifact panel: stdout, stderr, JUnit, coverage, trace, screenshot.
- Failure analysis entry when a run fails.

Rules:

- Show ToolDefinition risk level and approval requirement before execution.
- Never show a confident conclusion without artifacts.

### 8.7 CI/CD 管理

Purpose: turn local code changes into test patch evidence and a quality conclusion.

V1 scope:

- Local repository and manual diff input.
- Base/head selection when local Git data is available.
- Changed file summary.
- Diff risk analysis.
- UnitTestPatch generation and review.
- PatchScopeGate result.
- New test execution.
- Regression plan and regression execution.
- CI/CD quality report.

Layout:

- Repository overview: repo, branch, base, head, changed files.
- Diff risk panel: risk level, impacted modules, summary, affected tests.
- Patch review panel: UnitTestPatch diff, test intent, coverage target, scope gate.
- Regression plan panel: pytest command, rationale, estimated duration.
- Execution results: new tests, regression tests, stdout/stderr/JUnit.
- Report section: merge recommendation, blockers, failure classification, evidence links.

V2 boundary:

- GitHub Actions, GitLab CI, webhook ingestion, PR comments, and remote CI sync are later capabilities.

### 8.8 报告中心

Purpose: present traceable conclusions.

Layout:

- Report list: type, related entity, conclusion, generated time, evidence completeness.
- Report detail: summary, metrics, evidence, missing evidence, AI explanation, suggested next step.
- Export actions: Markdown, HTML, JSON.

Rules:

- Evidence and artifacts appear before AI explanation.
- Include CI/CD quality report as one report type.
- If evidence is missing, show `insufficient_evidence` instead of a confident result.

### 8.9 RAG 知识库

Purpose: manage V1 knowledge surfaces without building an internal RAG runtime.

V1 scope:

- ContextArtifact source list.
- KnowledgeAdapter provider configuration state.
- Safe-to-show and prompt-allowed metadata.
- Redaction status.
- Search/evidence test panel when an external provider is configured.
- Evidence usage history by AI task.

Layout:

- Left source group: 项目文档, API notes, OpenAPI, fixture, 日志, 历史缺陷摘要.
- Main table: name, type, owner, safe_to_show, redaction_applied, allowed_for_prompt, last used.
- Right drawer: content summary, safety metadata, context manifest, recent AI tasks.
- Test panel: query input, provider status, evidence id, source, snippet, score when available.

Rules:

- V1 does not create vector indexes, embeddings, chunk stores, or rerankers.
- `use_knowledge=false` means external KnowledgeAdapter is disabled, not that selected ContextArtifacts are disabled.
- The page must distinguish local `上下文工件` from external knowledge evidence.

### 8.10 Prompt / Skill 中心

Purpose: make AI behavior versioned, inspectable, and measurable.

Layout:

- PromptVersion table: name, version, hash, applicable Agent, status.
- SkillVersion table: name, version, input schema, output schema, safety gate.
- Detail drawer: template, schema, allowed tools, sample input, sample output.
- Effectiveness metrics: adoption rate, schema pass rate, failure rate, average token, average latency.

Rules:

- Do not create a plugin marketplace in V1.
- Focus on local registry, version traceability, and quality metrics.

### 8.11 工具适配器 / MCP 中心

Purpose: manage callable tools and their safety policy.

Layout:

- ToolDefinition table: name, schema, risk level, approval required, timeout, enabled state.
- ToolInvocation table: called at, input summary, status, artifact, error code.
- MCP placeholder panel: future server configuration state.

Rules:

- Internal Tool Adapter is first.
- MCP is not a V1 runtime dependency.
- ToolInvocation can only execute allowlisted ToolDefinitions.

### 8.12 设置

Purpose: maintain single-user project context.

Layout:

- Project profile.
- Module tree.
- Repository configuration.
- Environment configuration.
- TestCommand allowlist.
- Context artifact settings.
- Model/mock provider settings.

Rules:

- No RBAC, tenant, member, department, SSO, enterprise audit, or organization management pages in V1.

## 9. States

Every AI or execution surface needs complete states:

- Loading: skeleton matching final layout.
- Empty: short explanation and one primary next action.
- Error: reason, provider/tool, retry action, raw artifact when available.
- Pending review: explicit review action.
- Approved/rejected: show who/when in V1 single-user form.
- Running: stage, elapsed time, Agent/tool, cancellable state when supported.
- Failed: evidence first, then classification.
- Insufficient evidence: do not infer a pass/fail conclusion.

## 10. Implementation Notes For AI Coding

- Keep frontend changes inside the existing Vue/Vite/Arco app unless the active task says otherwise.
- Prefer Arco components for layout primitives, forms, tables, drawers, tags, modals, tabs, and notifications.
- Use shared page templates before creating one-off layouts.
- Keep visible UI text Chinese-first.
- Keep data identifiers stable where backend contracts require them.
- Add route/page shells incrementally. Do not implement every page deeply before the V0.1 evidence loop works.
- When migrating WHartTest patterns, adapt the structure and include required license attribution if copying non-trivial code.
- Do not copy MeterSphere source. Recreate interaction patterns from scratch.
- Do not add internal RAG, vector DB, embedding service, or MCP runtime as part of the frontend page work.

## 11. Acceptance Checklist

A frontend page is ready for V1 implementation review when:

- It fits one of the page templates above.
- It uses the final navigation label.
- It displays review state and evidence state.
- It keeps primary action close to the review surface.
- It records or displays Prompt/Skill/model trace when AI output is shown.
- It shows artifacts before AI explanation when reporting execution or failure.
- It works on desktop and mobile without body horizontal scrolling.
- It does not introduce enterprise management scope.
