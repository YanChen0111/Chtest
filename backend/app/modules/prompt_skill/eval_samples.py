from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvalSample:
    fixture_name: str
    prompt_name: str
    model_name: str
    task_type: str
    fixture_content: str
    input_json: dict


def load_default_eval_samples(root: Path) -> list[EvalSample]:
    fixture_root = root / "docs/fixtures/eval-bench"
    return [
        _sample(
            fixture_root,
            fixture_name="requirements",
            prompt_name="requirement_review",
            model_name="mock-requirement-review",
            task_type="requirement_review",
            input_key="requirement",
        ),
        _sample(
            fixture_root,
            fixture_name="code-changes",
            prompt_name="cicd_change_analysis",
            model_name="mock-cicd-analysis",
            task_type="cicd_change_analysis",
            input_key="diff_summary",
        ),
        _sample(
            fixture_root,
            fixture_name="failed-runs",
            prompt_name="failure_analysis",
            model_name="mock-failure-analysis",
            task_type="failure_analysis",
            input_key="failure_summary",
        ),
        _sample(
            fixture_root,
            fixture_name="bug-history",
            prompt_name="report_generation",
            model_name="mock-report-generator",
            task_type="report_generation",
            input_key="evidence_summary",
        ),
    ]


def _sample(
    fixture_root: Path,
    *,
    fixture_name: str,
    prompt_name: str,
    model_name: str,
    task_type: str,
    input_key: str,
) -> EvalSample:
    fixture_content = (fixture_root / f"{fixture_name}.md").read_text(encoding="utf-8")
    return EvalSample(
        fixture_name=fixture_name,
        prompt_name=prompt_name,
        model_name=model_name,
        task_type=task_type,
        fixture_content=fixture_content,
        input_json={
            input_key: fixture_content,
            "use_knowledge": False,
            "context_artifact_ids": [],
            "context_manifest": [],
        },
    )
