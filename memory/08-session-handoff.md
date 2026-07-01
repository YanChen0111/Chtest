# Session Handoff

## 2026-07-01 Slice 20 Task 5 完成

本轮完成：

- 按用户要求继续多子代理并发：
  - 一个只读检查 CI/CD 前端页面和测试模式；
  - 一个只读检查后端 read surface 是否能暴露 `ci_run_metadata`。
- 完成 Slice 20 Task 5：Add CI import frontend evidence display。
- `CI/CD 质量中心` 新增导入 CI 证据展示：
  - Provider inert label；
  - 导入状态；
  - CI 结论；
  - QualityGateDecision 仍为本地门禁状态；
  - Job / external run id；
  - inert artifact references。
- 风险分析证据表继续只显示 `risk_analysis`。
- 进行了一个必要的窄后端 read surface 改动：
  - `GET /api/cicd/runs/{id}` 的 `analysis_artifacts` 现在包含
    `risk_analysis` 和 `ci_run_metadata`；
  - 没有走 RAG/extension surface；
  - 没有新增远程 provider 控件。
- 新增前端 API 类型和页面测试，断言不会出现重新运行、取消流水线、
  Webhook、Token、部署、发布等远程控制文案。
- Slice 20 task table 已记录 Task 4 commit `554e74c`，Task 5 done pending
  commit。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 20 Task 6：Add CI import golden
  smoke。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/api/test_ci_run_metadata_import.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- CI metadata import API tests：`53 passed`。
- Existing CI/CD quality center + import API tests：`60 passed`。
- Frontend suite：`15` files passed，`20` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 5：`feat(frontend): show ci import evidence`。
- 继续 Slice 20 Task 6：Add CI import golden smoke。

## 2026-07-01 Slice 20 Task 4 完成

本轮完成：

- 按用户要求继续多子代理并发：
  - 一个只读检查 router/schema/API 测试模式；
  - 一个只读检查 service/model/artifact 持久化规则。
- 完成 Slice 20 Task 4：Add CI run import API。
- 新增 `POST /api/cicd/runs/import`。
- 新增 import API response schemas。
- 持久化 imported CI metadata 为 evidence-only 记录：
  - `CICDRun(status=imported, source_type=ci_import, trigger_type=imported)`；
  - imported `CICDChangedFile` rows；
  - `ci_run_metadata.json` Artifact；
  - compatible `changed_files.json` Artifact。
- API 错误映射覆盖：
  - invalid payload；
  - remote control fields；
  - credentials；
  - provider operation；
  - external fetch；
  - duplicate external run。
- duplicate 范围按 project/repository/provider/external_run_id。
- import 不创建 `QualityGateDecision`、`UnitTestPatch`、`AutomationDraft`、
  `TestRun` 或 `Report`。
- Slice 20 task table 已记录 Task 3 commit `21ce127`，Task 4 done pending
  commit。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 20 Task 5：Add CI import frontend
  evidence display。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/api/test_ci_run_metadata_import.py -q
git diff --check
```

验证结果：

- CI metadata import API tests：`53 passed`。
- Existing CI/CD quality center + import API tests：`60 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 4：`feat(cicd): add ci metadata import api`。
- 继续 Slice 20 Task 5：frontend evidence display。

## 2026-07-01 Slice 20 Task 3 完成

本轮完成：

- 启动本地 Web 预览：
  - Vite 服务运行在 `http://127.0.0.1:5173/`。
  - 已在内置浏览器打开，页面标题为 `Chtest AI 测试工作台`。
- 按用户要求启动两个只读子代理并发检查：
  - 一个检查 `cicd` service/schema/test 可复用点；
  - 一个检查 Slice 20 合同、负向字段和文档更新边界。
- 完成 Slice 20 Task 3：Add deterministic CI metadata parser。
- 新增 parser-only CI import schemas。
- 新增 deterministic parser service：
  - 解析静态 CI metadata JSON；
  - 复用现有 changed-file role/risk 分类；
  - 输出 `ci_run_metadata.json` 内容和 metadata；
  - artifact references 仅作为 inert references 保存；
  - 不调用远程 provider，不下载 URL。
- 新增 CI import 专用错误类：
  - `INVALID_CI_IMPORT_PAYLOAD`
  - `CI_IMPORT_CONTROL_FIELD_REJECTED`
  - `CI_IMPORT_CREDENTIAL_REJECTED`
  - `CI_IMPORT_UNSUPPORTED_PROVIDER_OPERATION`
  - `CI_IMPORT_EXTERNAL_FETCH_FORBIDDEN`
- 新增测试覆盖正向解析、changed-file 规范化、控制字段、凭据字段、外部抓取字段、provider operation 和 malformed payload。
- Slice 20 task table 已记录 Task 2 commit `2201b94`，Task 3 done pending
  commit。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 20 Task 4：Add CI run import API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/api/test_ci_run_metadata_import.py -q
```

验证结果：

- CI metadata import parser tests：`46 passed`。
- Existing CI/CD quality center + parser tests：`53 passed`。

下次推荐任务：

- 先运行 `git diff --check` 并提交 Task 3：
  `feat(cicd): add ci metadata import parser`。
- 然后继续 Slice 20 Task 4：Add CI run import API。

## 2026-06-30 Slice 20 Task 2 完成

本轮完成：

- 完成 Slice 20 Task 2：Define CI import contract boundary。
- 数据合同已定义：
  - `source_type=ci_import`。
  - provider 只是 inert source label。
  - imported CI conclusion 只是 evidence，不自动通过 QualityGateDecision。
- API 合同已定义：
  - `POST /api/cicd/runs/import`。
  - static CI metadata import request/response。
  - 拒绝 webhook、trigger、rerun、cancel、schedule、PR comment、commit
    status update、deploy、release、credentials、external fetch 和 provider
    operation。
- 状态机合同已定义：
  - import 是本地 evidence import 状态，不是 remote provider execution。
  - `quality_gate_status` 在显式 quality gate recompute 前保持 `pending`。
- Artifact 合同已定义：
  - `ci_run_metadata.json`。
  - imported artifact references 是 inert references。
  - `remote_fetch_performed=false`。
- Error code 合同已定义：
  - CI import payload/control/credential/provider/fetch/duplicate rejection
    codes。
- 已处理文档评审发现：
  - 数据合同补齐 `imported` / `import_failed` CICDRun statuses。
  - 数据合同补齐 `ci_run_metadata` Artifact type。
  - provider label 清单保持一致。
  - API 合同显式 `trigger_type=imported`。
  - 明确 imported CI run details 存入 `ci_run_metadata.json`，不是 CICDRun
    columns。
- Slice 20 task table 已记录 Task 1 commit `b1acde6`，Task 2 done pending
  commit。
- 用户已在 2026-07-01 明确同意继续开发。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 20 Task 3：Add deterministic CI
  metadata parser。

本轮验证：

```bash
rg -n "ci_import|CI import|imported CI|ci_run_metadata|remote CI provider|QualityGateDecision|CI_IMPORT_" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/06-error-code-contract.md docs/implementation/slices/slice-20-ci-run-metadata-import.md
git diff --check
```

验证结果：

- Contract boundary keywords found across data, API, state-machine, artifact,
  error-code, and Slice 20 docs。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 2。
- 开始 Slice 20 Task 3：deterministic CI metadata parser。

## 2026-06-30 V2 Next Slice Selection 完成

本轮完成：

- 按用户要求启动多个子代理并发评估下一条 V2 小切片。
- 子代理结论：
  - 方向 B：推荐 JMeter local execution evidence，但不推荐 Appium 或
    traffic capture 先做。
  - 方向 C：推荐 local review attribution/history，但必须排除 RBAC、
    tenants、permissions、SSO、enterprise audit。
  - 方向 D：推荐 import-only CI evidence bridge。
- 最终选择方向 D：
  `Slice 20: CI Run Metadata Import`。
- 选择理由：
  - 直接复用 Slice 15/16 的 CICDRun、CICDChangedFile、Artifact、
    QualityGateDecision 和 CI/CD 管理证据链。
  - 把外部 CI 的事实结果导入 Chtest，而不是让 Chtest 控制远程 CI。
  - imported CI status 是 evidence，不是 QualityGateDecision authority。
- 新增计划：
  `docs/implementation/slices/slice-20-ci-run-metadata-import.md`。
- 更新 V2 scope options：
  - 记录 Slice 19 已完成。
  - 推荐 Slice 20 import-only CI metadata evidence。
- 更新 `NEXT_AI_TASK.md` 到 Slice 20 Task 1。

本轮验证：

```bash
test -f docs/implementation/slices/slice-20-ci-run-metadata-import.md
rg -n "CI Run Metadata Import|Product Value Answer|Non-goals|Task Table|import-only|remote CI provider" docs/implementation/slices/slice-20-ci-run-metadata-import.md docs/implementation/10-v2-scope-options.md
git diff --check
```

验证结果：

- Slice 20 plan file exists。
- Scope keywords found in Slice 20 plan and V2 scope options。
- `git diff --check` clean。

下次推荐任务：

- 提交本 planning task。
- 继续 Slice 20 Task 2：Define CI import contract boundary。

## 2026-06-30 Slice 19 Completion Gate 完成

本轮完成：

- 完成 Slice 19：Deterministic Knowledge Retrieval Stub。
- Slice 19 task table 已记录：
  - Task 5 commit：`b578fac`。
  - Task 6 commit：`ebd67af`。
  - Completion Gate：done，pending commit。
- 确认本 slice 只交付本地 deterministic ContextArtifact retrieval stub：
  - 同项目 ContextArtifact 检索。
  - `safe_to_show=true` 且 `allowed_for_prompt=true` 才能进入 prompt。
  - evidence artifact 记录 query terms、matched terms、scores、snippets、
    ContextArtifact ids。
  - RAG 知识库展示 latest retrieval evidence。
- 未新增 vector database、embedding、reranking、external RAG provider runtime、
  MCP runtime、RBAC、tenants、permissions、marketplace、cloud sync 或 remote CI
  provider integration。
- 已将 `NEXT_AI_TASK.md` 切换到：
  Select the next V2 small slice after Slice 19 completion。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Backend deterministic retrieval + requirement review + extension surface +
  golden smoke：`23 passed`。
- Frontend suite：`15` files passed，`19` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 completion gate。
- 然后按 `NEXT_AI_TASK.md` 做规划任务：选择下一个 V2 小切片。

## 2026-06-30 Slice 19 Task 6 完成

本轮完成：

- 完成 Slice 19 Task 6：Add deterministic retrieval golden smoke。
- 新增 fixture：
  `docs/fixtures/08-deterministic-knowledge-retrieval-golden.md`。
- 新增 golden smoke：
  `backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py`。
- Golden 证明完整证据链：
  - safe `coupon-api-notes.md` ContextArtifact。
  - deterministic local KnowledgeAdapter stub。
  - requirement review `use_knowledge=true`。
  - `used_knowledge=true` 和 exact `used_context_artifact_ids`。
  - AITask owned `knowledge_retrieval` evidence Artifact。
  - persisted `knowledge_retrieval.json` 中的 query terms、matched terms、
    score、snippet、SHA256、prompt eligibility、redaction 状态。
  - RAG 知识库 `/knowledge-base` 可读取 latest retrieval evidence。
- Golden 明确排除 vector database、embedding、reranking、external RAG
  provider、MCP runtime、RBAC、tenants、permissions、marketplace、cloud sync 和
  remote CI provider integration。
- Golden 暴露并修复了一个窄后端 surface 缺口：Requirement Review 现在把
  bounded retrieval result summaries 同步写入 `knowledge_retrieval` Artifact
  metadata，确保 RAG 知识库 `/knowledge-base` 可以稳定读取 snippets、scores
  和 matched terms。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Completion Gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
git diff --check
```

验证结果：

- Golden smoke：`1 passed`。
- Related backend deterministic retrieval + requirement review + extension
  surface + golden tests：`23 passed`。
- `git diff --check` clean。

下次推荐任务：

- 先提交 Task 6。
- 然后按 `NEXT_AI_TASK.md` 运行 Slice 19 Completion Gate：
  backend API + requirement review + extension surface + golden smoke +
  frontend test + diff check。

## 2026-06-30 Slice 19 Task 5 完成

本轮完成：

- 完成 Slice 19 Task 5：Add retrieval evidence frontend display。
- RAG 知识库页面新增 deterministic retrieval evidence 展示：
  - 检索证据计数。
  - KnowledgeAdapter 检索模式。
  - ContextArtifact 行展示检索次数和最近检索时间。
  - 最近检索证据展示 query terms、matched terms、scores、snippets 和来源
    ContextArtifact。
  - 无 evidence 时显示空态，不暴露检索发起控件。
- 前端类型/store 已支持 `latest_retrievals`、`retrieved_count`、
  `latest_retrieved_at`。
- 为了让页面展示真实 evidence，补了很窄的 backend extension surface：
  `/knowledge-base` 从 `knowledge_retrieval` artifacts 派生
  `latest_retrievals`、`retrieved_count`、`latest_retrieved_at`。
- 没有新增 vector search、Embedding、provider runtime config、MCP runtime、
  RBAC、tenants、permissions、marketplace 或 remote sync 控件。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Task 6：Add deterministic
  retrieval golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py backend/app/tests/api/test_deterministic_knowledge_retrieval.py -q
git diff --check
```

验证结果：

- Frontend suite：`15` files passed，`19` tests passed。
- Extension + deterministic retrieval API tests：`12 passed`。
- `git diff --check` clean。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 新增 deterministic retrieval golden smoke。
- Golden 需要证明 ContextArtifact -> deterministic retrieval -> requirement
  review -> knowledge_retrieval evidence -> RAG 知识库 surface。

## 2026-06-30 Slice 19 Task 4 完成

本轮完成：

- 完成 Slice 19 Task 4：Attach retrieval evidence to AI task flows。
- Requirement Review 在 `use_knowledge=true` 时会调用 deterministic local
  retrieval。
- 只有实际检索到 snippets 时才记录：
  - `used_knowledge=true`
  - `used_context_artifact_ids`
  - `retrieval_evidence_artifact_id`
- 新增 `knowledge_retrieval.json` evidence artifact：
  - owner 为 AITask。
  - `artifact_type=knowledge_retrieval`。
  - metadata 包含 `created_by_component=DeterministicKnowledgeAdapter`、
    `retrieval_mode=deterministic_local`、query terms、result count、retrieved
    ContextArtifact ids、redaction 状态。
  - 文件内容包含 query text、query terms、matched terms、scores、snippets、
    SHA256、ContextArtifact ids、allowed_for_prompt 和 redaction 信息。
- 保持旧行为：
  - `use_knowledge=false` 不触发 retrieval。
  - 显式 `context_artifact_ids` 仍进入 AI task context manifest。
  - adapter 未配置或无命中时 `used_knowledge=false`，不写
    `knowledge_retrieval` artifact。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Task 5：Add retrieval evidence
  frontend display。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py -q
git diff --check
```

验证结果：

- `16 passed`。
- `git diff --check` clean。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 在 RAG 知识库前端展示 deterministic retrieval evidence。
- 前端只展示已有 evidence，不新增 vector search、provider runtime config、
  MCP runtime、RBAC、tenants、permissions、marketplace 或 remote sync 控件。

## 2026-06-30 Slice 19 Task 3 完成

本轮完成：

- 完成 Slice 19 Task 3：Add local KnowledgeAdapter retrieval service。
- 新增 deterministic local retrieval service：
  - 读取同项目 ContextArtifact。
  - 仅匹配 `safe_to_show=true` 且 `allowed_for_prompt=true` 的上下文。
  - 使用确定性关键词重合匹配，支持英文和中文词项。
  - 返回 bounded snippet、score、matched terms、ContextArtifact id、SHA256、
    redaction 和 prompt eligibility 信息。
- 新增
  `POST /api/projects/{project_id}/knowledge-adapter/retrieve`，供后续
  workflow/frontend 使用。
- 允许 KnowledgeAdapterConfig 使用 V2
  `provider_type=deterministic_local`，但更新配置本身仍保持
  `used_knowledge=false`。
- 新增 `backend/app/tests/api/test_deterministic_knowledge_retrieval.py`：
  覆盖 service、API、禁用/未配置 adapter、配置入口和中文 query terms。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Task 4：Attach retrieval evidence
  to AI task flows。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py -q
git diff --check
```

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 把 deterministic retrieval 接入 requirement review。
- AITask 只有在 retrieved snippets 实际用于 prompt 时才记录
  `used_knowledge=true`。
- 需要写 `knowledge_retrieval` evidence artifact，并记录 query terms、
  matched terms、scores、snippets、ContextArtifact ids。
- 继续排除 frontend、vector database、embeddings、reranking、background
  indexing、external RAG provider、MCP runtime、RBAC、tenants、permissions 或
  marketplace。

## 2026-06-30 Slice 19 Task 2 完成

本轮完成：

- 完成 Slice 19 Task 2：Define deterministic retrieval contract boundary。
- 更新 `docs/contracts/01-data-model-contract.md`：
  - AITask `input_json` / `output_json` 记录 deterministic retrieval 约定。
  - KnowledgeAdapterConfig `provider_type` 增加 V2
    `deterministic_local` 受限模式。
  - Artifact type 增加 `knowledge_retrieval`。
- 更新 `docs/contracts/02-api-contract.md`：
  - `use_knowledge=true` 只在 deterministic local retrieval 有证据时允许。
  - RAG 知识库 surface 可展示 latest retrieval evidence。
  - KnowledgeAdapter config 可配置本地 deterministic matching 参数。
- 更新 `docs/contracts/03-state-machines.md`：
  - retrieval 不新增 AITask 状态，只写 evidence artifact。
  - `disabled` / `not_configured` 强制 `used_knowledge=false`。
- 更新 `docs/contracts/04-artifact-contract.md`：
  - 增加 `knowledge_retrieval.json` 路径和 artifact shape。
  - 记录 query terms、matched terms、scores、snippets、ContextArtifact ids。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Task 3：Add local
  KnowledgeAdapter retrieval service。

本轮验证：

```bash
rg -n "Deterministic|KnowledgeAdapter|ContextArtifact|used_knowledge|retrieval|retrieved" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
git diff --check
```

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 新增 deterministic retrieval backend service 和 focused
  tests。
- 不要加入 frontend、vector database、embeddings、reranking、background
  indexing、external RAG provider、MCP runtime、RBAC、tenants、permissions 或
  marketplace。

## 2026-06-30 Slice 19 Task 1 完成

本轮完成：

- 完成 Slice 19 Task 1：Add Deterministic Knowledge Retrieval task plan。
- 新增
  `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`。
- 将 Slice 19 收敛为本地 deterministic ContextArtifact retrieval stub：
  - 只读取同项目已有 ContextArtifact。
  - 只匹配 safe_to_show 且 allowed_for_prompt 的上下文。
  - 使用确定性关键词/精确匹配，不使用向量库或外部 provider。
  - 记录 retrieved ContextArtifact ids、snippets、scores、matched terms。
  - `used_knowledge=true` 只允许在 deterministic local stub 实际使用证据时出现。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Task 2：Define deterministic
  retrieval contract boundary。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 更新四份 contracts。
- 先定义 retrieval evidence artifact、`used_knowledge=true` 条件、API/状态边界，
  再写产品代码。
- 继续排除 vector database、embeddings、reranking、background indexing、
  external RAG provider、MCP runtime、RBAC、tenants、permissions、marketplace。

## 2026-06-30 V2 Task 3 完成

本轮完成：

- 完成 V2 Task 3：Select next small V2 slice。
- 更新 `docs/implementation/10-v2-scope-options.md`：
  - 记录 Slice 18 Newman API Execution 已完成。
  - 推荐下一条小切片为
    `Slice 19: Deterministic Knowledge Retrieval Stub`。
  - 明确这是本地确定性 ContextArtifact retrieval stub，不是完整 RAG 平台。
  - 继续排除 vector database、embeddings、reranking、background indexing、
    external RAG provider、MCP runtime、RBAC、tenants、permissions、
    marketplace、remote CI/CD provider integration。
- 已将 `NEXT_AI_TASK.md` 切换到 V2 Task 4：Draft Slice 19 Deterministic
  Knowledge Retrieval Stub plan。

下次推荐任务：

- 起草
  `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`。
- 只做计划，不新增产品代码。
- 先定义 contracts、artifacts、API 行为、frontend evidence display 和
  non-goals，再开始实现。

## 2026-06-30 Slice 18 Completion Gate 完成

本轮完成：

- 完成 Slice 18：Newman API Execution。
- 更新 `docs/implementation/slices/slice-18-newman-api-execution.md`：
  - 所有任务行标记 done。
  - 记录 completion evidence。
  - 记录 Newman API + golden、frontend、diff 验证结果。
- 已将 `NEXT_AI_TASK.md` 切换到 V2 Task 3：Select next small V2 slice。

最终验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_newman_execution.py backend/app/tests/golden/test_newman_api_execution_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Newman API + golden tests：`5 passed`。
- Frontend suite：`15` test files passed，`18` tests passed。
- `git diff --check` clean。

Slice 18 结果：

- Newman API execution 已作为 allowlisted local TestCommand 路径接入。
- `command_type=newman`，`runner_mode=newman_local`。
- 证据包含 TestRun、assertion-level TestResult、stdout/stderr、
  `newman_json`、`parsed_output`。
- 前端新增 `API 执行` 页面，只展示 TestCommand-based Newman evidence。
- Golden smoke 覆盖 deterministic Newman collection 和一个可见失败断言。
- 未加入 arbitrary shell、Postman cloud/workspace/editor、remote CI/CD、
  RAG/MCP runtime、RBAC、tenants、permissions、marketplace、release 或
  deployment automation。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 V2 Task 3：Select next small V2 slice。
- 优先从 `docs/implementation/10-v2-scope-options.md` 中选择小切片；如产品优先级
  不清楚，先停在规划评审，不直接加新功能。

## 2026-06-30 Slice 18 Task 5 完成

本轮完成：

- 完成 Slice 18 Task 5：Add Newman API execution golden smoke。
- 新增 `backend/app/tests/golden/test_newman_api_execution_golden.py`。
- 新增 `docs/fixtures/07-newman-api-execution-golden.md`。
- Golden path 覆盖：
  - Project。
  - `TestCommand.command_type=newman`。
  - `TestRun.runner_mode=newman_local`。
  - stdout/stderr、`newman_json`、`parsed_output` artifacts。
  - assertion-level TestResult。
  - failed assertion 作为证据可见。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 18 Completion Gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_newman_api_execution_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_newman_execution.py backend/app/tests/golden/test_newman_api_execution_golden.py -q
git diff --check
```

验证结果：

- Newman golden smoke：`1 passed`。
- Newman API + golden：`5 passed`。
- `git diff --check` clean。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 18 completion gate。
- 只记录完成证据和下一步，不新增产品行为。

## 2026-06-30 Slice 18 Task 4 完成

本轮完成：

- 完成 Slice 18 Task 4：Add Newman API execution frontend shell。
- 新增 `frontend/src/views/execution/NewmanExecutionView.vue`：
  - 中文页面标题 `API 执行`。
  - 只接受 TestCommand ID，不展示 AutomationDraft 入口。
  - 使用 `runner_mode=newman_local`。
  - 展示集合名、状态、退出码、耗时、请求数、断言数。
  - 展示 `newman_json`、`parsed_output`、stdout/stderr/JUnit 工件。
  - 展示断言级 TestResult 和失败信息。
- 新增 `frontend/src/views/execution/NewmanExecutionView.spec.ts`。
- 更新 router 和导航，加入 `execution/newman` / `API 执行`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 18 Task 5：Add Newman API execution
  golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Frontend suite：`15` test files passed，`18` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 新增 Newman golden smoke 和 fixture 文档。
