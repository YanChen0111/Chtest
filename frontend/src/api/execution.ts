import { apiClient } from './client';

export interface TestRunCreateRequest {
  readonly project_id: string;
  readonly automation_draft_id?: string | null;
  readonly test_command_id?: string | null;
  readonly reason?: string | null;
  readonly runner_mode?: string;
}

export interface TestResultRead {
  readonly id: string;
  readonly project_id: string;
  readonly test_run_id: string;
  readonly test_name: string;
  readonly test_file: string | null;
  readonly status: string;
  readonly duration_ms: number | null;
  readonly failure_message: string | null;
  readonly failure_artifact_ids: string[];
  readonly metadata: Record<string, unknown>;
}

export interface TestRunArtifactRead {
  readonly id: string;
  readonly project_id: string;
  readonly owner_entity_type: string;
  readonly owner_entity_id: string;
  readonly artifact_type: string;
  readonly file_path: string;
  readonly mime_type: string;
  readonly size_bytes: number;
  readonly sha256: string;
  readonly metadata_json: Record<string, unknown>;
}

export interface TestRunRead {
  readonly id: string;
  readonly project_id: string;
  readonly automation_draft_id: string | null;
  readonly test_command_id: string | null;
  readonly tool_invocation_id: string | null;
  readonly name: string;
  readonly command: string;
  readonly working_directory: string;
  readonly runner_mode: string;
  readonly run_workspace: string | null;
  readonly repository_readonly: boolean;
  readonly network_enabled: boolean;
  readonly runtime_artifact_ids: string[];
  readonly dependency_snapshot_artifact_id: string | null;
  readonly environment_snapshot_artifact_id: string | null;
  readonly status: string;
  readonly exit_code: number | null;
  readonly duration_ms: number | null;
  readonly parsed_result: Record<string, number>;
  readonly test_results: TestResultRead[];
  readonly artifacts: TestRunArtifactRead[];
}

export async function createTestRun(data: TestRunCreateRequest): Promise<TestRunRead> {
  return apiClient.postJson<TestRunRead, TestRunCreateRequest>('/test-runs', data);
}

export async function getTestRun(testRunId: string): Promise<TestRunRead> {
  return apiClient.getJson<TestRunRead>(`/test-runs/${testRunId}`);
}
