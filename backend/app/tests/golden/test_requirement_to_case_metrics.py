from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from backend.app.tests.golden.test_requirement_to_case import (
    ASGIClient,
    api_client,
    candidate_by_title,
    golden_review_plan,
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
                "decision_table_acknowledged": True,
                "use_knowledge": False,
            "context_artifact_ids": [],
        },
    )
    assert generation_response.status_code == 202
    generation = generation_response.json()

    candidates_response = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates")
    assert candidates_response.status_code == 200
    candidates = candidates_response.json()["items"]

    for title, payload in golden_review_plan(candidates).items():
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