- 继续保持 deterministic local fixture，不加入 Postman cloud、collection
  editor、remote CI/CD、RAG/MCP runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 18 Task 3 完成

本轮完成：

- 完成 Slice 18 Task 3：Add Newman runner/parser backend。
- 新增 `backend/app/modules/execution/newman_runner.py`：
  - 校验 `npx newman run ...` allowlist。
  - 禁止 shell chaining、redirection、substitution、pipes 等任意 shell 行为。
  - 解析 Newman JSON reporter 输出。
  - 将 request/assertion 映射为 TestResult candidate。
- 更新 `backend/app/modules/execution/service.py`：
  - `runner_mode=newman_local` 分支。
  - TestRun/TestResult 持久化。
  - stdout/stderr、`newman_json`、`parsed_output` artifacts。
- 更新 `backend/app/modules/projects/service.py`：
  - TestCommand allowlist 支持 `command_type=newman`。
- 新增 `backend/app/tests/api/test_newman_execution.py`：
  - fake `npx` deterministic fixture。
  - runner parse/rejection tests。
  - `/api/test-runs` Newman command execution测试。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 18 Task 4：Add Newman API execution
  frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_newman_execution.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/api/test_playwright_minimal_loop.py backend/app/tests/api/test_test_commands.py -q
git diff --check
```

验证结果：

- Newman focused API tests：`4 passed`。
- 相邻 execution/project tests：`27 passed`。
- `git diff --check` clean。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 增加 Newman API 执行前端页面。
- 页面只展示执行证据和 artifact，不做 collection editor、secret manager、
  remote CI/CD、Postman cloud 或 marketplace。

## 2026-06-30 Slice 18 Task 2 完成

本轮完成：

- 完成 Slice 18 Task 2：Define Newman execution contract boundary。
- 更新 `docs/contracts/01-data-model-contract.md`：
  - `TestCommand.command_type` 增加 `newman`。
  - `TestRun.runner_mode` 增加 `newman_local`。
  - 定义 Newman TestRun/TestResult 解析字段和脱敏规则。
  - 定义 `newman_collection_run` ToolDefinition allowlist 边界。
- 更新 `docs/contracts/02-api-contract.md`：
  - Newman 复用 `/api/test-runs`。
  - 不新增 `POST /api/newman-runs`。
  - 定义 Newman request rules、parsed_result shape 和 artifact response。
- 更新 `docs/contracts/03-state-machines.md`：
  - Newman 仍走 ToolInvocation allowlist。
  - Newman assertion failure 映射为 TestRun `failed`。
  - 启动、超时、allowlist、解析器错误映射为 `error` 或 `timeout`。
- 更新 `docs/contracts/04-artifact-contract.md`：
  - 增加 `newman_json` artifact type。
  - 明确 `parsed_output`、optional `junit`、脱敏和非触发规则。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 18 Task 3：Add Newman
  runner/parser backend。

本轮验证：

```bash
rg -n "Newman|newman|newman_json|command_type|ToolDefinition" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-18-newman-api-execution.md
git diff --check
```

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 新增 Newman backend runner/parser。
- 先写 `backend/app/tests/api/test_newman_execution.py` 的确定性 fixture 测试。
- 不要加入 frontend、Postman cloud、collection editor、remote CI/CD、RAG/MCP
  runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 18 Task 1 完成

本轮完成：

- 完成 Slice 18 Task 1：Add Newman API Execution task plan。
- 新增 `docs/implementation/slices/slice-18-newman-api-execution.md`。
- 将第一个 V2 slice 收敛为 Newman API execution evidence：
  - approved `TestCommand.command_type=newman`。
  - ToolDefinition/TestCommand allowlist。
  - stdout/stderr、Newman JSON、parsed_result、TestResult evidence。
  - API 执行页面只展示执行证据，不做 Postman workspace parity。
- 明确排除 arbitrary shell、Postman cloud/editor、remote CI/CD provider、
  runner marketplace、RAG/MCP runtime、RBAC、tenants、permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 18 Task 2：Define Newman execution
  contract boundary。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 更新四份 contracts。
- 先定义 `command_type=newman`、Newman artifact、parsed result 和
  ToolDefinition allowlist 边界，再写产品代码。

## 2026-06-30 Frontend Chinese Copy Review 完成

本轮按用户反馈完成：

- 保留 `Prompt`、`Skill`、`PromptVersion`、`SkillVersion`、`Agent`、
  `AutomationDraft`、`TestCommand`、`TestRun`、`ContextArtifact`、
  `ToolDefinition` 等产品/模型术语。
- 将页面里的普通英文说明和指标文案中文化，包括：
  - 需求评审、用例生成评审、用例库。
  - 自动化草稿中心。
  - pytest 执行中心与 Playwright 执行。
  - CI/CD 质量中心。
  - 报告中心。
  - RAG 知识库。
  - 项目设置。
  - Prompt / Skill 中心状态和必填契约显示。
- 为后端枚举增加前端显示层中文映射，不改变 API 数据：
  - passed/failed/pending/analyzed 等状态。
  - high/medium/low 等风险。
  - functional/ui/api 等用例类型。
  - approved_after_edit 等评审状态。
  - source/modified/source file changed 等 CI/CD 变更字段。
- 同步更新前端组件测试断言。

本轮验证：

```bash
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Frontend：`14` test files passed，`17` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 回到 `NEXT_AI_TASK.md`：V2 Task 2，起草 Slice 18 Newman API Execution
  plan。

## 2026-06-30 V2 Task 1 完成

本轮完成：

- 完成 V2 Task 1：Draft V2 scope options。
- 新增 `docs/implementation/10-v2-scope-options.md`。
- 规划 4 个候选方向：
  - RAG Knowledge Runtime。
  - Tool And Runner Expansion。
  - Team Review And Governance。
  - CI/CD Integration Bridge。
- 推荐第一条 V2 slice：`Slice 18: Newman API Execution`。
- 保留仍需显式提升的 out-of-scope：full RAG platform、MCP runtime、
  RBAC/tenants、remote CI/CD control、broad dashboards 等。
- 已将 `NEXT_AI_TASK.md` 切换到 V2 Task 2：Draft Slice 18 Newman API
  Execution plan。

下次推荐任务：

- 起草 `docs/implementation/slices/slice-18-newman-api-execution.md`。
- 先定义 slice 计划，不直接新增产品代码。

## 2026-06-30 Post-V1 Task 4 完成

本轮完成：

- 完成 Post-V1 Task 4：Optional frontend screenshot capture or V2 planning。
- 本地 web 已在 `http://localhost:5174/` 可访问。
- 通过内置浏览器捕获 release screenshots：
  - `docs/release/v1/screenshots/ai-workbench.png`
  - `docs/release/v1/screenshots/cicd-quality-center.png`
  - `docs/release/v1/screenshots/report-center.png`
  - `docs/release/v1/screenshots/rag-knowledge-base.png`
- 更新 `docs/release/v1/README.md` 链接截图。
- 已将 `NEXT_AI_TASK.md` 切换到 V2 Task 1：Draft V2 scope options。

下次推荐任务：

- 起草 `docs/implementation/10-v2-scope-options.md`。
- 只做 V2 scope options，不直接加入产品代码或运行时扩张。

## 2026-06-30 Post-V1 Task 3 完成

本轮完成：

- 完成 Post-V1 Task 3：Write V1 manual walkthrough and acceptance evidence
  details。
- 扩展 `docs/release/v1/manual-walkthrough.md` 为 release-ready checklist，
  覆盖项目上下文、需求评审、用例生成、AutomationDraft、pytest execution、
  failure analysis/report、CI/CD Quality Center 和 extension surfaces。
- 扩展 `docs/release/v1/acceptance-evidence.md`，加入 release status、
  blocker status、coverage table、evidence chain 和 non-goals。
- 更新 `docs/release/v1/README.md`，链接 release packaging decision。
- 已将 `NEXT_AI_TASK.md` 切换到 Post-V1 Task 4：Optional frontend
  screenshot capture or V2 planning。

下次推荐任务：

- 决定是否捕获前端截图；如果不需要截图，则将 release package 标记为文档
  complete 并切入 V2 planning。

## 2026-06-30 Post-V1 Task 2 完成

本轮完成：

- 完成 Post-V1 Task 2：Create V1 release package skeleton。
- 新增 `docs/release/v1/README.md`。
- 新增 `docs/release/v1/acceptance-evidence.md`。
- 新增 `docs/release/v1/manual-walkthrough.md`。
- 新增 `docs/release/v1/screenshots/.gitkeep` 作为可选截图目录占位。
- Release package skeleton 链接 V1 acceptance evidence，并保留 V1 non-goals。
- 已将 `NEXT_AI_TASK.md` 切换到 Post-V1 Task 3：Write V1 manual walkthrough
  and acceptance evidence details。

下次推荐任务：

- 扩展 `docs/release/v1/manual-walkthrough.md` 和
  `docs/release/v1/acceptance-evidence.md`，写成 release-ready 文档。

## 2026-06-30 Post-V1 Task 1 完成

本轮完成：

- 完成 Post-V1 Task 1：Decide release packaging and demo artifact strategy。
- 新增 `docs/implementation/09-post-v1-release-packaging-plan.md`。
- 决策：V1 自动化验收采用当前 composable golden suite；不在 V1 packaging 前
  新增大型 narrative E2E 自动化测试。
- 决策：补轻量 release package，包含 release note、manual walkthrough、
  acceptance evidence，截图作为可选材料。
- 更新 `docs/implementation/08-v1-final-acceptance-handoff.md` 的剩余决策。
- 已将 `NEXT_AI_TASK.md` 切换到 Post-V1 Task 2：Create V1 release package
  skeleton。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 创建 `docs/release/v1/` 文档骨架。
- 继续保持 documentation-only，不加入 RAG runtime、MCP runtime、RBAC、
  tenants、permissions 或 remote CI provider integration。

## 2026-06-30 V1 Completion Review Task 4 完成

本轮完成：

- 完成 V1 Completion Review Task 4：Prepare final V1 acceptance handoff。
- 新增 `docs/implementation/08-v1-final-acceptance-handoff.md`。
- 汇总 V1 release recommendation：`GO`。
- 链接 completion audit、release acceptance report、V1 release spine 和产品
  scope。
- 记录 automated evidence：
  - Backend V1 golden release-acceptance suite：`10 passed`。
  - Frontend workbench suite：`14` test files passed，`17` tests passed。
  - `git diff --check` clean。
- 记录剩余非阻塞决策：是否补单一叙事型 E2E demo、是否为 release notes
  增加截图、是否清理旧 slice task table 的 stale pending commit 文字。
- 已将 `NEXT_AI_TASK.md` 切换到 Post-V1 Task 1：Decide release packaging and
  demo artifact strategy。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Post-V1 Task 1。
- 先做 release packaging 决策，不直接加入 RAG runtime、MCP runtime、RBAC、
  tenants、permissions 或 remote CI provider integration。

## 2026-06-30 V1 Completion Review Task 3 完成

本轮完成：

- 完成 V1 Completion Review Task 3：Fix full-suite golden isolation
  assertions。
- 只修改 5 个 historical golden smoke 的断言，不修改产品代码。
- 将旧的 later-slice table absence assertions 改为 row/behavior absence
  assertions：
  - AutomationDraft flow 不创建 `TestRun`、`TestResult`、`Report` rows。
  - Pytest runner flow 不创建 `Report`、`QualityGateDecision` rows。
  - Playwright runner flow 不创建 `Report`、`FailureAnalysis`、
    `QualityGateDecision` rows。
  - Report/FailureAnalysis flow 不创建 `QualityGateDecision` rows。
  - CI/CD Quality Center analysis flow 不创建 `QualityGateDecision` rows。
- 更新 `docs/implementation/07-v1-release-acceptance.md`，release
  recommendation 从 `NO-GO` 更新为 `GO`。
- 已将 `NEXT_AI_TASK.md` 切换到 V1 Completion Review Task 4：Prepare final
  V1 acceptance handoff。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py backend/app/tests/golden/test_extension_surface_golden.py -q
```

验证结果：

- 原失败 golden smokes：`5 passed`。
- V1 full golden release-acceptance suite：`10 passed`。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 V1 Completion Review Task 4。
- 创建最终 V1 acceptance handoff，整理 release evidence 和剩余非阻塞风险。

## 2026-06-30 V1 Completion Review Task 2 完成

本轮完成：

- 完成 V1 Completion Review Task 2：Run V1 release acceptance。
- 新增 `docs/implementation/07-v1-release-acceptance.md`。
- 后端 V1 full golden release-acceptance suite 首次运行结果为 `5 failed,
  5 passed`。
- 前端 Vitest release check 通过：`14` test files passed，`17` tests
  passed。
- `git diff --check` clean。
- 已将 release recommendation 标记为 `NO-GO`。
- 已将 `NEXT_AI_TASK.md` 切换到 V1 Completion Review Task 3：Fix
  full-suite golden isolation assertions。

阻塞原因：

- 5 个历史 slice golden smoke 使用 `test_runs`、`reports`、
  `quality_gate_decisions` 等“表不存在”断言来证明 later-slice behavior 未被
  涉及。
- 完整 V1 应用在 release acceptance 中会先注册全部 SQLAlchemy models，再
  `Base.metadata.create_all`，所以 later-slice tables 会存在。
- 应保留原意，但改为断言没有相关 rows 或 behavior 被当前 flow 创建。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 V1 Completion Review Task 3。
- 只修复 golden isolation assertions，不修改产品代码。
- 修复后重新运行完整 release-acceptance verification command set。

## 2026-06-30 V1 Completion Review Task 1 完成

本轮完成：

- 完成 V1 Completion Review Task 1：Audit V1 completion evidence and remaining
  gaps。
- 新增 `docs/implementation/06-v1-completion-audit.md`。
- 审计已实现闭环：Requirement To Case、Case To Automation Evidence、CI/CD
  Quality Center、Extension Surface、Frontend Shells。
- 记录可用 verification commands 和推荐 V1 release-acceptance command set。
- 记录 remaining gaps：是否需要单一端到端 V1 demo、ToolInvocation 链接、
  runtime artifact 期望、旧 slice 表 pending commit 文档清理、release
  acceptance report。
- 已将 `NEXT_AI_TASK.md` 切换到 V1 Completion Review Task 2：Run V1 release
  acceptance。

本轮验证：

```bash
test -f docs/implementation/06-v1-completion-audit.md && rg -n "Implemented|Remaining gaps|Verification|Next task" docs/implementation/06-v1-completion-audit.md
git diff --check
```

验证结果：

- V1 completion audit exists and names evidence, gaps, verification, and next
  task。
- `git diff --check` clean。

修改文件：

- `docs/implementation/06-v1-completion-audit.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 V1 Completion Review Task 2：Run V1 release
  acceptance。
- 该任务只运行和记录 release acceptance，不新增产品代码。

## 2026-06-30 Slice 17 Completion Gate 完成

本轮完成：

- 完成 Slice 17 completion gate。
- 确认 Slice 17 所有任务均为 `done`，并记录提交号：
  `73a1885`、`f2812cf`、`afffbc9`、`fbbde4f`、`b1d8f5d`、
  `94fbf21`、`2322e42`。
- 完成组合验收：Extension Surface API、golden smoke、frontend shell 均已
  覆盖。
- 已在 `docs/implementation/slices/slice-17-extension-surface.md` 写入
  completion evidence。
- 已在 `memory/07-dev-log.md` 写入 Slice 17 completion log。
- 已将 `NEXT_AI_TASK.md` 切换到 V1 Completion Review Task 1：Audit V1
  completion evidence and remaining gaps。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_extension_surface_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Extension Surface API + golden smoke：`6 passed`
- Frontend shell：`14 passed`，`17 tests passed`
- `git diff --check` clean

Slice 17 保持的非目标：

- 未加入 vector index、embedding、reranking 或外部 RAG provider。
- 未加入 MCP server/client runtime、remote MCP call 或插件市场。
- 未加入 RBAC、tenants、permissions、marketplace、cloud sync。
- 未触发 release、deployment 或 remote CI provider integration。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 V1 Completion Review Task 1。
- 这是 audit-only 任务，先梳理 V1 completion evidence 和 remaining gaps，
  不直接新增产品代码。

## 2026-06-30 Slice 17 Task 7 Extension Surface Golden Smoke 完成

本轮完成：

- 完成 Slice 17 Task 7：Add Extension Surface golden smoke。
- 新增 `docs/fixtures/06-extension-surface-golden.md`。
- 新增 `backend/app/tests/golden/test_extension_surface_golden.py`。
- Golden smoke 验证 Project -> ContextArtifact -> AITask
  `context_artifact_ids` -> KnowledgeAdapter empty state -> RAG 知识库 surface
  -> MCP-ready ToolDefinition schema。
- 验证 `used_knowledge=false`，同时 `used_context_artifact_ids` 正确记录。
- 验证 ToolDefinition 仅暴露 schema/readiness，不包含 MCP server URL 或
  transport。
- 验证没有 `rag_indexes`、`embeddings`、`mcp_servers`、`mcp_clients`、
  `tenants`、`roles`、`permissions` 表。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_extension_surface_golden.py -q
git diff --check
```

验证结果：

- Extension Surface golden smoke：`1 passed`
- `git diff --check` clean。

修改文件：

- `backend/app/tests/golden/test_extension_surface_golden.py`
- `docs/fixtures/06-extension-surface-golden.md`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 completion gate。
- 组合验证 backend extension API、golden smoke 和 frontend tests，记录
  completion evidence，再选择下一 V1 任务。

## 2026-06-30 Slice 17 Task 6 RAG 知识库 Frontend Shell 完成

本轮完成：

- 完成 Slice 17 Task 6：Add RAG 知识库 frontend shell。
- 新增 `frontend/src/api/extension.ts` 和 `frontend/src/stores/extension.ts`。
- 新增 `frontend/src/views/extension/KnowledgeBaseView.vue` 与组件测试。
- 在导航中加入 `RAG 知识库` 页面。
- 页面展示 ContextArtifact inventory、safe_to_show、allowed_for_prompt、
  usage_count、KnowledgeAdapter 状态、non-goals 和 MCP-ready ToolDefinition
  readiness。
- 按用户验收反馈优化 `AI 工作台`：最近 AI 任务和任务详情改为上下布局，
  避免左右挤压；将主要英文标签中文化。
- 同步中文化全局 `Mock Provider`、`Evidence Loop`、
  `Prompt / Skill 中心` 等可见文案。
- 未加入 vector search、RAG runtime、MCP runtime、marketplace、cloud sync、
  RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 7：Add Extension Surface
  golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Frontend：`14 passed`，`17 tests passed`
- `git diff --check` clean。
- Web 验收：`http://localhost:5174/` 和 `RAG 知识库` 页面均可打开；
  AI 工作台已为上下布局。

修改文件：

- `frontend/src/api/extension.ts`
- `frontend/src/stores/extension.ts`
- `frontend/src/views/extension/KnowledgeBaseView.vue`
- `frontend/src/views/extension/KnowledgeBaseView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `frontend/src/styles/global.css`
- `frontend/src/layouts/WorkbenchLayout.vue`
- `frontend/src/layouts/WorkbenchLayout.spec.ts`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 7：Add Extension Surface golden
  smoke。
- Golden smoke 应证明 ContextArtifact、KnowledgeAdapter empty state、
  MCP-ready ToolDefinition schema 和 AI task context evidence 串联可用，
  同时确认没有 RAG/MCP runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 17 Task 5 MCP-ready Tool Schema 完成

本轮完成：

- 完成 Slice 17 Task 5：Add MCP-ready ToolDefinition schema metadata。
- 新增 `ToolDefinition` model，用于保存 tool schema、risk、approval、
  allowlist、artifact policy、`is_mcp_ready` 和 `mcp_metadata_json`。
- 新增 `GET /api/projects/{project_id}/tool-definitions`。
- API 返回 built-in/project ToolDefinition schema/readiness。
- `tool_type=mcp_proxy` 仅作为 schema intent 展示，不触发 MCP runtime。
- 未加入 MCP server/client 包、远程 MCP 调用、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 6：Add RAG 知识库 frontend
  shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q
git diff --check
```

验证结果：

- `5 passed`
- `git diff --check` clean。

修改文件：

- `backend/app/modules/extension/__init__.py`
- `backend/app/modules/extension/models.py`
- `backend/app/modules/extension/router.py`
- `backend/app/modules/extension/schemas.py`
- `backend/app/modules/extension/service.py`
- `backend/app/tests/api/test_extension_surface.py`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 6：Add RAG 知识库 frontend shell。
- 前端使用浅色工作台 UI，展示 ContextArtifact、KnowledgeAdapter 和
  MCP-ready ToolDefinition readiness，不加入 vector search、RAG runtime、MCP
  runtime、marketplace、cloud sync、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 17 Task 4 Knowledge Base Context API 完成

本轮完成：

- 完成 Slice 17 Task 4：Add RAG 知识库 ContextArtifact API shell。
- 新增 `GET /api/projects/{project_id}/knowledge-base`。
- 返回 KnowledgeAdapter 状态、ContextArtifact inventory、source_ref、
  MIME type、redaction、allowed_for_prompt、usage_count、latest_used_at。
- usage 只从 `AITask.context_artifact_ids` 聚合，不新增单独知识库表。
- 返回 non_goals：`no_vector_index`、`no_embedding`、`no_reranking`、
  `no_external_rag_runtime`。
- 未加入 semantic search、embedding、vector index、reranking 或外部 RAG
  provider 调用。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 5：Add MCP-ready
  ToolDefinition schema metadata。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q
git diff --check
```

验证结果：

- `4 passed`
- `git diff --check` clean。

修改文件：

- `backend/app/modules/extension/router.py`
- `backend/app/modules/extension/schemas.py`
- `backend/app/modules/extension/service.py`
- `backend/app/tests/api/test_extension_surface.py`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 5：Add MCP-ready ToolDefinition
  schema metadata。
- 该任务只补 ToolDefinition schema/readiness，不加入 MCP runtime、remote MCP
  调用、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 17 Task 3 KnowledgeAdapter Shell 完成

本轮完成：

- 完成 Slice 17 Task 3：Add KnowledgeAdapter empty interface/schema。
- 新增 `backend/app/modules/extension` 模块。
- 新增 `KnowledgeAdapterConfig` model、read/update schema、service 和 router。
- 新增 `GET /api/projects/{project_id}/knowledge-adapter`，未配置时返回
  `not_configured`、`provider_type=none`、`used_knowledge=false`。
- 新增 `PUT /api/projects/{project_id}/knowledge-adapter`，只允许 `none/stub`
  provider 和 `not_configured/disabled/configured_stub` 状态。
- 拒绝 `api_key`、vector DB、embedding、reranker、remote URL、MCP transport
  等运行时配置。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 4：Add RAG 知识库
  ContextArtifact API shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q
git diff --check
```

验证结果：

- `3 passed`
- `git diff --check` clean。

修改文件：

- `backend/app/main.py`
- `backend/app/modules/extension/__init__.py`
- `backend/app/modules/extension/models.py`
- `backend/app/modules/extension/router.py`
- `backend/app/modules/extension/schemas.py`
- `backend/app/modules/extension/service.py`
- `backend/app/tests/api/test_extension_surface.py`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 4：Add RAG 知识库
  ContextArtifact API shell。
- 该任务继续复用 ContextArtifact，不建立单独知识库表，不加入 semantic
  search、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 17 Task 2 Extension Surface Contract Boundary 完成

本轮完成：

- 完成 Slice 17 Task 2：Add Extension Surface contract boundary。
- 在 data model contract 中定义 `KnowledgeAdapterStatus`、
  `KnowledgeAdapterConfig`、ToolDefinition MCP-ready metadata 边界。
