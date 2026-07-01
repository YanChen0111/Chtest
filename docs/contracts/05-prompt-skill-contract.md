# Chtest Prompt And Skill Contract

## 1. 文档目的

本文定义 PromptVersion 和 SkillVersion 的文件格式、版本规则、输出约束和质量门禁。Chtest 的 AI 能力必须可追溯、可复盘、可比较，不能依赖临时口头提示词。

## 2. Prompt 目录

```text
prompts/
  requirement_review/v1.md
  risk_matrix/v1.md
  case_generation/v1.md
  case_review/v1.md
  automation_draft_generation/v1.md
  cicd_change_analysis/v1.md
  unit_test_generation/v1.md
  regression_selection/v1.md
  tool_execution/v1.md
  failure_analysis/v1.md
  report_generation/v1.md
```

Future knowledge-driven prompts are added only after their data and artifact
contracts exist:

```text
prompts/
  knowledge_card_extraction/v1.md
  requirement_understanding/v1.md
  risk_analysis/v1.md
  coverage_analysis/v1.md
  test_design/v1.md
  evidence_case_generation/v1.md
  evidence_case_review/v1.md
  case_dedup/v1.md
  automation_readiness/v1.md
  knowledge_feedback/v1.md
```

## 3. Skill 目录

```text
skills/
  requirement-review-skill/v1.md
  test-case-generation-skill/v1.md
  testcase-review-skill/v1.md
  automation-draft-skill/v1.md
  unit-test-generation-skill/v1.md
  regression-selection-skill/v1.md
  tool-execution-skill/v1.md
  failure-analysis-skill/v1.md
  report-generation-skill/v1.md
```

Future knowledge-driven skills:

```text
skills/
  knowledge-ingestion-skill/v1.md
  risk-analysis-skill/v1.md
  coverage-analysis-skill/v1.md
  test-design-skill/v1.md
  knowledge-feedback-skill/v1.md
```

Future skills extend the V1 testing workflow; they do not enable full RAG
runtime, vector databases, GraphRAG runtime, MCP runtime, external provider
calls, generated-case auto-approval, or tool execution by themselves.

## 4. Prompt 文件格式

每个 Prompt 文件必须包含以下段落：

```markdown
# Prompt: requirement_review v1

## Agent
RequirementReviewAgent

## Purpose
Generate six-dimensional requirement review output.

## Input Schema
```json
{"type":"object","required":["requirement"],"properties":{"requirement":{"type":"string"}}}
```

## Output Schema
```json
{"type":"object","required":["scores","issues"],"properties":{"scores":{"type":"object"},"issues":{"type":"array"}}}
```

## Instructions
Return JSON only. Do not include markdown fences in the model output.

## Failure Output
{"error_code":"UNABLE_TO_REVIEW","message":"reason","recoverable":true}
```

规则：

- 主输出必须是 JSON。
- 不允许把自由散文作为主结果。
- 输出 schema 必须能被后端校验。
- Prompt 内容变化必须生成新 hash。
- 已发布版本不能覆盖。

## 4.1 Context Input Contract

RequirementReviewAgent and CaseGenerationAgent may receive local ContextArtifacts.

Prompt input must include:

```json
{
  "use_knowledge": false,
  "context_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
  "context_manifest": [
    {
      "artifact_id": "00000000-0000-0000-0000-000000000371",
      "title": "coupon-api-notes.md",
      "mime_type": "text/markdown",
      "sha256": "sha256:example",
      "redaction_applied": false
    }
  ]
}
```

Rules:

- `use_knowledge=false` means external RAG/KnowledgeAdapter is disabled.
- ContextArtifact content is still available to the prompt when `context_artifact_ids` is non-empty.
- Prompt input artifacts must save `context_manifest.json`.
- Model output or parsed AITask output must expose `used_context_artifact_ids`.
- Model output must not claim external evidence when `used_knowledge=false`.

## 4.2 Knowledge Evidence Input Contract

