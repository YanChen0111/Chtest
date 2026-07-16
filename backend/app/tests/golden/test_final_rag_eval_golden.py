from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.schemas import ContextArtifactCreate
from backend.app.modules.ai_runtime.service import create_context_artifact
from backend.app.modules.extension.models import KnowledgeAdapterConfig
from backend.app.modules.extension.service import retrieve_deterministic_knowledge
from backend.app.modules.knowledge import models as knowledge_models
from backend.app.modules.knowledge.optional_providers import search_optional_provider
from backend.app.modules.projects.models import Project, Workspace


ROOT = Path(__file__).parents[4]
FIXTURE = ROOT / "docs/fixtures/18-final-rag-eval.md"
QUERY = "expired coupon checkout"


def _session_and_store(tmp_path: Path) -> tuple[Session, LocalArtifactStore]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(engine, expire_on_commit=False, future=True)()
    return session, LocalArtifactStore(root=tmp_path / "artifacts")


def _project(session: Session, name: str) -> Project:
    workspace = session.query(Workspace).filter_by(name="Personal Workspace").one_or_none()
    if workspace is None:
        workspace = Workspace(name="Personal Workspace")
        session.add(workspace)
        session.flush()
    project = Project(workspace=workspace, name=name)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def _artifact(
    session: Session,
    store: LocalArtifactStore,
    project: Project,
    title: str,
    content: str,
    *,
    safe_to_show: bool = True,
    allowed_for_prompt: bool = True,
):
    artifact = create_context_artifact(
        session,
        store,
        ContextArtifactCreate(
            project_id=project.id,
            title=title,
            artifact_type="context_markdown",
            mime_type="text/markdown",
            content=content,
            source_ref=f"manual:{title}",
        ),
    )
    metadata = dict(artifact.metadata_json)
    metadata.update({"safe_to_show": safe_to_show, "allowed_for_prompt": allowed_for_prompt})
    artifact.metadata_json = metadata
    session.add(artifact)
    session.commit()
    session.refresh(artifact)
    return artifact


def test_final_rag_eval_reports_recall_precision_safety_and_fallback(tmp_path: Path) -> None:
    assert FIXTURE.exists()
    assert knowledge_models.TestKnowledgeCard.__tablename__ == "test_knowledge_cards"
    session, store = _session_and_store(tmp_path)
    try:
        project = _project(session, "Checkout")
        other_project = _project(session, "Billing")
        session.add(
            KnowledgeAdapterConfig(
                project_id=project.id,
                adapter_name="default",
                status="configured_stub",
                provider_type="deterministic_local",
                config_json={"match_mode": "keyword_overlap", "max_results": 10},
            ),
        )
        session.commit()

        required_a = _artifact(
            session,
            store,
            project,
            "coupon-api-notes.md",
            "Expired coupon validation blocks checkout before payment submit.",
        )
        required_b = _artifact(
            session,
            store,
            project,
            "coupon-checkout-contract.md",
            "Checkout rejects expired coupon codes and explains the coupon failure.",
        )
        _artifact(session, store, project, "inventory-notes.md", "Warehouse stock reservation rules.")
        _artifact(
            session,
            store,
            project,
            "private-secrets.md",
            "Expired coupon checkout internal-only implementation detail.",
            safe_to_show=False,
            allowed_for_prompt=False,
        )
        _artifact(
            session,
            store,
            other_project,
            "billing-coupon-notes.md",
            "Expired coupon checkout billing details.",
        )

        result = retrieve_deterministic_knowledge(session, store, project.id, QUERY)
        ids = {item.context_artifact_id for item in result.results}
        required_ids = {required_a.id, required_b.id}
        relevant_ids = required_ids

        recall = len(ids & required_ids) / len(required_ids)
        precision = len(ids & relevant_ids) / len(ids)
        safety_exclusion = all(item.allowed_for_prompt and item.context_artifact_id in required_ids for item in result.results)

        assert recall == 1.0
        assert precision == 1.0
        assert safety_exclusion
        assert required_ids.issubset(ids)
        assert all(item.redaction_applied is False for item in result.results)
        assert all(item.source_ref.startswith("manual:") for item in result.results)
        assert all(item.score > 0 and item.matched_terms and item.sha256 for item in result.results)

        fallback = search_optional_provider(
            "qdrant",
            None,
            query_text=QUERY,
            limit=5,
            filters={"same_project_only": True},
            retrieval_mode="hybrid",
        )
        assert fallback.degraded is True
        assert fallback.fallback_reason == "provider_unavailable"
        assert fallback.provider_type == "qdrant"
        assert fallback.matches == ()
    finally:
        session.close()
