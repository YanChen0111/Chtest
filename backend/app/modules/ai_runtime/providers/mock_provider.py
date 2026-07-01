from __future__ import annotations

import json

from backend.app.modules.ai_runtime.providers.base import (
    LLMProviderError,
    LLMProviderRequest,
    LLMProviderResponse,
    LLMProviderTimeoutError,
    ProviderArtifactPayload,
)


class MockLLMProvider:
    provider = "mock"
    default_model = "mock-model"
    network_required = False
    deterministic = True
    supported_models = {
        "mock-requirement-review",
        "mock-case-generator",
        "mock-automation-draft",
        "mock-cicd-analysis",
        "mock-unit-test-generator",
        "mock-failure-analysis",
        "mock-report-generator",
    }

    def generate(self, request: LLMProviderRequest) -> LLMProviderResponse:
        if request.model_name not in self.supported_models:
            raise LLMProviderError(f"unsupported mock model: {request.model_name}")

        if request.mode == "provider_error":
            raise LLMProviderError("forced provider error")
        if request.mode == "timeout":
            raise LLMProviderTimeoutError("forced timeout")
        if request.mode == "schema_invalid":
            return self._schema_invalid_response(request)

        output_json = self._success_output(request)
        return LLMProviderResponse(
            provider=self.provider,
            model_name=request.model_name,
            status="succeeded",
            output_json=output_json,
            artifacts=self._success_artifacts(request, output_json),
            token_usage_json={
                "prompt_tokens": 128,
                "completion_tokens": 256,
                "total_tokens": 384,
            },
        )

    def _success_output(self, request: LLMProviderRequest) -> dict:
        context_ids = [str(context_id) for context_id in request.context_artifact_ids]
        knowledge_retrieval = request.input_json.get("knowledge_retrieval")
        used_knowledge = bool(
            isinstance(knowledge_retrieval, dict)
            and knowledge_retrieval.get("used_knowledge")
            and knowledge_retrieval.get("results"),
        )
        if request.model_name == "mock-requirement-review":
            return {
                "overall_score": 82,
                "scores": {
                    "completeness": 78,
                    "clarity": 85,
                    "consistency": 88,
                    "testability": 84,
                    "feasibility": 82,
                    "logic": 75,
                },
                "issues": [
                    {
                        "type": "missing_boundary",
                        "severity": "medium",
                        "text": "未说明优惠券金额等于订单应付金额时是否允许支付金额为 0",
                    },
                    {
                        "type": "missing_rule",
                        "severity": "medium",
                        "text": "未说明优惠券最低消费门槛和适用商品范围",
                    },
                ],
                "clarification_questions": [
                    "优惠券是否可以与平台活动叠加？",
                    "优惠券金额等于订单应付金额时是否允许提交？",
                ],
                "risk_items": [
                    {
                        "title": "优惠券与积分互斥规则",
                        "risk_level": "high",
                        "suggestion": "覆盖同时选择优惠券和积分时的提交阻断",
                    },
                    {
                        "title": "优惠券金额超过应付金额",
                        "risk_level": "high",
                        "suggestion": "覆盖优惠券金额大于订单金额时的金额计算和错误提示",
                    },
                ],
                "used_knowledge": used_knowledge,
                "used_context_artifact_ids": context_ids,
            }

        if request.model_name == "mock-case-generator":
            return {
                "cases": [
                    {
                        "title": "可用优惠券可成功抵扣订单金额",
                        "priority": "P0",
                        "test_type": "functional",
                        "precondition": "用户存在一张未过期且满足使用条件的优惠券",
                        "steps": ["登录用户账号", "创建包含可用商品的订单", "进入结算页", "选择可用优惠券", "提交订单"],
                        "expected_results": ["订单提交成功", "最终支付金额等于订单应付金额减优惠券金额"],
                        "requirement_refs": ["用户在提交订单时，可以选择一张可用优惠券"],
                        "ai_reason": "覆盖优惠券主流程",
                    },
                    {
                        "title": "优惠券不可与积分同时使用",
                        "priority": "P0",
                        "test_type": "functional",
                        "precondition": "用户同时拥有可用优惠券和可用积分",
                        "steps": ["进入结算页", "选择优惠券", "选择积分抵扣", "提交订单"],
                        "expected_results": ["系统阻止同时使用", "页面提示优惠券不可与积分同时使用"],
                        "requirement_refs": ["优惠券不可与积分同时使用"],
                        "ai_reason": "覆盖互斥规则",
                    },
                    {
                        "title": "过期优惠券不可用于结算",
                        "priority": "P0",
                        "test_type": "functional",
                        "precondition": "用户存在一张已过期优惠券",
                        "steps": ["进入结算页", "查看优惠券列表", "尝试选择已过期优惠券", "提交订单"],
                        "expected_results": ["已过期优惠券不可选或提交失败", "页面提示优惠券已过期"],
                        "requirement_refs": ["过期优惠券不可使用"],
                        "ai_reason": "覆盖有效期边界",
                    },
                    {
                        "title": "优惠券金额不能超过订单应付金额",
                        "priority": "P1",
                        "test_type": "functional",
                        "precondition": "订单应付金额小于优惠券金额",
                        "steps": ["进入结算页", "选择金额大于订单应付金额的优惠券", "提交订单"],
                        "expected_results": ["系统按规则阻断或限制抵扣", "最终支付金额不会为负数"],
                        "requirement_refs": ["优惠券金额不能超过订单应付金额"],
                        "ai_reason": "覆盖金额边界",
                    },
                    {
                        "title": "提交订单后展示优惠后的最终支付金额",
                        "priority": "P1",
                        "test_type": "ui",
                        "precondition": "用户选择一张可用优惠券",
                        "steps": ["进入结算页", "选择优惠券", "提交订单", "查看订单确认页"],
                        "expected_results": ["订单确认页展示优惠后的最终支付金额", "金额与结算页一致"],
                        "requirement_refs": ["系统需要展示优惠后的最终支付金额"],
                        "ai_reason": "覆盖 UI 展示一致性",
                    },
                ],
                "used_knowledge": False,
                "used_context_artifact_ids": context_ids,
            }

        if request.model_name == "mock-automation-draft":
            return self._with_context(
                {
                    "target_framework": "pytest",
                    "draft_code": "def test_coupon_amount_cannot_exceed_order_total():\n    assert True\n",
                    "review_notes": ["Generated by deterministic mock provider."],
                },
                context_ids,
            )

        if request.model_name == "mock-cicd-analysis":
            return self._with_context(
                {
                    "summary": "优惠券应用逻辑新增金额超过订单总额时的阻断分支。",
                    "overall_risk": "medium",
                    "impacted_modules": ["coupon", "checkout"],
                    "changed_files": [
                        {
                            "path": "src/coupon.py",
                            "file_role": "source",
                            "risk_level": "medium",
                            "risk_reasons": ["新增业务分支", "需要补充分支覆盖"],
                        },
                    ],
                    "test_recommendations": [
                        {
                            "type": "unit",
                            "target": "tests/test_coupon.py",
                            "reason": "新增 coupon.amount > order_total 分支需要单测覆盖",
                        },
                    ],
                },
                context_ids,
            )

        if request.model_name == "mock-unit-test-generator":
            return self._with_context(
                {
                    "target_framework": "pytest",
                    "test_intent": "覆盖优惠券金额大于订单总额的新分支",
                    "coverage_target": ["src/coupon.py apply_coupon coupon.amount > order_total"],
                    "risk_notes": ["patch 只修改 tests/test_coupon.py"],
                    "patch": (
                        "diff --git a/tests/test_coupon.py b/tests/test_coupon.py\n"
                        "--- a/tests/test_coupon.py\n"
                        "+++ b/tests/test_coupon.py\n"
                        "@@\n"
                        "+def test_coupon_amount_cannot_exceed_order_total():\n"
                        "+    assert True\n"
                    ),
                },
                context_ids,
            )

        if request.model_name == "mock-failure-analysis":
            return self._with_context(
                {
                    "classification": "product_defect",
                    "confidence": 0.86,
                    "evidence": ["pytest failure indicates coupon amount branch regression"],
                    "recommended_action": "Review coupon amount validation and add focused regression test.",
                },
                context_ids,
            )

        if request.model_name == "mock-report-generator":
            return self._with_context(
                {
                    "report_json": {
                        "conclusion": "needs_attention",
                        "summary": "Mock report generated from deterministic evidence.",
                    },
                    "report_markdown": "# Mock Quality Report\n\nConclusion: needs_attention\n",
                },
                context_ids,
            )

        raise LLMProviderError(f"unsupported mock model: {request.model_name}")

    def _schema_invalid_response(self, request: LLMProviderRequest) -> LLMProviderResponse:
        output_json = {"invalid": True}
        error_json = {
            "error_code": "MOCK_SCHEMA_INVALID",
            "message": "forced schema-invalid mock output",
            "recoverable": True,
        }
        return LLMProviderResponse(
            provider=self.provider,
            model_name=request.model_name,
            status="schema_invalid",
            output_json=output_json,
            artifacts=[
                self._json_artifact("raw_llm_output", "raw_output.json", output_json),
                self._json_artifact("schema_validation", "schema_validation.json", error_json),
            ],
            error_json=error_json,
            token_usage_json={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        )

    def _success_artifacts(
        self,
        request: LLMProviderRequest,
        output_json: dict,
    ) -> list[ProviderArtifactPayload]:
        artifacts = [
            self._json_artifact("input_json", "input.json", request.input_json),
            self._json_artifact("raw_llm_output", "raw_output.json", output_json),
            self._json_artifact("parsed_output", "parsed_output.json", output_json),
            self._json_artifact("schema_validation", "schema_validation.json", {"schema_valid": True}),
        ]
        if request.context_artifact_ids:
            artifacts.append(
                self._json_artifact(
                    "input_json",
                    "context_manifest.json",
                    {
                        "context_artifact_ids": [str(context_id) for context_id in request.context_artifact_ids],
                        "context_manifest": request.context_manifest,
                    },
                ),
            )
        return artifacts

    def _with_context(self, output_json: dict, context_ids: list[str]) -> dict:
        return {
            **output_json,
            "used_knowledge": False,
            "used_context_artifact_ids": context_ids,
        }

    def _json_artifact(self, artifact_type: str, file_name: str, payload: dict) -> ProviderArtifactPayload:
        content = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return ProviderArtifactPayload(
            artifact_type=artifact_type,
            file_name=file_name,
            mime_type="application/json",
            content=content,
        )
