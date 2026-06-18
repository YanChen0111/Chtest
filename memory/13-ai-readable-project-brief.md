# AI Readable Project Brief

> 本文件是给后续 AI 开发会话快速读取的浓缩上下文。它不替代 docs，而是帮助 AI 在几分钟内恢复项目方向、边界和下一步。

## 1. 项目一句话

Chtest V1 是面向个人测试工程师、自动化测试工程师的 AI 测试设计与自动化落地工作台。长期方向是小团队 AI 测试工作台 + Agent / Skill / MCP 测试工具生态。

## 2. V1 三条最小闭环

### 主线 A：需求到用例

```text
需求输入
  -> AI 六维需求评审
  -> 风险矩阵
  -> AI 生成结构化候选用例
  -> 人工评审
  -> 正式用例库
  -> 用例质量指标
```

### 主线 B：用例到自动化

```text
需求/用例
  -> AI 生成 AutomationDraft
  -> 人工审批或编辑
  -> pytest/Playwright 执行
  -> artifact 收集
  -> 失败归因
  -> 报告
```

### 支线 C：代码到质量

```text
本地 Git diff
  -> 变更风险分析
  -> AI 生成 UnitTestPatch
  -> 人工审批
  -> pytest 新增测试和回归
  -> Git 质量报告
```

Git Quality Center 是 V1 支线能力，不压过需求到自动化主线。

## 3. 硬约束

- 项目位置：`/Users/yanchen/VscodeProject/Chtest`。
- 第一版单用户，不做 RBAC、多租户、团队协作。
- 第一版使用 PostgreSQL + Redis + Docker Compose。
- V1 技术栈冻结：FastAPI、SQLAlchemy 2、Pydantic v2、Alembic、Vue 3、Arco、Redis + RQ。
- 不做一次性演示，要真实可用。
- AI 生成用例必须进入评审窗口，不能直接入库。
- AI 生成 AutomationDraft 必须审批后执行，不能直接写业务项目。
- AI 生成 UnitTestPatch 必须人工审批，只允许写测试目录。
- V1 禁止 AI 自动修改业务源码。
- RAG 不内置，只保留 Knowledge/RAG Adapter。
- MCP 不作为 V1 强依赖，先实现 Internal Tool Adapter。
- ToolInvocation 只能执行 ToolDefinition allowlist。
- 每个完成 Task 必须测试并 commit；Slice 完成或重大上下文变化时更新 `memory/07-dev-log.md` 和 `memory/08-session-handoff.md`；会话结束但 Slice 未完成时更新 handoff 的 Task table。

## 4. 必读文档顺序

后续 AI 开工前按顺序读：

1. `memory/README.md`
2. `memory/13-ai-readable-project-brief.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/contracts/05-prompt-skill-contract.md`
9. `docs/implementation/01-v1-development-process.md`
10. `docs/implementation/02-v1-slice-plan.md`
11. `memory/11-implementation-slices.md`
12. `memory/08-session-handoff.md`

按任务追加 fixtures：

- 需求到用例：`docs/fixtures/01-golden-requirement-to-case.md`
- 用例到自动化：`docs/fixtures/02-golden-case-to-playwright.md`
- Git 质量：`docs/fixtures/03-golden-git-quality.md`

## 5. 当前优先级

当前应进入 V1 实施，而不是继续扩写大而全规划。

推荐下一个开发切片顺序：

```text
Slice 1 -> Slice 2 -> Slice 2.5 -> Slice 3
Repository and Deploy Skeleton -> Backend Core -> Frontend Foundation -> Project Core
```

具体任务：

- 创建 backend/frontend/worker/deploy/prompts/skills/mcp_tools 目录。
- 写 Docker Compose。
- 启动 PostgreSQL 和 Redis。
- 建 FastAPI health/ready。
- 建 Alembic。
- 建单用户上下文。
- 建 Vue + Vite + Arco + router/store/API 前端基础布局。
- 建 Project / Module / Repository / Environment / TestCommand API 和 Project Settings 前端入口。

## 6. 不要做什么

- 不要先做完整 RAG。
- 不要先做企业权限。
- 不要先做插件市场。
- 不要先做复杂低代码 UI 自动化。
- 不要让 AI 结果绕过人工评审。
- 不要让工具执行任意 shell。
- 不要让 AI 自动修改业务源码。
- 不要把 WHartTest 或 MeterSphere 大段源码直接复制进来。

## 7. 参考框架使用方式

参考源码在：

- `参考框架/WHartTest`
- `参考框架/metersphere`

使用原则：

- WHartTest 优先参考 AI/MCP/Skill/用例生成/执行器思想。
- MeterSphere 优先参考用例评审、报告、测试资产管理视图。
- 只迁移能力，不迁移企业复杂度。
- 只借鉴结构，不复制大段源码。

## 8. 每次开发后的交接格式

如果 Slice 完成，更新 `memory/07-dev-log.md` 和 `memory/08-session-handoff.md`，并在 handoff 至少写：

```text
本轮完成：
本轮验证：
修改文件：
未完成问题：
下次推荐任务：
风险提醒：
```

如果 Slice 未完成，只需要更新 `memory/08-session-handoff.md` 的 Task table，记录当前 Task 状态、未验证事项、风险和下一步；不强制更新 `memory/07-dev-log.md`，除非出现重大上下文变化。

## 9. 给后续 AI 的一句话

优先把 Chtest 做成可运行、可评审、可执行、可报告的个人 AI 测试设计与自动化落地工作台。任何新能力都必须服务“需求到用例”“用例到自动化”“Git 到质量报告”三条最小闭环。
