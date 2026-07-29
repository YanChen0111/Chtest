from __future__ import annotations

import os
import re
import uuid
from pathlib import PurePosixPath

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime import service
from backend.app.modules.ai_runtime.artifact_store import ArtifactPathError, LocalArtifactStore
from backend.app.modules.ai_runtime.model_config import (
    ModelConnectionConfig,
    ModelConnectionConfigError,
    load_model_connection_config,
    merge_model_connection_config,
    public_model_connection_config,
    save_model_connection_config,
)
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.ai_runtime.providers.base import LLMProviderError, LLMProviderRequest, LLMProviderTimeoutError
from backend.app.modules.ai_runtime.providers.factory import create_llm_provider
from backend.app.modules.ai_runtime.schemas import (
    AITaskDetailRead,
    AITaskListRead,
    ContextArtifactCreate,
    ContextArtifactListRead,
    ContextArtifactRead,
    ModelConnectionConfigRead,
    ModelConnectionTestRead,
    ModelConnectionConfigUpdate,
)
from backend.app.modules.projects.router import get_session


ARTIFACT_ROOT = os.getenv("CHTEST_ARTIFACT_ROOT", "artifacts")

router = APIRouter(tags=["ai-runtime"])

SECRET_SUMMARY_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{6,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE),
    re.compile(r"\b(?:api[_-]?key|token|secret)\b\s*[:=]\s*['\"]?[^'\"\s,;}]+", re.IGNORECASE),
]


def get_artifact_store() -> LocalArtifactStore:
    return LocalArtifactStore(root=ARTIFACT_ROOT)


def project_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "PROJECT_NOT_FOUND",
            "message": "Project not found.",
            "details": {},
        },
    )


def ai_task_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "AI_TASK_NOT_FOUND",
            "message": "AI task not found.",
            "details": {},
        },
    )


def artifact_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "ARTIFACT_NOT_FOUND",
            "message": "Artifact not found.",
            "details": {},
        },
    )


def artifact_file_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "ARTIFACT_FILE_NOT_FOUND",
            "message": "Artifact file not found.",
            "details": {},
        },
    )


def artifact_path_unsafe() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "error_code": "ARTIFACT_PATH_UNSAFE",
            "message": "Artifact path is unsafe.",
            "details": {},
        },
    )


def artifact_download_not_allowed() -> HTTPException:
    return HTTPException(
        status_code=403,
        detail={
            "error_code": "ARTIFACT_DOWNLOAD_NOT_ALLOWED",
            "message": "Artifact download is disabled by the current evidence safety state.",
            "details": {},
        },
    )


def artifact_not_local() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "ARTIFACT_NOT_LOCAL",
            "message": "Artifact is an inert external reference, not a local file.",
            "details": {},
        },
    )


def context_artifact_not_allowed() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "CONTEXT_ARTIFACT_NOT_ALLOWED",
            "message": "Context artifact type or MIME type is not allowed.",
            "details": {},
        },
    )


def context_artifact_too_large() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "CONTEXT_ARTIFACT_TOO_LARGE",
            "message": "Context artifact exceeds the V1 size limit.",
            "details": {},
        },
    )


def context_artifact_secret_detected() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "CONTEXT_ARTIFACT_SECRET_DETECTED",
            "message": "Context artifact content contains a high-risk secret.",
            "details": {},
        },
    )


def context_artifact_extraction_failed() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "CONTEXT_ARTIFACT_EXTRACTION_FAILED",
            "message": "Document content could not be extracted safely.",
            "details": {},
        },
    )


def context_artifact_extractor_unavailable() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={
            "error_code": "CONTEXT_ARTIFACT_EXTRACTOR_UNAVAILABLE",
            "message": "The required document extractor is not available on this host.",
            "details": {},
        },
    )


def model_config_invalid(message: str) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "MODEL_CONFIG_INVALID",
            "message": message,
            "details": {},
        },
    )


@router.get("/settings/model-connection", response_model=ModelConnectionConfigRead)
def read_model_connection_config() -> ModelConnectionConfigRead:
    try:
        config = load_model_connection_config()
    except ModelConnectionConfigError as exc:
        raise model_config_invalid(str(exc)) from exc
    return ModelConnectionConfigRead(**public_model_connection_config(config))


@router.put("/settings/model-connection", response_model=ModelConnectionConfigRead)
def update_model_connection_config(data: ModelConnectionConfigUpdate) -> ModelConnectionConfigRead:
    try:
        existing_config = load_model_connection_config()
        config = merge_model_connection_config(
            existing_config=existing_config,
            import_config_text=data.import_config_text,
            import_auth_json=data.import_auth_json,
            codex_config_toml=data.codex_config_toml,
            codex_auth_json=data.codex_auth_json,
            api_key=data.api_key,
            provider=data.provider,
            model_name=data.model_name,
            base_url=data.base_url,
            wire_api=data.wire_api,
        )
        save_model_connection_config(config)
    except ModelConnectionConfigError as exc:
        raise model_config_invalid(str(exc)) from exc
    return ModelConnectionConfigRead(**public_model_connection_config(config))


