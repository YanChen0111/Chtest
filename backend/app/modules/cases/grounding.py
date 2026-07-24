from __future__ import annotations

import hashlib
import json
import re
from typing import Any

GROUNDING_CONTRACT_VERSION = "requirement-claims-v1"


class CaseGroundingInvalidError(Exception):
    pass


def build_requirement_claim_snapshot(
    *,
    requirement_id: str,
    requirement_title: str,
    requirement_content: str,
    requirement_document: dict[str, Any] | None,
    risk_items: list[dict[str, Any]],
    knowledge_evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    claims: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add_claim(source_type: str, source_ref: str, text: str) -> None:
        normalized = _normalize_text(text)
        key = (source_type, normalized.casefold())
        if len(normalized) < 4 or key in seen:
            return
        seen.add(key)
        digest = hashlib.sha256(f"{source_type}\n{source_ref}\n{normalized}".encode()).hexdigest()[:16]
        claims.append(
            {
                "claim_id": f"CLM-{digest}",
                "source_type": source_type,
                "source_ref": source_ref,
                "text": normalized,
            },
        )

    requirement_ref = f"requirement:{requirement_id}"
    for text in _claim_sentences(f"{requirement_title}\n{requirement_content}"):
        add_claim("requirement", requirement_ref, text)

    if requirement_document:
        artifact_id = str(requirement_document.get("artifact_id") or "")
        for text in _claim_sentences(str(requirement_document.get("content") or ""))[:80]:
            add_claim("requirement_document", f"artifact:{artifact_id}", text)

    for risk in risk_items:
        risk_id = str(risk.get("id") or "")
        text = ". ".join(
            str(risk.get(key) or "").strip()
            for key in ("title", "impact", "suggestion")
            if str(risk.get(key) or "").strip()
        )
        add_claim("risk", f"risk:{risk_id}", text)

    for evidence in knowledge_evidence:
        evidence_id = str(evidence.get("knowledge_evidence_id") or evidence.get("evidence_id") or "")
        text = ". ".join(
            str(evidence.get(key) or "").strip()
            for key in ("title", "snippet")
            if str(evidence.get(key) or "").strip()
        )
        if evidence_id:
            add_claim("knowledge_evidence", f"knowledge_evidence:{evidence_id}", text)

    payload: dict[str, Any] = {
        "version": GROUNDING_CONTRACT_VERSION,
        "requirement_id": requirement_id,
        "claims": claims,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["snapshot_hash"] = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def validate_case_grounding(output: dict[str, Any], snapshot: dict[str, Any]) -> None:
    if snapshot.get("version") != GROUNDING_CONTRACT_VERSION:
        raise CaseGroundingInvalidError
    claims = snapshot.get("claims")
    if not isinstance(claims, list) or not claims:
        raise CaseGroundingInvalidError
    claims_by_id = {
        str(claim.get("claim_id")): claim
        for claim in claims
        if isinstance(claim, dict) and claim.get("claim_id") and claim.get("text")
    }
    if len(claims_by_id) != len(claims):
        raise CaseGroundingInvalidError

    for case in output.get("cases", []):
        coverage_claims = case.get("coverage_claims")
        if not isinstance(coverage_claims, list) or not coverage_claims:
            raise CaseGroundingInvalidError
        case_text = _case_text(case)
        cited_ids: list[str] = []
        cited_source_types: set[str] = set()
        for citation in coverage_claims:
            if not isinstance(citation, dict):
                raise CaseGroundingInvalidError
            claim_id = str(citation.get("claim_id") or "")
            evidence = str(citation.get("evidence") or "").strip()
            claim = claims_by_id.get(claim_id)
            if claim is None or not evidence:
                raise CaseGroundingInvalidError
            claim_text = str(claim["text"])
            if not _has_semantic_overlap(claim_text, evidence) or not _has_semantic_overlap(claim_text, case_text):
                raise CaseGroundingInvalidError
            _validate_source_link(case, claim)
            cited_ids.append(claim_id)
            cited_source_types.add(str(claim.get("source_type") or ""))
        if not cited_source_types.intersection({"requirement", "requirement_document", "risk"}):
            raise CaseGroundingInvalidError
        case["covered_requirement_ids"] = list(dict.fromkeys(cited_ids))
        case["grounding_assessment"] = {
            "status": "pass",
            "contract_version": GROUNDING_CONTRACT_VERSION,
            "snapshot_hash": snapshot.get("snapshot_hash"),
            "claim_ids": list(dict.fromkeys(cited_ids)),
        }


def _validate_source_link(case: dict[str, Any], claim: dict[str, Any]) -> None:
    source_type = str(claim.get("source_type") or "")
    source_ref = str(claim.get("source_ref") or "")
    source_id = source_ref.partition(":")[2]
    if source_type == "risk" and source_id not in {str(item) for item in case.get("risk_refs", [])}:
        raise CaseGroundingInvalidError
    if source_type == "knowledge_evidence":
        evidence_ids = {
            str(item.get("knowledge_evidence_id") or item.get("evidence_id") or "")
            for item in case.get("source_knowledge_evidence", [])
            if isinstance(item, dict)
        }
        if source_id not in evidence_ids:
            raise CaseGroundingInvalidError


def _claim_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)
    parts = re.split(r"(?:\r?\n)+|(?<=[。！？!?;；])\s*|(?<=[.])\s+(?=[A-Z0-9])", cleaned)
    return [_normalize_text(part) for part in parts if len(_normalize_text(part)) >= 4]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip(" \t\r\n-*#")


def _case_text(case: dict[str, Any]) -> str:
    return " ".join(
        [
            str(case.get("title") or ""),
            str(case.get("precondition") or ""),
            *(str(item) for item in case.get("steps", [])),
            *(str(item) for item in case.get("expected_results", [])),
            str(case.get("ai_reason") or ""),
        ],
    )


def _has_semantic_overlap(source: str, target: str) -> bool:
    source_terms = _semantic_terms(source)
    return bool(source_terms.intersection(_semantic_terms(target)))


def _semantic_terms(text: str) -> set[str]:
    normalized = text.casefold()
    terms = set(re.findall(r"[a-z0-9][a-z0-9_-]{2,}", normalized))
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", normalized):
        terms.update(chunk[index : index + 2] for index in range(len(chunk) - 1))
    return terms
