from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from backend.app.modules.cases.grounding import (
    CaseGroundingInvalidError,
    build_requirement_claim_snapshot,
    validate_case_grounding,
)


@dataclass(frozen=True)
class GroundingCaseDiagnostic:
    case_name: str
    accepted: bool
    claim_ids: tuple[str, ...]
    status: str


@dataclass(frozen=True)
class GroundingVersionMetrics:
    version: str
    valid_citation_recall: float
    requirement_coverage: float
    accepted_cases: int
    total_cases: int
    missing_expected_claim_ids: tuple[str, ...]
    unexpected_claim_ids: tuple[str, ...]
    case_diagnostics: tuple[GroundingCaseDiagnostic, ...]


@dataclass(frozen=True)
class ClaimGroundingEvalResult:
    versions: tuple[GroundingVersionMetrics, ...]
    unsupported_case_rejection: float
    rejected_unsupported_cases: int
    total_unsupported_cases: int
    requirement_coverage_drift: dict[str, float]


def run_claim_grounding_eval(corpus: dict[str, Any]) -> ClaimGroundingEvalResult:
    _validate_corpus_shape(corpus)
    snapshot = build_requirement_claim_snapshot(**corpus["snapshot_input"])
    claims_by_key = _resolve_claim_keys(snapshot, corpus["claim_keys"])
    expected_citation_ids = {
        claims_by_key[key]["claim_id"] for key in corpus["expected_valid_citation_claim_keys"]
    }
    expected_requirement_ids = {
        claims_by_key[key]["claim_id"] for key in corpus["expected_requirement_claim_keys"]
    }

    version_metrics = tuple(
        sorted(
            (
                _evaluate_version(
                    run,
                    snapshot,
                    claims_by_key,
                    expected_citation_ids,
                    expected_requirement_ids,
                )
                for run in corpus["version_runs"]
            ),
            key=lambda item: item.version,
        ),
    )
    rejected = sum(
        _is_rejected(_hydrate_case(case_spec, claims_by_key), snapshot)
        for case_spec in corpus["unsupported_cases"]
    )
    unsupported_total = len(corpus["unsupported_cases"])
    metrics_by_version = {item.version: item for item in version_metrics}
    baseline = metrics_by_version[corpus["baseline_version"]].requirement_coverage
    drift = {
        item.version: round(item.requirement_coverage - baseline, 6)
        for item in version_metrics
    }
    return ClaimGroundingEvalResult(
        versions=version_metrics,
        unsupported_case_rejection=_ratio(rejected, unsupported_total),
        rejected_unsupported_cases=rejected,
        total_unsupported_cases=unsupported_total,
        requirement_coverage_drift=drift,
    )


def _evaluate_version(
    run: dict[str, Any],
    snapshot: dict[str, Any],
    claims_by_key: dict[str, dict[str, Any]],
    expected_citation_ids: set[str],
    expected_requirement_ids: set[str],
) -> GroundingVersionMetrics:
    accepted_claim_ids: set[str] = set()
    accepted_cases = 0
    diagnostics: list[GroundingCaseDiagnostic] = []
    for case_spec in run["cases"]:
        case = _hydrate_case(case_spec, claims_by_key)
        try:
            validate_case_grounding({"cases": [case]}, snapshot)
        except CaseGroundingInvalidError:
            diagnostics.append(
                GroundingCaseDiagnostic(
                    case_name=str(case_spec.get("name") or case.get("title") or "unnamed"),
                    accepted=False,
                    claim_ids=_declared_claim_ids(case),
                    status="grounding_invalid",
                ),
            )
            continue
        accepted_cases += 1
        claim_ids = tuple(case["grounding_assessment"]["claim_ids"])
        accepted_claim_ids.update(claim_ids)
        diagnostics.append(
            GroundingCaseDiagnostic(
                case_name=str(case_spec.get("name") or case.get("title") or "unnamed"),
                accepted=True,
                claim_ids=claim_ids,
                status="pass",
            ),
        )

    version = f'{run["prompt_version"]}|{run["skill_version"]}'
    return GroundingVersionMetrics(
        version=version,
        valid_citation_recall=_ratio(
            len(accepted_claim_ids & expected_citation_ids),
            len(expected_citation_ids),
        ),
        requirement_coverage=_ratio(
            len(accepted_claim_ids & expected_requirement_ids),
            len(expected_requirement_ids),
        ),
        accepted_cases=accepted_cases,
        total_cases=len(run["cases"]),
        missing_expected_claim_ids=tuple(sorted(expected_citation_ids - accepted_claim_ids)),
        unexpected_claim_ids=tuple(sorted(accepted_claim_ids - expected_citation_ids)),
        case_diagnostics=tuple(diagnostics),
    )