- 在 API contract 中定义 RAG 知识库 surface、KnowledgeAdapter config、
  MCP-ready ToolDefinition schema API 边界。
- 在 state machine contract 中定义 KnowledgeAdapterConfig 状态机。
- 在 artifact contract 中明确 Extension Surface artifact rules。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 3：Add KnowledgeAdapter empty
  interface/schema。

本轮验证：

```bash
rg -n "KnowledgeAdapter|RAG 知识库|ToolDefinition|MCP-ready|Non-goals" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-17-extension-surface.md
git diff --check
```

验证结果：

- Slice 17 contracts name extension surface scope and non-goals。
- `git diff --check` clean。

修改文件：

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 3：Add KnowledgeAdapter empty
  interface/schema。
- 该任务只做 backend shell，不加入 RAG runtime、MCP runtime、RBAC、tenants
  或 permissions。

## 2026-06-30 Slice 17 Task 1 Extension Surface Plan 完成

本轮完成：

- 完成 Slice 17 Task 1：Add Extension Surface task plan。
- 新增 `docs/implementation/slices/slice-17-extension-surface.md`。
- 将 Slice 17 拆为 contract boundary、KnowledgeAdapter empty shell、RAG 知识库
  ContextArtifact API shell、MCP-ready ToolDefinition schema、frontend shell、
  golden smoke、completion gate。
- 明确 RAG 知识库是 ContextArtifact 管理和使用展示表面，不是内置 RAG
  runtime。
- 明确 KnowledgeAdapter 在 V1 只保留空接口/配置状态，不做 retrieval。
- 明确 MCP-ready 只落到 ToolDefinition schema metadata，不引入 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 2：Add Extension Surface
  contract boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-17-extension-surface.md && rg -n "KnowledgeAdapter|RAG 知识库|MCP-ready|Non-goals" docs/implementation/slices/slice-17-extension-surface.md
git diff --check
```

验证结果：

- Slice 17 planning document exists and names scope/non-goals。
- `git diff --check` clean。

修改文件：

- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 2：Add Extension Surface contract
  boundary。
- 该任务只更新 contracts 和 slice task plan，不写运行时代码，不加入 RAG
  runtime、MCP runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 16 Completion Gate 完成

本轮完成：

- 完成 Slice 16 completion gate。
- 确认 Slice 16 所有任务均为 `done`，并记录提交号：
  `c0db91c`、`c164d88`、`ae601ff`、`f8c4156`、`c22f6e5`、
  `824cb4b`、`f4bbc73`、`f6333c5`、`e27cc7b`、`e17ec01`、
  `b0ee6b8`。
- 完成组合验收：UnitTestPatch regression API、golden smoke、frontend shell
  均已覆盖。
- 已在 `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
  写入 completion evidence。
- 已在 `memory/07-dev-log.md` 写入 Slice 16 completion log。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 1：Add Extension Surface task
  plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- UnitTestPatch regression API + golden smoke：`23 passed`
- Frontend shell：`13 passed`，`16 tests passed`
- `git diff --check` clean

Slice 16 保持的非目标：

- 未触发 merge、push、release、deployment。
- 未集成 remote CI provider、webhooks、PR comments。
- 未加入 RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- UnitTestPatch 不允许修改业务源码。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 1：Add Extension Surface task plan。
- 这是 planning-only 任务，先创建
  `docs/implementation/slices/slice-17-extension-surface.md`，不要直接改产品代码。

## 2026-06-30 Slice 16 Task 11 UnitTestPatch Golden Smoke 完成

本轮完成：

- 完成 Slice 16 Task 11：Add UnitTestPatch golden smoke。
- 新增 `backend/app/tests/golden/test_unit_test_patch_regression_golden.py`。
- Golden smoke 使用 `docs/fixtures/03-golden-cicd-quality.md` 的 local diff
  和 UnitTestPatch 语义。
- 验证 local diff -> CICDRun -> risk analysis -> UnitTestPatch ->
  PatchScopeGate -> approve/apply -> new-test/regression TestRun ->
  QualityGateDecision -> CI/CD quality Report 完整链路。
- 验证 UnitTestPatch 只修改 `tests/test_coupon.py`，PatchScopeGate 通过。
- 验证没有 AutomationDraft，也没有 tenants/roles/permissions/RAG/MCP
  相关表行为。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q
```

验证结果：

- `1 passed`

修改文件：

- `backend/app/tests/golden/test_unit_test_patch_regression_golden.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 执行 Slice 16 completion gate：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q`
  和 `npm --prefix frontend run test -- --run`。
- 完成后记录 Slice 16 completion evidence，并寻找 Slice 17 或下一 V1
  优先级。

## 2026-06-30 Slice 16 Task 10 UnitTestPatch Frontend Shell 完成

本轮完成：

- 完成 Slice 16 Task 10：Add UnitTestPatch frontend shell。
- 扩展 `frontend/src/api/cicd.ts`，加入 UnitTestPatch generation/review、
  new-test/regression、QualityGateDecision、CI/CD quality report API 类型和调用。
- 扩展 `frontend/src/stores/cicd.ts`，集中管理 UnitTestPatch、review status、
  new TestRun、regression plan/run、quality gate、quality report 状态。
- 扩展 `CicdQualityCenterView.vue`，展示 UnitTestPatch diff、test intent、
  coverage target、PatchScopeGate result、new-test/regression evidence、
  QualityGateDecision 和 report artifact references。
- 前端支持 approve/reject 操作。
- 未暴露 merge、release、deployment、remote CI provider 或 PR controls。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 11：Add UnitTestPatch golden
  smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
```

验证结果：

- `13 passed`
- `16 tests passed`

修改文件：

- `frontend/src/api/cicd.ts`
- `frontend/src/stores/cicd.ts`
- `frontend/src/views/cicd/CicdQualityCenterView.vue`
- `frontend/src/views/cicd/CicdQualityCenterView.spec.ts`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 11：Add UnitTestPatch golden smoke。
- Golden smoke 需要证明 local diff -> UnitTestPatch -> tests/regression ->
  quality gate -> report evidence 的完整链路。

## 2026-06-30 Slice 16 Task 9 CI/CD Quality Report API 完成

本轮完成：

- 完成 Slice 16 Task 9：Add CI/CD quality report API。
- 新增 `POST /api/cicd/runs/{id}/generate-report`。
- 创建 `report_type=cicd_quality` 的 Report，关联 `related_entity_type=CICDRun`。
- Report conclusion 使用最新 QualityGateDecision status，不重算或覆盖
  `CICDRun.quality_gate_status`。
- 生成 `cicd_quality_evidence_manifest` artifact，引用 QualityGateDecision、
  UnitTestPatch/PatchScopeGate、new-test、regression 和 evidence artifacts。
- 当前任务未触发 merge/push/release/deployment/remote CI/PR comments。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 10：Add UnitTestPatch
  frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `22 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 10：Add UnitTestPatch frontend
  shell。
- 该任务只补前端 CI/CD Quality Center shell，不加入 merge/release/remote CI
  provider/PR controls。

## 2026-06-30 Slice 16 Task 8 QualityGateDecision API 完成

本轮完成：

- 完成 Slice 16 Task 8：Add QualityGateDecision API。
- 新增 `POST /api/cicd/runs/{id}/quality-gate`。
- 每次 compute 都创建新的 QualityGateDecision，并更新
  `CICDRun.quality_gate_status`。
- required evidence 缺失时返回 `needs_review`，不会误判为 `passed`。
- new-test 或 regression evidence 失败时返回 `failed`，并写入具体
  blocking reason。
- patch scope、applied UnitTestPatch、new-test、regression evidence 齐全且无
  failure 时返回 `passed`。
- 当前任务未触发 merge/push/release/deployment/remote CI/PR comments，也未创建
  Report。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 9：Add CI/CD quality report
  API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `21 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 9：Add CI/CD quality report API。
- 该任务只生成本地 evidence-backed Report，不重算/覆盖
  QualityGateDecision，不触发外部 CI 或 PR 行为。

## 2026-06-30 Slice 16 Task 7 New-Test/Regression API 完成

本轮完成：

- 完成 Slice 16 Task 7：Add new-test and regression API。
- 新增 `POST /api/cicd/runs/{id}/run-new-tests`，通过 allowlisted
  TestCommand 创建 `cicd_run_id` 已设置的 TestRun 证据。
- 当请求带 `unit_test_patch_id` 时，要求对应 UnitTestPatch 已为
  `applied` 状态。
- 新增 `POST /api/cicd/runs/{id}/select-regression`，写入
  `artifact_type=regression_plan`、`owner_entity_type=CICDRun` 的
  regression plan artifact metadata。
- 新增 `POST /api/cicd/runs/{id}/run-regression`，基于 regression plan 和
  allowlisted TestCommand 创建 CICD-linked TestRun 记录。
- 当前任务只排队/记录 TestRun evidence，不执行任意 shell 字符串，不计算
  QualityGateDecision，不创建 Report。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 8：Add
  QualityGateDecision API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `18 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 8：Add QualityGateDecision API。
- 该任务只计算本地 evidence-backed gate，不触发 merge/push/release/
  deployment/remote CI/PR comments，也不创建 Report。

## 2026-06-30 Slice 16 Task 6 UnitTestPatch Apply API 完成

本轮完成：

- 完成 Slice 16 Task 6：Add UnitTestPatch apply API。
- 新增 `POST /api/cicd/unit-test-patches/{id}/apply`。
- Apply 只允许 `approved` UnitTestPatch。
- Apply 前重新运行 PatchScopeGate；若 patch 修改非测试路径，返回
  `PATCH_SCOPE_REJECTED`，patch 状态变为 `apply_failed`，不写 artifact。
- 成功 apply 时 patch 状态变为 `applied`，并写入
  `artifact_type=unit_test_patch`、`owner_entity_type=UnitTestPatch` 的
  artifact metadata。
- Artifact metadata 保留原始 `patch_text` 和最新 `scope_gate_result`。
- 当前任务没有将 patch 应用到业务仓库文件，也没有运行测试命令，没有创建
  TestRun、QualityGateDecision 或 Report。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 7：Add new-test and
  regression API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `14 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 7：Add new-test and regression
  API。
- 该任务只创建 CICD-linked TestRun 和 regression_plan artifact evidence，
  不计算 QualityGateDecision，不创建 Report。

## 2026-06-30 Slice 16 Task 5 UnitTestPatch Generation/Review API 完成

本轮完成：

- 完成 Slice 16 Task 5：Add UnitTestPatch generation/review API。
- 新增 `POST /api/cicd/runs/{id}/unit-test-patches`，生成 deterministic
  mock UnitTestPatch candidate。
- 生成流程创建 succeeded mock `UnitTestAgent` AITask，写入
  `UnitTestPatch.scope_gate_result_json`，并返回 review UI 所需
  `scope_gate_result`。
- PatchScopeGate 通过时 patch 状态为 `scope_validated`，失败时为
  `scope_rejected`。
- 新增 approve/reject endpoints：
  `POST /api/cicd/unit-test-patches/{id}/approve` 与
  `POST /api/cicd/unit-test-patches/{id}/reject`。
- `scope_rejected` patch 不能 approve，会返回
  `UNIT_TEST_PATCH_INVALID_STATUS`。
- 任务未 apply patches，未运行测试命令，未创建 TestRun、
  QualityGateDecision 或 Report。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 6：Add UnitTestPatch apply
  API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `12 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 6：Add UnitTestPatch apply API。
- 该任务只能通过受控 service path apply 已批准且 scope gate 通过的测试
  patch；不能修改业务源码，不能运行测试命令。

## 2026-06-30 Slice 16 Task 4 PatchScopeGate Service 完成

本轮完成：

- 完成 Slice 16 Task 4：Add PatchScopeGate service。
- 新增 `evaluate_patch_scope()`，解析 UnitTestPatch unified diff 目标路径并返回
  `allowed`、`checked_paths`、`blocked_paths`、`forbidden_patterns`、
  `risk_level`、`reason`。
- 允许 `tests/`、`test/`、`__tests__/`、`test_*.py`、`*_test.py`、
  `.test.*`、`.spec.*` 等测试路径。
- 拒绝 source、config/build、migration、generated artifact、unknown
  non-test 路径，拒绝原因使用 `PATCH_SCOPE_REJECTED`。
- 修复审查发现的 generated 绕过风险：`dist/`、`coverage/`、`build/`
  等 generated 路径即使命名为 `.test/.spec` 也必须拒绝。
- 新增 `PatchScopeGateRead` schema，字段与 `patch_scope_gate.json`
  artifact metadata 对齐。
- 任务未 apply patches，未修改目标仓库文件，未运行 patch 内测试命令。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 5：Add UnitTestPatch
  generation/review API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `9 passed`

修改文件：

- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 5：Add UnitTestPatch
  generation/review API。
- 该任务只生成、校验、审批/拒绝 UnitTestPatch，不 apply patch，不运行测试。

## 2026-06-30 Slice 16 Task 3 UnitTestPatch/QualityGateDecision Model Schema 完成

本轮完成：

- 完成 Slice 16 Task 3：Add UnitTestPatch and QualityGateDecision
  model/schema。
- 新增 `UnitTestPatch` 模型，覆盖 `cicd_run_id`、`ai_task_id`、
  `patch_text`、`target_framework`、`scope_gate_result_json`、
  `test_intent`、`coverage_target_json`、`status`、`review_comment`。
- 新增 `QualityGateDecision` 模型，覆盖 `project_id`、`cicd_run_id`、
  `status`、`summary`、`blocking_reasons_json`、`evidence_artifact_ids`、
  `decided_by`、`status_detail_json`。
- 新增 UnitTestPatch / QualityGateDecision create/read schemas，使用 API
  层字段名 `scope_gate_result`、`coverage_target`、`blocking_reasons`、
  `status_detail`。
- 任务只做 persistence/schema，不 apply patches，不触发测试运行流程。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 4：Add PatchScopeGate
  service。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `4 passed`

修改文件：

- `backend/app/modules/cicd/models.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 4：Add PatchScopeGate service。
- 当前任务只做统一 diff 路径 scope gate，不 apply patches 或运行测试命令。

## 2026-06-30 Slice 16 Task 2 UnitTestPatch/Regression Contract Boundary 完成

本轮完成：

- 完成 Slice 16 Task 2：Add UnitTestPatch and regression contract boundary。
- 在数据模型合同中补充 UnitTestPatch review-gate、PatchScopeGate
  `scope_gate_result_json`、scope_rejected 不可 approve、applied patch
  evidence 规则。
- 在 API 合同中补充 UnitTestPatch generation/review/apply、run-new-tests、
  regression、QualityGateDecision、CI/CD quality report 的证据要求和非目标。
- 在状态机合同中补充 UnitTestPatch apply 前置条件和 QualityGateDecision
  不触发 merge/push/release/deployment/remote CI 行为。
- 在 artifact 合同中补充 `unit_test.patch`、`patch_scope_gate.json`、
  `regression_plan.json`、`quality_gate.json` 的 Slice 16 artifact rules。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 3：Add UnitTestPatch and
  QualityGateDecision model/schema。

本轮验证：

```bash
rg -n "UnitTestPatch|PatchScopeGate|QualityGateDecision|run-new-tests|run-regression" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

修改文件：

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 3：Add UnitTestPatch and
  QualityGateDecision model/schema。
- 当前任务只做 model/schema，不 apply patches 或 run tests。

## 2026-06-30 Slice 16 Task 1 UnitTestPatch/Regression Task Plan 完成

本轮完成：

- 完成 Slice 16 Task 1：Add UnitTestPatch And Regression task plan。
- 新增 `docs/implementation/slices/slice-16-unit-test-patch-regression.md`。
- 将 Slice 16 拆为 contract boundary、UnitTestPatch/QualityGateDecision
  model/schema、PatchScopeGate、patch generation/review、patch apply、
  new-test/regression API、QualityGateDecision API、CI/CD quality report API、
  frontend shell、golden smoke、completion gate。
- 明确 Slice 16 覆盖 review-gated UnitTestPatch、PatchScopeGate、pytest
  regression、QualityGateDecision 和 CI/CD quality report evidence。
- 明确不加入 merge/push/release/deployment、remote CI provider integration、
  RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 2：Add UnitTestPatch and
  regression contract boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-16-unit-test-patch-regression.md && rg -n "UnitTestPatch|PatchScopeGate|Verification Command|Non-goals" docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

修改文件：

- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 2：Add UnitTestPatch and regression
  contract boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 15 Completion Gate 完成

本轮完成：

- 完成 Slice 15 completion gate。
- 确认 Slice 15 所有任务均为 `done`，并记录提交号：
  `6133121`、`a8a5482`、`788d6c0`、`a0391fa`、`2e51d06`、
  `3a6df10`、`362ce0e`、`6e59820`。
- 完成组合验收：CI/CD Quality API、golden smoke、frontend shell 均已覆盖。
- 已在 `docs/implementation/slices/slice-15-cicd-quality-center.md` 写入
  completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 1：Add UnitTestPatch And
  Regression task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/golden/test_cicd_quality_center_golden.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- CI/CD Quality API + golden smoke：`8 passed`
- Frontend workbench shell：`13 passed, 16 tests passed`

Slice 15 保持的非目标：

- 未创建 UnitTestPatch、QualityGateDecision、TestRun 或 Report records。
- 未加入 merge/release decisions、remote CI provider integration、webhooks、
  PR comments、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 1：Add UnitTestPatch And
  Regression task plan。
- 这是 planning-only 任务，先创建
  `docs/implementation/slices/slice-16-unit-test-patch-regression.md`，不要直接改产品代码。

## 2026-06-30 Slice 15 Task 8 CI/CD Quality Golden Smoke 完成

本轮完成：

- 完成 Slice 15 Task 8：Add CI/CD Quality Center golden smoke。
- 新增 `backend/app/tests/golden/test_cicd_quality_center_golden.py`。
- Golden smoke 使用本地 diff 场景创建 Project/Repository fixture records。
- 通过 API 创建 CICDRun，验证 local_diff/manual/local、changed files 和
  pending quality_gate_status。
- 通过 API 触发 analyze，验证 succeeded AITask、risk_analysis artifact、
  analyzed status 和 medium overall_risk。
- 验证未创建 AutomationDraft、TestRun、Report 或 quality_gate_decisions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_center_golden.py -q
```

验证结果：

- CI/CD Quality Center golden smoke：`1 passed`

修改文件：

- `backend/app/tests/golden/test_cicd_quality_center_golden.py`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/golden/test_cicd_quality_center_golden.py -q && npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 15 Task 7 CI/CD Quality Frontend Shell 完成

本轮完成：

- 完成 Slice 15 Task 7：Add CI/CD Quality Center frontend shell。
- 新增 `frontend/src/api/cicd.ts`，覆盖 CICDRun create/get/list/analyze。
- 新增 `frontend/src/stores/cicd.ts`，管理 local_diff 输入、run 状态和
  analysis 刷新。
- 新增 `frontend/src/views/cicd/CicdQualityCenterView.vue`。
- 页面支持输入 Project/Repository/Base/Head/diff_text，创建 CICDRun 并触发
  mock risk_analysis。
- 页面展示 changed files、file_role、risk_level、risk_reasons 和
  risk_analysis artifact。
- CI/CD 质量中心导航由 `待接入` 更新为 `就绪`。
- 未展示 merge/release decisions 或 remote CI provider controls。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 8：Add CI/CD Quality Center
  golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
```

验证结果：

- Frontend workbench tests：`13 passed, 16 tests passed`

修改文件：

- `frontend/src/api/cicd.ts`
- `frontend/src/stores/cicd.ts`
- `frontend/src/views/cicd/CicdQualityCenterView.vue`
- `frontend/src/views/cicd/CicdQualityCenterView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 8：Add CI/CD Quality Center golden
  smoke。
- 当前任务不要创建 UnitTestPatch、QualityGateDecision、TestRun 或 Report
  records。

## 2026-06-30 Slice 15 Task 6 CI/CD Analyze API 完成

本轮完成：

- 完成 Slice 15 Task 6：Add CI/CD analyze API。
- 新增 `POST /api/cicd/runs/{id}/analyze`。
- Analyze 创建 succeeded AITask，`task_type=cicd_change_analysis`。
- Analyze 根据 changed_files 更新 CICDRun status 为 `analyzed`，
  overall_risk 为最高 changed file risk。
- 写入 `risk_analysis` artifact，owner 为 CICDRun，metadata 包含 provider、
  model、prompt、skill、overall_risk、changed_file_count 和 analysis_json。
- GET CI/CD run 会返回 analysis_artifacts。
- 未创建 UnitTestPatch、regression plan、QualityGateDecision、TestRun 或
  Report records。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 7：Add CI/CD Quality Center
  frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

验证结果：

- CI/CD Quality Center focused tests：`7 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_cicd_quality_center.py`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 7：Add CI/CD Quality Center
  frontend shell。
- 当前任务不要展示 merge/release decisions 或 remote CI provider controls。

## 2026-06-30 Slice 15 Task 5 CI/CD Run API 完成

本轮完成：

- 完成 Slice 15 Task 5：Add CI/CD run create/list/get API。
- 新增 `backend/app/modules/cicd/router.py` 并在 `backend/app/main.py`
  挂载 `/api/cicd`。
- `POST /api/cicd/runs` 支持 local_diff/manual/local 输入，解析 diff_text
  并持久化 CICDChangedFile rows。
- `GET /api/cicd/runs` 和 `GET /api/cicd/runs/{id}` 返回 changed_files。
- 创建 `diff_patch` 和 `changed_files` artifacts，owner 为 CICDRun。
- 未创建 UnitTestPatch、TestRun、QualityGateDecision 或 Report records。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 6：Add CI/CD analyze API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

验证结果：

- CI/CD Quality Center focused tests：`6 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_cicd_quality_center.py`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 6：Add CI/CD analyze API。
- 当前任务不要创建 UnitTestPatch、regression plan、QualityGateDecision、
  TestRun 或 Report records。

## 2026-06-30 Slice 15 Task 4 Local Diff Parser 完成

本轮完成：

- 完成 Slice 15 Task 4：Add local diff parser service。
- 新增 `backend/app/modules/cicd/service.py`。
- `parse_local_diff` 支持解析 modified、added、deleted、renamed unified
  diff file blocks。
- parser 可输出 `changed_files.json` 兼容的 manifest item。
- 支持按路径和扩展名确定 language 与 file_role：source、test、docs、
  config、migration、fixture、build、unknown。
- 支持基于 file_role、change_type 和变更行数生成 deterministic risk_level
  与 risk_reasons。
- 未调用远程 CI provider，也未执行 git remote 操作。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 5：Add CI/CD run
  create/list/get API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

验证结果：

- CI/CD Quality Center focused tests：`5 passed`

修改文件：

- `backend/app/modules/cicd/service.py`
- `backend/app/tests/api/test_cicd_quality_center.py`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 5：Add CI/CD run create/list/get
  API。
- 当前任务不要创建 UnitTestPatch、TestRun、QualityGateDecision 或 Report
  records。

## 2026-06-30 Slice 15 Task 3 CICDRun/CICDChangedFile Model Schema 完成

本轮完成：

- 完成 Slice 15 Task 3：Add CICDRun and CICDChangedFile model/schema。
- 新增 `backend/app/modules/cicd/` 模块。
- 新增 CICDRun model，覆盖 project、repository、source_type、
  trigger_type、provider、pipeline/base/head、summary、overall_risk、
  quality_gate_status 和 status。
- 新增 CICDChangedFile model，覆盖 path、old_path、change_type、language、
  file_role、risk_level、risk_reasons、lines_added、lines_deleted。
