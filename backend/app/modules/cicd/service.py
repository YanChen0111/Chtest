from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.cicd.models import CICDChangedFile, CICDRun, UnitTestPatch
from backend.app.modules.cicd.schemas import CICDRunAnalyzeRequest, CICDRunCreateRequest, UnitTestPatchGenerateRequest
from backend.app.modules.projects.models import Project, Repository


class ProjectNotFoundError(Exception):
    pass


class RepositoryInvalidError(Exception):
    pass


class CICDRunNotFoundError(Exception):
    pass


class CICDRunInvalidInputError(Exception):
    pass


class UnitTestPatchNotFoundError(Exception):
    pass


class UnitTestPatchInvalidStatusError(Exception):
    pass


class PatchScopeRejectedError(Exception):
    pass


@dataclass
class ParsedChangedFile:
    path: str
    old_path: str | None
    change_type: str
    language: str | None
    file_role: str
    risk_level: str
    risk_reasons: list[str] = field(default_factory=list)
    lines_added: int = 0
    lines_deleted: int = 0

    def to_manifest_item(self) -> dict:
        return {
            "path": self.path,
            "old_path": self.old_path,
            "change_type": self.change_type,
            "language": self.language,
            "file_role": self.file_role,
            "risk_level": self.risk_level,
            "risk_reasons": self.risk_reasons,
            "lines_added": self.lines_added,
            "lines_deleted": self.lines_deleted,
        }


@dataclass
class PatchScopeGateResult:
    allowed: bool
    checked_paths: list[str]
    blocked_paths: list[str]
    forbidden_patterns: list[str]
    risk_level: str
    reason: str | None = None

    def to_artifact_metadata(self) -> dict:
        body = {
            "allowed": self.allowed,
            "checked_paths": self.checked_paths,
            "blocked_paths": self.blocked_paths,
            "forbidden_patterns": self.forbidden_patterns,
            "risk_level": self.risk_level,
        }
        if self.reason is not None:
            body["reason"] = self.reason
        return body


def parse_local_diff(diff_text: str) -> list[ParsedChangedFile]:
    changed_files: list[ParsedChangedFile] = []
    current: dict | None = None

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            if current is not None:
                changed_files.append(build_changed_file(current))
            current = start_file_block(line)
            continue
        if current is None:
            continue
        if line.startswith("new file mode"):
            current["change_type"] = "added"
            continue
        if line.startswith("deleted file mode"):
            current["change_type"] = "deleted"
            continue
        if line.startswith("rename from "):
            current["old_path"] = line.removeprefix("rename from ").strip()
            current["change_type"] = "renamed"
            continue
        if line.startswith("rename to "):
            current["path"] = line.removeprefix("rename to ").strip()
            current["change_type"] = "renamed"
            continue
        if line.startswith("+++") and not line.startswith("++++"):
            new_path = normalize_diff_path(line.removeprefix("+++ ").strip())
            if new_path is not None:
                current["path"] = new_path
            continue
        if line.startswith("---") and not line.startswith("----"):
            old_path = normalize_diff_path(line.removeprefix("--- ").strip())
            if old_path is not None and current.get("change_type") == "deleted":
                current["path"] = old_path
            continue
        if line.startswith("+") and not line.startswith("+++"):
            current["lines_added"] += 1
            continue
        if line.startswith("-") and not line.startswith("---"):
            current["lines_deleted"] += 1

    if current is not None:
        changed_files.append(build_changed_file(current))
    return changed_files


def evaluate_patch_scope(patch_text: str) -> PatchScopeGateResult:
    checked_paths = parse_patch_target_paths(patch_text)
    blocked_paths: list[str] = []
    forbidden_patterns: list[str] = []

    for path in checked_paths:
        is_allowed, reason = classify_patch_scope_path(path)
        if not is_allowed:
            blocked_paths.append(path)
            forbidden_patterns.append(reason)

    allowed = not blocked_paths and bool(checked_paths)
    return PatchScopeGateResult(
        allowed=allowed,
        checked_paths=checked_paths,
        blocked_paths=blocked_paths,
        forbidden_patterns=forbidden_patterns,
        risk_level="low" if allowed else "high",
        reason=None if allowed else "PATCH_SCOPE_REJECTED",
    )


