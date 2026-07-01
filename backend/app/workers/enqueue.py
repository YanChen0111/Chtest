from __future__ import annotations

import uuid
from collections import deque
from dataclasses import dataclass

from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.models import AITask


@dataclass(frozen=True)
class AIQueueJob:
    ai_task_id: uuid.UUID


class FakeAIQueue:
    def __init__(self) -> None:
        self._jobs: deque[AIQueueJob] = deque()

    def push(self, job: AIQueueJob) -> None:
        self._jobs.append(job)

    def pop_next(self) -> AIQueueJob | None:
        if not self._jobs:
            return None
        return self._jobs.popleft()


def enqueue_ai_task(session: Session, queue: FakeAIQueue, ai_task_id: uuid.UUID) -> AIQueueJob:
    ai_task = session.get(AITask, ai_task_id)
    if ai_task is None:
        raise ValueError("AI task not found.")
    if ai_task.status != "created":
        raise ValueError("Only created AI tasks can be enqueued.")

    ai_task.status = "pending"
    session.add(ai_task)
    session.commit()
    job = AIQueueJob(ai_task_id=ai_task.id)
    queue.push(job)
    return job
