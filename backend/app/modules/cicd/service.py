from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.cicd.models import CICDChangedFile, CICDRun, QualityGateDecision, UnitTestPatch
from backend.app.modules.cicd.schemas import (
    CICDImportArtifactReference,
    CICDImportChangedFile,
    CICDRegressionRunRequest,
    CICDRegressionSelectRequest,
    CICDQualityReportRequest,
    CICDRunMetadataImportRequest,
    CICDRunAnalyzeRequest,
    CICDRunCreateRequest,
    CICDRunNewTestsRequest,
    QualityGateComputeRequest,
    UnitTestPatchGenerateRequest,
)
from backend.app.modules.execution.models import TestRun
from backend.app.modules.projects.models import Project, Repository, TestCommand
from backend.app.modules.reporting.models import Report
from backend.app.modules.review_history.service import append_review_history


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


class TestCommandInvalidError(Exception):
    pass


class RegressionPlanInvalidError(Exception):
    pass


class QualityGateDecisionMissingError(Exception):
    pass


class CIImportError(Exception):
    error_code = "INVALID_CI_IMPORT_PAYLOAD"

    def __init__(self, message: str = "") -> None:
        super().__init__(message or self.error_code)


class CIImportInvalidPayloadError(CIImportError):
    error_code = "INVALID_CI_IMPORT_PAYLOAD"


class CIImportControlFieldRejectedError(CIImportError):
    error_code = "CI_IMPORT_CONTROL_FIELD_REJECTED"


class CIImportCredentialRejectedError(CIImportError):
    error_code = "CI_IMPORT_CREDENTIAL_REJECTED"


class CIImportUnsupportedProviderOperationError(CIImportError):
    error_code = "CI_IMPORT_UNSUPPORTED_PROVIDER_OPERATION"


class CIImportExternalFetchForbiddenError(CIImportError):
    error_code = "CI_IMPORT_EXTERNAL_FETCH_FORBIDDEN"


class CIImportDuplicateExternalRunError(CIImportError):
    error_code = "CI_IMPORT_DUPLICATE_EXTERNAL_RUN"


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
class ParsedCIArtifactReference:
    name: str
    kind: str
    external_url: str | None = None
    sha256: str | None = None
    size_bytes: int | None = None

    def to_manifest_item(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind,
            "external_url": self.external_url,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "inert_reference": True,
        }


@dataclass
class ParsedCIRunMetadataImport:
    source_type: str
    provider: str
    trigger_type: str
    external_run_id: str
    pipeline_name: str
    job_name: str | None
    conclusion: str
    status: str | None
    base_ref: str | None
    head_ref: str | None
    commit_sha: str | None
    started_at: str | None
    finished_at: str | None
    duration_ms: int | None
    external_url: str | None
    changed_files: list[ParsedChangedFile] = field(default_factory=list)
    artifact_references: list[ParsedCIArtifactReference] = field(default_factory=list)
    import_mode: str = "static_json"

    def to_artifact_metadata(self) -> dict:
        return {
            "created_by_component": "CICDRunMetadataImport",
            "source_type": self.source_type,
            "provider": self.provider,
            "provider_is_inert_label": True,
            "import_mode": self.import_mode,
            "changed_file_count": len(self.changed_files),
            "artifact_reference_count": len(self.artifact_references),
            "remote_fetch_performed": False,
            "quality_gate_auto_decision": False,
        }

    def to_artifact_content(self) -> dict:
        return {
            "source_type": self.source_type,
            "provider": self.provider,
            "provider_is_inert_label": True,
            "trigger_type": self.trigger_type,
            "external_run_id": self.external_run_id,
            "pipeline_name": self.pipeline_name,
            "job_name": self.job_name,
            "conclusion": self.conclusion,
            "status": self.status,
            "base_ref": self.base_ref,
            "head_ref": self.head_ref,
            "commit_sha": self.commit_sha,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_ms": self.duration_ms,
            "external_url": self.external_url,
            "import_mode": self.import_mode,
            "changed_files": [item.to_manifest_item() for item in self.changed_files],
            "artifact_references": [item.to_manifest_item() for item in self.artifact_references],
            "remote_fetch_performed": False,
            "quality_gate_auto_decision": False,
        }