def parse_patch_target_paths(patch_text: str) -> list[str]:
    paths: list[str] = []
    current_path: str | None = None
    for line in patch_text.splitlines():
        if line.startswith("diff --git "):
            current_path = None
            parts = line.split()
            if len(parts) > 3:
                current_path = normalize_diff_path(parts[3])
            continue
        if line.startswith("rename to "):
            current_path = line.removeprefix("rename to ").strip()
            continue
        if line.startswith("+++") and not line.startswith("++++"):
            new_path = normalize_diff_path(line.removeprefix("+++ ").strip())
            if new_path is not None:
                current_path = new_path
            continue
        if line.startswith("---") and not line.startswith("----") and current_path is None:
            old_path = normalize_diff_path(line.removeprefix("--- ").strip())
            if old_path is not None:
                current_path = old_path
            continue
        if current_path is not None and line.startswith("@@"):
            if current_path not in paths:
                paths.append(current_path)
    return paths


def classify_patch_scope_path(path: str) -> tuple[bool, str]:
    if is_generated_artifact_path(path):
        return False, f"generated artifact path modified: {path}"
    if is_test_path(path):
        return True, ""
    file_role = classify_file_role(path)
    if file_role in {"source", "config", "migration", "build"}:
        scope_role = "config" if file_role == "build" else file_role
        return False, f"{scope_role} path modified: {path}"
    return False, f"unknown non-test path modified: {path}"


def is_test_path(path: str) -> bool:
    pure_path = PurePosixPath(path)
    parts = set(pure_path.parts)
    name = pure_path.name.lower()
    suffixes = "".join(pure_path.suffixes).lower()
    return (
        "tests" in parts
        or "test" in parts
        or "__tests__" in parts
        or name.startswith("test_")
        or name.endswith("_test.py")
        or ".test." in name
        or ".spec." in name
        or suffixes.endswith(".test.ts")
        or suffixes.endswith(".test.tsx")
        or suffixes.endswith(".spec.ts")
        or suffixes.endswith(".spec.tsx")
    )


def is_generated_artifact_path(path: str) -> bool:
    pure_path = PurePosixPath(path)
    parts = set(pure_path.parts)
    generated_parts = {"dist", "build", "coverage", ".next", ".nuxt", "node_modules", "__pycache__"}
    return bool(parts.intersection(generated_parts))


def start_file_block(line: str) -> dict:
    parts = line.split()
    old_path = normalize_diff_path(parts[2]) if len(parts) > 2 else None
    path = normalize_diff_path(parts[3]) if len(parts) > 3 else old_path
    return {
        "path": path or "unknown",
        "old_path": old_path if old_path != path else None,
        "change_type": "modified",
        "lines_added": 0,
        "lines_deleted": 0,
    }


def build_changed_file(block: dict) -> ParsedChangedFile:
    path = block["path"]
    old_path = block.get("old_path")
    change_type = block["change_type"]
    lines_added = block["lines_added"]
    lines_deleted = block["lines_deleted"]
    file_role = classify_file_role(path, old_path)
    language = detect_language(path)
    risk_level, risk_reasons = classify_risk(file_role, change_type, lines_added, lines_deleted, path)
    return ParsedChangedFile(
        path=path,
        old_path=old_path,
        change_type=change_type,
        language=language,
        file_role=file_role,
        risk_level=risk_level,
        risk_reasons=risk_reasons,
        lines_added=lines_added,
        lines_deleted=lines_deleted,
    )


def normalize_diff_path(path: str) -> str | None:
    if path == "/dev/null":
        return None
    if path.startswith("a/") or path.startswith("b/"):
        return path[2:]
    return path


def classify_file_role(path: str, old_path: str | None = None) -> str:
    pure_path = PurePosixPath(path)
    old_name = PurePosixPath(old_path).name.lower() if old_path else ""
    parts = set(pure_path.parts)
    name = pure_path.name.lower()
    suffix = pure_path.suffix.lower()
    if "tests" in parts or "test" in parts or name.startswith("test_") or name.endswith(".spec.ts"):
        return "test"
    if "docs" in parts or suffix in {".md", ".mdx", ".rst"}:
        return "docs"
    if "migrations" in parts or "migration" in parts:
        return "migration"
    if "fixtures" in parts or "fixture" in parts:
        return "fixture"
    build_names = {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "pyproject.toml", "poetry.lock"}
    if name in build_names or old_name in build_names:
        return "build"
    if suffix in {".yml", ".yaml", ".toml", ".ini", ".cfg", ".json"}:
        return "config"
    if suffix in {".py", ".ts", ".tsx", ".js", ".jsx", ".vue", ".go", ".java"}:
        return "source"
    return "unknown"


