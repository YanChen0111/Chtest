from backend.app.modules.knowledge.query_planner import build_retrieval_query_plan, expanded_retrieval_query


def test_query_planner_adds_domain_and_risk_variants_without_changing_original() -> None:
    plan = build_retrieval_query_plan("OTA 下载失败后网络重连是否支持重试")

    assert plan["strategy"] == "deterministic_query_planner_v1"
    assert plan["exact_query"] == "OTA 下载失败后网络重连是否支持重试"
    assert "下载" in plan["domain_terms"]
    assert "失败" in plan["risk_terms"]
    assert len(plan["variants"]) >= 2
    assert "OTA 下载失败后网络重连是否支持重试" in expanded_retrieval_query(plan)