- 新增 create/read/list schemas，read schema 可嵌入 changed_files 和
  analysis_artifacts。
- 未创建 UnitTestPatch、QualityGateDecision、TestRun 或 Report records。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 4：Add local diff parser
  service。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

验证结果：

- CICDRun/CICDChangedFile model/schema tests：`4 passed`

修改文件：

- `backend/app/modules/cicd/__init__.py`
- `backend/app/modules/cicd/models.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_cicd_quality_center.py`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 4：Add local diff parser service。
- 当前任务只解析 local unified diff text，不调用远程 CI provider 或执行 git
  remote 操作。

## 2026-06-30 Slice 15 Task 2 CI/CD Quality Contract Boundary 完成

本轮完成：

- 完成 Slice 15 Task 2：Add CI/CD Quality Center contract boundary。
- 在数据模型合同中明确 CICDRun 的 Slice 15 边界：`local_diff` /
  `manual_check`、`trigger_type=manual`、`provider=local`，且
  `quality_gate_status` 在 Slice 15 保持 `pending`。
- 在 API 合同中明确 Slice 15 只实现 `/api/cicd/runs` create/list/get 和
  `/api/cicd/runs/{id}/analyze`。
- 将 UnitTestPatch、run-new-tests、regression、QualityGateDecision 和
  CI/CD quality report endpoints 标记为 Slice 16+ placeholder。
- 在 artifact 合同中定义 `diff.patch`、`changed_files.json`、
  `risk_analysis.json` 的 Slice 15 artifact 边界和 metadata 要求。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 3：Add CICDRun and
  CICDChangedFile model/schema。

本轮验证：

```bash
rg -n "CICDRun|CICDChangedFile|POST /api/cicd/runs|local_diff|remote CI" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-15-cicd-quality-center.md
```

修改文件：

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 3：Add CICDRun and CICDChangedFile
  model/schema。
- 当前任务只做 model/schema，不创建 UnitTestPatch、QualityGateDecision、
  TestRun 或 Report records。

## 2026-06-30 Slice 15 Task 1 CI/CD Quality Center Task Plan 完成

本轮完成：

- 完成 Slice 15 Task 1：Add CI/CD Quality Center task plan。
- 新增 `docs/implementation/slices/slice-15-cicd-quality-center.md`。
- 将 Slice 15 拆为 contract boundary、CICDRun/CICDChangedFile
  model/schema、local diff parser、run create/list/get API、analyze API、
  frontend shell、golden smoke、completion gate。
- 明确 Slice 15 只做 local-first CICDRun、CICDChangedFile、local diff
  analysis 和 evidence surface。
- 明确 UnitTestPatch、regression、QualityGateDecision、CI/CD quality report
  不在 Slice 15 实现。
- 明确不加入 merge/release decisions、remote CI provider integration、
  webhooks、PR comments、RAG runtime、MCP runtime、RBAC、tenants 或
  permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 2：Add CI/CD Quality Center
  contract boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-15-cicd-quality-center.md && rg -n "CI/CD Quality Center|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-15-cicd-quality-center.md
```

修改文件：

- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 2：Add CI/CD Quality Center
  contract boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 14 Completion Gate 完成

本轮完成：

- 完成 Slice 14 completion gate。
- 确认 Slice 14 所有任务均为 `done`，并记录提交号：
  `dcedd23`、`ee168bc`、`f9ebb7a`、`0f9a163`、`811316d`、
  `c4971a3`、`04b6425`。
- 完成组合验收：FailureAnalysis/Report API、golden smoke、frontend shell 均
  已覆盖。
- 已在 `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
  写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 1：Add CI/CD Quality Center
  task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py backend/app/tests/golden/test_report_failure_analysis_golden.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- Report/FailureAnalysis API + golden smoke：`9 passed`
- Frontend workbench shell：`12 passed, 15 tests passed`

Slice 14 保持的非目标：

- 未加入 CI/CD quality gates、merge/release decisions、RAG runtime、MCP
  runtime、RBAC、tenants、permissions 或 broad report analytics。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 1：Add CI/CD Quality Center task
  plan。
- 这是 planning-only 任务，先创建
  `docs/implementation/slices/slice-15-cicd-quality-center.md`，不要直接改产品代码。

## 2026-06-30 Slice 14 Task 7 Report/FailureAnalysis Golden Smoke 完成

本轮完成：

- 完成 Slice 14 Task 7：Add automation execution report golden smoke。
- 新增 `backend/app/tests/golden/test_report_failure_analysis_golden.py`。
- golden smoke 种子化 failed TestRun、stderr artifact 和 failed TestResult。
- 通过 API 创建 FailureAnalysis，并验证分类为 `test_script_issue`、
  AITask 为 `succeeded`。
- 通过 API 创建 automation_execution Report，并验证 conclusion、metrics、
  evidence_manifest、report artifacts 和持久化 metadata。
- 验证没有创建 `quality_gate_decisions` 表。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_report_failure_analysis_golden.py -q
```

验证结果：

- Report/FailureAnalysis golden smoke：`1 passed`

修改文件：

- `backend/app/tests/golden/test_report_failure_analysis_golden.py`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py backend/app/tests/golden/test_report_failure_analysis_golden.py -q && npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 14 Task 6 Report/FailureAnalysis Frontend Shell 完成

本轮完成：

- 完成 Slice 14 Task 6：Add Report and FailureAnalysis frontend shell。
- 新增 `frontend/src/api/reporting.ts`，覆盖 FailureAnalysis create/get 和
  automation_execution Report create/get。
- 新增 `frontend/src/stores/reporting.ts`，串联 TestRun ID、FailureAnalysis
  和 Report 状态。
- 新增 `frontend/src/views/reporting/ReportFailureAnalysisView.vue`，页面先展示
  evidence_manifest，再展示失败分析和报告结论。
- 报告中心导航由 `待接入` 更新为 `就绪`，路由为
  `/reports/failure-analysis`。
- 新增 `ReportFailureAnalysisView.spec.ts`，验证失败分析、执行报告和
  evidence-first 展示顺序。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 7：Add automation execution
  report golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
```

验证结果：

- Frontend workbench tests：`12 passed, 15 tests passed`

修改文件：

- `frontend/src/api/reporting.ts`
- `frontend/src/stores/reporting.ts`
- `frontend/src/views/reporting/ReportFailureAnalysisView.vue`
- `frontend/src/views/reporting/ReportFailureAnalysisView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 7：Add automation execution report
  golden smoke。
- 当前任务只补 golden smoke，不添加 CI/CD QualityGateDecision records。

## 2026-06-30 Slice 14 Task 5 Automation Execution Report API 完成

本轮完成：

- 完成 Slice 14 Task 5：Add automation execution Report API。
- 新增 `POST /api/reports`，支持 `report_type=automation_execution` 和
  `related_entity_type=TestRun`。
- 新增 `GET /api/reports/{id}`，返回 conclusion、summary、metrics、
  artifact_ids、evidence_manifest 和 report artifacts。
- Report 生成 `report_md`、`report_json` 和 `evidence_manifest.json`
  artifact metadata。
- conclusion 从 TestRun parsed_result、TestResult rows 和 TestRun artifacts
  推导；缺少 execution artifact 时不会返回 passed，而是
  `insufficient_evidence`。
- 未创建 CI/CD quality reports 或 QualityGateDecision records。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 6：Add Report and
  FailureAnalysis frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q
```

验证结果：

- Report/FailureAnalysis API focused tests：`8 passed`

修改文件：

- `backend/app/modules/reporting/router.py`
- `backend/app/modules/reporting/service.py`
- `backend/app/tests/api/test_report_failure_analysis.py`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 6：Add Report and FailureAnalysis
  frontend shell。
- 当前任务保持 evidence-first，不加入 CI/CD quality gates、RAG runtime、MCP
  runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 14 Task 4 FailureAnalysis API 完成

本轮完成：

- 完成 Slice 14 Task 4：Add FailureAnalysis API。
- 新增 `backend/app/modules/reporting/service.py`，从 TestRun、
  TestResult 和 TestRun artifacts 生成 deterministic mock FailureAnalysis。
- 新增 `backend/app/modules/reporting/router.py` 并在 `backend/app/main.py`
  挂载 `/api/test-runs/{id}/failure-analysis`。
- `POST /api/test-runs/{id}/failure-analysis` 会创建 succeeded AITask 和
  draft FailureAnalysis，不创建 Report 或 repair task。
- `GET /api/test-runs/{id}/failure-analysis` 返回 evidence-first read model。
- 缺少 stdout/stderr/TestResult/artifact evidence 时返回
  `classification=insufficient_evidence`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 5：Add automation execution
  Report API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q
```

验证结果：

- FailureAnalysis API focused tests：`6 passed`

修改文件：

- `backend/app/modules/reporting/router.py`
- `backend/app/modules/reporting/service.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_report_failure_analysis.py`
- `docs/contracts/02-api-contract.md`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 5：Add automation execution Report
  API。
- 当前任务不要创建 CI/CD quality reports 或 QualityGateDecision records。

## 2026-06-30 Slice 14 Task 3 FailureAnalysis/Report Model Schema 完成

本轮完成：

- 完成 Slice 14 Task 3：Add FailureAnalysis and Report model schema。
- 新增 `backend/app/modules/reporting/` 模块，包含 FailureAnalysis/Report
  SQLAlchemy models 和 create/read schemas。
- FailureAnalysis 覆盖 project、test_run、test_result、ai_task、
  classification、confidence、evidence_artifact_ids、summary、root_cause、
  suggested_actions 和 status。
- Report 覆盖 project、report_type、title、related entity、status、
  conclusion、summary、metrics_json 和 artifact_ids。
- 新增 `backend/app/tests/api/test_report_failure_analysis.py`，验证模型默认值、
  UUID artifact list 持久化、schema 字段名和 evidence_manifest response。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 4：Add FailureAnalysis API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q
```

验证结果：

- FailureAnalysis/Report focused model/schema tests：`4 passed`

修改文件：

- `backend/app/modules/reporting/__init__.py`
- `backend/app/modules/reporting/models.py`
- `backend/app/modules/reporting/schemas.py`
- `backend/app/tests/api/test_report_failure_analysis.py`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 4：Add FailureAnalysis API。
- 当前任务不要创建 repair tasks 或 reports。

## 2026-06-30 Slice 14 Task 2 Report And FailureAnalysis Contract 完成

本轮完成：

- 完成 Slice 14 Task 2：Add Report and FailureAnalysis API contract boundary。
- 收紧 `docs/contracts/02-api-contract.md` 的 FailureAnalysis create/get
  合同，要求 evidence-first、支持 deterministic mock provider、缺证据时返回
  `insufficient_evidence`。
- 收紧 automation_execution Report create/get 合同，要求
  `evidence_manifest.json`、report artifact ids、TestRun/TestResult/artifact
  evidence 支撑 conclusion。
- 在 `docs/contracts/04-artifact-contract.md` 补充 evidence_manifest artifact
  rules。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 3：Add FailureAnalysis and
  Report model schema。

本轮验证：

```bash
rg -n "FailureAnalysis|POST /api/test-runs/.*/failure-analysis|POST /api/reports|evidence_manifest" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-14-report-and-failure-analysis.md
```

修改文件：

- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 3：Add FailureAnalysis and Report
  model schema。
- 当前任务只做 model/schema，不调用 AI providers 或写 report artifacts。

## 2026-06-30 Slice 14 Task 1 Report And Failure Analysis Task Plan 完成

本轮完成：

- 完成 Slice 14 Task 1：Add Report And Failure Analysis task plan。
- 新增 `docs/implementation/slices/slice-14-report-and-failure-analysis.md`。
- 将 Slice 14 拆为 API/artifact contract、FailureAnalysis/Report
  model/schema、FailureAnalysis API、automation_execution Report API、frontend
  shell、golden smoke、completion gate。
- 明确 Slice 14 只做 evidence-backed FailureAnalysis、evidence manifest 和
  automation_execution Report。
- 明确不加入 CI/CD quality gates、merge/release decisions、RAG runtime、MCP
  runtime、RBAC、tenants、permissions 或 broad report center analytics。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 2：Add Report and
  FailureAnalysis API contract boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-14-report-and-failure-analysis.md
rg -n "Report And Failure Analysis|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-14-report-and-failure-analysis.md
```

修改文件：

- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 2：Add Report and FailureAnalysis
  API contract boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 13 Completion Gate 完成

本轮完成：

- 完成 Slice 13 completion gate。
- 确认 Slice 13 所有任务均为 `done`，并记录提交号：
  `f882a4a`、`1205e95`、`b7c65f2`、`ac3f7c8`、`47d0618`、`a201335`。
- 完成组合验收：Playwright contract、runner adapter、execution API、
  frontend shell、golden smoke 均已覆盖。
- 已在 `docs/implementation/slices/slice-13-playwright-minimal-loop.md` 写入
  completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 1：Add Report And Failure
  Analysis task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- Playwright API + golden smoke：`9 passed`
- Frontend workbench shell：`11 passed, 14 tests passed`

Slice 13 保持的非目标：

- 未加入 reports、failure analysis、CI/CD quality、RAG runtime、MCP runtime、
  RBAC、tenants、permissions、low-code UI automation 或 browser matrix。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 1：Add Report And Failure Analysis
  task plan。
- 这是 planning-only 任务，先创建
  `docs/implementation/slices/slice-14-report-and-failure-analysis.md`，不要直接改产品代码。

## 2026-06-30 Slice 13 Task 6 Playwright Golden Smoke 完成

本轮完成：

- 完成 Slice 13 Task 6：Add Playwright golden smoke。
- 新增 `backend/app/tests/golden/test_playwright_minimal_loop_golden.py`。
- golden smoke 复用 reviewed golden UI TestCase -> AutomationDraft -> edit ->
  approve 链路。
- 已批准 Playwright AutomationDraft 通过 `POST /api/test-runs` +
  `runner_mode=playwright_local` 执行 controlled Playwright path。
- 使用 deterministic fake runner output，不依赖真实浏览器二进制。
- 验证 TestRun、TestResult、runtime_manifest/stdout/stderr/playwright_trace/
  screenshot Artifact metadata 均持久化。
- 验证没有创建 Report、FailureAnalysis 或 QualityGateDecision。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_playwright_minimal_loop_golden.py -q
```

验证结果：

- Playwright minimal golden smoke：`1 passed`

修改文件：

- `backend/app/tests/api/test_playwright_minimal_loop.py`
- `backend/app/tests/golden/test_playwright_minimal_loop_golden.py`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py -q && npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 13 Task 5 Playwright Execution Frontend Shell 完成

本轮完成：

- 完成 Slice 13 Task 5：Add Playwright execution frontend shell。
- 扩展 `frontend/src/stores/execution.ts`，支持传入 `runnerMode` 和
  Playwright reason。
- 新增 `frontend/src/views/execution/PlaywrightExecutionView.vue`，通过
  `runner_mode=playwright_local` 启动 Playwright run。
- 页面展示 status、command、exit_code、duration、runner_mode、
  parsed_result metrics、trace/screenshot artifacts 和 TestResult rows。
- 新增 `PlaywrightExecutionView.spec.ts` 覆盖启动、刷新、trace/screenshot
  证据展示。
- 接入 `execution/playwright` 路由，并在工作台导航中加入
  `Playwright 执行`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 6：Add Playwright golden
  smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
```

验证结果：

- Frontend workbench shell tests：`11 passed, 14 tests passed`

修改文件：

- `frontend/src/stores/execution.ts`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 6：Add Playwright golden smoke。
- golden smoke 使用 deterministic fake runner output，不依赖真实浏览器二进制。

## 2026-06-30 Slice 13 Task 4 Playwright Execution API 完成

本轮完成：

- 完成 Slice 13 Task 4：Add Playwright execution API。
- 扩展 `backend/app/modules/execution/service.py`，通过既有
  `POST /api/test-runs` 支持 `runner_mode=playwright_local`。
- 支持 approved Playwright AutomationDraft 和 configured Playwright
  TestCommand 两条来源。
- Playwright draft 会复制到 Chtest-managed 临时运行目录后执行。
- 执行结果会持久化 TestRun、TestResult、stdout/stderr/runtime_manifest 以及
  playwright_trace/screenshot Artifact metadata。
- 新增 focused API tests 覆盖 approved draft、unapproved reject、configured
  TestCommand。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 5：Add Playwright execution
  frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/api/test_playwright_minimal_loop.py -q
```

验证结果：

- Playwright execution API focused tests：`8 passed`
- Pytest + Playwright execution API regression：`18 passed`

修改文件：

- `backend/app/modules/execution/service.py`
- `backend/app/tests/api/test_playwright_minimal_loop.py`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 5：Add Playwright execution frontend
  shell。
- 前端只做 minimal Playwright execution workbench shell，不加入 low-code
  automation editor、report 或 quality gate。

## 2026-06-30 Slice 13 Task 3 Playwright Runner Adapter 完成

本轮完成：

- 完成 Slice 13 Task 3：Add Playwright runner adapter。
- 新增 `backend/app/modules/execution/playwright_runner.py`。
- adapter 复用 TestCommand allowlist 口径，只接受 `npx playwright test ...`
  命令并拒绝 forbidden shell operators。
- adapter 捕获 stdout、stderr、exit_code、duration_ms，并解析
  passed/failed/skipped/error/total 计数。
- adapter 可发现 `playwright_trace` zip 和 `screenshot` png artifact
  candidates。
- 新增 `backend/app/tests/api/test_playwright_minimal_loop.py`，使用 fake npx
  可执行文件做确定性测试，不依赖真实浏览器或 Playwright 包。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 4：Add Playwright execution API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py -q
```

验证结果：

- Playwright runner adapter focused tests：`5 passed`

修改文件：

- `backend/app/modules/execution/playwright_runner.py`
- `backend/app/tests/api/test_playwright_minimal_loop.py`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 4：Add Playwright execution API。
- 通过 `POST /api/test-runs` + `runner_mode=playwright_local` 接入，不新增报告或质量门禁。

## 2026-06-30 Slice 13 Task 2 Playwright Execution Contract 完成

本轮完成：

- 完成 Slice 13 Task 2：Add Playwright execution API contract and task boundary。
- 在 `docs/contracts/02-api-contract.md` 中明确 Playwright minimal execution
  复用 `POST /api/test-runs`、`GET /api/test-runs/{id}`，通过
  `runner_mode=playwright_local` 区分。
- Request 支持 approved Playwright AutomationDraft 或 configured Playwright
  TestCommand，命令必须 backend assembled 或 allowlist validated。
- Response 复用 TestRun/TestResult evidence shape，并允许返回
  `playwright_trace` 和 `screenshot` artifact metadata。
- 在 `docs/contracts/04-artifact-contract.md` 补充 Playwright trace/screenshot
  artifact rules。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 3：Add Playwright runner
  adapter。

本轮验证：

```bash
rg -n "Playwright|POST /api/test-runs|playwright_trace|screenshot" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-13-playwright-minimal-loop.md
```

修改文件：

- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 3：Add Playwright runner adapter。
- 当前任务只做 adapter，不接 router/API orchestration。

## 2026-06-30 Slice 13 Task 1 Playwright Minimal Loop Task Plan 完成

本轮完成：

- 完成 Slice 13 Task 1：Add Playwright Minimal Loop task plan。
- 新增 `docs/implementation/slices/slice-13-playwright-minimal-loop.md`。
- 将 Slice 13 拆为 API/artifact contract、Playwright runner adapter、
  Playwright execution API、frontend shell、golden smoke、completion gate。
- 明确 Slice 13 只做 minimal Playwright smoke execution、trace/screenshot
  evidence 和 frontend inspection。
- 明确不加入 reports、failure analysis、CI/CD quality gates、RAG runtime、
  MCP runtime、RBAC、tenants、permissions、low-code UI automation 或 browser
  matrix。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 2：Add Playwright execution API
  contract and task boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-13-playwright-minimal-loop.md
rg -n "Playwright Minimal Loop|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-13-playwright-minimal-loop.md
```

修改文件：

- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 2：Add Playwright execution API
  contract and task boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 12 Completion Gate 完成

本轮完成：

- 完成 Slice 12 completion gate。
- 确认 Slice 12 所有任务均为 `done`，并记录提交号：
  `bcd8974`、`db5de11`、`9f6c42c`、`44ac287`、`e40ccaa`、
  `fef7559`、`7185e5b`。
- 完成组合验收：TestRun/TestResult model/schema、pytest runner adapter、
  TestRun API、frontend execution shell、golden smoke 均已覆盖。
- 修复 pytest combined collection 的 import mismatch：golden smoke 文件名从
  `test_testrunner_pytest.py` 调整为 `test_testrunner_pytest_golden.py`。
- 已在 `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
  写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 1：Add Playwright Minimal
  Loop task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/golden/test_testrunner_pytest_golden.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- TestRunner API + golden smoke：`11 passed`
- Frontend workbench shell：`10 passed, 13 tests passed`

Slice 12 保持的非目标：

- 未加入 Playwright execution、reports、CI/CD quality、RAG runtime、MCP
  runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 1：Add Playwright Minimal Loop task
  plan。
- 这是 planning-only 任务，先创建
  `docs/implementation/slices/slice-13-playwright-minimal-loop.md`，不要直接改产品代码。

## 2026-06-30 Slice 12 Task 7 Pytest Execution Golden Smoke 完成

本轮完成：

- 完成 Slice 12 Task 7：Add Pytest Execution Golden Smoke。
- 新增 `backend/app/tests/golden/test_testrunner_pytest_golden.py`。
- golden smoke 复用 reviewed golden TestCase -> AutomationDraft -> edit ->
  approve 链路。
- 已批准 AutomationDraft 通过 `POST /api/test-runs` 执行 controlled pytest。
- 验证 TestRun、TestResult、runtime_manifest/stdout/stderr Artifact metadata
  均持久化。
- 验证没有创建 Report 或 QualityGateDecision 表/记录。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_testrunner_pytest_golden.py -q
```

验证结果：

- Pytest execution golden smoke：`1 passed`

修改文件：

- `backend/app/tests/golden/test_testrunner_pytest_golden.py`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/golden/test_testrunner_pytest_golden.py -q && npm --prefix frontend run test -- --run`。
- 完成后在 Slice 12 文档记录 completion evidence，并选择下一 V1 slice。

## 2026-06-30 Slice 12 Task 6 Pytest Execution Frontend Shell 完成

本轮完成：

- 完成 Slice 12 Task 6：Add Pytest Execution Frontend Shell。
- 新增 `frontend/src/api/execution.ts` 和 `frontend/src/stores/execution.ts`，
  接入 `POST /api/test-runs`、`GET /api/test-runs/{id}`。
- 新增 `frontend/src/views/execution/PytestExecutionView.vue`，支持从
  approved AutomationDraft 或 configured TestCommand 启动 pytest run。
- 页面展示 status、command、working_directory、exit_code、duration、
  runner_mode、readonly/network metadata、parsed_result metrics、Artifact
  rows 和 TestResult rows。
- 接入 `execution/pytest` 路由，并将工作台导航里的 `执行中心` 标为就绪。
- 新增 `PytestExecutionView.spec.ts` 覆盖启动、刷新和证据展示。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 7：Add Pytest Execution
  Golden Smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
```

验证结果：

- Frontend workbench shell tests：`10 passed, 13 tests passed`

修改文件：