def detect_language(path: str) -> str | None:
    suffix = PurePosixPath(path).suffix.lower()
    return {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".vue": "vue",
        ".go": "go",
        ".java": "java",
        ".md": "markdown",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
    }.get(suffix)


def classify_risk(
    file_role: str,
    change_type: str,
    lines_added: int,
    lines_deleted: int,
    path: str,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    total_changed = lines_added + lines_deleted
    if file_role == "source":
        reasons.append("source file changed")
    elif file_role == "test":
        reasons.append("test file changed")
    elif file_role == "docs":
        reasons.append("documentation changed")
    elif file_role in {"config", "build", "migration"}:
        reasons.append(f"{file_role} file changed")
    else:
        reasons.append("unknown file role")

    if change_type == "deleted":
        reasons.append("file deleted")
    if change_type == "renamed":
        reasons.append("file renamed")
    if total_changed >= 80:
        reasons.append("large change")

    if file_role in {"migration", "config"} or total_changed >= 80:
        return "high", reasons
    if file_role in {"source", "build"} or (change_type in {"deleted", "renamed"} and file_role not in {"docs", "test"}):
        return "medium", reasons
    return "low", reasons


def create_cicd_run(session: Session, data: CICDRunCreateRequest) -> CICDRun:
    project = session.get(Project, data.project_id)
    if project is None:
        raise ProjectNotFoundError
    if data.repository_id is not None:
        repository = session.get(Repository, data.repository_id)
        if repository is None or repository.project_id != project.id:
            raise RepositoryInvalidError
    if data.source_type not in {"local_diff", "manual_check"}:
        raise CICDRunInvalidInputError
    if data.trigger_type != "manual" or data.provider != "local":
        raise CICDRunInvalidInputError

    cicd_run = CICDRun(
        project_id=project.id,
        repository_id=data.repository_id,
        source_type=data.source_type,
        trigger_type="manual",
        provider="local",
        pipeline_name=data.pipeline_name,
        base_ref=data.base_ref,
        head_ref=data.head_ref,
        status="created",
    )
    session.add(cicd_run)
    session.flush()

    if data.diff_text:
        parsed_files = parse_local_diff(data.diff_text)
        for parsed in parsed_files:
            session.add(
                CICDChangedFile(
                    cicd_run_id=cicd_run.id,
                    path=parsed.path,
                    old_path=parsed.old_path,
                    change_type=parsed.change_type,
                    language=parsed.language,
                    file_role=parsed.file_role,
                    risk_level=parsed.risk_level,
                    risk_reasons_json=parsed.risk_reasons,
                    lines_added=parsed.lines_added,
                    lines_deleted=parsed.lines_deleted,
                ),
            )
        create_cicd_run_artifacts(session, cicd_run, data.diff_text, parsed_files)
    session.commit()
    session.refresh(cicd_run)
    return cicd_run


def list_cicd_runs(session: Session) -> list[CICDRun]:
    return list(session.scalars(select(CICDRun).order_by(CICDRun.created_at.desc())))


def get_cicd_run(session: Session, cicd_run_id: uuid.UUID) -> CICDRun:
    cicd_run = session.get(CICDRun, cicd_run_id)
    if cicd_run is None:
        raise CICDRunNotFoundError
    return cicd_run


def create_cicd_run_artifacts(
    session: Session,
    cicd_run: CICDRun,
    diff_text: str,
    parsed_files: list[ParsedChangedFile],
) -> list[Artifact]:
    manifest = {"changed_files": [item.to_manifest_item() for item in parsed_files]}
    specs = [
        (
            "diff_patch",
            "diff.patch",
            "text/x-diff",
            len(diff_text.encode("utf-8")),
            {"source_type": cicd_run.source_type},
        ),
        (
            "changed_files",
            "changed_files.json",
            "application/json",
            0,
            {"changed_file_count": len(parsed_files), "manifest_json": manifest},
        ),
    ]
    artifacts: list[Artifact] = []
    for artifact_type, filename, mime_type, size_bytes, metadata in specs:
        artifact = Artifact(
            project_id=cicd_run.project_id,
            owner_entity_type="CICDRun",
            owner_entity_id=cicd_run.id,
            artifact_type=artifact_type,
            file_path=f"artifacts/projects/{cicd_run.project_id}/cicd-quality/{cicd_run.id}/{filename}",
            mime_type=mime_type,
            size_bytes=size_bytes,
            sha256=f"sha256:{artifact_type}:{cicd_run.id}",
            metadata_json=metadata,
        )
        session.add(artifact)
        artifacts.append(artifact)
    session.flush()
    return artifacts


def analyze_cicd_run(session: Session, cicd_run_id: uuid.UUID, data: CICDRunAnalyzeRequest) -> tuple[CICDRun, AITask, Artifact]:
    cicd_run = get_cicd_run(session, cicd_run_id)
    changed_files = list(cicd_run.changed_files)
    overall_risk = max_risk(changed_files)
    output = {
        "overall_risk": overall_risk,
        "changed_file_count": len(changed_files),
        "risk_reasons": sorted({reason for item in changed_files for reason in item.risk_reasons_json}),
        "recommended_actions": ["Review changed files before UnitTestPatch generation."],
    }
    ai_task = AITask(
        project_id=cicd_run.project_id,
        agent_name="CICDChangeAnalysisAgent",
        task_type="cicd_change_analysis",
        prompt_version_id=stable_version_uuid(data.prompt_version),
        skill_version_id=stable_version_uuid(data.skill_version),
        model_provider=data.model_provider,
        model_name=data.model_name,
        status="succeeded",
        input_json={
            "cicd_run_id": str(cicd_run.id),
            "changed_file_ids": [str(item.id) for item in changed_files],
        },
        output_json=output,
    )
    session.add(ai_task)
    session.flush()
    artifact = Artifact(
        project_id=cicd_run.project_id,
        owner_entity_type="CICDRun",
        owner_entity_id=cicd_run.id,
        artifact_type="risk_analysis",
        file_path=f"artifacts/projects/{cicd_run.project_id}/cicd-quality/{cicd_run.id}/risk_analysis.json",
        mime_type="application/json",
        size_bytes=0,
        sha256=f"sha256:risk_analysis:{cicd_run.id}",
        metadata_json={
            "model_provider": data.model_provider,
            "model_name": data.model_name,
            "prompt_version": data.prompt_version,
            "skill_version": data.skill_version,
            "overall_risk": overall_risk,
            "changed_file_count": len(changed_files),
            "analysis_json": output,
        },
    )
    session.add(artifact)
    cicd_run.overall_risk = overall_risk
    cicd_run.status = "analyzed"
    session.add(cicd_run)
    session.commit()
    session.refresh(cicd_run)
    return cicd_run, ai_task, artifact


def generate_unit_test_patch(
    session: Session,
    cicd_run_id: uuid.UUID,
    data: UnitTestPatchGenerateRequest,
) -> UnitTestPatch:
    cicd_run = get_cicd_run(session, cicd_run_id)
    patch_text = data.patch_text or default_unit_test_patch(cicd_run)
    scope_gate_result = evaluate_patch_scope(patch_text)
    status = "scope_validated" if scope_gate_result.allowed else "scope_rejected"
    ai_task = AITask(
        project_id=cicd_run.project_id,
        agent_name="UnitTestAgent",
        task_type="unit_test_patch",
        prompt_version_id=stable_version_uuid(data.prompt_version),
        skill_version_id=stable_version_uuid(data.skill_version),
        model_provider=data.model_provider,
        model_name=data.model_name,
        status="succeeded",
        input_json={
            "cicd_run_id": str(cicd_run.id),
            "target_framework": data.target_framework,
            "coverage_target": data.coverage_target,
        },
        output_json={
            "patch_text": patch_text,
            "scope_gate_result": scope_gate_result.to_artifact_metadata(),
            "test_intent": data.test_intent,
        },
    )
    session.add(ai_task)
    session.flush()
    patch = UnitTestPatch(
        cicd_run_id=cicd_run.id,
        ai_task_id=ai_task.id,
        patch_text=patch_text,
        target_framework=data.target_framework,
        scope_gate_result_json=scope_gate_result.to_artifact_metadata(),
        test_intent=data.test_intent,
        coverage_target_json=data.coverage_target,
        status=status,
    )
    session.add(patch)
    session.commit()
    session.refresh(patch)
    return patch


def approve_unit_test_patch(session: Session, unit_test_patch_id: uuid.UUID, review_comment: str | None) -> UnitTestPatch:
    patch = get_unit_test_patch(session, unit_test_patch_id)
    if patch.status not in {"scope_validated", "awaiting_review"}:
        raise UnitTestPatchInvalidStatusError
    if not patch.scope_gate_result_json.get("allowed", False):
        raise UnitTestPatchInvalidStatusError
    patch.status = "approved"
    patch.review_comment = review_comment
    session.add(patch)
    session.commit()
    session.refresh(patch)
    return patch


def reject_unit_test_patch(session: Session, unit_test_patch_id: uuid.UUID, review_comment: str | None) -> UnitTestPatch:
    patch = get_unit_test_patch(session, unit_test_patch_id)
    if patch.status not in {"generated", "scope_validated", "scope_rejected", "awaiting_review"}:
        raise UnitTestPatchInvalidStatusError
    patch.status = "rejected"
    patch.review_comment = review_comment
    session.add(patch)
    session.commit()
    session.refresh(patch)
    return patch


def apply_unit_test_patch(session: Session, unit_test_patch_id: uuid.UUID) -> tuple[UnitTestPatch, Artifact]:
    patch = get_unit_test_patch(session, unit_test_patch_id)
    if patch.status != "approved":
        raise UnitTestPatchInvalidStatusError
    scope_gate_result = evaluate_patch_scope(patch.patch_text)
    if not scope_gate_result.allowed:
        patch.status = "apply_failed"
        patch.scope_gate_result_json = scope_gate_result.to_artifact_metadata()
        session.add(patch)
        session.commit()
        raise PatchScopeRejectedError

    patch.scope_gate_result_json = scope_gate_result.to_artifact_metadata()
    patch.status = "applied"
    artifact = Artifact(
        project_id=patch.cicd_run.project_id,
        owner_entity_type="UnitTestPatch",
        owner_entity_id=patch.id,
        artifact_type="unit_test_patch",
        file_path=f"artifacts/projects/{patch.cicd_run.project_id}/cicd-quality/{patch.cicd_run_id}/unit-test-patches/{patch.id}/unit_test.patch",
        mime_type="text/x-diff",
        size_bytes=len(patch.patch_text.encode("utf-8")),
        sha256=f"sha256:unit_test_patch:{patch.id}",
        metadata_json={
            "scope_gate_result": scope_gate_result.to_artifact_metadata(),
            "patch_text": patch.patch_text,
            "target_framework": patch.target_framework,
        },
    )
    session.add(patch)
    session.add(artifact)
    session.commit()
    session.refresh(patch)
    session.refresh(artifact)
    return patch, artifact


def get_unit_test_patch(session: Session, unit_test_patch_id: uuid.UUID) -> UnitTestPatch:
    patch = session.get(UnitTestPatch, unit_test_patch_id)
    if patch is None:
        raise UnitTestPatchNotFoundError
    return patch


def default_unit_test_patch(cicd_run: CICDRun) -> str:
    return "\n".join(
        [
            "diff --git a/tests/test_cicd_generated.py b/tests/test_cicd_generated.py",
            "new file mode 100644",
            "--- /dev/null",
            "+++ b/tests/test_cicd_generated.py",
            "@@ -0,0 +1,2 @@",
            "+def test_generated_unit_patch_placeholder():",
            f"+    assert {str(cicd_run.id)!r}",
            "",
        ],
    )


def analysis_artifacts_for_run(session: Session, cicd_run: CICDRun) -> list[Artifact]:
    return list(
        session.scalars(
            select(Artifact)
            .where(
                Artifact.owner_entity_type == "CICDRun",
                Artifact.owner_entity_id == cicd_run.id,
                Artifact.artifact_type == "risk_analysis",
            )
            .order_by(Artifact.created_at.asc()),
        ),
    )


def max_risk(changed_files: list[CICDChangedFile]) -> str:
    order = {"low": 1, "medium": 2, "high": 3}
    if not changed_files:
        return "medium"
    return max((item.risk_level for item in changed_files), key=lambda value: order.get(value, 2))


def stable_version_uuid(version: str) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_URL, f"chtest:{version}")
