from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


QUALITY_AGENT_VERSION = "deterministic-case-quality-v1"
REQUIRED_COVERAGE_DIMENSIONS = ("positive", "negative", "boundary", "state", "permission", "risk")


@dataclass(frozen=True)
class QualityFinding:
    code: str
    severity: str
    message: str
    evidence: tuple[str, ...] = ()


def evaluate_case_quality(case: dict[str, Any]) -> dict[str, Any]:
    findings: list[QualityFinding] = []
    evidence = tuple(
        str(item.get("knowledge_evidence_id") or item.get("evidence_id"))
        for item in case.get("source_knowledge_evidence", [])
        if isinstance(item, dict) and (item.get("knowledge_evidence_id") or item.get("evidence_id"))
    )
    if not evidence:
        findings.append(QualityFinding("missing_evidence", "warning", "Candidate has no persisted knowledge evidence."))
    if not case.get("expected_results"):
        findings.append(QualityFinding("missing_expected_result", "error", "Candidate has no verifiable expected result."))
    if not case.get("steps"):
        findings.append(QualityFinding("missing_steps", "error", "Candidate has no executable test steps."))
    if not str(case.get("generation_reason") or case.get("ai_reason") or "").strip():
        findings.append(QualityFinding("missing_generation_reason", "warning", "Candidate does not explain why it exists."))
    return {
        "agent": "CaseReviewAgent",
        "version": QUALITY_AGENT_VERSION,
        "status": "needs_review" if findings else "pass",
        "finding_count": len(findings),
        "findings": [asdict(item) for item in findings],
        "evidence_ids": list(evidence),
    }


def evaluate_coverage_gaps(case: dict[str, Any]) -> dict[str, Any]:
    covered = sorted(
        {
            str(item.get("key") or item.get("dimension") or "").strip().lower()
            for item in case.get("coverage_dimensions", [])
            if isinstance(item, dict)
        }
        & set(REQUIRED_COVERAGE_DIMENSIONS),
    )
    missing = [item for item in REQUIRED_COVERAGE_DIMENSIONS if item not in covered]
    return {
        "agent": "CoverageGapAgent",
        "version": QUALITY_AGENT_VERSION,
        "status": "gap" if missing else "covered",
        "covered_dimensions": covered,
        "missing_dimensions": missing,
        "finding_count": len(missing),
    }


def evaluate_automation_readiness(case: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if not case.get("steps"):
        blockers.append("missing_steps")
    if not case.get("expected_results"):
        blockers.append("missing_expected_results")
    test_type = str(case.get("test_type") or "functional")
    framework = "playwright" if test_type == "ui" else "pytest"
    return {
        "framework": framework,
        "status": "blocked" if blockers else "ready_for_review",
        "blockers": blockers,
        "required_fixtures": [],
        "confidence": 0.9 if not blockers else 0.3,
    }


def evaluate_case_quality_bundle(case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    review = evaluate_case_quality(case)
    gaps = evaluate_coverage_gaps(case)
    review["coverage_gap"] = gaps
    return review, evaluate_automation_readiness(case)