- `frontend/src/api/execution.ts`
- `frontend/src/stores/execution.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 7：Add Pytest Execution Golden
  Smoke。
- 复用 golden reviewed case -> approved AutomationDraft setup，验证
  TestRun/TestResult/artifact metadata，不创建 Report 或 QualityGateDecision。

## 2026-06-30 Slice 12 Task 5 TestRun API 完成

本轮完成：

- 完成 Slice 12 Task 5：Add TestRun API。
- 新增 `backend/app/modules/execution/service.py` 和 `router.py`，接入
  `POST /api/test-runs`、`GET /api/test-runs/{id}`。
- `POST /api/test-runs` 支持 approved AutomationDraft 和 configured
  TestCommand 两条来源。
- approved AutomationDraft 会复制到 Chtest-managed 临时运行目录后通过
  pytest runner 执行；未批准 draft 返回 `TEST_RUN_INVALID_INPUT`。
- 执行结果会持久化 TestRun、TestResult、stdout/stderr/runtime_manifest
  Artifact metadata。
- 已在 `backend/app/main.py` 注册 execution router。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 6：Add Pytest Execution
  Frontend Shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q
```

验证结果：

- TestRun API focused tests：`10 passed`

修改文件：

- `backend/app/main.py`
- `backend/app/modules/execution/router.py`
- `backend/app/modules/execution/service.py`
- `backend/app/tests/api/test_testrunner_pytest.py`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 6：Add Pytest Execution Frontend
  Shell。
- 前端只做 pytest execution workbench shell，不加入 report/quality gate。

## 2026-06-30 Slice 12 Task 4 Pytest Runner Adapter 完成

本轮完成：

- 完成 Slice 12 Task 4：Add Pytest Runner Adapter。
- 新增 `backend/app/modules/execution/pytest_runner.py`，提供
  `PytestRunner`、`PytestRunnerResult` 和 `PytestRunnerCommandError`。
- adapter 复用 TestCommand allowlist 口径，只接受 `pytest ...` 命令并拒绝
  forbidden shell operators。
- adapter 使用 `python -m pytest` 执行已验证命令，捕获 stdout、stderr、
  exit_code、duration_ms，并解析 passed/failed/skipped/error/total 计数。
- 新增测试覆盖成功执行、拒绝 shell operator、拒绝非 allowlisted
  `python -m pytest` 输入。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 5：Add TestRun API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q
```

验证结果：

- TestRun/TestResult model/schema + pytest runner adapter：`7 passed`

修改文件：

- `backend/app/modules/execution/pytest_runner.py`
- `backend/app/tests/api/test_testrunner_pytest.py`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 5：Add TestRun API。
- 需要接 router/service/main，创建和读取 TestRun/TestResult evidence。
- 不要生成 report 或 QualityGateDecision。

## 2026-06-30 Slice 12 Task 3 TestRun/TestResult Model Schema 完成

本轮完成：

- 完成 Slice 12 Task 3：Add TestRun and TestResult model schema。
- 新增 `backend/app/modules/execution/` 模块，包含 TestRun/TestResult SQLAlchemy
  models 和 create/read schemas。
- TestRun 覆盖 project、automation_draft、test_command、command、working
  directory、runner metadata、artifact ids、status、exit_code、duration 和
  parsed_result_json。
- TestResult 覆盖 test_run、test_name、test_file、status、duration、
  failure_message、failure_artifact_ids 和 parser metadata。
- 新增 `backend/app/tests/api/test_testrunner_pytest.py`，验证模型默认值、
  UUID artifact list 持久化、schema 字段名和 embedded TestResult response。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 4：Add Pytest Runner Adapter。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q
```

验证结果：

- TestRun/TestResult focused model/schema tests：`4 passed`

修改文件：

- `backend/app/modules/execution/__init__.py`
- `backend/app/modules/execution/models.py`
- `backend/app/modules/execution/schemas.py`
- `backend/app/tests/api/test_testrunner_pytest.py`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 4：Add Pytest Runner Adapter。
- 当前任务只做 adapter，不接 router/API orchestration。
- 继续保持 pytest-only、local_subprocess、allowlisted command、no Playwright。

## 2026-06-30 Slice 12 Task 2 TestRun API Contract 完成

本轮完成：

- 完成 Slice 12 Task 2：Add TestRun API contract and task boundary。
- 优化 `docs/contracts/02-api-contract.md` 的 Test Run API 合同，明确
  `POST /api/test-runs`、`GET /api/test-runs/{id}` 和 TestResult 明细返回。
- 规定 V1 TestRun 只接受 approved AutomationDraft 或 configured
  TestCommand 作为执行源，pytest 命令由后端组装或通过 allowlist 验证。
- 明确 `runner_mode=local_subprocess`、repository readonly、network disabled、
  runtime/dependency/environment artifacts、stdout/stderr/JUnit artifact metadata。
- 明确该 API 不创建 reports、QualityGateDecision、CI/CD workflow state、
  FailureAnalysis、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 3：Add TestRun and TestResult
  model schema。

本轮验证：

```bash
rg -n "TestRun|POST /api/test-runs|TestResult" docs/contracts/02-api-contract.md docs/implementation/slices/slice-12-testrunner-pytest-execution.md
```

修改文件：

- `docs/contracts/02-api-contract.md`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 3：Add TestRun and TestResult
  model schema。
- 先写 `backend/app/tests/api/test_testrunner_pytest.py` 红灯，再补
  `backend/app/modules/execution/models.py` 和 `schemas.py`。
- 当前任务不要加入 subprocess execution。

## 2026-06-30 Slice 12 Task 1 TestRunner Pytest Execution Task Plan 完成

本轮完成：

- 完成 Slice 12 Task 1：新增 TestRunner Pytest Execution task plan。
- 新增 `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`，将 Slice 12 拆为 API contract、TestRun/TestResult model/schema、pytest runner adapter、TestRun API、frontend shell、golden smoke、completion gate。
- 明确 Slice 12 只做 approval-gated pytest execution 和证据捕获，不加入 Playwright、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 2：Add TestRun API contract and task boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-12-testrunner-pytest-execution.md
rg -n "TestRunner Pytest Execution|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-12-testrunner-pytest-execution.md
```

修改文件：

- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 2：Add TestRun API contract and task boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 11 AutomationDraft Completion Gate 完成

本轮完成：

- 完成 Slice 11 completion gate。
- 确认 Slice 11 所有任务均为 `done`，并记录提交号：
  `7704bbf`、`2d5bdec`、`7824172`、`bb6162a`、`b75dc1a`、`9a821df`。
- 确认 AutomationDraft model/schema、generation API、review API、frontend shell、golden smoke 均已覆盖。
- 已在 `docs/implementation/slices/slice-11-automation-draft-foundation.md` 写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 1：Add TestRunner Pytest Execution task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_test_case_library_golden.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- AutomationDraft API + golden draft + Test Case Library golden：`7 passed`
- Frontend workbench shell tests：`9 passed, 12 tests passed`

Slice 11 保持的非目标：

- 未加入 TestRun/TestResult execution、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 1：Add TestRunner Pytest Execution task plan。
- 这是 planning-only 任务，先创建 `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`，不要直接改产品代码。

## 2026-06-30 Slice 11 Task 6 AutomationDraft Golden Smoke 完成

本轮完成：

- 完成 Slice 11 Task 6：新增 AutomationDraft golden smoke。
- 新增 `backend/app/tests/golden/test_automation_draft_golden.py`，复用 golden Test Case Library setup。
- 验证 reviewed golden TestCase 可以创建 AutomationDraft，并包含 draft_code、suggested_file_path、execution_notes、risk_notes、draft_generated 状态。
- 验证 golden draft 可以 edit 后 approve。
- 验证 approved draft 未创建 runtime_artifact/promoted_artifact，且当前 DB 无 test_runs、test_results、reports 表，确认本 slice 没有执行/报告副作用。
- 为复用 golden setup，`test_test_case_library_golden.py` 提取 `create_reviewed_golden_cases` helper，并给 ASGIClient 增加 PATCH 支持。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_automation_draft_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_test_case_library_golden.py -q
```

验证结果：

- AutomationDraft golden smoke：`1 passed`
- AutomationDraft API / golden draft / Test Case Library golden regression：`7 passed`

修改文件：

- `backend/app/tests/golden/test_automation_draft_golden.py`
- `backend/app/tests/golden/test_test_case_library_golden.py`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_test_case_library_golden.py -q`
  和 `npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 11 Task 5 AutomationDraft Frontend Review Shell 完成

本轮完成：

- 完成 Slice 11 Task 5：新增 AutomationDraft frontend review shell。
- 新增 `frontend/src/api/automation.ts` 和 `frontend/src/stores/automation.ts`，支持 create/get/edit/approve API wiring。
- 新增 `AutomationDraftReviewView.vue`，展示草稿代码、建议路径、执行说明、风险说明、状态、审批要求，并支持保存评审编辑和批准草稿。
- 接入 `automation/drafts` 路由，并将工作台导航里的 `自动化草稿中心` 标为就绪。
- 扩展 `ApiClient.patchJson` 以支持合同中的 PATCH endpoint。
- 未添加执行/运行按钮、report 链接、CI/CD quality action、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 6：Add AutomationDraft golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/automation/AutomationDraftReviewView.spec.ts
npm --prefix frontend run test -- --run
```

验证结果：

- AutomationDraft frontend focused test：`1 passed`
- Frontend test suite：`9 passed, 12 tests passed`

修改文件：

- `frontend/src/api/client.ts`
- `frontend/src/api/automation.ts`
- `frontend/src/stores/automation.ts`
- `frontend/src/views/automation/AutomationDraftReviewView.vue`
- `frontend/src/views/automation/AutomationDraftReviewView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 6：Add AutomationDraft golden smoke。
- 复用 golden Test Case Library setup，验证 reviewed golden TestCase -> edit -> approve AutomationDraft 且无执行副作用。

## 2026-06-30 Slice 11 Task 4 AutomationDraft Review API 完成

本轮完成：

- 完成 Slice 11 Task 4：新增 AutomationDraft edit and approve API。
- 新增 `GET /api/automation/drafts/{id}`、`PATCH /api/automation/drafts/{id}`、`POST /api/automation/drafts/{id}/approve`。
- 支持 reviewer 编辑 draft_code、suggested_file_path、execution_notes、risk_notes、review_comment。
- 支持 `draft_generated/edited -> approved`，非法 approve action 返回 `AUTOMATION_DRAFT_INVALID_ACTION`。
- 未创建 TestRun、TestResult、runtime artifacts、reports 或执行副作用。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 5：Add AutomationDraft frontend review shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_test_case_library.py -q
```

验证结果：

- AutomationDraft focused test：`5 passed`
- AutomationDraft + Test Case Library API regression：`8 passed`

修改文件：

- `backend/app/modules/automation/router.py`
- `backend/app/modules/automation/service.py`
- `backend/app/tests/api/test_automation_draft.py`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 5：Add AutomationDraft frontend review shell。
- 先写 `frontend/src/views/automation/AutomationDraftReviewView.spec.ts` 红灯，再补 API/store/router/layout/view。

## 2026-06-30 Slice 11 Task 3 AutomationDraft Generation API 完成

本轮完成：

- 完成 Slice 11 Task 3：新增 AutomationDraft generation API。
- 新增 `POST /api/automation/drafts`。
- 创建 deterministic mock AutomationDraft，并同步创建 succeeded AITask。
- Draft 包含 draft_code、target_framework、suggested_file_path、execution_notes、risk_notes、approval_required、execution_strategy。
- 只生成 review-gated draft，不执行、不写入目标仓库、不创建 TestRun/TestResult/runtime artifact/report。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 4：Add AutomationDraft edit and approve API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_test_case_library.py -q
```

验证结果：

- AutomationDraft focused test：`3 passed`
- AutomationDraft + Test Case Library API regression：`6 passed`

修改文件：

- `backend/app/main.py`
- `backend/app/modules/automation/router.py`
- `backend/app/modules/automation/service.py`
- `backend/app/tests/api/test_automation_draft.py`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 4：Add AutomationDraft edit and approve API。
- 继续在 `backend/app/tests/api/test_automation_draft.py` 中先写红灯，再补 get/edit/approve service/router。

## 2026-06-30 Slice 11 Task 2 AutomationDraft Model Schema 完成

本轮完成：

- 完成 Slice 11 Task 2：新增 AutomationDraft model and schema alignment。
- 新增 `backend/app/modules/automation` 模块。
- 新增 `AutomationDraft` SQLAlchemy model，字段对齐数据模型合同：project_id、test_case_id、requirement_id、ai_task_id、target_framework、draft_code、execution_strategy、approval_required、status、runtime/promoted artifact 等。
- 新增 AutomationDraft create/edit/approve/read schemas，为后续 API 任务准备。
- 未加入 draft generation endpoint、edit/approve endpoint、execution、frontend、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 3：Add AutomationDraft generation API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_test_case_library.py -q
```

验证结果：

- AutomationDraft model/schema focused test：`2 passed`
- AutomationDraft + Test Case Library API regression：`5 passed`

修改文件：

- `backend/app/modules/automation/__init__.py`
- `backend/app/modules/automation/models.py`
- `backend/app/modules/automation/schemas.py`
- `backend/app/tests/api/test_automation_draft.py`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 3：Add AutomationDraft generation API。
- 继续在 `backend/app/tests/api/test_automation_draft.py` 中先写红灯，再补 service/router。

## 2026-06-30 Slice 11 Task 1 AutomationDraft Foundation Task Plan 完成

本轮完成：

- 完成 Slice 11 Task 1：新增 AutomationDraft Foundation task plan。
- 新增 `docs/implementation/slices/slice-11-automation-draft-foundation.md`，将 Slice 11 拆为 model/schema、generation API、edit/approve API、frontend review shell、golden smoke、completion gate。
- 明确 Slice 11 只做 draft generation/review/approval foundation，不加入 pytest/Playwright 执行、runtime copy、TestRun/TestResult、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 2：Add AutomationDraft model and schema alignment。

本轮验证：

```bash
test -f docs/implementation/slices/slice-11-automation-draft-foundation.md
rg -n "AutomationDraft Foundation|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-11-automation-draft-foundation.md
```

修改文件：

- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 2：Add AutomationDraft model and schema alignment。
- 先写 `backend/app/tests/api/test_automation_draft.py` 红灯，再补 model/schema。

## 2026-06-30 Slice 10 Test Case Library Completion Gate 完成

本轮完成：

- 完成 Slice 10 completion gate。
- 确认 Slice 10 所有任务均为 `done`，并记录提交号：
  `03114cd`、`11942b3`、`0e0ad8e`、`41f9518`、`b12f323`。
- 确认 Test Case Library API contract、backend API、frontend shell、golden smoke 均已覆盖。
- 已在 `docs/implementation/slices/slice-10-test-case-library.md` 写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 1：Add AutomationDraft Foundation task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_requirement_to_case.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- Test Case Library API + golden library + requirement-to-case golden：`5 passed`
- Frontend workbench shell tests：`8 passed, 11 tests passed`

Slice 10 保持的非目标：

- 未加入 AutomationDraft generation、execution、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 1：Add AutomationDraft Foundation task plan。
- 这是 planning-only 任务，先创建 `docs/implementation/slices/slice-11-automation-draft-foundation.md`，不要直接改产品代码。

## 2026-06-30 Slice 10 Task 5 Test Case Library Golden Smoke 完成

本轮完成：

- 完成 Slice 10 Task 5：新增 Test Case Library golden smoke。
- 新增 `backend/app/tests/golden/test_test_case_library_golden.py`，复用 golden requirement-to-case fixture setup 和 review plan。
- 验证评审后 library API 返回 4 条 reviewed TestCase。
- 验证编辑后的过期优惠券用例保留 `准备已过期优惠券` 步骤和 `coupon_state=expired` input data。
- 验证 keyword 过滤可以找到 golden UI 用例。
- 修复 golden/API 同名测试文件导致的 pytest collection import mismatch，golden 文件采用唯一文件名。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_case_library_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_requirement_to_case.py -q
```

验证结果：

- Test Case Library golden smoke：`1 passed`
- Test Case Library API / golden library / requirement-to-case golden regression：`5 passed`

修改文件：

- `backend/app/tests/golden/test_test_case_library_golden.py`
- `docs/implementation/slices/slice-10-test-case-library.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_requirement_to_case.py -q`
  和 `npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 10 Task 4 Test Case Library Frontend Shell 完成

本轮完成：

- 完成 Slice 10 Task 4：新增 Test Case Library frontend shell。
- 前端 API/store 新增 `GET /api/test-cases` wiring。
- 新增 `frontend/src/views/cases/TestCaseLibraryView.vue`，展示已评审用例列表、关键词筛选、步骤、预期结果、标签、评审状态和来源信息。
- 接入 `cases/library` 路由，并将工作台导航里的 `用例库` 标为就绪。
- 未添加 AutomationDraft 按钮、执行按钮、reports、dashboard 图表、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 Task 5：Add Test Case Library golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/cases/TestCaseLibraryView.spec.ts
npm --prefix frontend run test -- --run
```

验证结果：

- Test Case Library frontend focused test：`1 passed`
- Frontend test suite：`8 passed, 11 tests passed`

修改文件：

- `frontend/src/api/cases.ts`
- `frontend/src/stores/cases.ts`
- `frontend/src/views/cases/TestCaseLibraryView.vue`
- `frontend/src/views/cases/TestCaseLibraryView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-10-test-case-library.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 Task 5：Add Test Case Library golden smoke。
- 复用 golden requirement-to-case fixture setup，验证已评审用例能从 library API 查询。

## 2026-06-30 Slice 10 Task 3 Test Case Library Backend API 完成

本轮完成：

- 完成 Slice 10 Task 3：新增 Test Case Library backend API。
- 新增 `GET /api/test-cases`，返回已持久化的 TestCase records，不返回未评审 GeneratedCaseCandidate。
- 支持 `project_id` 必填过滤，以及 module_id、status、test_type、priority、keyword 可选过滤。
- keyword 覆盖 title、precondition、steps、expected_results、input_data、tags 的简单匹配。
- 响应返回 `items` 和 `total`，并包含 TestCase Library 合同字段。
- 未新增 TestCase mutation、AutomationDraft、execution、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 Task 4：Add Test Case Library frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_case_metrics.py backend/app/tests/api/test_test_case_library.py -q
```

验证结果：

- Test Case Library API focused test：`3 passed`
- Case Generation / Case Review / Case Metrics / Test Case Library API regression：`15 passed`

修改文件：

- `backend/app/modules/cases/router.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/tests/api/test_test_case_library.py`
- `docs/implementation/slices/slice-10-test-case-library.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 Task 4：Add Test Case Library frontend shell。
- 先写 `frontend/src/views/cases/TestCaseLibraryView.spec.ts` 红灯，再补 API/store/router/layout/view。

## 2026-06-30 Slice 10 Task 2 Test Case Library API Contract 完成

本轮完成：

- 完成 Slice 10 Task 2：新增 Test Case Library API contract and task boundary。
- 在 `docs/contracts/02-api-contract.md` 增加 `GET /api/test-cases`。
- 合同定义了 `TestCaseListRead` 响应字段，以及 project_id、module_id、status、test_type、priority、keyword 查询过滤。
- 明确该端点只浏览已评审 TestCase，不创建/修改 TestCase，不加入 AutomationDraft、执行、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 Task 3：Add Test Case Library backend API。

本轮验证：

```bash
rg -n "Test Case Library|GET /api/test-cases|TestCaseList" docs/contracts/02-api-contract.md docs/implementation/slices/slice-10-test-case-library.md
```

修改文件：

- `docs/contracts/02-api-contract.md`
- `docs/implementation/slices/slice-10-test-case-library.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 Task 3：Add Test Case Library backend API。
- 先写 `backend/app/tests/api/test_test_case_library.py` 红灯，再补 schemas/service/router。

## 2026-06-30 Slice 10 Task 1 Test Case Library Task Plan 完成

本轮完成：

- 完成 Slice 10 Task 1：新增 Test Case Library task plan。
- 新增 `docs/implementation/slices/slice-10-test-case-library.md`，将 Slice 10 拆为 API contract、backend API、frontend shell、golden smoke、completion gate。
- 明确 Slice 10 只浏览/搜索已评审 TestCase，不加入 AutomationDraft、执行、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 Task 2：Add Test Case Library API contract and task boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-10-test-case-library.md
rg -n "Test Case Library|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-10-test-case-library.md
```

修改文件：

- `docs/implementation/slices/slice-10-test-case-library.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 Task 2：Add Test Case Library API contract and task boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 09 Case Metrics Completion Gate 完成

本轮完成：

- 完成 Slice 09 completion gate。
- 确认 Slice 09 所有任务均为 `done`，并记录提交号：
  `470fa23`、`0e1c81d`、`da6b606`、`46580ea`。
- 确认 Case Metrics 后端计算、API、前端 shell、golden metrics smoke 均已覆盖。
- 已在 `docs/implementation/slices/slice-09-case-metrics.md` 写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 Task 1：Add Test Case Library task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- Case Metrics API + golden requirement-to-case + golden metrics smoke：`6 passed`
- Frontend workbench shell tests：`7 passed, 10 tests passed`

Slice 09 保持的非目标：

- 未加入 Test Case Library workflow、AutomationDraft、执行、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 Task 1：Add Test Case Library task plan。
- 这是 planning-only 任务，先创建 `docs/implementation/slices/slice-10-test-case-library.md`，不要直接改产品代码。

## 2026-06-30 Slice 09 Task 5 Case Metrics Golden Smoke 完成

本轮完成：

- 完成 Slice 09 Task 5：新增 Case Metrics golden smoke。
- 新增 `backend/app/tests/golden/test_requirement_to_case_metrics.py`，复用现有 golden requirement-to-case fixture setup。
- golden smoke 按优惠券结算评审计划提交 approve、approve_after_edit、needs_optimization 动作后，调用 metrics API 验证 batch 指标。
- 断言 `generated_count >= 5`、`approved_count == 3`、`edited_count == 1`、`optimization_count == 1`、`review_progress >= 1.0`、`acceptance_rate == 0.8`。
- 未加入 browser automation、frontend、execution、AutomationDraft、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 09 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case_metrics.py -q
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/api/test_case_metrics.py -q
```

验证结果：

- Case Metrics golden smoke：`1 passed`
- Requirement To Case golden / Case Metrics golden / Case Metrics API regression：`6 passed`

修改文件：

- `backend/app/tests/golden/test_requirement_to_case_metrics.py`
- `docs/implementation/slices/slice-09-case-metrics.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 09 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py -q`
  和 `npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 09 Task 4 Case Metrics Frontend Shell 完成

本轮完成：

- 完成 Slice 09 Task 4：新增 Case Metrics frontend shell。
- 前端 API 新增 `GET /api/case-generation/tasks/{generation_task_id}/metrics` wiring。
- Pinia case store 在生成候选用例后加载 batch metrics，并在评审动作成功后刷新 metrics。
- `用例生成评审` shell 新增紧凑批次指标条，展示生成总数、直接通过、拒绝、采纳率、编辑率、评审进度、字段完整率。
- 未新增 dashboard route、chart dependency、Test Case Library、AutomationDraft、执行、reports、CI/CD、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 09 Task 5：Add Case Metrics golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/cases/CaseGenerationReviewView.spec.ts
npm --prefix frontend run test -- --run
```

验证结果：

- Case Generation Review frontend focused test：`1 passed`
- Frontend test suite：`7 passed, 10 tests passed`

修改文件：

- `frontend/src/api/cases.ts`
- `frontend/src/stores/cases.ts`
- `frontend/src/views/cases/CaseGenerationReviewView.vue`
- `frontend/src/views/cases/CaseGenerationReviewView.spec.ts`
- `docs/implementation/slices/slice-09-case-metrics.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 09 Task 5：Add Case Metrics golden smoke。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case_metrics.py -q`。

## 2026-06-30 Slice 09 Task 3 Case Metrics API 完成

本轮完成：

- 完成 Slice 09 Task 3：新增 Case Metrics API。
- 新增 `GET /api/case-generation/tasks/{generation_task_id}/metrics`，返回 batch-level case metrics。
- API 复用 Task 2 的 `calculate_case_metrics`，不新增 metric table。
- 未加入 frontend、Test Case Library、AutomationDraft、执行、reports、CI/CD、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 09 Task 4：Add Case Metrics frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_case_metrics.py -q
git diff --check
```

