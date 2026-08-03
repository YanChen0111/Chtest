import { apiClient } from './client';

export type WorkflowQueueBucket = 'waiting_review' | 'waiting_approval' | 'can_continue';

export interface WorkflowQueueItem {
  readonly id: string;
  readonly project_id: string;
  readonly workflow_kind: string;
  readonly subject_ref: string;
  readonly current_stage: string;
  readonly gate_state: string;
  readonly bucket: WorkflowQueueBucket;
  readonly lock_version: number;
  readonly current_snapshot_id: string;
  readonly input_snapshot_hash: string;
  readonly approval_decision_id: string | null;
  readonly can_continue: boolean;
  readonly route_path: string | null;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface WorkflowQueueGroups {
  readonly waiting_review: WorkflowQueueItem[];
  readonly waiting_approval: WorkflowQueueItem[];
  readonly can_continue: WorkflowQueueItem[];
}

export interface WorkflowQueueRead {
  readonly project_id: string;
  readonly total: number;
  readonly groups: WorkflowQueueGroups;
  readonly items: WorkflowQueueItem[];
}

export async function listWorkflowQueue(projectId: string): Promise<WorkflowQueueRead> {
  return apiClient.getJson<WorkflowQueueRead>(`/projects/${projectId}/workflow-runs`);
}