@router.post("/settings/model-connection/test", response_model=ModelConnectionTestRead)
def test_model_connection_config(data: ModelConnectionConfigUpdate | None = None) -> ModelConnectionTestRead:
    try:
        existing_config = load_model_connection_config()
        if data is not None and model_connection_update_has_values(data):
            config = merge_model_connection_config(
                existing_config=existing_config,
                import_config_text=data.import_config_text,
                import_auth_json=data.import_auth_json,
                codex_config_toml=data.codex_config_toml,
                codex_auth_json=data.codex_auth_json,
                api_key=data.api_key,
                provider=data.provider,
                model_name=data.model_name,
                base_url=data.base_url,
                wire_api=data.wire_api,
            )
        else:
            config = existing_config
    except ModelConnectionConfigError as exc:
        raise model_config_invalid(str(exc)) from exc
    if config is None:
        return model_connection_test_read(
            ok=False,
            message="Model connection is not configured.",
            error_code="MODEL_CONFIG_MISSING",
        )

    try:
        provider = create_llm_provider(
            config.provider,
            base_url=config.base_url,
            api_key=config.api_key,
            wire_api=config.wire_api,
            timeout_seconds=20,
            max_output_tokens=32,
        )
        response = provider.generate(
            LLMProviderRequest(
                task_type="model_connection_test",
                model_name=config.model_name,
                input_json={"instruction": "Reply with the single word ok."},
            ),
        )
    except ValueError as exc:
        return model_connection_test_read(
            config=config,
            ok=False,
            message=str(exc),
            error_code="MODEL_PROVIDER_UNSUPPORTED",
        )
    except LLMProviderTimeoutError:
        return model_connection_test_read(
            config=config,
            ok=False,
            message="Model connection test timed out.",
            error_code="MODEL_CONNECTION_TIMEOUT",
            suggestion="Check whether the model gateway is reachable from this machine, then retry.",
        )
    except LLMProviderError as exc:
        return model_connection_provider_error_read(config, exc)

    if response.status != "succeeded":
        return model_connection_test_read(
            config=config,
            ok=False,
            message="Model connection test returned an invalid response.",
            error_code="MODEL_CONNECTION_INVALID_RESPONSE",
            suggestion="The endpoint responded, but not in the expected Responses API shape. Check wire API compatibility.",
        )
    response_text = response.output_json.get("response_text")
    if not isinstance(response_text, str) or not response_text.strip():
        return model_connection_test_read(
            config=config,
            ok=False,
            message="Model connection test returned an empty response.",
            error_code="MODEL_CONNECTION_EMPTY_RESPONSE",
            suggestion="Check the model name and gateway compatibility, or use a model/wire API that returns visible text.",
        )
    return model_connection_test_read(
        config=config,
        ok=True,
        message="Model connection test succeeded.",
    )