CI_IMPORT_ALLOWED_PROVIDERS = {
    "imported",
    "github_actions",
    "gitlab_ci",
    "jenkins",
    "circleci",
    "buildkite",
    "other",
}
CI_IMPORT_ALLOWED_CONCLUSIONS = {"success", "failure", "cancelled", "skipped", "timed_out", "unknown"}
CI_IMPORT_ALLOWED_CHANGE_TYPES = {"added", "modified", "deleted", "renamed"}
CI_IMPORT_CONTROL_FIELDS = {
    "webhook",
    "event_action",
    "signature",
    "delivery_id",
    "callback_url",
    "trigger",
    "rerun",
    "cancel",
    "schedule",
    "workflow_dispatch",
    "pr_comment",
    "commit_status_update",
    "branch_protection",
    "merge",
    "deploy",
    "release",
    "tag",
    "publish",
    "environment_promotion",
}
CI_IMPORT_CREDENTIAL_FIELDS = {
    "token",
    "secret",
    "oauth",
    "oauth_token",
    "pat",
    "private_key",
    "password",
    "credential_id",
    "organization_permissions",
}
CI_IMPORT_EXTERNAL_FETCH_FIELDS = {
    "fetch_artifacts",
    "download_artifacts",
    "download_url",
    "fetch_logs",
    "fetch_external_urls",
}


def parse_ci_run_metadata_import(payload: dict | CICDRunMetadataImportRequest) -> ParsedCIRunMetadataImport:
    raw_payload = payload.model_dump(mode="python") if isinstance(payload, CICDRunMetadataImportRequest) else payload
    if not isinstance(raw_payload, dict):
        raise CIImportInvalidPayloadError("CI import payload must be an object")

    reject_forbidden_ci_import_fields(raw_payload)
    request = coerce_ci_import_request(raw_payload)
    validate_ci_import_request(request)
    changed_files = [normalize_ci_import_changed_file(item) for item in request.changed_files]
    artifact_references = [normalize_ci_import_artifact_reference(item) for item in request.artifact_references]

    return ParsedCIRunMetadataImport(
        source_type=request.source_type,
        provider=request.provider,
        trigger_type=request.trigger_type,
        external_run_id=request.external_run_id,
        pipeline_name=request.pipeline_name,
        job_name=request.job_name,
        conclusion=request.conclusion,
        status=request.status,
        base_ref=request.base_ref,
        head_ref=request.head_ref,
        commit_sha=request.commit_sha,
        started_at=request.started_at,
        finished_at=request.finished_at,
        duration_ms=request.duration_ms if request.duration_ms is not None else request.duration,
        external_url=request.external_url,
        changed_files=changed_files,
        artifact_references=artifact_references,
    )


