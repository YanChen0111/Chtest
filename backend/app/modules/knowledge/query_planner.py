from __future__ import annotations

import re


_TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}|[\u4e00-\u9fff]{2,}")
_RISK_TERMS = {
    "异常", "失败", "超时", "重试", "回滚", "恢复", "中断", "断网", "权限", "兼容", "边界", "并发",
    "error", "fail", "timeout", "retry", "rollback", "recovery", "offline", "permission", "boundary",
}
_DOMAIN_EXPANSIONS = {
    "ota": ("升级", "固件", "下载", "版本"),
    "upgrade": ("ota", "firmware", "download", "version"),
    "充电": ("充电桩", "充电开始", "充电结束", "枪"),
    "coupon": ("优惠券", "折扣", "结算"),
    "优惠券": ("coupon", "折扣", "结算"),
    "网络": ("wifi", "4g", "mqtt", "重连"),
    "network": ("wifi", "4g", "mqtt", "reconnect"),
}


def build_retrieval_query_plan(text: str) -> dict[str, list[str] | str]:
    """Build bounded, deterministic query variants for requirement retrieval."""
    normalized = " ".join(text.split())
    tokens = list(dict.fromkeys(_TOKEN_PATTERN.findall(normalized.lower())))
    risk_terms = list(dict.fromkeys([term for term in _RISK_TERMS if term in normalized.lower()]))
    domain_terms: list[str] = []
    for token, expansions in _DOMAIN_EXPANSIONS.items():
        if token in normalized.lower():
            domain_terms.extend(expansions)
    domain_terms = list(dict.fromkeys(domain_terms))
    exact = normalized[:500]
    variants = [exact]
    if domain_terms:
        variants.append(" ".join([*tokens[:12], *domain_terms[:12]]))
    if risk_terms:
        variants.append(" ".join([*tokens[:12], *risk_terms]))
    return {
        "strategy": "deterministic_query_planner_v1",
        "exact_query": exact,
        "tokens": tokens[:30],
        "domain_terms": domain_terms[:20],
        "risk_terms": risk_terms[:20],
        "variants": list(dict.fromkeys(variants))[:3],
    }


def expanded_retrieval_query(plan: dict[str, list[str] | str]) -> str:
    variants = plan.get("variants", [])
    if not isinstance(variants, list):
        return str(plan.get("exact_query", ""))
    return " ".join(str(item) for item in variants if item)[:1200]