def _validate_corpus_shape(corpus: dict[str, Any]) -> None:
    version_runs = corpus.get("version_runs")
    unsupported_cases = corpus.get("unsupported_cases")
    expected_citations = corpus.get("expected_valid_citation_claim_keys")
    expected_requirements = corpus.get("expected_requirement_claim_keys")
    if not isinstance(version_runs, list) or not version_runs:
        raise ValueError("Eval corpus must contain version_runs")
    if not isinstance(unsupported_cases, list) or not unsupported_cases:
        raise ValueError("Eval corpus must contain unsupported_cases")
    if not isinstance(expected_citations, list) or not expected_citations:
        raise ValueError("Eval corpus must contain expected valid citation claims")
    if not isinstance(expected_requirements, list) or not expected_requirements:
        raise ValueError("Eval corpus must contain expected requirement claims")

    versions: list[str] = []
    for run in version_runs:
        if not isinstance(run.get("cases"), list) or not run["cases"]:
            raise ValueError("Every eval version must contain cases")
        versions.append(f'{run["prompt_version"]}|{run["skill_version"]}')
    if len(set(versions)) != len(versions):
        raise ValueError("Eval corpus versions must be unique")
    if corpus.get("baseline_version") not in versions:
        raise ValueError("Eval corpus baseline_version must identify a version run")


def _resolve_claim_keys(
    snapshot: dict[str, Any],
    claim_key_specs: dict[str, dict[str, str]],
) -> dict[str, dict[str, Any]]:
    resolved: dict[str, dict[str, Any]] = {}
    for key, spec in claim_key_specs.items():
        matches = [
            claim
            for claim in snapshot["claims"]
            if claim["source_type"] == spec["source_type"]
            and spec["text_contains"].casefold() in claim["text"].casefold()
        ]
        if len(matches) != 1:
            raise ValueError(f"Claim key {key!r} resolved to {len(matches)} claims")
        resolved[key] = matches[0]
    return resolved


def _hydrate_case(
    case_spec: dict[str, Any],
    claims_by_key: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    case = copy.deepcopy(case_spec["case"])
    citations = []
    for citation_spec in case_spec.get("citations", []):
        claim = claims_by_key.get(citation_spec.get("claim_key", ""))
        claim_id = citation_spec.get("claim_id") or (claim and claim["claim_id"])
        evidence = citation_spec.get("evidence") or (claim and claim["text"])
        citations.append({"claim_id": claim_id, "evidence": evidence})
    if citations:
        case["coverage_claims"] = citations
    return case


def _is_rejected(case: dict[str, Any], snapshot: dict[str, Any]) -> bool:
    try:
        validate_case_grounding({"cases": [case]}, snapshot)
    except CaseGroundingInvalidError:
        return True
    return False


def _declared_claim_ids(case: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        str(citation.get("claim_id") or "")
        for citation in case.get("coverage_claims", [])
        if isinstance(citation, dict)
    )


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        raise ValueError("Eval corpus metric denominator must not be zero")
    return round(numerator / denominator, 6)
