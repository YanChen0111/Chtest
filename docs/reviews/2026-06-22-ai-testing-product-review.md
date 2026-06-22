# 2026-06-22 AI Testing Product Review

## 1. PM Verdict

Chtest 的方向是正确的，但价值不在“AI 生成更多用例”。真正有市场辨识度的方向是：

```text
需求或代码变更
  -> AI 分析风险与测试点
  -> 人工评审测试资产
  -> 审批 AutomationDraft 或 UnitTestPatch
  -> sandbox runner 执行
  -> 记录 artifacts、snapshots、stdout/stderr、JUnit、trace
  -> 失败归因或 repair candidate
  -> 生成证据报告
  -> 反哺 AI 质量指标
```

这个方向比通用测试管理系统、简单 AI 用例生成器、模型榜单、RAG 平台都更适合 V1。它能帮助个人测试工程师和自动化测试工程师把 AI 输出变成可审查、可执行、可追踪、可度量的测试证据。

结论：继续执行 Strategy B，先证明证据闭环，再扩功能。

## 2. Market And Big-Company Signals

| Source | Landing Pattern | Chtest Implication |
|---|---|---|
| GitHub Copilot cloud agent | Agent researches repo, plans, changes branch, runs automated tests/linters in an ephemeral environment, then exposes logs, commits, PR, and PR outcome metrics. | Chtest must make execution logs, artifacts, runner mode, review, and metrics first-class product objects. |
| OpenAI Codex | Coding tasks run in isolated cloud sandbox, can run test harnesses/linters/type checkers, and provide terminal logs/test outputs for human review before integration. | Chtest runner sandbox, test output citation, manual approval, and project instructions are not nice-to-have; they are trust infrastructure. |
| Google Jules | User selects GitHub repo/branch, agent clones to Cloud VM, produces a plan, provides a diff for approval, and creates a PR. | Chtest should keep plan/diff/artifact approval before promotion, especially for AutomationDraft and UnitTestPatch. |
| Meta TestGen-LLM | Meta evaluates generated unit tests by build success, reliable pass, coverage increase, and engineer acceptance. | Chtest metrics should prioritize accepted/useful/executable tests, not generation volume. |
| Google OSS-Fuzz LLM work | Generated fuzz targets are compiled, executed, measured by coverage, and repaired through error feedback. | Chtest repair loop must be evidence-driven and stop when evidence is insufficient. |
| DORA 2025 | AI amplifies existing strengths and weaknesses; ROI comes from improving the underlying engineering system, not only buying tools. | Chtest must improve context quality, review gates, execution reliability, and feedback metrics as a system. |
| APITestGenie 2026 research | Requirements + API specifications + LLMs can generate executable API tests, but requirement/API detail strongly affects success. | V1 ContextArtifact and future OpenAPI/Newman path are valuable, but context quality must be visible and measured. |

Product inference: 大厂落地 AI 测试不是“给测试人员一个聊天框”。更成熟的形态是把 AI 放进工程流水线：上下文输入、结构化输出、受控执行、证据记录、人审门禁、质量指标。

## 3. Product Value Assessment

Strong value:

- AI 把测试设计、自动化草稿、失败归因这些高耗时环节前置加速。
- 人工评审和审批让测试工程师保留质量控制权。
- runner artifacts 让 AI 结果可验证，避免“看起来会测”的假价值。
- AI 质量指标让产品从“内容生成工具”升级成“可改进的测试工程系统”。

Best V1 wedge:

```text
Requirement -> reviewed case -> approved AutomationDraft -> sandbox execution -> evidence report
```

Do not dilute the wedge with:

- enterprise admin/RBAC/SSO;
- full test management parity;
- broad RAG platform;
- model marketplace;
- complex low-code UI automation;
- Newman/JMeter/Appium before pytest/Playwright evidence loop works.

## 4. Technical Architecture Review

Current stack is reasonable and should not be changed before Slice 1:

| Area | Judgment |
|---|---|
| FastAPI + Pydantic v2 | Good fit for typed API contracts, AI output validation, and state-machine enforcement. |
| SQLAlchemy 2 + Alembic + PostgreSQL | Good fit for evidence records, artifacts, state transitions, and metrics. |
| Redis + RQ | Enough for V1 AI/tool/report jobs. Do not introduce Temporal/Celery before real workflow pain appears. |
| Vue 3 + TypeScript + Vite + Arco | Good fit for a dense testing workbench with tables, drawers, approval panels, and evidence inspection. |
| Docker Compose | Correct V1 local-first environment; also supports repeatable product acceptance. |
| Mock Provider first | Correct. Deterministic eval must exist before real-model tuning. |
| Docker runner preference | Correct and important. Local subprocess must remain a development fallback, not the product trust path. |

Architecture risks to watch:

- RQ retry/idempotency must be designed before real provider calls and runner execution.
- Artifact storage is core product data; do not treat it as disposable logs.
- Frontend scaffold must happen before feature pages, or later UI work will fragment.
- Git Quality is useful but must remain a support workflow until the requirement-to-automation loop is usable.
- ContextArtifact is the correct pre-RAG step; do not build vector search before the evidence loop has adoption.

## 5. Vibe Coding Review

The current vibe coding governance is directionally strong: Slice, Task, verification, commit, handoff, contracts-first, and rollback rules are exactly what long-running AI development needs.

Required operating constraints:

- One Slice has one product value answer.
- Every Task has an exact verification command before coding starts.
- Every completed Task has a commit.
- Every AI-generated test asset remains review-gated.
- Every runner execution records artifacts and snapshots.
- After two or three failed repair attempts, stop and write evidence instead of continuing speculative edits.
- Do not add broad platform features before `docs/fixtures/00-v1-demo-path.md` passes.
- Plan -> diff -> verification -> commit -> handoff must be visible in every session.

Product-manager concern: without these constraints, vibe coding will naturally drift into broad CRUD, disconnected pages, and impressive-looking but untrusted AI output.

## 6. Optimization Plan

### P0

- Keep Strategy B as the current product strategy.
- Build Slice 1, Slice 2, Slice 2.5, then Slice 3 in that order.
- Treat `docs/fixtures/00-v1-demo-path.md` as release spine.
- Make `docker_runner` the preferred acceptance runner as early as practical.
- Implement mock-provider eval bench with schema, evidence, unsafe output, usefulness, first-run pass, manual edit, and repair success metrics.
- Make TestRun artifacts and sandbox metadata visible from the UI/API.

### P1

- Productize AutomationRepairTask after the first failed-run evidence loop works.
- Add AI effectiveness views by prompt, skill, model, and task type.
- Add Markdown/HTML/JSON/JUnit/CSV export from the same evidence manifest.
- Add OpenAPI/Newman only after pytest/Playwright execution artifacts are stable.

### P2

- Add MCP integrations, RAG provider, enterprise collaboration, broader tool adapters, and model-routing only after V1 evidence loop has repeatable usage.

## 7. External Sources

- GitHub Copilot cloud agent: <https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent>
- GitHub Copilot vibe coding tutorial: <https://docs.github.com/en/copilot/tutorials/vibe-coding>
- OpenAI Codex introduction: <https://openai.com/index/introducing-codex/>
- Google Jules: <https://jules.google/>
- DORA State of AI-assisted Software Development 2025: <https://dora.dev/research/2025/dora-report/>
- Meta TestGen-LLM paper: <https://arxiv.org/abs/2402.09171>
- Google OSS-Fuzz AI-powered fuzzing: <https://security.googleblog.com/2023/08/ai-powered-fuzzing-breaking-bug-hunting.html>
- APITestGenie 2026 paper: <https://arxiv.org/abs/2604.02039>

## 8. Final Decision

Chtest should continue as an AI testing evidence workbench. The product direction is correct if implementation stays narrow, evidence-first, review-gated, and measurable.

The next correct move is not more planning breadth. The next correct move is Slice 1 runnable foundation, then the shortest path to the V1 minimum evidence demo.