Future evidence-backed prompts may receive `KnowledgeEvidence` only after the
`TestKnowledgeCard` and `KnowledgeEvidence` contracts are defined.

Prompt input must separate raw task input, local context, and knowledge evidence:

```json
{
  "task_input": {},
  "context_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
  "knowledge_evidence": [
    {
      "evidence_id": "KE-001",
      "knowledge_card_id": "TKC-001",
      "source_artifact_id": "00000000-0000-0000-0000-000000000371",
      "source_card_version": 1,
      "retrieval_mode": "structured_filter",
      "snippet": "Expired coupons cannot be used during checkout.",
      "allowed_for_prompt": true
    }
  ],
  "forbidden_claims": [
    "Do not claim payment gateway behavior unless evidence cites it."
  ]
}
```

Rules:

- `knowledge_evidence` must contain only prompt-eligible evidence.
- Prompt output must list `used_knowledge_evidence_ids` when a generated result
  relies on knowledge evidence.
- Prompt output must list `unsupported_claims` when useful cases cannot be
  supported by available evidence.
- Missing evidence should produce lower confidence or coverage gap notes, not
  fabricated references.
- External provider metadata must stay in evidence artifacts and normalized
  fields; provider schemas must not leak into prompt output contracts.

## 5. Skill 文件格式

每个 Skill 文件必须包含以下段落：

```markdown
# Skill: test-case-generation-skill v1

## Applies To
- CaseGenerationAgent

## Methodology
- Equivalence partitioning
- Boundary value analysis
- State transition testing
- Error guessing

## Input Contract
Describe accepted input fields.

## Output Contract
Describe required output fields.

## Quality Gates
- Every case must have explicit expected result.
- Every case must reference requirement text.

## Forbidden Actions
- Do not create vague cases like "verify it works".
- Do not skip negative scenarios for P0/P1 flows.

## Tool Permissions
- KnowledgeAdapter.search_context optional.
```

## 6. V1 Prompt/Skill 映射

| 流程 | Agent | Prompt | Skill |
|---|---|---|---|
| 需求评审 | RequirementReviewAgent | requirement_review:v1 | requirement-review-skill:v1 |
| 风险矩阵 | RequirementReviewAgent | risk_matrix:v1 | requirement-review-skill:v1 |
| 用例生成 | CaseGenerationAgent | case_generation:v1 | test-case-generation-skill:v1 |
| 用例评审 | CaseReviewAgent | case_review:v1 | testcase-review-skill:v1 |
| 自动化草稿 | AutomationDraftAgent | automation_draft_generation:v1 | automation-draft-skill:v1 |
| CI/CD 变更分析 | CICDChangeAnalysisAgent | cicd_change_analysis:v1 | regression-selection-skill:v1 |
| 单测 patch | UnitTestAgent | unit_test_generation:v1 | unit-test-generation-skill:v1 |
| 回归选择 | RegressionAgent | regression_selection:v1 | regression-selection-skill:v1 |
| 工具执行计划 | ToolExecutionAgent | tool_execution:v1 | tool-execution-skill:v1 |
| 失败归因 | FailureAnalysisAgent | failure_analysis:v1 | failure-analysis-skill:v1 |
| 报告生成 | ReportAgent | report_generation:v1 | report-generation-skill:v1 |

## 6.1 Final Knowledge-Driven Prompt/Skill Mapping

This mapping is planning guidance. It becomes implementation truth only after
the related product and contract documents are promoted.

