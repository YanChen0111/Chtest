import { apiClient } from './client';

export interface AITaskListItem {
  readonly id: string;
  readonly project_id: string;
  readonly agent_name: string;
  readonly task_type: string;
  readonly status: string;
  readonly model_provider: string;
  readonly model_name: string;
  readonly context_artifact_ids: string[];
  readonly started_at: string | null;
  readonly finished_at: string | null;
}

export interface AITaskListResponse {
  readonly items: AITaskListItem[];
  readonly total: number;
}

export interface AIArtifactSummary {
  readonly id: string;
  readonly artifact_type: string;
  readonly file_path: string;
  readonly mime_type: string;
  readonly size_bytes: number;
  readonly sha256: string;
  readonly safe_to_show: boolean;
  readonly redaction_applied: boolean;
}

export interface LLMCallLogSummary {
  readonly id: string;
  readonly provider: string;
  readonly model_name: string;
  readonly call_index: number;
  readonly status: string;
  readonly request_artifact_id: string | null;
  readonly response_artifact_id: string | null;
  readonly parsed_artifact_id: string | null;
  readonly schema_validation_artifact_id: string | null;
  readonly token_usage_json: Record<string, unknown>;
  readonly latency_ms: number | null;
  readonly error_json: Record<string, unknown> | null;
  readonly started_at: string | null;
  readonly finished_at: string | null;
}

export interface AITaskDetail {
  readonly id: string;
  readonly project_id: string;
  readonly agent_name: string;
  readonly task_type: string;
  readonly status: string;
  readonly prompt_version_id: string;
  readonly skill_version_id: string;
  readonly model_provider: string;
  readonly model_name: string;
  readonly token_usage: Record<string, unknown>;
  readonly used_knowledge: boolean;
  readonly context_artifact_ids: string[];
  readonly used_context_artifact_ids: string[];
  readonly context_manifest_artifact_id: string | null;
  readonly artifacts: AIArtifactSummary[];
  readonly llm_call_logs: LLMCallLogSummary[];
  readonly started_at: string | null;
  readonly finished_at: string | null;
}

export async function listProjectAITasks(projectId: string): Promise<AITaskListResponse> {
  return apiClient.getJson<AITaskListResponse>(`/projects/${projectId}/ai-tasks`);
}

export async function getAITaskDetail(aiTaskId: string): Promise<AITaskDetail> {
  return apiClient.getJson<AITaskDetail>(`/ai-tasks/${aiTaskId}`);
}