验证结果：

- Case Metrics focused test：`4 passed`
- Case Generation / Case Review / Case Metrics regression：`12 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/cases/router.py`
- `backend/app/tests/api/test_case_metrics.py`
- `docs/implementation/slices/slice-09-case-metrics.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 09 Task 4：Add Case Metrics frontend shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

## 2026-06-29 Slice 09 Task 2 Case Metrics Backend Calculation 完成

本轮完成：

- 完成 Slice 09 Task 2：新增 case generation batch metrics service 计算。
- 新增 `CaseMetricsRead` schema。
- 新增 `calculate_case_metrics`，从 CaseGenerationTask/GeneratedCaseCandidate 计算 generated_count、approved_count、edited_count、rejected_count、optimization_count、reviewed_count、acceptance_rate、edit_rate、rejection_rate、optimization_rate、review_progress、field_complete_rate。
- 未新增 metric table，未加入 API route、frontend、Test Case Library、AutomationDraft、执行、reports、CI/CD、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 09 Task 3：Add Case Metrics API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_case_metrics.py -q
git diff --check
```

验证结果：

- Case Metrics focused test：`2 passed`
- Case Generation / Case Review / Case Metrics regression：`10 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/tests/api/test_case_metrics.py`
- `docs/implementation/slices/slice-09-case-metrics.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 09 Task 3：Add Case Metrics API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py -q`。

## 2026-06-29 Slice 06 Requirement To Case Mainline 完成

本轮完成：

- 完成 Slice 06 completion gate。
- 确认 Slice 06 所有任务均为 `done` 且都有提交号。
- 后端已跑通 Requirement Review、Case Generation、Case Review、golden requirement-to-case smoke。
- 前端已接入 Requirement Review shell 和 Case Generation Review shell。
- 已在 `docs/implementation/slices/slice-06-requirement-to-case.md` 写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 09 Task 1：Add Case Metrics task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/golden/test_requirement_to_case.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Backend Slice 06 chain：`15 passed`
- Frontend workbench shell tests：`7 passed, 10 tests passed`
- `git diff --check` 无输出。

Slice 06 保持的非目标：

- 未加入 AutomationDraft、执行、Playwright、CI/CD 质量中心、报告中心、真实 provider、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 09 Task 1：Add Case Metrics task plan。
- 下一步先补 `docs/implementation/slices/slice-09-case-metrics.md`，不要直接写模型/API。

## 2026-06-29 Slice 06 Task 9 Case Generation Review Frontend Shell 完成

本轮完成：

- 完成 Slice 06 Task 9：新增 Case Generation Review frontend shell。
- 新增 `frontend/src/views/cases/CaseGenerationReviewView.vue`，支持启动 mock case generation、展示候选用例、查看步骤/预期结果/AI 理由，并提交 approve、approve_after_edit、reject、needs_optimization 评审动作。
- 新增 `frontend/src/api/cases.ts` 和 `frontend/src/stores/cases.ts`，最小接入 Case Generation 和 Case Review API。
- 把 `用例生成评审` 路由/导航状态接入现有 workbench shell。
- 未加入 AutomationDraft、执行、browser automation、真实 provider、RAG runtime、MCP runtime、RBAC 或 tenants。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 completion gate。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/cases/CaseGenerationReviewView.spec.ts
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Case Generation Review frontend focused test：`1 passed`
- Frontend test suite：`7 passed, 10 tests passed`
- `git diff --check` 无输出。

修改文件：

- `frontend/src/views/cases/CaseGenerationReviewView.vue`
- `frontend/src/views/cases/CaseGenerationReviewView.spec.ts`
- `frontend/src/api/cases.ts`
- `frontend/src/stores/cases.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/golden/test_requirement_to_case.py -q`
  和 `npm --prefix frontend run test -- --run`。

风险提醒：

- completion gate 只做验证和记忆/进度收口；不要加入新的产品行为。

## 2026-06-29 Slice 06 Task 8 Requirement Review Frontend Shell 完成

本轮完成：

- 完成 Slice 06 Task 8：新增 Requirement Review frontend shell。
- 新增 `frontend/src/views/requirements/RequirementReviewView.vue`，支持录入需求、触发 mock RequirementReviewAgent、展示评分、问题、澄清问题、风险项和上下文使用。
- 新增 `frontend/src/api/requirements.ts` 和 `frontend/src/stores/requirements.ts`，最小接入 Requirement create、review start、review get API。
- 扩展 `ApiClient.postJson`，并把 `需求评审` 路由/导航状态接入现有 workbench shell。
- 未加入 Case Generation Review、AutomationDraft、执行、browser automation、真实 provider、RAG runtime、MCP runtime、RBAC 或 tenants。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 9：Add Case Generation Review frontend shell。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/requirements/RequirementReviewView.spec.ts
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Requirement Review frontend focused test：`1 passed`
- Frontend test suite：`6 passed, 9 tests passed`
- `git diff --check` 无输出。

修改文件：

- `frontend/src/views/requirements/RequirementReviewView.vue`
- `frontend/src/views/requirements/RequirementReviewView.spec.ts`
- `frontend/src/api/client.ts`
- `frontend/src/api/requirements.ts`
- `frontend/src/stores/requirements.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 9：Add Case Generation Review frontend shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

风险提醒：

- Task 9 只做 Case Generation Review frontend shell；不要加入 AutomationDraft、执行、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 7 Requirement To Case Golden Smoke 完成

本轮完成：

- 完成 Slice 06 Task 7：新增 fixture-aligned backend golden smoke。
- 新增 `backend/app/tests/golden/test_requirement_to_case.py`，覆盖项目/模块/需求创建、Requirement Review、Case Generation、候选用例列表和 Case Review。
- golden smoke 使用 `docs/fixtures/01-golden-requirement-to-case.md` 的优惠券结算规则、目标测试类型和人工评审动作。
- 验证 RequirementReview 六维评分、RiskItem、GeneratedCaseCandidate、TestCase 创建和批次指标。
- 未加入 browser automation、执行、AutomationDraft、frontend、真实 provider、RAG runtime、MCP runtime、RBAC 或 tenants。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 8：Add Requirement Review frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/golden/test_requirement_to_case.py -q
git diff --check
```

验证结果：

- Requirement To Case golden smoke：`1 passed`
- Requirement Review / Case Generation / Case Review / Golden regression：`15 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/tests/golden/test_requirement_to_case.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 8：Add Requirement Review frontend shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

风险提醒：

- Task 8 是 frontend shell；不要加入 Case Generation Review、AutomationDraft、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 6 Case Review API 完成

本轮完成：

- 完成 Slice 06 Task 6：新增 Case Review API。
- 新增 `POST /api/case-review/items/{candidate_id}/approve`，支持 `approve`、`approve_after_edit`、`reject`、`needs_optimization`。
- `approve` 会从 GeneratedCaseCandidate 创建官方 TestCase，并保留候选原始内容。
- `approve_after_edit` 会从人工编辑后的 case payload 创建官方 TestCase。
- `reject` 和 `needs_optimization` 只更新候选状态与 review comment，不创建 TestCase。
- 已阻止 `approved`、`approved_after_edit`、`rejected` 终态候选再次评审。
- 未加入 CaseReviewAgent 优化实现、执行、AutomationDraft、frontend、真实 provider、RAG runtime、MCP runtime、RBAC 或 tenants。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 7：Add Requirement To Case golden smoke。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_review.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py -q
git diff --check
```

验证结果：

- Case Review API focused test：`5 passed`
- Requirement Review / Case Generation / Case Review regression：`14 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/cases/router.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/tests/api/test_case_review.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 7：Add Requirement To Case golden smoke。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py -q`。

风险提醒：

- Task 7 只做 backend golden smoke；不要加入 frontend、AutomationDraft、browser automation、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 5 Case Generation Mock Flow 完成

本轮完成：

- 完成 Slice 06 Task 5：新增 Case Generation API 和 deterministic mock agent flow。
- 新增 `POST /api/case-generation/tasks`，同步运行 mock CaseGenerationAgent，创建 AITask、AI artifacts、LLMCallLog。
- 新增 `GET /api/case-generation/tasks/{id}/candidates`，返回 generated candidates 的 API 合同字段。
- 成功输出通过本任务 schema guard 后才写 CaseGenerationTask/GeneratedCaseCandidate。
- mock schema_invalid 路径会保留 AITask failed 状态、raw output artifact、schema_invalid LLMCallLog，但不写 CaseGenerationTask/GeneratedCaseCandidate/TestCase。
- 生成候选不会自动进入 TestCase library。
- 未加入 Case Review API、frontend、AutomationDraft、真实 provider、外部 RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 6：Add Case Review API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirements.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q
git diff --check
```

验证结果：

- Case Generation API focused test：`3 passed`
- Requirement/Case Generation/AI Runtime regression：`31 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/cases/router.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_case_generation.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 6：Add Case Review API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_review.py -q`。

风险提醒：

- Task 6 只做 candidate review actions；不要执行 cases、不要加入 AutomationDraft、frontend、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 4 Case Generation Models 完成

本轮完成：

- 完成 Slice 06 Task 4：新增 CaseGenerationTask、GeneratedCaseCandidate、TestCase 模型与迁移。
- 新增 `backend/app/modules/cases/` 模块骨架和 read schema。
- 新增 Alembic migration `20260629_0005_case_generation.py`，沿用现有 UUID、timestamp、JSONB/SQLite JSON、Postgres text[]/SQLite JSON list 兼容模式。
- 为 target_test_types、steps、expected_results、input_data、tags、requirement/risk refs 等 JSON/list 字段启用 Mutable tracking。
- 未加入 Case Generation API、mock flow、Case Review API、frontend、AutomationDraft、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 5：Add Case Generation API and mock agent flow。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/db/test_prompt_skill_models.py backend/app/tests/db/test_requirement_review_models.py backend/app/tests/db/test_case_generation_models.py -q
git diff --check
```

验证结果：

- Case Generation model focused test：`4 passed`
- DB model regression：`25 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/cases/__init__.py`
- `backend/app/modules/cases/models.py`
- `backend/app/modules/cases/schemas.py`
- `backend/alembic/versions/20260629_0005_case_generation.py`
- `backend/app/tests/db/test_case_generation_models.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 5：Add Case Generation API and mock agent flow。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py -q`。

风险提醒：

- Task 5 可以复用 AI Runtime 和 deterministic mock provider，但仍不能加入 Case Review API、frontend、AutomationDraft、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 3 Requirement Review Mock Flow 完成

本轮完成：

- 完成 Slice 06 Task 3：新增 Requirement Review API 和 deterministic mock agent flow。
- 新增 `POST /api/requirements/{id}/review`，同步运行 mock RequirementReviewAgent，创建 AITask、AI artifacts、LLMCallLog。
- 新增 `GET /api/requirements/{id}/review`，返回 review scores、issues、clarification questions、test design notes、risk items、context usage 和 context manifest artifact id。
- 成功输出通过本任务 schema guard 后才写 RequirementReview/RiskItem。
- mock schema_invalid 路径会保留 AITask failed 状态和 raw output artifact，但不写 RequirementReview/RiskItem。
- 保留 `use_knowledge=false` 语义：不使用外部 RAG，但显式 `context_artifact_ids` 仍记录到 AITask 并作为 used context 返回。
- 未加入 case generation、frontend、真实 provider、外部 RAG runtime、MCP runtime、RBAC 或 tenants。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 4：Add Case Generation models and migration。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirements.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q
git diff --check
```

验证结果：

- Requirement Review API focused test：`6 passed`
- Requirement/AI Runtime regression：`28 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/requirements/router.py`
- `backend/app/modules/requirements/service.py`
- `backend/app/modules/requirements/schemas.py`
- `backend/app/tests/api/test_requirement_review.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 4：Add Case Generation models and migration。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py -q`。

风险提醒：

- Task 4 只做 CaseGenerationTask、GeneratedCaseCandidate、TestCase models/migration/schema/test；不要加入 Case Generation API、mock flow、case review、frontend 或 AutomationDraft。

## 2026-06-29 Slice 06 Task 2 Requirement API 完成

本轮完成：

- 完成 Slice 06 Task 2：新增 Requirement create/get/list API。
- 新增 `POST /api/requirements`、`GET /api/requirements/{id}`、`GET /api/projects/{project_id}/requirements`。
- 新增 Requirement service，校验 project 存在和 module 归属同一 project。
- 扩展 Requirement schema：create、read、list envelope。
- 将 requirements router 注册到 FastAPI main。
- 未启动 RequirementReviewAgent，未创建 RequirementReview/RiskItem/CaseGeneration，未加入 frontend、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 3：Add Requirement Review API and mock agent flow。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirements.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py backend/app/tests/api/test_modules.py backend/app/tests/api/test_requirements.py -q
git diff --check
```

验证结果：

- Requirement API focused test：`9 passed`
- Project/Module/Requirement API regression：`25 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/requirements/router.py`
- `backend/app/modules/requirements/service.py`
- `backend/app/modules/requirements/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_requirements.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 3：Add Requirement Review API and mock agent flow。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py -q`。

风险提醒：

- Task 3 可以复用 AI Runtime 和 deterministic mock provider，但仍不能加入 case generation、frontend、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 1 Requirement Review Models 完成

本轮完成：

- 完成 Slice 06 Task 1：新增 Requirement、RequirementReview、RiskItem 数据模型与迁移。
- 新增 `backend/app/modules/requirements/` 模块骨架和 read schema。
- 新增 Alembic migration `20260629_0004_requirement_review.py`，沿用现有 UUID、timestamp、JSONB/SQLite JSON 兼容模式。
- RequirementReview 的 issues、clarification questions、test design notes 使用 MutableList，支持 JSON list 原地更新持久化。
- 为 7 个评分字段添加 0-100 check constraint。
- 未加入 API、worker、mock agent flow、case generation、frontend、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 2：Add Requirement API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_requirement_review_models.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/db/test_prompt_skill_models.py backend/app/tests/db/test_requirement_review_models.py -q
git diff --check
```

验证结果：

- Requirement Review model focused test：`6 passed`
- DB model regression：`21 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/requirements/__init__.py`
- `backend/app/modules/requirements/models.py`
- `backend/app/modules/requirements/schemas.py`
- `backend/alembic/versions/20260629_0004_requirement_review.py`
- `backend/app/tests/db/test_requirement_review_models.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 2：Add Requirement API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirements.py -q`。

风险提醒：

- Task 2 只做 Requirement create/get/list API；不要启动 RequirementReviewAgent，不要生成 risks/cases，不要加入 frontend。

## 2026-06-29 Slice 06 Task 0 Requirement To Case Plan 完成

本轮完成：

- 完成 Slice 06 Task 0：新增 Requirement To Case mainline task plan。
- 新增 `docs/implementation/slices/slice-06-requirement-to-case.md`。
- 将 M3 Requirement To Case 拆成 9 个小任务：Requirement Review models、Requirement API、Requirement Review mock flow、Case Generation models、Case Generation mock flow、Case Review API、Golden smoke、Requirement Review frontend shell、Case Generation Review frontend shell。
- 每个任务包含 expected files、verification command、non-goals 和 commit message。
- 明确 Slice 06 不包含 AutomationDraft、执行、CI/CD、RAG runtime、MCP runtime、RBAC 或多用户权限。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 1：Add Requirement Review models and migration。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_prompt_skill_models.py -q
git diff --check
```

验证结果：

- Prompt/Skill model smoke：`5 passed in 0.34s`

修改文件：

- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 1：Add Requirement Review models and migration。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/db/test_requirement_review_models.py -q`。

风险提醒：

- Task 1 只做 Requirement、RequirementReview、RiskItem model/migration/schema/test；不要混入 API、AI worker flow、case generation 或 frontend。

## 2026-06-29 Slice 05 Task 7 Prompt/Skill Frontend Shell 完成

本轮完成：

- 完成 Slice 05 Task 7：新增 Prompt/Skill Center read-only frontend shell。
- 新增 frontend API client：加载 `/api/prompt-versions` 和 `/api/skill-versions`。
- 新增 Pinia store：跟踪 prompts、skills、loading、error 和基础计数。
- 新增 route `/prompt-skill`，并将侧边栏 `Prompt / Skill 中心` 标记为就绪。
- 页面展示 PromptVersion / SkillVersion 数量、active 计数、适用 Agent、hash、状态、schema required 字段、quality gates 和 tool permissions。
- 未加入 prompt editing、marketplace、真实 provider、RAG 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 0：Create Slice 06 task plan。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/prompt-skill/PromptSkillCenterView.spec.ts
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Prompt/Skill Center focused spec：`1 passed`
- Frontend full test suite：`5 passed (5 files), 8 passed (8 tests)`
- `git diff --check` 无输出。

修改文件：

- `frontend/src/api/promptSkill.ts`
- `frontend/src/stores/promptSkill.ts`
- `frontend/src/views/prompt-skill/PromptSkillCenterView.vue`
- `frontend/src/views/prompt-skill/PromptSkillCenterView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `frontend/src/styles/global.css`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 0：Create Slice 06 task plan。
- 创建 `docs/implementation/slices/slice-06-requirement-to-case.md` 后，将 `NEXT_AI_TASK.md` 切到 Slice 06 的第一个可执行小任务。

风险提醒：

- Slice 06 尚无独立 task plan 文件；不要直接开始写需求/用例模型，先建立小任务边界。

## 2026-06-29 Slice 05 Task 6 Prompt/Skill API 完成

本轮完成：