@router.get("/artifacts/{artifact_id}/download")
def download_artifact(
    artifact_id: uuid.UUID,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> Response:
    artifact = session.get(Artifact, artifact_id)
    if artifact is None:
        raise artifact_not_found()
    if artifact.metadata_json.get("safe_to_show") is False or (
        artifact.artifact_type == "knowledge_retrieval"
        and artifact.metadata_json.get("safe_to_show") is not True
    ):
        raise artifact_download_not_allowed()
    if "://" in artifact.file_path or artifact.file_path.startswith("//"):
        raise artifact_not_local()

    try:
        content = store.read_bytes(artifact.file_path)
    except ArtifactPathError as exc:
        raise artifact_path_unsafe() from exc
    except FileNotFoundError as exc:
        raise artifact_file_not_found() from exc

    filename = safe_artifact_filename(artifact.file_path)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(
        content=content,
        media_type=artifact.mime_type or "application/octet-stream",
        headers=headers,
    )


@router.post(
    "/context-artifacts",
    response_model=ContextArtifactRead,
    status_code=status.HTTP_201_CREATED,
)
def create_context_artifact(
    data: ContextArtifactCreate,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> ContextArtifactRead:
    try:
        artifact = service.create_context_artifact(session, store, data)
    except service.ProjectNotFoundError as exc:
        raise project_not_found() from exc
    except service.ContextArtifactNotAllowedError as exc:
        raise context_artifact_not_allowed() from exc
    except service.ContextArtifactTooLargeError as exc:
        raise context_artifact_too_large() from exc
    except service.ContextArtifactSecretDetectedError as exc:
        raise context_artifact_secret_detected() from exc
    except service.ContextArtifactExtractorUnavailableError as exc:
        raise context_artifact_extractor_unavailable() from exc
    except service.ContextArtifactExtractionError as exc:
        raise context_artifact_extraction_failed() from exc

    return context_artifact_read(artifact)


@router.get(
    "/projects/{project_id}/context-artifacts",
    response_model=ContextArtifactListRead,
)
def list_context_artifacts(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ContextArtifactListRead:
    try:
        items = service.list_context_artifacts(session, project_id)
    except service.ProjectNotFoundError as exc:
        raise project_not_found() from exc
    return ContextArtifactListRead(items=items, total=len(items))


@router.delete("/context-artifacts/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_context_artifact(
    artifact_id: uuid.UUID,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> None:
    try:
        service.delete_context_artifact(session, store, artifact_id)
    except service.ContextArtifactNotFoundError as exc:
        raise artifact_not_found() from exc


@router.get("/ai-tasks/{ai_task_id}", response_model=AITaskDetailRead)
def get_ai_task(
    ai_task_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> AITaskDetailRead:
    try:
        return service.get_ai_task_detail(session, ai_task_id)
    except service.AITaskNotFoundError as exc:
        raise ai_task_not_found() from exc


@router.get("/projects/{project_id}/ai-tasks", response_model=AITaskListRead)
def list_project_ai_tasks(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> AITaskListRead:
    try:
        return service.list_project_ai_tasks(session, project_id)
    except service.ProjectNotFoundError as exc:
        raise project_not_found() from exc


def context_artifact_read(artifact: Artifact) -> ContextArtifactRead:
    return ContextArtifactRead(
        id=artifact.id,
        project_id=artifact.project_id,
        owner_entity_type=artifact.owner_entity_type,
        owner_entity_id=artifact.owner_entity_id,
        artifact_type=artifact.artifact_type,
        mime_type=artifact.mime_type,
        file_path=artifact.file_path,
        sha256=f"sha256:{artifact.sha256}",
        metadata=artifact.metadata_json,
    )


def model_connection_test_read(
    *,
    ok: bool,
    message: str,
    error_code: str | None = None,
    http_status: int | None = None,
    diagnostic: str | None = None,
    suggestion: str | None = None,
    config: ModelConnectionConfig | None = None,
) -> ModelConnectionTestRead:
    public_config = public_model_connection_config(config)
    return ModelConnectionTestRead(
        ok=ok,
        provider=public_config["provider"],
        model_name=public_config["model_name"],
        base_url=public_config["base_url"],
        wire_api=public_config["wire_api"],
        message=message,
        error_code=error_code,
        http_status=http_status,
        diagnostic=diagnostic,
        suggestion=suggestion,
    )


def model_connection_update_has_values(data: ModelConnectionConfigUpdate) -> bool:
    return any(
        isinstance(value, str) and value.strip()
        for value in [
            data.provider,
            data.model_name,
            data.base_url,
            data.wire_api,
            data.api_key,
            data.import_config_text,
            data.import_auth_json,
            data.codex_config_toml,
            data.codex_auth_json,
        ]
    )


def model_connection_provider_error_read(
    config: ModelConnectionConfig,
    exc: LLMProviderError,
) -> ModelConnectionTestRead:
    error_text = str(exc)
    status_match = re.search(r"HTTP (?P<status>\d{3})", error_text)
    if status_match:
        http_status = int(status_match.group("status"))
        suggestion_by_status = {
            400: "The gateway rejected the request shape. Check wire API, model name, and whether the endpoint supports /responses.",
            401: "Authentication failed. Check that the API key is valid for this gateway.",
            403: "The gateway refused the request. Check API key permissions, account access, model access, and gateway allowlists.",
            404: "The endpoint was not found. Check whether Base URL should end at /v1 or whether the gateway supports /responses.",
            408: "The gateway timed out. Check gateway health or try again.",
            429: "The gateway rate limit or quota was hit. Check account quota and retry later.",
        }
        if http_status >= 500:
            suggestion = "The model gateway returned a server error. Check gateway health and upstream provider status."
        else:
            suggestion = suggestion_by_status.get(
                http_status,
                "Check the Base URL, API key, provider, model name, and gateway logs.",
            )
        return model_connection_test_read(
            config=config,
            ok=False,
            message=f"Model gateway returned HTTP {http_status}.",
            error_code=f"MODEL_CONNECTION_HTTP_{http_status}",
            http_status=http_status,
            diagnostic=f"HTTP {http_status}",
            suggestion=suggestion,
        )

    if "invalid JSON" in error_text:
        return model_connection_test_read(
            config=config,
            ok=False,
            message="Model gateway returned invalid JSON.",
            error_code="MODEL_CONNECTION_INVALID_JSON",
            diagnostic="Invalid JSON response",
            suggestion="Check whether the Base URL points to a Responses-compatible JSON API endpoint.",
        )

    return model_connection_test_read(
        config=config,
        ok=False,
        message="Model connection test failed before a valid response was received.",
        error_code="MODEL_CONNECTION_FAILED",
        diagnostic=safe_provider_error_summary(error_text),
        suggestion="Check network reachability, Base URL, API key, provider, model name, and gateway logs.",
    )


def safe_provider_error_summary(error_text: str) -> str:
    text = error_text.strip()
    if not text:
        return "Provider error"
    for pattern in SECRET_SUMMARY_PATTERNS:
        text = pattern.sub("[redacted]", text)
    return text[:240]


def safe_artifact_filename(file_path: str) -> str:
    name = PurePosixPath(file_path).name
    safe = "".join(character if character.isalnum() or character in {"-", "_", "."} else "_" for character in name)
    return safe or "artifact"