| 流程 | Agent | Prompt | Skill | Human gate |
|---|---|---|---|---|
| 知识卡片抽取 | KnowledgeIngestionAgent | knowledge_card_extraction:v1 | knowledge-ingestion-skill:v1 | prompt eligibility |
| 需求理解 | RequirementUnderstandingAgent | requirement_understanding:v1 | requirement-review-skill:v1 | requirement confirmation |
| 风险分析 | RiskAnalysisAgent | risk_analysis:v1 | risk-analysis-skill:v1 | review for P0/P1 |
| 覆盖分析 | CoverageAnalysisAgent | coverage_analysis:v1 | coverage-analysis-skill:v1 | coverage gap confirmation |
| 测试设计 | TestDesignAgent | test_design:v1 | test-design-skill:v1 | optional |
| 证据化用例生成 | CaseGenerationAgent | evidence_case_generation:v1 | test-case-generation-skill:v1 | case review |
| 证据化用例评审 | CaseReviewAgent | evidence_case_review:v1 | testcase-review-skill:v1 | case promotion |
| 用例去重 | DedupAgent | case_dedup:v1 | testcase-review-skill:v1 | duplicate merge |
| 自动化可行性 | AutomationReadinessAgent | automation_readiness:v1 | automation-draft-skill:v1 | automation draft approval |
| 知识反馈 | KnowledgeFeedbackAgent | knowledge_feedback:v1 | knowledge-feedback-skill:v1 | knowledge card review |

## 7. 输出 JSON 约束

### 7.1 用例生成输出

```json
{
  "cases": [
    {
      "title": "过期优惠券不可提交订单",
      "priority": "P0",
      "test_type": "functional",
      "precondition": "存在一张已过期优惠券",
      "steps": ["登录", "进入结算页", "选择过期优惠券", "提交订单"],
      "expected_results": ["系统阻止提交", "展示错误提示"],
      "input_data": {"coupon_status": "expired"},
      "requirement_refs": ["过期优惠券不可使用"],
      "risk_refs": ["RISK-001"],
      "ai_reason": "覆盖优惠券有效期边界"
    }
  ]
}
```

### 7.2 AutomationDraft 输出

```json
{
  "drafts": [
    {
      "target_framework": "pytest",
      "title": "test_expired_coupon_cannot_checkout",
      "suggested_file_path": "tests/test_coupon_checkout.py",
      "draft_language": "python",
      "draft_code": "def test_expired_coupon_cannot_checkout():\n    assert True",
      "execution_notes": ["需要替换为真实 fixture"],
      "risk_notes": ["草稿不能直接写入业务仓库"]
    }
  ]
}
```

### 7.3 UnitTestPatch 输出

```json
{
  "patch": "diff --git a/tests/test_coupon.py b/tests/test_coupon.py\n...",
  "target_framework": "pytest",
  "test_intent": "cover expired coupon rejection",
  "coverage_target": ["coupon validation branch"],
  "risk_notes": ["patch only modifies tests/"]
}
```

### 7.4 RegressionPlan 输出

```json
{
  "recommended_test_command_ids": ["00000000-0000-0000-0000-000000000302"],
  "reasons": ["Changed source branch is covered by pytest unit command."],
  "risk_coverage": ["src/coupon.py coupon.amount > order_total"],
  "needs_review": false
}
```

### 7.5 Report 输出

```json
{
  "conclusion": "passed",
  "summary": "Patch scope, new tests, and regression passed with evidence.",
  "metrics": {"new_tests_passed": true, "regression_passed": true},
  "evidence_artifact_ids": ["00000000-0000-0000-0000-000000001601"],
  "next_actions": []
}
```

### 7.6 Evidence-Backed Case Generation Output

```json
{
  "cases": [
    {
      "title": "过期优惠券不可提交订单",
      "priority": "P0",
      "test_type": "functional",
      "precondition": "存在一张已过期优惠券",
      "steps": ["登录", "进入结算页", "选择过期优惠券", "提交订单"],
      "expected_results": ["系统阻止提交", "展示错误提示"],
      "covered_requirement_ids": ["REQ-001"],
      "covered_risk_ids": ["RISK-001"],
      "source_knowledge_evidence_ids": ["KE-001"],
      "generation_reason": "覆盖优惠券有效期边界和结算阻断风险",
      "automation_readiness": {
        "suitable": true,
        "target_frameworks": ["pytest", "playwright"],
        "blockers": []
      },
      "quality_score": {
        "overall": 86,
        "requirement_coverage": 90,
        "risk_coverage": 85,
        "evidence_completeness": 90,
        "executability": 80,
        "hallucination_risk": 5
      },
      "review_findings": [],
      "coverage_gap_notes": []
    }
  ],
  "unsupported_claims": [],
  "used_knowledge_evidence_ids": ["KE-001"]
}
```