def reject_forbidden_ci_import_fields(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized_key = key.lower()
            if normalized_key == "provider_operation":
                raise CIImportUnsupportedProviderOperationError
            if normalized_key in CI_IMPORT_CONTROL_FIELDS:
                raise CIImportControlFieldRejectedError
            if normalized_key in CI_IMPORT_EXTERNAL_FETCH_FIELDS:
                raise CIImportExternalFetchForbiddenError
            if normalized_key in CI_IMPORT_CREDENTIAL_FIELDS or any(
                marker in normalized_key for marker in ("token", "secret", "password", "private_key")
            ):
                raise CIImportCredentialRejectedError
            reject_forbidden_ci_import_fields(item)
    elif isinstance(value, list):
        for item in value:
            reject_forbidden_ci_import_fields(item)


def coerce_ci_import_request(payload: dict) -> CICDRunMetadataImportRequest:
    try:
        return CICDRunMetadataImportRequest(**payload)
    except Exception as exc:
        raise CIImportInvalidPayloadError(str(exc)) from exc


def validate_ci_import_request(request: CICDRunMetadataImportRequest) -> None:
    if request.source_type != "ci_import":
        raise CIImportInvalidPayloadError("source_type must be ci_import")
    if request.trigger_type != "imported":
        raise CIImportInvalidPayloadError("trigger_type must be imported")
    if request.provider not in CI_IMPORT_ALLOWED_PROVIDERS:
        raise CIImportInvalidPayloadError("unsupported provider label")
    if request.conclusion not in CI_IMPORT_ALLOWED_CONCLUSIONS:
        raise CIImportInvalidPayloadError("unsupported conclusion")
    if not request.external_run_id.strip() or not request.pipeline_name.strip():
        raise CIImportInvalidPayloadError("external_run_id and pipeline_name are required")
    if not request.changed_files:
        raise CIImportInvalidPayloadError("changed_files must not be empty")
    if request.duration_ms is not None and request.duration_ms < 0:
        raise CIImportInvalidPayloadError("duration_ms must not be negative")
    if request.duration is not None and request.duration < 0:
        raise CIImportInvalidPayloadError("duration must not be negative")


def normalize_ci_import_changed_file(item: CICDImportChangedFile) -> ParsedChangedFile:
    path = item.path.strip()
    old_path = item.old_path.strip() if item.old_path else None
    if not path or path.startswith("/") or ".." in PurePosixPath(path).parts:
        raise CIImportInvalidPayloadError("changed file path is invalid")
    if old_path is not None and (old_path.startswith("/") or ".." in PurePosixPath(old_path).parts):
        raise CIImportInvalidPayloadError("changed file old_path is invalid")
    if item.change_type not in CI_IMPORT_ALLOWED_CHANGE_TYPES:
        raise CIImportInvalidPayloadError("changed file change_type is invalid")
    if item.lines_added < 0 or item.lines_deleted < 0:
        raise CIImportInvalidPayloadError("changed file line counts must not be negative")

    file_role = classify_file_role(path, old_path)
    language = detect_language(path)
    risk_level, risk_reasons = classify_risk(file_role, item.change_type, item.lines_added, item.lines_deleted, path)
    return ParsedChangedFile(
        path=path,
        old_path=old_path,
        change_type=item.change_type,
        language=language,
        file_role=file_role,
        risk_level=risk_level,
        risk_reasons=risk_reasons,
        lines_added=item.lines_added,
        lines_deleted=item.lines_deleted,
    )


def normalize_ci_import_artifact_reference(item: CICDImportArtifactReference) -> ParsedCIArtifactReference:
    name = item.name.strip()
    kind = item.kind.strip()
    external_url = item.external_url.strip() if item.external_url else None
    if not name or not kind:
        raise CIImportInvalidPayloadError("artifact reference name and kind are required")
    if item.size_bytes is not None and item.size_bytes < 0:
        raise CIImportInvalidPayloadError("artifact reference size_bytes must not be negative")
    return ParsedCIArtifactReference(
        name=name,
        kind=kind,
        external_url=external_url,
        sha256=item.sha256,
        size_bytes=item.size_bytes,
    )


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


def import_ci_run_metadata(session: Session, data: CICDRunMetadataImportRequest) -> tuple[CICDRun, ParsedCIRunMetadataImport, list[Artifact]]:
    if data.project_id is None:
        raise CIImportInvalidPayloadError("project_id is required")
    project = session.get(Project, data.project_id)
    if project is None:
        raise ProjectNotFoundError
    if data.repository_id is not None:
        repository = session.get(Repository, data.repository_id)
        if repository is None or repository.project_id != project.id:
            raise RepositoryInvalidError

    parsed = parse_ci_run_metadata_import(data)
    if ci_import_duplicate_exists(session, data.project_id, data.repository_id, parsed.provider, parsed.external_run_id):
        raise CIImportDuplicateExternalRunError

    cicd_run = CICDRun(
        project_id=project.id,
        repository_id=data.repository_id,
        source_type="ci_import",
        trigger_type="imported",
        provider=parsed.provider,
        pipeline_name=parsed.pipeline_name,
        base_ref=parsed.base_ref,
        head_ref=parsed.head_ref,
        quality_gate_status="pending",
        status="imported",
    )
    session.add(cicd_run)
    session.flush()

    for parsed_file in parsed.changed_files:
        session.add(
            CICDChangedFile(
                cicd_run_id=cicd_run.id,
                path=parsed_file.path,
                old_path=parsed_file.old_path,
                change_type=parsed_file.change_type,
                language=parsed_file.language,
                file_role=parsed_file.file_role,
                risk_level=parsed_file.risk_level,
                risk_reasons_json=parsed_file.risk_reasons,
                lines_added=parsed_file.lines_added,
                lines_deleted=parsed_file.lines_deleted,
            ),
        )

    artifacts = create_ci_import_artifacts(session, cicd_run, parsed)
    session.commit()
    session.refresh(cicd_run)
    for artifact in artifacts:
        session.refresh(artifact)
    return cicd_run, parsed, artifacts


def ci_import_duplicate_exists(
    session: Session,
    project_id: uuid.UUID,
    repository_id: uuid.UUID | None,
    provider: str,
    external_run_id: str,
) -> bool:
    artifacts = session.scalars(
        select(Artifact).where(
            Artifact.project_id == project_id,
            Artifact.owner_entity_type == "CICDRun",
            Artifact.artifact_type == "ci_run_metadata",
        ),
    )
    repository_key = str(repository_id) if repository_id is not None else None
    for artifact in artifacts:
        metadata = artifact.metadata_json
        if (
            metadata.get("repository_id") == repository_key
            and metadata.get("provider") == provider
            and metadata.get("external_run_id") == external_run_id
        ):
            return True
    return False


def create_ci_import_artifacts(
    session: Session,
    cicd_run: CICDRun,
    parsed: ParsedCIRunMetadataImport,
) -> list[Artifact]:
    content = parsed.to_artifact_content()
    metadata = parsed.to_artifact_metadata()
    metadata.update(
        {
            "repository_id": str(cicd_run.repository_id) if cicd_run.repository_id is not None else None,
            "external_run_id": parsed.external_run_id,
            "ci_conclusion": parsed.conclusion,
            "content_json": content,
        },
    )
    changed_files_manifest = {"changed_files": [item.to_manifest_item() for item in parsed.changed_files]}
    specs = [
        (
            "ci_run_metadata",
            "ci_run_metadata.json",
            metadata,
        ),
        (
            "changed_files",
            "changed_files.json",
            {
                "changed_file_count": len(parsed.changed_files),
                "manifest_json": changed_files_manifest,
            },
        ),
    ]
    artifacts: list[Artifact] = []
    for artifact_type, filename, artifact_metadata in specs:
        artifact = Artifact(
            project_id=cicd_run.project_id,
            owner_entity_type="CICDRun",
            owner_entity_id=cicd_run.id,
            artifact_type=artifact_type,
            file_path=f"artifacts/projects/{cicd_run.project_id}/cicd-quality/{cicd_run.id}/{filename}",
            mime_type="application/json",
            size_bytes=0,
            sha256=f"sha256:{artifact_type}:{cicd_run.id}",
            metadata_json=artifact_metadata,
        )
        session.add(artifact)
        artifacts.append(artifact)
    session.flush()
    return artifacts


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
    from_status = patch.status
    patch.status = "approved"
    patch.review_comment = review_comment
    session.add(patch)
    append_review_history(
        session,
        project_id=patch.cicd_run.project_id,
        entity_type="UnitTestPatch",
        entity_id=patch.id,
        related_entity_type="CICDRun",
        related_entity_id=patch.cicd_run_id,
        action="approve",
        from_status=from_status,
        to_status=patch.status,
        comment=review_comment,
    )
    session.commit()
    session.refresh(patch)
    return patch


def reject_unit_test_patch(session: Session, unit_test_patch_id: uuid.UUID, review_comment: str | None) -> UnitTestPatch:
    patch = get_unit_test_patch(session, unit_test_patch_id)
    if patch.status not in {"generated", "scope_validated", "scope_rejected", "awaiting_review"}:
        raise UnitTestPatchInvalidStatusError
    from_status = patch.status
    patch.status = "rejected"
    patch.review_comment = review_comment
    session.add(patch)
    append_review_history(
        session,
        project_id=patch.cicd_run.project_id,
        entity_type="UnitTestPatch",
        entity_id=patch.id,
        related_entity_type="CICDRun",
        related_entity_id=patch.cicd_run_id,
        action="reject",
        from_status=from_status,
        to_status=patch.status,
        comment=review_comment,
    )
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


def run_new_tests(session: Session, cicd_run_id: uuid.UUID, data: CICDRunNewTestsRequest) -> TestRun:
    cicd_run = get_cicd_run(session, cicd_run_id)
    if data.unit_test_patch_id is not None:
        patch = get_unit_test_patch(session, data.unit_test_patch_id)
        if patch.cicd_run_id != cicd_run.id or patch.status != "applied":
            raise UnitTestPatchInvalidStatusError
    command = get_active_test_command(session, cicd_run.project_id, data.test_command_id)
    test_run = create_cicd_test_run(
        session,
        cicd_run,
        command,
        name=f"CI/CD new tests: {command.name}",
        parsed_result={
            "run_type": "new_tests",
            "unit_test_patch_id": str(data.unit_test_patch_id) if data.unit_test_patch_id else None,
        },
    )
    session.commit()
    session.refresh(test_run)
    return test_run


def select_regression(session: Session, cicd_run_id: uuid.UUID, data: CICDRegressionSelectRequest) -> tuple[Artifact, list[uuid.UUID], list[str]]:
    cicd_run = get_cicd_run(session, cicd_run_id)
    commands = [get_active_test_command(session, cicd_run.project_id, command_id) for command_id in data.candidate_test_command_ids]
    recommended_ids = [command.id for command in commands]
    reasons = ["Selected active pytest regression command." for _command in commands]
    artifact = Artifact(
        project_id=cicd_run.project_id,
        owner_entity_type="CICDRun",
        owner_entity_id=cicd_run.id,
        artifact_type="regression_plan",
        file_path=f"artifacts/projects/{cicd_run.project_id}/cicd-quality/{cicd_run.id}/regression_plan.json",
        mime_type="application/json",
        size_bytes=0,
        sha256=f"sha256:regression_plan:{cicd_run.id}:{len(recommended_ids)}",
        metadata_json={
            "skill_version": data.skill_version,
            "recommended_test_command_ids": [str(command_id) for command_id in recommended_ids],
            "reasons": reasons,
        },
    )
    session.add(artifact)
    session.commit()
    session.refresh(artifact)
    return artifact, recommended_ids, reasons


def run_regression(session: Session, cicd_run_id: uuid.UUID, data: CICDRegressionRunRequest) -> list[TestRun]:
    cicd_run = get_cicd_run(session, cicd_run_id)
    artifact = session.get(Artifact, data.regression_plan_artifact_id)
    if artifact is None or artifact.owner_entity_type != "CICDRun" or artifact.owner_entity_id != cicd_run.id or artifact.artifact_type != "regression_plan":
        raise RegressionPlanInvalidError
    test_runs: list[TestRun] = []
    for command_id in data.test_command_ids:
        command = get_active_test_command(session, cicd_run.project_id, command_id)
        test_runs.append(
            create_cicd_test_run(
                session,
                cicd_run,
                command,
                name=f"CI/CD regression: {command.name}",
                parsed_result={
                    "run_type": "regression",
                    "regression_plan_artifact_id": str(data.regression_plan_artifact_id),
                },
            ),
        )
    session.commit()
    for test_run in test_runs:
        session.refresh(test_run)
    return test_runs


def compute_quality_gate(session: Session, cicd_run_id: uuid.UUID, data: QualityGateComputeRequest) -> QualityGateDecision:
    cicd_run = get_cicd_run(session, cicd_run_id)
    from_status = cicd_run.quality_gate_status
    patch = latest_unit_test_patch(session, cicd_run.id)
    new_tests = test_runs_by_type(session, cicd_run.id, "new_tests")
    regression = test_runs_by_type(session, cicd_run.id, "regression")
    patch_artifacts = patch_artifacts_for_run(session, cicd_run.id)

    blocking_reasons: list[str] = []
    status_detail = {
        "patch_scope_gate": patch.scope_gate_result_json if patch is not None else {},
        "unit_test_patch": {
            "id": str(patch.id) if patch is not None else None,
            "status": patch.status if patch is not None else "missing",
        },
        "new_tests": summarize_test_runs(new_tests),
        "regression": summarize_test_runs(regression),
        "failure_analysis": "not_requested" if not data.include_failure_analysis else "not_available",
    }

    if patch is None or patch.status != "applied":
        blocking_reasons.append("missing applied UnitTestPatch evidence")
    elif not patch.scope_gate_result_json.get("allowed", False):
        blocking_reasons.append("patch scope gate rejected")

    if not new_tests:
        blocking_reasons.append("missing new-test evidence")
    elif any_test_run_failed(new_tests):
        blocking_reasons.append("new-test evidence failed")

    if not regression:
        blocking_reasons.append("missing regression evidence")
    elif any_test_run_failed(regression):
        blocking_reasons.append("regression evidence failed")

    status_value = decide_quality_gate_status(blocking_reasons)
    summary = {
        "passed": "CI/CD quality gate passed with patch, new-test, and regression evidence.",
        "failed": "CI/CD quality gate failed due to blocking evidence.",
        "needs_review": "CI/CD quality gate needs review because required evidence is missing.",
    }[status_value]
    decision = QualityGateDecision(
        project_id=cicd_run.project_id,
        cicd_run_id=cicd_run.id,
        status=status_value,
        summary=summary,
        blocking_reasons_json=blocking_reasons,
        evidence_artifact_ids=[artifact.id for artifact in patch_artifacts],
        decided_by="system",
        status_detail_json=status_detail,
    )
    cicd_run.quality_gate_status = status_value
    session.add(decision)
    session.add(cicd_run)
    session.flush()
    append_review_history(
        session,
        project_id=cicd_run.project_id,
        entity_type="QualityGateDecision",
        entity_id=decision.id,
        related_entity_type="CICDRun",
        related_entity_id=cicd_run.id,
        action="compute_quality_gate",
        from_status=from_status,
        to_status=status_value,
        comment=summary,
        evidence_artifact_ids=decision.evidence_artifact_ids,
        metadata={"quality_gate_decision_id": str(decision.id)},
    )
    session.commit()
    session.refresh(decision)
    session.refresh(cicd_run)
    return decision


def generate_cicd_quality_report(
    session: Session,
    cicd_run_id: uuid.UUID,
    data: CICDQualityReportRequest,
) -> tuple[Report, Artifact]:
    cicd_run = get_cicd_run(session, cicd_run_id)
    decision = latest_quality_gate_decision(session, cicd_run.id)
    if decision is None:
        raise QualityGateDecisionMissingError
    patch = latest_unit_test_patch(session, cicd_run.id)
    new_tests = test_runs_by_type(session, cicd_run.id, "new_tests")
    regression = test_runs_by_type(session, cicd_run.id, "regression")
    evidence_artifacts = collect_cicd_quality_evidence_artifacts(session, cicd_run.id)
    manifest = build_cicd_quality_manifest(cicd_run, decision, patch, new_tests, regression, evidence_artifacts, data.report_format)
    report = Report(
        project_id=cicd_run.project_id,
        report_type="cicd_quality",
        title="CI/CD quality report",
        related_entity_type="CICDRun",
        related_entity_id=cicd_run.id,
        status="ready",
        conclusion=decision.status,
        summary=f"CI/CD quality gate is {decision.status}: {decision.summary}",
        metrics_json={
            "quality_gate_decision_id": str(decision.id),
            "quality_gate_status": decision.status,
            "unit_test_patch_status": patch.status if patch is not None else "missing",
            "new_test_run_count": len(new_tests),
            "regression_run_count": len(regression),
            "evidence_artifact_count": len(evidence_artifacts),
        },
        artifact_ids=[],
    )
    session.add(report)
    session.flush()
    manifest_artifact = Artifact(
        project_id=cicd_run.project_id,
        owner_entity_type="Report",
        owner_entity_id=report.id,
        artifact_type="report_json",
        file_path=f"artifacts/projects/{cicd_run.project_id}/cicd-quality/{cicd_run.id}/reports/{report.id}/evidence_manifest.json",
        mime_type="application/json",
        size_bytes=0,
        sha256=f"sha256:cicd_quality_manifest:{report.id}",
        metadata_json={
            "manifest_kind": "cicd_quality_evidence_manifest",
            "quality_gate_decision_id": str(decision.id),
            "manifest_json": manifest,
        },
    )
    session.add(manifest_artifact)
    session.flush()
    report.artifact_ids = [manifest_artifact.id]
    session.add(report)
    session.commit()
    session.refresh(report)
    session.refresh(manifest_artifact)
    return report, manifest_artifact


def latest_quality_gate_decision(session: Session, cicd_run_id: uuid.UUID) -> QualityGateDecision | None:
    return session.scalar(
        select(QualityGateDecision)
        .where(QualityGateDecision.cicd_run_id == cicd_run_id)
        .order_by(QualityGateDecision.created_at.desc()),
    )


def collect_cicd_quality_evidence_artifacts(session: Session, cicd_run_id: uuid.UUID) -> list[Artifact]:
    unit_test_patch_artifacts = patch_artifacts_for_run(session, cicd_run_id)
    cicd_run_artifacts = list(
        session.scalars(
            select(Artifact).where(
                Artifact.owner_entity_type == "CICDRun",
                Artifact.owner_entity_id == cicd_run_id,
                Artifact.artifact_type.in_({"regression_plan", "quality_gate"}),
            ),
        ),
    )
    return unit_test_patch_artifacts + cicd_run_artifacts


def build_cicd_quality_manifest(
    cicd_run: CICDRun,
    decision: QualityGateDecision,
    patch: UnitTestPatch | None,
    new_tests: list[TestRun],
    regression: list[TestRun],
    artifacts: list[Artifact],
    report_format: list[str],
) -> dict:
    evidence_kinds = list(dict.fromkeys([artifact.artifact_type for artifact in artifacts]))
    if patch is not None:
        evidence_kinds.append("patch_scope_gate")
    if new_tests:
        evidence_kinds.append("new_tests")
    if regression:
        evidence_kinds.append("regression")
    return {
        "cicd_run_id": str(cicd_run.id),
        "quality_gate_decision_id": str(decision.id),
        "quality_gate_status": decision.status,
        "quality_gate_summary": decision.summary,
        "blocking_reasons": decision.blocking_reasons_json,
        "unit_test_patch_id": str(patch.id) if patch is not None else None,
        "unit_test_patch_status": patch.status if patch is not None else "missing",
        "new_test_run_ids": [str(test_run.id) for test_run in new_tests],
        "regression_run_ids": [str(test_run.id) for test_run in regression],
        "evidence_artifact_ids": [str(artifact.id) for artifact in artifacts],
        "evidence_kinds": evidence_kinds,
        "report_format": report_format,
    }


def decide_quality_gate_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "passed"
    if any("failed" in reason or "rejected" in reason for reason in blocking_reasons):
        return "failed"
    return "needs_review"


def latest_unit_test_patch(session: Session, cicd_run_id: uuid.UUID) -> UnitTestPatch | None:
    return session.scalar(
        select(UnitTestPatch)
        .where(UnitTestPatch.cicd_run_id == cicd_run_id)
        .order_by(UnitTestPatch.created_at.desc()),
    )


def test_runs_by_type(session: Session, cicd_run_id: uuid.UUID, run_type: str) -> list[TestRun]:
    runs = list(
        session.scalars(
            select(TestRun)
            .where(TestRun.cicd_run_id == cicd_run_id)
            .order_by(TestRun.created_at.asc()),
        ),
    )
    return [test_run for test_run in runs if test_run.parsed_result_json.get("run_type") == run_type]


def summarize_test_runs(test_runs: list[TestRun]) -> dict:
    if not test_runs:
        return {"status": "missing", "test_run_ids": []}
    if any_test_run_failed(test_runs):
        status_value = "failed"
    elif all(test_run.status == "succeeded" and test_run.exit_code == 0 for test_run in test_runs):
        status_value = "succeeded"
    else:
        status_value = "pending"
    return {
        "status": status_value,
        "test_run_ids": [str(test_run.id) for test_run in test_runs],
    }


def any_test_run_failed(test_runs: list[TestRun]) -> bool:
    return any(test_run.status == "failed" or (test_run.exit_code is not None and test_run.exit_code != 0) for test_run in test_runs)


def patch_artifacts_for_run(session: Session, cicd_run_id: uuid.UUID) -> list[Artifact]:
    patches = list(session.scalars(select(UnitTestPatch).where(UnitTestPatch.cicd_run_id == cicd_run_id)))
    patch_ids = {patch.id for patch in patches}
    if not patch_ids:
        return []
    return list(
        session.scalars(
            select(Artifact).where(
                Artifact.owner_entity_type == "UnitTestPatch",
                Artifact.owner_entity_id.in_(patch_ids),
                Artifact.artifact_type == "unit_test_patch",
            ),
        ),
    )


def get_active_test_command(session: Session, project_id: uuid.UUID, test_command_id: uuid.UUID) -> TestCommand:
    command = session.get(TestCommand, test_command_id)
    if command is None or command.project_id != project_id or command.status != "active":
        raise TestCommandInvalidError
    return command


def create_cicd_test_run(
    session: Session,
    cicd_run: CICDRun,
    command: TestCommand,
    name: str,
    parsed_result: dict,
) -> TestRun:
    test_run = TestRun(
        project_id=cicd_run.project_id,
        cicd_run_id=cicd_run.id,
        test_command_id=command.id,
        name=name,
        command=command.command,
        working_directory=command.working_directory,
        runner_mode="local_subprocess",
        repository_readonly=True,
        network_enabled=False,
        status="queued",
        parsed_result_json=parsed_result,
    )
    session.add(test_run)
    session.flush()
    return test_run


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
                Artifact.artifact_type.in_({"risk_analysis", "ci_run_metadata"}),
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
