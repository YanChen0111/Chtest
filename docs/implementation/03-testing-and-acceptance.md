# Chtest Testing And Acceptance

## 1. 测试目标

Chtest V1 的测试重点不是追求复杂覆盖率，而是保证证据闭环和三条最小闭环稳定。

第一验收对象是 V1 Minimum Demo：

```text
需求 -> ContextArtifact -> AI 评审 -> 候选用例 -> 人工评审 -> AutomationDraft -> 审批 -> runner 执行 -> artifacts -> report
```

随后保证三条最小闭环：

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
| Runner sandbox | pytest + Docker smoke when available | runtime workspace、readonly repo、network setting、snapshot artifact |
| Frontend smoke | Vitest / Playwright | 核心页面能加载和提交 |
| E2E smoke | Docker Compose | 服务启动、V1 Minimum Demo 和三条 Golden Path |

## 3. Contract Tests

必须覆盖：

- `docs/contracts/01-data-model-contract.md` 中核心枚举和必填字段。
- `docs/contracts/02-api-contract.md` 中核心 API 的 request/response。
- `docs/contracts/03-state-machines.md` 中非法迁移拒绝。
- `docs/contracts/04-artifact-contract.md` 中 artifact 路径和 metadata。
- `docs/contracts/05-prompt-skill-contract.md` 中 JSON schema 校验。
- ContextArtifact 必须复用 Artifact 表，并校验 `owner_entity_type=Project`、`owner_entity_id=project_id`。
- ContextArtifact 必须覆盖 secret scan、redaction、allowed MIME、max size、`safe_to_show` 服务端计算。

## 4. Golden Path Acceptance

### 4.0 V1 Minimum Demo Evidence Loop

使用：`docs/fixtures/00-v1-demo-path.md`

通过标准：

- Project、Module、Repository、Environment、TestCommand 创建成功。
- ContextArtifact 创建成功，并能看到 `safe_to_show` 和 `redaction_applied`。
- RequirementReview 显示 `used_knowledge=false` 和实际 `used_context_artifact_ids`。
- CaseGeneration 显示实际 `used_context_artifact_ids`。
- AITask artifact 包含 `context_manifest.json`。
- 至少一个候选用例通过人工评审进入 TestCase。
- Mock AutomationDraftAgent 生成 pytest AutomationDraft。
- AutomationDraft 审批后才能执行。
- TestRunner 执行 pytest，并保存 stdout/stderr/JUnit artifacts。
- TestRun 记录 runtime artifact ids、runtime_manifest、dependency_snapshot、environment_snapshot 和 runner sandbox metadata。
- Report 生成并引用 evidence。

产品价值验收：

- 用户能看到 AI 分析的需求和使用的 ContextArtifact。
- 用户能看到哪个 AutomationDraft runtime artifact 被执行。
- 用户能看到 runner mode、运行工作区、依赖快照、环境快照和 artifact 证据。
- 用户能从报告判断结论是否可信，以及失败后的下一步。

### 4.1 需求到用例

使用：`docs/fixtures/01-golden-requirement-to-case.md`

通过标准：

- Requirement 创建成功。
- ContextArtifact 创建成功，并能看到 `safe_to_show` 和 `redaction_applied`。
- RequirementReview 生成六维评分。
- RequirementReview 显示 `used_knowledge=false` 和实际 `used_context_artifact_ids`。
- RiskItem 至少 2 条。
- GeneratedCaseCandidate 至少 5 条。
- CaseGeneration 显示实际 `used_context_artifact_ids`。
- 每条候选有 steps、expected_results、requirement_refs。
- 至少 4 条候选进入 approved / approved_after_edit / needs_optimization。
- CaseQualityMetric 可计算。
- AITask artifact 包含 `context_manifest.json`。

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

## 5. Smoke 命令建议

后端：

```bash
cd backend && uv run pytest app/tests -q
```

API：

```bash
cd backend && uv run pytest app/tests/api -q
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
- V1 Minimum Demo 用 mock LLM 跑通。
- 三条 Golden Path 至少能用 mock LLM 跑通。
- V1 Minimum Demo 能展示已使用的 ContextArtifact 和 `context_manifest.json`。
- docker runner 可用时作为产品验收 runner；不可用时记录 local fallback 原因和风险。
- ToolInvocation 不允许任意 shell。
- UnitTestPatch 不能修改业务源码。
- 未审批的 AutomationDraft 不能执行。
- AutomationDraft TestRun 必须记录 runtime manifest、dependency snapshot、environment snapshot 和 runner sandbox metadata。
- ContextArtifact 不能绕过 secret scan/redaction。
- 报告无 evidence 时不能标记 passed。
- `memory/08-session-handoff.md` 明确下一步。