### 7.7 Knowledge Card Extraction Output

```json
{
  "knowledge_cards": [
    {
      "knowledge_type": "BoundaryCondition",
      "source_artifact_id": "00000000-0000-0000-0000-000000000371",
      "source_span": "section:coupon-validity",
      "source_quote_or_hash": "Expired coupons cannot be used during checkout.",
      "module_key": "checkout/coupon",
      "risk_type": "business",
      "case_type_hint": "negative",
      "confidence": 0.91,
      "safe_to_show": true,
      "allowed_for_prompt": true
    }
  ],
  "rejected_items": [],
  "unsupported_claims": []
}
```

## 8. 质量门禁

| 输出 | 门禁 |
|---|---|
| RequirementReview | 必须包含六维评分和至少一个测试设计建议 |
| GeneratedCaseCandidate | 必须有步骤、预期、需求引用、AI 理由 |
| AutomationDraft | 必须标明 target_framework、suggested_file_path、draft_code |
| UnitTestPatch | 必须通过 PatchScopeGate，不能修改业务源码 |
| RegressionPlan | 每个推荐命令必须有 reason |
| FailureAnalysis | 无证据时必须返回 insufficient_evidence |
| Report | 每个结论必须引用 artifact 或结构化指标 |
| TestKnowledgeCard | 必须引用 source artifact、source span 或 hash、review status、prompt eligibility |
| KnowledgeEvidence | 必须引用 knowledge card 或 source artifact，且标明 retrieval reason |
| Evidence-backed GeneratedCaseCandidate | 必须引用 evidence ids、覆盖风险、生成原因、review findings、coverage gap notes |

## 9. 版本与指标

每次 AI Task 必须记录：

- prompt_name。
- prompt_version。
- prompt_hash。
- skill_name。
- skill_version。
- skill_hash。
- model_provider。
- model_name。
- schema_valid。
- quality_gate_result。

指标按 PromptVersion 和 SkillVersion 聚合：采纳率、编辑率、驳回率、schema 通过率、执行通过率、失败率、平均 token、平均耗时。

Future knowledge-driven metrics also aggregate by PromptVersion and
SkillVersion:

- evidence precision。
- hallucination rate。
- duplicate rate。
- required-case coverage。
- boundary/exception coverage。
- historical-defect coverage。
- human acceptance rate。
- edit distance after review。
- automation readiness rate。

## 10. Prompt/Skill Promotion Rules

- New PromptVersion and SkillVersion records start as draft.
- Draft versions must pass schema examples and golden fixtures before active.
- Active versions must not be overwritten; changes create a new version/hash.
- Output-field changes require contract and fixture updates before prompt or
  skill activation.
- A new version may replace the active version only when it preserves schema
  validity and does not regress evidence precision, hallucination rate,
  duplicate rate, and human acceptance rate on the selected eval set.
- Rollback must keep old prompt and skill hashes addressable by historical
  AITask records.
- Prompt/Skill files must not contain secrets, credentials, private customer
  data, or unreviewed provider-specific instructions.

## 11. Skill Content Requirements

Every Skill must include:

```text
Applies To
Methodology
Input Contract
Output Contract
Quality Gates
Evidence Requirements
Forbidden Actions
Tool Permissions
Review Escalation
Failure Output
```

Knowledge-driven skills must also define:

- what evidence is sufficient for a recommendation;
- when to lower confidence;
- when to create coverage gap notes;
- when to reject an output as hallucinated or unverifiable;
- which fields require human review before reuse.
