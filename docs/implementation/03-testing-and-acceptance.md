# Chtest Testing And Acceptance

## 1. 测试目标

Chtest V1 的测试重点不是追求复杂覆盖率，而是保证三条最小闭环稳定：

1. 需求到用例。
2. 用例到自动化。
3. Git 到质量报告。

## 2. 测试分层

| 层 | 工具 | 目标 |
|---|---|---|
| Backend unit | pytest | service、state transition、schema validation |
| API | FastAPI TestClient | API request/response contract |
| Worker | pytest + fake queue | AITask、ToolInvocation 状态推进 |
| Tool Adapter | mock subprocess | allowlist、timeout、artifact 保存 |
| Frontend smoke | Vitest / Playwright | 核心页面能加载和提交 |
| E2E smoke | Docker Compose | 服务启动和三条 Golden Path |

## 3. Contract Tests

必须覆盖：

- `docs/contracts/01-data-model-contract.md` 中核心枚举和必填字段。
- `docs/contracts/02-api-contract.md` 中核心 API 的 request/response。
- `docs/contracts/03-state-machines.md` 中非法迁移拒绝。
- `docs/contracts/04-artifact-contract.md` 中 artifact 路径和 metadata。
- `docs/contracts/05-prompt-skill-contract.md` 中 JSON schema 校验。

## 4. Golden Path Acceptance

### 4.1 需求到用例

使用：`docs/fixtures/01-golden-requirement-to-case.md`

通过标准：

- Requirement 创建成功。
- RequirementReview 生成六维评分。
- RiskItem 至少 2 条。
- GeneratedCaseCandidate 至少 5 条。
- 每条候选有 steps、expected_results、requirement_refs。
- 至少 4 条候选进入 approved / approved_after_edit / needs_optimization。
- CaseQualityMetric 可计算。

产品价值验收：

- 用户能看懂 AI 发现了哪些需求问题。
- 用户能判断候选用例为什么被接受、编辑或拒绝。
- 报告能展示 Prompt/Skill/model 对生成质量的影响。

### 4.2 用例到自动化

使用：`docs/fixtures/02-golden-case-to-playwright.md`

通过标准：

- AutomationDraft 生成。
- 未审批前无法执行。
- 审批后创建 TestRun。
- pytest 或 Playwright 至少一个最小执行闭环通过。
- stdout/stderr/JUnit 或 trace/screenshot 保存为 artifact。
- TestRun 记录 runtime_manifest、dependency_snapshot、environment_snapshot 和 runner sandbox metadata。
- Report 生成。

产品价值验收：

- 用户能看到实际执行的是哪个 AutomationDraft runtime artifact。
- 用户能看到首次执行是否通过，以及失败时的下一步建议。
- 用户能看到 AutomationDraft approval rate、first-run pass rate、repair success rate 的基础数据。

### 4.3 Git 到质量报告

使用：`docs/fixtures/03-golden-git-quality.md`

通过标准：

- GitChangeSet 创建。
- GitChangedFile 分类为 source。
- GitDiffAgent 识别新增分支风险。
- UnitTestPatch 只修改 tests/。
- PatchScopeGate 通过。
- 审批后执行 pytest。
- GitQualityReport 生成，结论引用 evidence。

产品价值验收：

- 用户能看到 diff 风险、生成 patch 的安全门禁结果和回归结论。
- 用户能判断 AI patch 是否只影响测试目录。

## 5. Smoke 命令建议

后端：

```bash
pytest backend/app/tests -q
```

API：

```bash
pytest backend/app/tests/api -q
```

Docker：

```bash
docker compose -f deploy/docker-compose.yml up --build
```

健康检查：

```bash
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:8000/ready
```

## 6. 发布验收

V1 发布前必须满足：

- Docker Compose 可启动。
- `/health` 和 `/ready` 通过。
- 三条 Golden Path 至少能用 mock LLM 跑通。
- ToolInvocation 不允许任意 shell。
- UnitTestPatch 不能修改业务源码。
- 未审批的 AutomationDraft 不能执行。
- AutomationDraft TestRun 必须记录 runtime manifest、dependency snapshot、environment snapshot 和 runner sandbox metadata。
- 报告无 evidence 时不能标记 passed。
- `memory/08-session-handoff.md` 明确下一步。
