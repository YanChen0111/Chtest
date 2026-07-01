from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from backend.app.tests.golden.test_requirement_to_case import (
    ASGIClient,
    api_client,
    candidate_by_title,
    seed_prompt_skill,
)


def test_golden_requirement_to_case_metrics_match_review_plan(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)

    project_response = client.post("/api/projects", json_body={"name": "Checkout System"})
    assert project_response.status_code == 201
    project = project_response.json()
    module_response = client.post(
        f"/api/projects/{project['id']}/modules",
        json_body={"name": "订单结算", "sort_order": 10},
    )
    assert module_response.status_code == 201
    module = module_response.json()

    requirement_response = client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "module_id": module["id"],
            "title": "优惠券结算规则",
            "content": (
                "# 优惠券结算规则\n\n"
                "用户在提交订单时，可以选择一张可用优惠券。优惠券不可与积分同时使用。"
                "过期优惠券不可使用。优惠券金额不能超过订单应付金额。"
                "提交订单后，系统需要展示优惠后的最终支付金额。"
            ),
            "source_type": "manual",
            "source_ref": "REQ-COUPON-001",
        },
    )
    assert requirement_response.status_code == 201
    requirement = requirement_response.json()

    review_start = client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={
            "prompt_version": "requirement_review:v1",
            "skill_version": "requirement-review-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-requirement-review",
            "use_knowledge": False,
            "context_artifact_ids": [],
        },
    )
    assert review_start.status_code == 202
    review_response = client.get(f"/api/requirements/{requirement['id']}/review")
    assert review_response.status_code == 200
    review = review_response.json()

    generation_response = client.post(
        "/api/case-generation/tasks",
        json_body={
            "project_id": project["id"],
            "requirement_id": requirement["id"],
            "requirement_review_id": review["id"],
            "target_test_types": ["functional", "ui"],
            "prompt_version": "case_generation:v1",
            "skill_version": "test-case-generation-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-case-generator",
            "use_knowledge": False,
            "context_artifact_ids": [],
        },
    )
    assert generation_response.status_code == 202
    generation = generation_response.json()

    candidates_response = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates")
    assert candidates_response.status_code == 200
    candidates = candidates_response.json()["items"]

    for title, payload in golden_review_plan().items():
        candidate = candidate_by_title(candidates, title)
        response = client.post(f"/api/case-review/items/{candidate['id']}/approve", json_body=payload)
        assert response.status_code == 200

    metrics_response = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/metrics")
    assert metrics_response.status_code == 200
    metrics = metrics_response.json()

    assert metrics["generated_count"] >= 5
    assert metrics["approved_count"] == 3
    assert metrics["edited_count"] == 1
    assert metrics["optimization_count"] == 1
    assert metrics["review_progress"] >= 1.0
    assert metrics["acceptance_rate"] == 0.8


def golden_review_plan() -> dict[str, dict[str, Any]]:
    return {
        "可用优惠券可成功抵扣订单金额": {"action": "approve", "review_comment": "主流程完整"},
        "优惠券不可与积分同时使用": {"action": "approve", "review_comment": "高风险互斥规则"},
        "过期优惠券不可用于结算": {
            "action": "approve_after_edit",
            "review_comment": "补充测试数据准备",
            "edited_case": {
                "title": "过期优惠券不可用于结算",
                "priority": "P0",
                "test_type": "functional",
                "precondition": "用户存在一张已过期优惠券，并已准备包含可用商品的订单",
                "steps": ["准备已过期优惠券", "进入结算页", "查看优惠券列表", "尝试选择已过期优惠券", "提交订单"],
                "expected_results": ["已过期优惠券不可选或提交失败", "页面提示优惠券已过期"],
                "input_data": {"coupon_state": "expired"},
                "tags": ["coupon", "boundary"],
            },
        },
        "优惠券金额不能超过订单应付金额": {
            "action": "needs_optimization",
            "review_comment": "需求未明确阻断或限制抵扣策略",
        },
        "提交订单后展示优惠后的最终支付金额": {"action": "approve", "review_comment": "UI 展示可测"},
    }