- 完成 Slice 05 Task 6：新增 read-only Prompt/Skill registry API。
- 新增 `/api/prompt-versions` 和 `/api/prompt-versions/{id}`。
- 新增 `/api/skill-versions` 和 `/api/skill-versions/{id}`。
- 响应包含 version identity、hash、status、agent/applicable agents、schema/gate metadata 和 content。
- 未添加 create/update/delete endpoint。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 7：Add Prompt/Skill frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_prompt_skill_registry.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_prompt_skill_registry.py backend/app/tests/api/test_ai_tasks.py -q
git diff --check
```

验证结果：

- Prompt/Skill registry API focused test：`5 passed in 0.57s`
- Prompt/Skill registry API + AI Task API regression：`9 passed in 0.67s`

修改文件：

- `backend/app/modules/prompt_skill/router.py`
- `backend/app/modules/prompt_skill/service.py`
- `backend/app/modules/prompt_skill/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_prompt_skill_registry.py`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 7：Add Prompt/Skill frontend shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

风险提醒：

- Task 7 只做 read-only frontend shell，不要加入 prompt editing、marketplace、真实 provider、RAG 或 MCP runtime。

## 2026-06-29 Slice 05 Task 5 Mock Provider Eval Bench 完成

本轮完成：

- 完成 Slice 05 Task 5：新增 deterministic mock-provider eval bench。
- 新增 `EvalSample` 和默认 eval samples，覆盖 requirements、code changes、failed runs、bug history 四类 fixture。
- 新增 eval bench 指标：`schema_valid_rate`、`evidence_complete_rate`、`unsafe_output_rate`、`manual_edit_rate`、`first_run_pass_rate`、`repair_success_rate`。
- Eval bench 使用运行时 Prompt Output Schema 校验 mock provider 输出，并将 schema mismatch 作为指标信号，不作为当前任务阻塞阈值。
- 新增 `docs/fixtures/eval-bench/*.md`，不包含真实 secrets 或 customer data。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 6：Add Prompt/Skill API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_eval_bench.py -q
git diff --check
```

验证结果：

- Eval bench focused test：`3 passed in 0.21s`

修改文件：

- `backend/app/modules/prompt_skill/eval_bench.py`
- `backend/app/modules/prompt_skill/eval_samples.py`
- `backend/app/tests/prompt_skill/test_eval_bench.py`
- `docs/fixtures/eval-bench/requirements.md`
- `docs/fixtures/eval-bench/code-changes.md`
- `docs/fixtures/eval-bench/failed-runs.md`
- `docs/fixtures/eval-bench/bug-history.md`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 6：Add Prompt/Skill API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_prompt_skill_registry.py -q`。

风险提醒：

- 当前 mock provider 输出与部分 Prompt Output Schema 不完全一致；eval bench 会量化该差异，后续可单独任务调整 mock 输出或 prompt schema。
- Task 6 只做 read-only registry API，不要加入 prompt editing、frontend、真实 provider、RAG 或 MCP runtime。

## 2026-06-29 Slice 05 Task 4 Registry Loader 完成

本轮完成：

- 完成 Slice 05 Task 4：新增 built-in Prompt/Skill registry loader。
- Loader 可发现运行时 `prompts/*/v1.md` 和 `skills/*/v1.md` 文件。
- Loader 解析 Prompt 的 Agent、Input Schema、Output Schema，解析 Skill 的 Applies To、Quality Gates、Forbidden Actions、Tool Permissions。
- Loader 使用稳定 `sha256:` 内容 hash，并可 idempotent 创建 PromptVersion / SkillVersion 记录。
- 对已有同名同版本但内容不同的 active record，loader 抛出 `RegistryContentConflict`，不覆盖已发布内容。
- 新增 `backend/app/modules/prompt_skill/service.py` 包装 seed 入口，供后续 API/启动流程复用。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 5：Add mock-provider eval bench。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_registry_loader.py -q
git diff --check
```

验证结果：

- Registry loader focused test：`4 passed in 0.31s`

修改文件：

- `backend/app/modules/prompt_skill/registry_loader.py`
- `backend/app/modules/prompt_skill/service.py`
- `backend/app/tests/prompt_skill/test_registry_loader.py`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 5：Add mock-provider eval bench。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_eval_bench.py -q`。

风险提醒：

- Task 5 只做 deterministic eval bench 和 fixture，不要引入真实 provider、API、frontend、RAG、MCP runtime 或公开 leaderboard。

## 2026-06-29 Slice 05 Task 3 Built-In Skill Files 完成

本轮完成：

- 完成 Slice 05 Task 3：新增 9 个内置 Skill v1 markdown 文件。
- Skill 文件从 `docs/fixtures/prompt-skill-seeds/skills/` 落位到运行时 `skills/` 目录。
- 新增 `backend/app/tests/prompt_skill/test_skill_files.py`，校验文件存在、必需章节、Applies To 映射、Quality Gates 和 Forbidden Actions 非空。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 4：Add registry loader and hash logic。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_skill_files.py -q
git diff --check
```

验证结果：

- Skill file focused test：`3 passed in 0.01s`

修改文件：

- `skills/automation-draft-skill/v1.md`
- `skills/failure-analysis-skill/v1.md`
- `skills/regression-selection-skill/v1.md`
- `skills/report-generation-skill/v1.md`
- `skills/requirement-review-skill/v1.md`
- `skills/test-case-generation-skill/v1.md`
- `skills/testcase-review-skill/v1.md`
- `skills/tool-execution-skill/v1.md`
- `skills/unit-test-generation-skill/v1.md`
- `backend/app/tests/prompt_skill/test_skill_files.py`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 4：Add registry loader and hash logic。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_registry_loader.py -q`。

风险提醒：

- Task 4 只添加 registry loader/service 和 focused test，不要混入 API、frontend、RAG、MCP runtime 或 prompt/skill 内容改写。

## 2026-06-29 Slice 05 Task 2 Built-In Prompt Files 完成

本轮完成：

- 完成 Slice 05 Task 2：新增 11 个内置 Prompt v1 markdown 文件。
- Prompt 文件从 `docs/fixtures/prompt-skill-seeds/prompts/` 落位到运行时 `prompts/` 目录。
- 新增 `backend/app/tests/prompt_skill/test_prompt_files.py`，校验文件存在、必需章节、Agent 映射、Input/Output Schema JSON 解析、JSON-only 指令和 Failure Output。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 3：Add built-in skill files。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_prompt_files.py -q
git diff --check
git diff --name-only
```

验证结果：

- Prompt file focused test：`4 passed in 0.01s`
- `git diff --check` 无输出。

修改文件：

- `prompts/automation_draft_generation/v1.md`
- `prompts/case_generation/v1.md`
- `prompts/case_review/v1.md`
- `prompts/cicd_change_analysis/v1.md`
- `prompts/failure_analysis/v1.md`
- `prompts/regression_selection/v1.md`
- `prompts/report_generation/v1.md`
- `prompts/requirement_review/v1.md`
- `prompts/risk_matrix/v1.md`
- `prompts/tool_execution/v1.md`
- `prompts/unit_test_generation/v1.md`
- `backend/app/tests/prompt_skill/test_prompt_files.py`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 3：Add built-in skill files。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_skill_files.py -q`。

风险提醒：

- Task 3 只添加 skill markdown 和对应 focused test，不要混入 registry loader、API、frontend、RAG 或 MCP runtime。

## 2026-06-29 Slice 04 Task 1 AI Runtime Models 完成

本轮完成：

- 完成 Slice 04 Task 1：新增 `AITask`、`Artifact`、`LLMCallLog` ORM models。
- 新增 AI Runtime Pydantic read schemas，并补齐 `created_at`、`updated_at`、`created_by`、`updated_by` 基字段。
- 新增 Alembic migration：`backend/alembic/versions/20260629_0002_ai_runtime_core.py`。
- `AITask.context_artifact_ids` 在 PostgreSQL 上使用 `UUID[]`，在 SQLite 测试路径使用 JSON 兼容存储，Python 层返回 `list[uuid.UUID]`。
- AI Runtime JSON dict 字段使用 `MutableDict`，避免 worker/provider 后续原地更新 `output_json`、`metadata_json` 等字段时静默丢失。
- PromptVersion / SkillVersion 仍按 Task 非目标不建表、不建 relationship、不加 FK；本任务仅保留 `prompt_version_id` 和 `skill_version_id` UUID 字段。
- Artifact 可表达 V1 ContextArtifact：`owner_entity_type=Project`、`owner_entity_id=project_id`、`artifact_type=context_markdown`、`metadata_json` 包含 `title/source_ref/safe_to_show/redaction_applied/allowed_for_prompt`。
- 额外新增 `backend/app/modules/ai_runtime/__init__.py` 作为包入口；这是 `NEXT_AI_TASK.md` expected files 外的必要 Python 包结构文件。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 2：Add Artifact store service。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py backend/app/tests/db/test_ai_runtime_models.py -q
git diff --check
```

验证结果：

- AI Runtime DB focused test：`6 passed in 0.40s`
- Project Core + AI Runtime DB regression：`10 passed in 0.49s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/ai_runtime/__init__.py`
- `backend/app/modules/ai_runtime/models.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/alembic/versions/20260629_0002_ai_runtime_core.py`
- `backend/app/tests/db/test_ai_runtime_models.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 2 Artifact store 尚未实现。
- 迁移层为 AI Runtime 三张表增加了 PostgreSQL `gen_random_uuid()` 和默认用户 UUID server default；早期 `20260626_0001_project_core.py` 仍保持原状，未在本任务中回改历史迁移。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 2：Add Artifact store service。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/artifacts/test_artifact_store.py -q`。

风险提醒：

- Artifact 文件写入、sha256 计算、atomic rename、path traversal 防护是 Task 2；不要在 Task 1 commit 中混入文件系统 store 逻辑。
- ContextArtifact API、redaction、mock provider、worker 状态流转和 AI Task API 仍属后续任务。

## 2026-06-29 Slice 04 Task 2 Artifact Store 完成

本轮完成：

- 完成 Slice 04 Task 2：新增本地 `LocalArtifactStore`。
- Artifact 写入使用同目录临时文件，并通过 `os.replace` 原子替换目标文件。
- 写入结果返回 artifact-relative `file_path`、`size_bytes` 和 `sha256`。
- 读取和写入均拒绝绝对路径、`..` 路径段、root escape 和 root 内 symlink escape。
- 写入失败时清理临时文件，不留下半成品目标文件。
- 新增 `ArtifactWriteResultRead` schema，供后续 API/service 复用。
- 修复 `.gitignore`：将 `artifacts/` 改为 `/artifacts/`，避免误忽略 `backend/app/tests/artifacts/` 测试目录。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 3：Add ContextArtifact API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/artifacts/test_artifact_store.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py -q
git diff --check
```

验证结果：

- Artifact store focused test：`10 passed in 0.11s`
- AI Runtime DB + Artifact store regression：`16 passed in 0.53s`
- `git diff --check` 无输出。

修改文件：

- `.gitignore`
- `backend/app/modules/ai_runtime/artifact_store.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/app/tests/artifacts/test_artifact_store.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 3 ContextArtifact API 尚未实现。
- Artifact store 本任务不做 DB 写入；Artifact row 创建属于 Task 3 service/API。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 3：Add ContextArtifact API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_context_artifacts.py -q`。

风险提醒：

- ContextArtifact 写入前的 secret scan / redaction 策略需要在 Task 3 API/service 中最小实现或明确保守拒绝；不要引入 RAG、vector index 或隐式上下文注入。

## 2026-06-29 Slice 04 Task 3 ContextArtifact API 完成

本轮完成：

- 完成 Slice 04 Task 3：新增 ContextArtifact create/list API。
- `POST /api/context-artifacts` 使用本地 Artifact store 写入内容，并创建 Artifact DB row。
- ContextArtifact Artifact row 使用 `owner_entity_type=Project`、`owner_entity_id=project_id`，客户端不能覆盖 owner fields。
- ContextArtifact `metadata_json` 同时包含 Artifact 基础 metadata：`created_by_component/source_entity_type/source_entity_id/description`，以及 ContextArtifact 专属字段：`title/source_ref/safe_to_show/redaction_applied/redaction_report_artifact_id/allowed_for_prompt`。
- MIME 校验按 `artifact_type` 绑定组合，拒绝 mismatched type/MIME。
- 内容大小限制为 V1 单个 ContextArtifact 1 MiB。
- 写入前对 `title`、`source_ref` 和 `content` 做基础 secret scan；发现高风险内容时返回 `CONTEXT_ARTIFACT_SECRET_DETECTED` 并拒绝保存。
- `GET /api/projects/{project_id}/context-artifacts` 只返回当前 project 的 project-level context artifacts。
- Create 响应不返回原始 content，避免绕过后续展示前 redaction view。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 4：Add Mock LLM Provider。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_context_artifacts.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py backend/app/tests/api/test_context_artifacts.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py backend/app/tests/api/test_context_artifacts.py -q
git diff --check
```

验证结果：

- ContextArtifact API focused test：`9 passed in 0.71s`
- Project API + ContextArtifact API regression：`16 passed in 0.80s`
- AI Runtime DB + Artifact store + ContextArtifact regression：`25 passed in 0.79s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/main.py`
- `backend/app/modules/ai_runtime/router.py`
- `backend/app/modules/ai_runtime/service.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/app/tests/api/test_context_artifacts.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 4 Mock LLM Provider 尚未实现。
- ContextArtifact API 当前只做保守拒绝式 secret scan，不做脱敏保存版本；后续若要 redaction artifact，需要单独任务补 `redaction_report.json`。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 4：Add Mock LLM Provider。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_mock_provider.py -q`。

风险提醒：

- 不要让 Mock Provider 调外部网络。
- 不要在 Task 4 顺手实现 worker handler、AI Task API 或业务 agent endpoint。

## 2026-06-29 Slice 04 Task 4 Mock LLM Provider 完成

本轮完成：

- 完成 Slice 04 Task 4：新增 deterministic Mock LLM Provider。
- 新增 provider base dataclass：`LLMProviderRequest`、`LLMProviderResponse`、`ProviderArtifactPayload`、provider error/timeout exceptions。
- Mock Provider 支持 `success`、`provider_error`、`schema_invalid`、`timeout` 四种测试模式。
- `mock-requirement-review` 输出六维评分、issues、clarification questions、risk items，并回显 `used_context_artifact_ids`。
- `mock-case-generator` 输出 Golden Path 候选用例基本结构。
- 按 mock provider contract 补齐 `mock-automation-draft`、`mock-cicd-analysis`、`mock-unit-test-generator`、`mock-failure-analysis`、`mock-report-generator` 的 deterministic 输出形状。
- Mock Provider 不调用网络、不读取 secrets、不引入真实 provider。
- 成功响应生成内存 artifact payload：`input.json`、`raw_output.json`、`parsed_output.json`、`schema_validation.json`；提供 context 时额外生成 `context_manifest.json`，内容包含 `context_artifact_ids` 和完整 `context_manifest`。
- 额外新增 `backend/app/modules/ai_runtime/providers/__init__.py` 作为包入口；这是 `NEXT_AI_TASK.md` expected files 外的必要 Python 包结构文件。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 5：Add AI Task Enqueue And Worker Handler。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_mock_provider.py -q
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/artifacts/test_artifact_store.py -q
git diff --check
```

验证结果：

- Mock Provider focused test：`11 passed in 0.01s`
- Mock Provider + ContextArtifact + Artifact store regression：`30 passed in 0.71s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/ai_runtime/providers/__init__.py`
- `backend/app/modules/ai_runtime/providers/base.py`
- `backend/app/modules/ai_runtime/providers/mock_provider.py`
- `backend/app/tests/ai_runtime/test_mock_provider.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 5 AI Task worker handler 尚未实现。
- 当前 provider 只产出内存 artifact payload；真正写 Artifact rows 由 Task 5 worker handler 完成。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 5：Add AI Task Enqueue And Worker Handler。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_ai_task_worker.py -q`。

风险提醒：

- Task 5 可以使用 fake queue，不要引入真实 Redis worker CLI，除非当前项目已有稳定 Redis worker 入口。
- Worker 应记录 LLMCallLog 和 Artifact rows，但不要顺手实现 AI Task API 或前端。

## 2026-06-29 Slice 04 Task 5 AI Task Worker 完成

本轮完成：

- 完成 Slice 04 Task 5：新增 fake AI queue 和 AI task worker handler。
- `enqueue_ai_task()` 将 `created` 的 AITask 转为 `pending`，并推入 `FakeAIQueue`。
- Worker 将 `pending` 任务先持久化为 `running`，再调用 Mock Provider。
- 成功路径写入 `input.json`、`context_manifest.json`、`raw_output.json`、`parsed_output.json`、`schema_validation.json` Artifact rows，并创建 LLMCallLog。
- `schema_invalid` 路径将 AITask 标为 `failed`，保存 raw/schema/error artifacts，并记录 LLMCallLog `schema_invalid`。
- `provider_error` 和 `timeout` 路径保留 input/context artifacts，写 `error.json`，将 AITask 标为 `failed`，并记录 LLMCallLog `failed` 或 `timeout`。
- `cancelled` 任务不会被 worker 执行。
- Artifact 写入失败会将 AITask 标为 `failed` 并写入 `ARTIFACT_WRITE_FAILED` error_json。
- 额外新增 `backend/app/workers/__init__.py` 和 `backend/app/workers/handlers/__init__.py` 作为包入口；这是 `NEXT_AI_TASK.md` expected files 外的必要 Python 包结构文件。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 6：Add AI Task API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_ai_task_worker.py -q
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_ai_task_worker.py backend/app/tests/ai_runtime/test_mock_provider.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q
git diff --check
```

验证结果：

- AI Task Worker focused test：`9 passed in 0.56s`
- Worker + Mock Provider regression：`20 passed in 0.59s`
- AI Runtime related regression：`45 passed in 1.03s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/ai_runtime/service.py`
- `backend/app/workers/__init__.py`
- `backend/app/workers/enqueue.py`
- `backend/app/workers/handlers/__init__.py`
- `backend/app/workers/handlers/ai_task_handler.py`
- `backend/app/tests/ai_runtime/test_ai_task_worker.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 6 AI Task API 尚未实现。
- Worker 当前使用 fake queue；没有引入真实 Redis worker CLI。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 6：Add AI Task API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_ai_tasks.py -q`。

风险提醒：

- AI Task API 只返回 artifact metadata 和路径，不要暴露 raw LLM output 内容。
- 不要在 Task 6 顺手实现 requirement review/case generation endpoint 或前端。

## 2026-06-29 Slice 04 Task 6 AI Task API 完成

本轮完成：

- 完成 Slice 04 Task 6：新增 AI Task status/detail API。
- 新增 `GET /api/ai-tasks/{ai_task_id}`，返回 task status、Agent、Prompt/Skill id、provider/model、token usage、context artifact ids、used context ids、context manifest artifact id、artifact summaries 和 LLM call logs。
- 新增 `GET /api/projects/{project_id}/ai-tasks`，按 project 返回最近 AI tasks 的最小列表。
- API 只返回 artifact metadata、safe flags、sha256 和路径，不返回 artifact 原始 content。
- `used_context_artifact_ids` 优先来自 task output，缺省时回退到 `AITask.context_artifact_ids`，保证前端能看见上下文使用。
- 按评审修复 worker artifact 安全 metadata：`raw_llm_output` 和 `error_json` 默认 `safe_to_show=false`，避免 API 把原始 LLM 输出标成可直接展示。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 7：Add AI task frontend status shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_ai_task_worker.py::test_worker_runs_pending_task_and_records_artifacts_and_llm_log -q
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_ai_task_worker.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ai_tasks.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ai_tasks.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_projects.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q
git diff --check
```

验证结果：

- Worker raw artifact metadata regression：`1 passed in 0.35s`
- AI Task Worker focused test：`9 passed in 0.47s`
- AI Task API focused test：`4 passed in 0.57s`
- Project API + ContextArtifact API + AI Task API regression：`20 passed in 0.79s`
- AI Runtime related regression：`49 passed in 0.94s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/ai_runtime/router.py`
- `backend/app/modules/ai_runtime/service.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/app/tests/api/test_ai_tasks.py`
- `backend/app/tests/ai_runtime/test_ai_task_worker.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 7 AI Workbench frontend status shell 尚未实现。
- 当前 AI Task API 不提供 artifact download/read endpoint；前端只能展示 metadata 和 file path。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 7：Add AI task frontend status shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

风险提醒：

- Slice 02.5 Frontend Foundation 已完成，可以进入 Task 7。
- 前端必须保持中文优先、浅色 Arco 工作台风格，只做最近 AI 任务列表和详情壳。
- 不要在 Task 7 展示 raw LLM output content；只展示 artifact metadata、safe flags 和路径。
- 不要在 Task 7 顺手实现完整 requirement review/case generation UI、图表大屏、RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 04 Task 7 AI Workbench 前端状态壳完成

本轮完成：

- 完成 Slice 04 Task 7：新增 AI Workbench frontend status shell。
- 新增 `frontend/src/api/aiTasks.ts`，按后端 schema 定义 AI task list/detail、artifact summary 和 LLM call log 类型，并封装 `GET /api/projects/{project_id}/ai-tasks` 与 `GET /api/ai-tasks/{id}`。
- 新增 `frontend/src/stores/aiTasks.ts` Pinia store，维护默认单用户 project、recent tasks、selected task、loading/error 状态和简要指标。
- 更新 `AI 工作台` 页面：保留后端健康 smoke，新增最近 AI 任务列表、任务详情、Prompt/Skill id、provider/model、token usage、上下文工件、已使用上下文、工件摘要和大模型调用日志。
- 工件区域只展示 artifact metadata、路径、MIME、大小、sha256、`safe_to_show` 和 `redaction_applied` 状态；不拉取或展示 raw LLM output content。
- 大模型调用日志展示 provider/model/status、response artifact id、latency 和 token usage，保留证据追溯入口。
- 页面继续使用 Vue 3 + Arco Design Vue，中文优先，浅色工作台布局，不新增完整需求评审 UI、case generation UI、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Completion Gate。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run test -- --run
npm --prefix frontend run build
```

验证结果：

- AI Workbench focused test：`3 passed`
- Frontend Vitest suite：`7 passed`
- Frontend build：通过；仍有既有 Arco bundle size warning。

修改文件：

- `frontend/src/api/aiTasks.ts`
- `frontend/src/stores/aiTasks.ts`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

未完成问题：

- Slice 04 completion gate 尚未执行。
- AI Workbench 当前只提供状态壳和 metadata 详情，不提供 artifact download/read、任务创建入口或完整业务评审动作。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Completion Gate。
- 完成后将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 1：Add PromptVersion and SkillVersion models。

风险提醒：

- Completion Gate 应跑 backend AI runtime regression、frontend tests、frontend build 和 `git diff --check`。
- 不要在 completion gate 顺手实现 Prompt/Skill models；先完成 Slice 04 总验收和 handoff。

## 2026-06-29 Slice 04 Completion Gate 完成

本轮完成：

- 完成 Slice 04 AI Runtime Core completion gate。
- `docs/implementation/slices/slice-04-ai-runtime-core.md` 中 Task 1-7 均为 `done`，并记录 commit：`11bb6cc`、`5b17d26`、`d7570ba`、`693e171`、`63efbc6`、`f006cb2`、`31ce363`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 1：Add PromptVersion and SkillVersion models。
- Slice 04 范围保持干净：未引入真实 provider、RAG/vector runtime、MCP runtime、requirement review endpoint 或 case generation endpoint。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q
npm --prefix frontend run test -- --run
npm --prefix frontend run build
git diff --check
```

验证结果：

- AI Runtime backend regression：`49 passed in 1.58s`
- Frontend Vitest suite：`7 passed`
- Frontend build：通过；仍有既有 Arco bundle size warning。
- `git diff --check` 无输出。

修改文件：

- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

未完成问题：

- Slice 05 Prompt And Skill Registry 尚未开始。
- AI Workbench 仍只展示 AI task/status/evidence metadata，不提供 artifact download/read 或任务创建入口。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 1：Add PromptVersion and SkillVersion models。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/db/test_prompt_skill_models.py -q`。

风险提醒：

- Slice 05 Task 1 只做 PromptVersion/SkillVersion models、schemas、migration 和 DB test。
- 不要在 Task 1 顺手添加 prompt markdown、skill markdown、registry loader、API、frontend、真实 provider、RAG/vector runtime 或 MCP runtime。

## 2026-06-29 Slice 05 Task 1 Prompt/Skill Models 完成

本轮完成：

- 完成 Slice 05 Task 1：新增 `PromptVersion` 和 `SkillVersion` models。
- 新增 `backend/app/modules/prompt_skill/models.py`，包含 `prompt_versions` 和 `skill_versions` 表定义。
- 新增 `backend/app/modules/prompt_skill/schemas.py`，提供 `PromptVersionRead` 和 `SkillVersionRead`。
- 新增 Alembic migration：`backend/alembic/versions/20260629_0003_prompt_skill_registry.py`。
- PromptVersion 字段覆盖：`name/version/hash/agent_name/content/input_schema_json/output_schema_json/status` 和通用 timestamp/user 字段。
- SkillVersion 字段覆盖：`name/version/hash/applicable_agents/content/quality_gates_json/forbidden_actions_json/tool_permissions_json/status` 和通用 timestamp/user 字段。
- 两张表均增加 `name + version` 唯一约束。
- JSON dict/list 字段使用 SQLAlchemy mutable 类型，支持 in-place 更新被持久化。
- `applicable_agents` 在 PostgreSQL 使用 `text[]`，SQLite 测试路径使用 JSON 兼容存储。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 2：Add built-in prompt files。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_prompt_skill_models.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/db/test_prompt_skill_models.py -q
git diff --check
```

验证结果：

- Prompt/Skill model focused test：`5 passed in 0.36s`
- Project Core + AI Runtime + Prompt/Skill DB regression：`15 passed in 0.38s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/prompt_skill/__init__.py`
- `backend/app/modules/prompt_skill/models.py`
- `backend/app/modules/prompt_skill/schemas.py`
- `backend/alembic/versions/20260629_0003_prompt_skill_registry.py`
- `backend/app/tests/db/test_prompt_skill_models.py`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

未完成问题：

- Built-in prompt markdown files 尚未添加。
- Built-in skill markdown files、registry loader、Prompt/Skill API、Prompt/Skill frontend shell 尚未开始。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 2：Add built-in prompt files。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_prompt_files.py -q`。

风险提醒：

- Task 2 只添加 prompt markdown 和 prompt file tests；不要顺手实现 skill files、registry loader、API 或 frontend。
- Prompt 输出必须 JSON-only，不允许 markdown fences 作为模型主输出。

## 当前用户最新明确要求

- Chtest 项目必须放在 `/Users/yanchen/VscodeProject/Chtest`。
- 第一版就做单用户模式。
- 第一版直接使用 PostgreSQL + Redis。
- 不要一次性演示，要真实能大幅提高测试效率的 AI 工具。
- 最新定位已校准为：面向个人测试工程师、自动化测试工程师的 AI 测试设计与自动化落地工作台。
- 长期方向是小团队 AI 测试工作台 + Agent / Skill / MCP 测试工具生态。
- V1 三条最小闭环：需求到用例、用例到自动化、CI/CD 质量中心中的本地 diff 到质量门禁和证据报告。
- 用户可见 CI/CD 支线页面统一为 `CI/CD 质量中心`；当前契约名使用 `CICDRun`、`CICDChangedFile`、`QualityGateDecision`、`UnitTestPatch`。
- 新增用户可见页面 `RAG 知识库`；RAG 功能只保留 ContextArtifact + KnowledgeAdapter surface，后续外部搭建后接入。
- MCP / Skill / Prompt / Agent 要分层设计并贯穿各流程。
- 新代码 push/PR/diff 后生成单测、执行回归，并有独立页面查看 Git 情况。
- 增加 Web 自动化能力，但 V1 只做 Playwright 最小闭环；Newman/JMeter 后置。
- 文档必须足够详细，方便后续 AI 读取后继续完成项目。
- 长期 AI 开发必须遵循 `docs/implementation/04-ai-vibecoding-governance.md`：小步 Task、每步验证、每个完成 Task 提交、可回滚；Slice 完成和重大上下文变化时更新 memory。
- 当前前端设计必须中文优先；页面标题、导航、按钮、表头、空状态和状态文案都用中文。
- 当前前端最终设计采用 A 方案浅色系、Vue 3 + Arco Design Vue、工作台式信息密度，详见 `docs/product/08-frontend-design-spec.md`。
- `ContextArtifact`、`AITask`、`LLMCallLog`、`Artifact` 的用户可见名称分别写成 `上下文工件`、`AI 任务`、`大模型调用日志`、`工件`。

## 当前本地状态

- 本地目录：`/Users/yanchen/VscodeProject/Chtest`
- memory 目录：`/Users/yanchen/VscodeProject/Chtest/memory`
- WHartTest：`/Users/yanchen/VscodeProject/Chtest/参考框架/WHartTest`，参考提交 `927bff2`
- MeterSphere：`/Users/yanchen/VscodeProject/Chtest/参考框架/metersphere`，参考提交 `5dc6df5`
- 参考框架目录应保留本地，但默认不纳入 Chtest Git 提交记录。
- Chtest 已初始化为独立 Git 仓库。
- 当前工作分支：`codex/cicd-quality-docs`。
- Git remote `origin` 已设置为 `https://github.com/2696437448-cmyk/Chtest.git`。
- 当前最新已 push commit：`1fb52c1 docs(process): tighten vibecoding readiness docs`。
- 本轮一致性修复开始前的最新本地提交：`6ed134a docs(memory): hand off slice one worker task`。
- 当前最新本地提交以 `git log -1 --oneline` 为准。
- 当前未 push 的本地提交包括 Slice 1 Tasks 1-3 和后续 handoff 更新。
- GitHub 提示仓库已迁移到 `https://github.com/YanChen0111/Chtest.git`，但当前 origin 仍指向旧地址。
- 本轮 ContextArtifact 文档契约修复作为本地提交保存；push 仍需用户明确要求。
- Slice 02.5 Task 1 已完成并提交：`daf5b7c feat(frontend): scaffold vue workbench app`。
- Slice 02.5 Task 2 已完成并提交：`2ec1c7c feat(frontend): add workbench shell`。
- Slice 02.5 Task 3 已完成并提交：`6526a2b build(frontend): wire vite dev container`。
- Slice 02.5 Task 4 已完成并提交：`de1f5fd feat(frontend): add health probe smoke`。
- Slice 02.5 Frontend Foundation 已完成。
- Slice 03 Task 1 已完成：Add Project Core models and migration。
- 当前 `NEXT_AI_TASK.md` 已切换到 Slice 03 Task 2：Add Project CRUD API。
- 当前前端 shell 已有中文主导航、AI 工作台首页、Pinia、Vue Router、Arco Design Vue、`api/client.ts` 和 `/health` smoke。
- 当前前端 build 会给出 bundle 偏大的 warning，来源于 Arco baseline；不是阻塞问题，但后续可以在稳定后做按需优化。
- 2026-06-26 已固化最终前端设计文档：`docs/product/08-frontend-design-spec.md` 和 `docs/superpowers/specs/2026-06-26-chtest-final-frontend-design.md`。
- 后续实现前端页面时优先读取 `docs/product/08-frontend-design-spec.md`、`docs/product/03-user-journey-and-page-prd.md` 和 `docs/product/06-frontend-ui-guidelines.md`。

## 2026-06-26 Slice 03 Task 1 后端迁移完成

本轮完成：

- 新增后端 Python 依赖入口：`backend/pyproject.toml`。
- 新增 SQLAlchemy 基础包和 Project Core 模型：`Workspace`、`User`、`Project`、`Module`、`Repository`、`Environment`、`TestCommand`。
- 新增 Alembic migration：`backend/alembic/versions/20260626_0001_project_core.py`。
- 新增聚焦 DB 测试：`backend/app/tests/db/test_project_core_models.py`。
- 将 WHartTest 参考源码映射写入 `docs/reference/01-open-source-migration-map.md`，明确只吸收项目聚合根、模块树、环境变量、测试命令入口，不迁移 RBAC、凭据、远程执行器和完整任务编排。
- 更新 `docs/implementation/slices/slice-03-project-core.md` 和 `NEXT_AI_TASK.md`。

本轮验证：

```bash
UV_CACHE_DIR=.tmp/uv-cache uv --project backend run pytest backend/app/tests/db/test_project_core_models.py -q
```

验证结果：

- `4 passed in 0.32s`

下一步：

- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 2：Add Project CRUD API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py -q`。
- 不要在 Task 2 顺手实现 repository path validation、environment mutation API、TestCommand validation、AI task models、ToolInvocation 或多用户权限。

## 2026-06-29 Slice 03 Task 2 Project API 完成

本轮完成：

- 完成 Slice 03 Task 2：新增 Project create/read/update API。
- 新增 Project Settings bootstrap API：返回 project、modules、repositories、environments、test_commands 和空的 tool_definitions。
- 新增最小 FastAPI app 入口和 Project router。
- 扩展 Project schema 和 service，复用 Task 1 的 SQLAlchemy Project Core models。
- 新增聚焦 API 测试：`backend/app/tests/api/test_projects.py`。
- 根据只读 code review 修复两个 API 契约缺口：422 validation error envelope 和重复项目名 409 envelope。
- 因当前 `.venv` 未安装 `httpx2`，测试使用文件内最小 ASGI client 直接调用 FastAPI app，不新增依赖。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 03 Task 3：Add Module tree API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py -q
git diff --check
```

验证结果：

- Project API focused test：`7 passed in 0.53s`
- Project Core DB regression：`4 passed in 0.35s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/main.py`
- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/modules/projects/service.py`
- `backend/app/tests/api/test_projects.py`
- `docs/implementation/slices/slice-03-project-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 3 尚未实现 Module tree API。
- 当前 Project API 只覆盖 Project 自身和 settings bootstrap；Repository、Environment、TestCommand 的 mutation 和 validation 留给 Slice 03 Task 4/5。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 3：Add Module tree API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_modules.py -q`。

风险提醒：

- 当前测试未使用 `fastapi.testclient.TestClient`，因为 Starlette 版本要求额外安装 `httpx2`；后续若统一 API 测试 fixture，可选择补依赖或保留轻量 ASGI client。

## 2026-06-29 Slice 03 Task 3 Module API 完成

本轮完成：

- 完成 Slice 03 Task 3：新增 Module create/list/update API。
- Root module 自动派生 `level=1` 和 `path=/{name}`。
- Child module 校验 parent 属于同一 project，并自动派生 `level`、`parent_id` 和层级 path。
- 强制五级模块树限制。
- 同一 project + 同一 parent 下 module name 冲突返回 `MODULE_ALREADY_EXISTS`。
- 根据只读 code review 修复父模块重命名后 descendant path 陈旧问题，新增回归测试覆盖。
- 新增聚焦 API 测试：`backend/app/tests/api/test_modules.py`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 03 Task 4：Add Repository and Environment API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_modules.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py -q
git diff --check
```

验证结果：

- Module API focused test：`9 passed in 0.61s`
- Project API regression：`7 passed in 0.48s`
- Project Core DB regression：`4 passed in 0.32s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/modules/projects/service.py`
- `backend/app/tests/api/test_modules.py`
- `docs/implementation/slices/slice-03-project-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 4 尚未实现 Repository and Environment API。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 4：Add Repository and Environment API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_repository_environment.py -q`。

风险提醒：

- Repository path allowlist 属于 Task 4，不要在 Task 3 里补。

## 2026-06-29 Slice 03 Task 4 Repository/Environment API 完成

本轮完成：

- 完成 Slice 03 Task 4：新增 Repository create/list/update API。
- 新增 Environment create/list/update API。
- Repository `local_path` 会校验路径存在，并且必须位于 `CHTEST_REPOSITORY_ALLOWLIST_ROOTS` 配置的 allowlist 根目录下。
- Repository 路径保存为 resolve 后的绝对路径。
- Environment 拒绝 secret-like 明文变量值，要求使用 `ref:` 引用形式。
- 根据只读 code review 补充 raw secret 拒绝测试和实现。
- 新增聚焦 API 测试：`backend/app/tests/api/test_repository_environment.py`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 03 Task 5：Add TestCommand API and validation。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_repository_environment.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_modules.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py -q
git diff --check
```

验证结果：

- Repository/Environment API focused test：`10 passed in 0.69s`
- Module API regression：`9 passed in 0.70s`
- Project API regression：`7 passed in 0.61s`
- Project Core DB regression：`4 passed in 0.40s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/modules/projects/service.py`
- `backend/app/tests/api/test_repository_environment.py`
- `docs/implementation/slices/slice-03-project-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 5 尚未实现 TestCommand API and validation。
- Repository create/update 不运行 git 命令；`.git` 校验和 Git workflow 细化如需启用，应在后续明确任务中补充。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 5：Add TestCommand API and validation。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_commands.py -q`。

风险提醒：

- TestCommand allowlist、working_directory 校验和禁止 shell operator 是 Task 5，不要在 Task 4 commit 中混入命令执行。

## 2026-06-29 Slice 03 Task 5 TestCommand API 完成

本轮完成：

- 完成 Slice 03 Task 5：新增 TestCommand create/list/update/validate API。
- TestCommand command_type 支持 V1 安全 allowlist：`pytest`、`npm test` / `npm run test`、`npx playwright test`。
- 禁止 shell operator 和多命令拼接，包括 `&&`、`||`、`;`、`|`、单 `&`、重定向、反引号、`$()` 和换行。
- `working_directory` 必须存在且位于所选 Repository `local_path` 下。
- `environment_id` 必须为空或属于同一 project。
- Validate endpoint 只做静态校验，不执行命令。
- 根据只读 code review 修复单 `&`/换行绕过、Playwright 前缀边界过松、跨项目 environment_id 三个问题。
- 新增聚焦 API 测试：`backend/app/tests/api/test_test_commands.py`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 03 Task 6：Add Project Settings frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_commands.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_repository_environment.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_modules.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py -q
git diff --check
```

验证结果：

- TestCommand API focused test：`9 passed in 1.10s`
- Repository/Environment API regression：`10 passed in 0.86s`
- Module API regression：`9 passed in 0.91s`
- Project API regression：`7 passed in 0.69s`
- Project Core DB regression：`4 passed in 0.45s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/modules/projects/service.py`
- `backend/app/tests/api/test_test_commands.py`
- `docs/implementation/slices/slice-03-project-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 6 尚未实现 Project Settings frontend shell。
- Slice 03 completion gate 尚未执行。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 6：Add Project Settings frontend shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

风险提醒：

- Task 5 没有执行命令、没有 git 命令执行、没有 ToolInvocation；后续 runner slice 必须继续复用这些安全校验，而不是接受任意 shell。

## 2026-06-29 Slice 03 Task 6 Project Settings 前端壳完成

本轮完成：

- 完成 Slice 03 Task 6：新增 Project Settings frontend shell。
- 新增 `frontend/src/api/projects.ts` typed API helper，读取 `/api/projects/{id}/settings`。
- 扩展 `frontend/src/api/client.ts` 支持 JSON 响应。
- 新增 `frontend/src/stores/projectSettings.ts`，管理项目设置加载、错误和数据状态。
- 新增 `frontend/src/views/settings/ProjectSettingsView.vue`，以中文工作台页面展示项目概览、模块树、仓库、环境变量和测试命令。
- 接入 Vue Router：`/settings/project` / route name `project-settings`。
- 导航中的 `Git 质量中心` 已改为 `CI/CD 质量中心`，设置入口指向项目设置页。
- 更新 WorkbenchLayout 让顶部标题优先使用 route meta title。
- 根据只读 code review 修复侧栏“设置”仍 fallback 到 AI 工作台的问题，并补充导航链接断言。
- `client.ts`、`stores/index.ts`、`global.css` 和 `WorkbenchLayout.*` 虽不在原 Expected Files 列表内，但分别是 JSON API 支持、导航接入、页面样式和 route title 行为的必要最小改动。

本轮验证：

```bash
npm --prefix frontend run test -- --run
npm --prefix frontend run build
git diff --check
```

验证结果：

- Frontend test：`4 passed (4), 6 passed (6)`
- Frontend build：通过；仍有既有 Arco bundle size warning。
- `git diff --check` 无输出。

修改文件：

- `frontend/src/api/client.ts`
- `frontend/src/api/projects.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `frontend/src/stores/projectSettings.ts`
- `frontend/src/layouts/WorkbenchLayout.vue`
- `frontend/src/layouts/WorkbenchLayout.spec.ts`
- `frontend/src/styles/global.css`
- `frontend/src/views/settings/ProjectSettingsView.vue`
- `frontend/src/views/settings/ProjectSettingsView.spec.ts`
- `docs/implementation/slices/slice-03-project-core.md`
- `memory/08-session-handoff.md`

未完成问题：

- Slice 03 completion gate 尚未执行。
- 当前前端使用默认 project id 作为 shell smoke；后续需要项目选择/创建流程后再改为真实当前项目上下文。

下次推荐任务：

- 执行 Slice 03 completion gate review。
- 若通过，更新 handoff 到 Slice 04 AI Runtime Core。

风险提醒：

- Project Settings 前端壳只做查看和基础刷新，不实现完整编辑表单、拖拽模块树或命令执行。

## 2026-06-29 Slice 03 Completion Gate 完成

本轮完成：

- Slice 03 Project Core 所有任务已完成并提交。
- `docs/implementation/slices/slice-03-project-core.md` task table 已更新 commit hash。
- `NEXT_AI_TASK.md` 已切换到 Slice 04 Task 1：Add AI Runtime models and migration。
- `memory/07-dev-log.md` 已追加 Slice 03 completion 记录。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py backend/app/tests/api/test_modules.py backend/app/tests/api/test_repository_environment.py backend/app/tests/api/test_test_commands.py backend/app/tests/db/test_project_core_models.py -q
npm --prefix frontend run test -- --run
npm --prefix frontend run build
git diff --check
```

验证结果：

- Backend Slice 03 related tests：`39 passed in 2.61s`
- Frontend test：`4 passed (4), 6 passed (6)`
- Frontend build：通过；仍有既有 Arco bundle size warning。
- `git diff --check` 无输出。

Slice 03 commits：

- `d87036d feat(projects): add project core backend`
- `6c12d64 feat(projects): add project settings api`
- `57e64f4 feat(projects): add module tree api`
- `7c8471f feat(projects): add repository and environment api`
- `47f6724 feat(projects): add test command validation`
- `524b7c7 feat(frontend): add project settings shell`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 1：Add AI Runtime models and migration。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py -q`。

风险提醒：

- 当前本地分支领先远端多个提交，尚未 push。
- 前端 build 的 Arco chunk size warning 仍是已知非阻塞项。
- Slice 04 不要引入真实 LLM、RAG/vector runtime、PromptVersion/SkillVersion models 或 MCP runtime；Task 1 只做 AITask/Artifact/LLMCallLog 模型和 migration。

## 2026-06-26 前端最终设计文档同步

本轮完成：

- 根据用户确认的 A 方案浅色系，新增最终前端设计规格。
- 将用户可见 CI/CD 支线页面统一为 `CI/CD 质量中心`。
- 将当前契约和 Golden Path 对齐到 `CICDRun`、`CICDChangedFile`、`CICDChangeAnalysisAgent`、`QualityGateDecision`、`/api/cicd/runs` 和 `docs/fixtures/03-golden-cicd-quality.md`。
- 新增 `RAG 知识库` 页面设计和 V1 边界说明。
- 同步产品、架构、实施计划、memory 和入口文档，方便后续 AI coding。

本轮验证：

- 文档变更需以本轮最终 `git diff --check` 和旧命名 grep 审计为准。

修改文件：

- `docs/product/08-frontend-design-spec.md`
- `docs/superpowers/specs/2026-06-26-chtest-final-frontend-design.md`
- `docs/product/*`
- `docs/architecture/*`
- `docs/implementation/*`
- `docs/README.md`
- `START_HERE_FOR_AI.md`
- `NEXT_AI_TASK.md`
- `memory/*`

未完成问题：

- 当前实现任务仍以 `NEXT_AI_TASK.md` 的 Slice 03 Task 1 为准，本轮不进入前端页面实现。

下次推荐任务：

- 继续 Slice 03 Task 1：Add Project Core models and migration。

风险提醒：

- `CI/CD 质量中心` 是 V1 本地 diff 支线，不是云 CI/CD 平台。
- `RAG 知识库` 是 ContextArtifact 和 KnowledgeAdapter surface，不是内置 RAG/vector/rerank 平台。

## 2026-06-23 继续执行更新

本轮完成：

- 根据产品/市场评审结果收紧 vibecoding 执行准备文档。
- 切出工作分支 `codex/chtest-vibecoding-foundation`，避免继续在 `main` 上叠加实现提交。
- 完成 Slice 1 Task 1：初始化 `backend/`、`frontend/`、`worker/`、`deploy/`、`prompts/`、`skills/`、`mcp_tools/`、`artifacts/` 八个顶层目录，并为每个目录加入 `.gitkeep`。
- `artifacts/` 受 `.gitignore` 忽略，已使用 `git add -f artifacts/.gitkeep` 只跟踪占位文件，运行产物仍保持忽略。
- 完成 Slice 1 Task 2：添加 PostgreSQL 和 Redis 的 Docker Compose 基础。
- 完成 Slice 1 Task 3：添加 backend container placeholder。
- 已更新 `NEXT_AI_TASK.md`，当前下一任务为 Slice 1 Task 4：Add worker container placeholder。
- 修复全量文档复审发现的漏改：入口文档仍指向已完成任务、`.env.example` 容器连接串使用本地回环地址、Artifact Docker 路径不一致、裸 Compose 启动命令不匹配 `deploy/docker-compose.yml` 位置、历史评审/计划文档未标注历史状态。

本轮验证：

```bash
git diff --check --cached
find backend frontend worker deploy prompts skills mcp_tools artifacts -maxdepth 1 -type f -name .gitkeep
docker compose --env-file .env.example -f deploy/docker-compose.yml config
docker compose -f deploy/docker-compose.yml config
```

验证结果：

- `git diff --check --cached` 无输出。
- `find ... .gitkeep` 打印 8 个 `.gitkeep` 文件。
- 两个 Docker Compose config 命令均能渲染，backend 环境变量使用 `postgres`、`redis` 和 `/opt/chtest/artifacts`。

本轮提交：

| Commit | Content | Verification |
|---|---|---|
| `58104e5` | 收紧执行准备文档，统一 Slice 1 验收命令，补充 sample repository 前置，降低早期指标看板优先级 | `git diff --check` |
| `a7cd981` | 初始化 8 个平台目录和 `.gitkeep` | `find backend frontend worker deploy prompts skills mcp_tools artifacts -maxdepth 1 -type f -name .gitkeep` |
| `360ab7a` | 添加 PostgreSQL 和 Redis Docker Compose 服务及本地 `.env.example` | `docker compose -f deploy/docker-compose.yml config` |
| `4160695` | 添加 backend Dockerfile、README 和 Docker Compose backend service placeholder | `docker compose -f deploy/docker-compose.yml config` |

下次推荐任务：

- Slice 1 Task 4：添加 worker container placeholder。
- 必读：`NEXT_AI_TASK.md`、`docs/implementation/slices/slice-01-platform-foundation.md`、`docs/deployment/01-docker-environment.md`。
- 验证命令：`docker compose -f deploy/docker-compose.yml config`。

风险提醒：

- 当前分支尚未 push。
- `origin` 仍指向旧 GitHub 地址；是否切换 remote 仍需用户明确确认。
- 不要在 Task 4 实现 RQ worker、AI runtime 或队列业务逻辑。

## 本轮完成

本轮按用户整理的优化稿执行了系统性文档优化：

新增：

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/fixtures/01-golden-requirement-to-case.md`
- `docs/fixtures/02-golden-case-to-playwright.md`
- `docs/fixtures/03-golden-cicd-quality.md`
- `docs/implementation/01-v1-development-process.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/03-testing-and-acceptance.md`

更新：

- `docs/product/02-v1-product-prd.md`
- `docs/product/05-non-goals-and-version-boundaries.md`
- `docs/architecture/03-implementation-technology.md`
- `docs/implementation/01-v1-delivery-plan.md`
- `docs/README.md`
- `memory/README.md`
- `memory/00-ai-session-protocol.md`
- `memory/11-implementation-slices.md`
- `memory/13-ai-readable-project-brief.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

## 当前正式文档结构重点

- AI 开工入口：`START_HERE_FOR_AI.md`
- V0.1 早期闭环：`docs/implementation/00-v0.1-walking-skeleton.md`
- 定位：`docs/product/01-positioning-and-scope.md`
- 总 PRD：`docs/product/02-v1-product-prd.md`
- 页面 PRD：`docs/product/03-user-journey-and-page-prd.md`
- 数据模型契约：`docs/contracts/01-data-model-contract.md`
- API 契约：`docs/contracts/02-api-contract.md`
- 状态机：`docs/contracts/03-state-machines.md`
- Artifact：`docs/contracts/04-artifact-contract.md`
- Prompt/Skill：`docs/contracts/05-prompt-skill-contract.md`
- Golden Path 0：`docs/fixtures/00-v1-demo-path.md`
- Golden Path 1：`docs/fixtures/01-golden-requirement-to-case.md`
- Golden Path 2：`docs/fixtures/02-golden-case-to-playwright.md`
- Golden Path 3：`docs/fixtures/03-golden-cicd-quality.md`
- 开发流程：`docs/implementation/01-v1-development-process.md`
- 切片计划：`docs/implementation/02-v1-slice-plan.md`
- Slice 1 Task Plan：`docs/implementation/slices/slice-01-platform-foundation.md`
- Slice 2 Task Plan：`docs/implementation/slices/slice-02-backend-core.md`
- 测试验收：`docs/implementation/03-testing-and-acceptance.md`
- AI vibecoding 治理：`docs/implementation/04-ai-vibecoding-governance.md`

## 下次 AI 会话开工步骤

1. 进入 `/Users/yanchen/VscodeProject/Chtest`。
2. 读取 `START_HERE_FOR_AI.md`。
3. 读取 `memory/README.md`。
4. 读取 `memory/13-ai-readable-project-brief.md`。
5. 读取 `docs/product/01-positioning-and-scope.md`。
6. 读取 `docs/implementation/00-v0.1-walking-skeleton.md`。
7. 读取 `docs/contracts/*`。
8. 根据任务读取 `docs/fixtures/*`。
9. 查看 `docs/implementation/01-v1-development-process.md`。
10. 读取 `docs/implementation/04-ai-vibecoding-governance.md`。
11. 查看 `docs/implementation/02-v1-slice-plan.md` 或 `memory/11-implementation-slices.md`。
12. 查看 `git status --short`。
13. 进入 Slice 03 Task 1：Add Project Core models and migration。
14. Slice 03 先做 backend models/migration，再做 API，再做 frontend Project Settings shell。
15. 前端页面文案继续保持中文优先；backend 这一轮不要顺手扩成 AI runtime、ToolInvocation 或多用户权限。
16. 每次只做一个 Slice 内的 1-3 个 Task；每个完成 Task 必须验证并 commit；Slice 完成或重大上下文变化时更新 handoff。

## Memory 更新原则

```text
Git 记录代码历史。
Memory 记录会话接续。
Contracts 记录实现真相。
```

- 每个 Task：测试 + commit。
- 每个 Slice：测试汇总 + commit 汇总 + 更新 memory。
- 每个重大变化：立即更新 memory。
- `memory/07-dev-log.md` 写长期摘要。
- `memory/08-session-handoff.md` 写下一轮 AI 如何接手。

## AI Vibecoding Task Table Template

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| - | planned | - | - | - |

Allowed statuses: `planned`, `doing`, `blocked`, `done`, `reverted`.

## Commit Record Template

| Commit | Content | Verification |
|---|---|---|
| - | - | - |

## Verification / Risk Template

```text
Unverified items:
Risk:
Next verification command:
Latest stable commit:
Next recommended Task:
```

## 推荐下一步

开始实现 V1 平台骨架：

- 先读 `START_HERE_FOR_AI.md` 和 `docs/implementation/00-v0.1-walking-skeleton.md`。
- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 1：先落 Project / Module / Repository / Environment / TestCommand 的 model 和 migration。
- PostgreSQL + Redis Compose 和 backend placeholder 已完成。
- 建 FastAPI 健康检查和数据库连接。
- 建 Alembic 迁移骨架。
- 建 Vue 3 + Arco 前端骨架。
- 做单用户上下文。
- 建 mock LLM provider，为后续 AI Task Core 铺路。
- 完成 Slice 1-5 后，优先跑 V0.1 Walking Skeleton，再扩展完整 V1 Minimum Demo。

## 仍需用户确认

- 是否需要把 Git remote `origin` 改为 `https://github.com/YanChen0111/Chtest.git`。
- 本轮 ContextArtifact 文档修复完成后，是否需要 push。
- LLM 第一接入方式：OpenAI 官方 API、Azure OpenAI、兼容代理网关，还是 Ollama。
