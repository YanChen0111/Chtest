from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.modules.projects.router import get_session
from backend.app.modules.workflow_control import service
from backend.app.modules.workflow_control.policy import ControlledStage, WorkflowKind
from backend.app.modules.workflow_control.schemas import WorkflowRunRead, WorkflowStageSnapshotRead

router = APIRouter(tags=["workflow-control"])


def workflow_not_found() -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={"error_code": "WORKFLOW_RUN_NOT_FOUND", "message": "Workflow run not found.", "details": {}},
    )


@router.get("/projects/{project_id}/workflow-runs/{run_id}", response_model=WorkflowRunRead)
def read_workflow_run(project_id: uuid.UUID, run_id: uuid.UUID, session: Session = Depends(get_session)) -> WorkflowRunRead:
    try:
        run, snapshot = service.get_workflow_run_authoritative(session, project_id, run_id)
    except service.WorkflowRunNotFoundError as exc:
        raise workflow_not_found() from exc
    return WorkflowRunRead(
        id=run.id,
        project_id=run.project_id,
        workflow_kind=WorkflowKind(run.workflow_kind),
        subject_ref=run.subject_ref,
        current_stage=ControlledStage(run.current_stage),
        gate_state=run.gate_state,
        input_snapshot_hash=run.input_snapshot_hash,
        current_snapshot_id=run.current_snapshot_id,
        completed_stages=[ControlledStage(value) for value in run.completed_stages_json],
        lock_version=run.lock_version,
        status=run.status,
        snapshot=WorkflowStageSnapshotRead(
            id=snapshot.id,
            stage=ControlledStage(snapshot.stage),
            stage_iteration=snapshot.stage_iteration,
            input_snapshot_hash=snapshot.input_snapshot_hash,
            created_by_actor=snapshot.created_by_actor,
            created_by_label=snapshot.created_by_label,
            created_at=snapshot.created_at.isoformat(),
        ),
    )
