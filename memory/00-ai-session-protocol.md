# AI Session Protocol

## 目的

本协议用于保证每次新的 AI 开发会话都能快速恢复上下文，并在结束时留下足够清晰的项目记忆。

Chtest V1 当前定位是面向个人测试工程师、自动化测试工程师的 AI 测试设计与自动化落地工作台，不是企业协作测试管理平台。任何新会话都必须以 memory、contracts、fixtures 文档为准，不依赖聊天上下文。

## 开工前流程

每次开始开发前，AI 必须：

1. 读取 `memory/README.md`。
2. 读取 `memory/13-ai-readable-project-brief.md`。
3. 读取 `memory/08-session-handoff.md`，确认上次交接。
4. 读取 `memory/04-project-constraints.md`，确认硬约束。
5. 读取 `docs/product/01-positioning-and-scope.md`，确认 V1 定位和三条最小闭环。
6. 读取 contracts：
   - `docs/contracts/01-data-model-contract.md`
   - `docs/contracts/02-api-contract.md`
   - `docs/contracts/03-state-machines.md`
   - `docs/contracts/04-artifact-contract.md`
   - `docs/contracts/05-prompt-skill-contract.md`
7. 根据任务读取 fixture：
   - 需求到用例：`docs/fixtures/01-golden-requirement-to-case.md`
   - 用例到自动化：`docs/fixtures/02-golden-case-to-playwright.md`
   - Git 质量：`docs/fixtures/03-golden-git-quality.md`
8. 读取 `docs/implementation/04-ai-vibecoding-governance.md`。
9. 查看 `memory/11-implementation-slices.md` 或 `docs/implementation/02-v1-slice-plan.md`。
10. 查看 `git status --short`。
11. 定义 Task Definition Of Ready，再开始设计或实现。

## 开发中要求

- 每次只做一个可验收 Slice；每次默认只做 1 个 Task，最多 1-3 个 Task。
- 不凭聊天上下文做关键假设，以 memory + contracts 为准。
- 如果用户临时调整方向，要同步更新对应 memory 文件。
- 如果发现文档与实现矛盾，先记录矛盾，再修正文档或实现。
- 每个重要设计决策都要写入 `06-architecture-decisions.md`。
- 每个完成并验证的 Task 必须 commit；commit 规则见 `docs/implementation/04-ai-vibecoding-governance.md`。
- Task 完成后默认不写 `memory/07-dev-log.md`，除非出现重大变化、阻塞、测试无法运行或文档/实现冲突。
- 每个 Slice 完成后必须更新 `memory/07-dev-log.md` 和 `memory/08-session-handoff.md`。
- 涉及 AI 流程时必须说明使用哪个 Agent、Skill、Prompt、Tool Adapter。
- 涉及数据模型、API、状态机时必须先检查 `docs/contracts/`。
- 涉及三条闭环时必须用对应 `docs/fixtures/` 验证。

## Slice Definition Of Done

每个 Slice 完成前必须满足：

- 有数据模型，或明确说明不需要数据模型。
- 有 API 契约，或明确说明只做内部能力。
- 有状态机，或复用现有状态机。
- 有 mock 数据或 fixture。
- 有最小测试或 smoke 验证。
- 有 UI 或 API 验证入口。
- 有 artifact/log 记录。
- 有失败状态和错误响应。
- 有 git diff 自查和 commit，或明确说明未提交原因。
- Slice 完成或重大上下文变化时 memory 已更新；普通 Task 完成以 git commit 为准。

## 收工前流程

### Slice 完成时

如果当前 Slice 已完成，AI 必须：

1. 更新 `memory/07-dev-log.md`：
   - Slice 名称
   - 完成内容
   - 验证命令和结果
   - commit 摘要
   - 遗留事项
2. 更新 `memory/08-session-handoff.md`：
   - 当前 Slice 状态
   - 本轮完成内容
   - 本轮验证命令和结果
   - commit table
   - 未完成问题
   - 风险提醒
   - 下一 Slice 或下一 Task
   - 最新稳定 commit
3. 如果改了架构、范围、技术选型、Agent/MCP/Skill/Prompt/RAG 设计或约束，更新对应文档。

### Slice 未完成时

如果会话结束但当前 Slice 未完成，AI 必须：

1. 更新 `memory/08-session-handoff.md` 的 Task table。
2. 记录当前 Task 状态、未验证事项、风险和下一步。
3. 记录已经产生的 commit 和验证命令。
4. 不强制更新 `memory/07-dev-log.md`，除非出现重大上下文变化、阻塞、测试无法运行或文档/实现冲突。

### 重大上下文变化时

无论 Task 或 Slice 是否完成，只要出现以下情况，必须立即更新 memory 或对应 docs：

- 产品定位变化。
- V1 范围变化。
- 技术栈变化。
- 数据模型契约变化。
- API 契约变化。
- 状态机变化。
- 安全或审批策略变化。
- 发现文档与实现冲突。
- 测试无法运行或连续失败。
- 出现阻塞，需要下一轮 AI 接手。
- 用户临时改变优先级。

## 禁止事项

- 禁止把临时聊天结论当成长期事实，除非写入 memory。
- 禁止在未确认约束前开始大规模实现。
- 禁止让 AI 生成内容直接进入正式资产而没有审查和验证。
- 禁止让 AI 自动修改业务源码。
- 禁止 UnitTestPatch 写测试目录以外的文件。
- 禁止未审批 AutomationDraft 进入执行。
- 禁止把 secret、生产凭证、生产写接口放进 Prompt 或测试上下文。
- 禁止第一版实现 RAG；只能预留 Knowledge/RAG Adapter。
- 禁止把 MCP 工具调用绕过 Chtest 的审批、日志和质量门禁。
- 禁止把 Chtest 第一版做成企业协作平台。
- 禁止测试失败后继续扩大实现范围。
- 禁止把多个 Slice 混在一个 commit。
- 禁止未经用户要求自动 push。

## 每次开工提示词

```text
请先读取 Chtest/memory/README.md、13-ai-readable-project-brief.md 和 08-session-handoff.md，
再读取 docs/product/01-positioning-and-scope.md、docs/contracts/*、docs/implementation/04-ai-vibecoding-governance.md 和本次任务相关 fixtures。
请基于 memory + contracts + governance 中的当前事实继续开发，不要依赖聊天上下文。
当前定位是个人测试/自动化测试工程师的 AI 测试设计与自动化落地工作台，不是企业协作测试管理平台。
如果发现 memory、contracts 或 governance 与当前任务冲突，先指出冲突并提出修正建议。
每个 Task 必须定义 DoR、运行验证、git diff 自查、commit，并更新 handoff；不要 push，除非我明确要求。
```
