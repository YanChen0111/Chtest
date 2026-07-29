import { apiClient } from './client';

export interface TestRunCreateRequest {
  readonly project_id: string;
  readonly automation_draft_id?: string | null;
  readonly test_command_id?: string | null;
  readonly execution_approval_decision_id?: string | null;
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
  readonly parsed_result: Record<string, number | string>;
  readonly test_results: TestResultRead[];
  readonly artifacts: TestRunArtifactRead[];
}

export interface ExecutionApprovalWorkflowActionRequest {
  readonly expected_version: number;
  readonly reviewer?: string;
  readonly comment?: string | null;
}

export interface ExecutionApprovalWorkflowEditRequest extends ExecutionApprovalWorkflowActionRequest {
  readonly execution_decisions: Record<string, unknown>[];
}

export interface ExecutionApprovalWorkflowContinueRequest {
  readonly expected_version: number;
  readonly approval_decision_id: string;
}

export interface ExecutionApprovalWorkflowRead {
  readonly project_id: string;
  readonly requirement_review_id: string;
  readonly workflow: {
    readonly run_id: string;
    readonly stage: string;
    readonly state: string;
    readonly lock_version: number;
    readonly snapshot_id: string;
    readonly approval_decision_id: string | null;
    readonly can_submit: boolean;
    readonly can_complete_review: boolean;
    readonly can_edit: boolean;
    readonly can_approve: boolean;
    readonly can_execute?: boolean;
    readonly can_continue: boolean;
  };
  readonly source_automation_draft_review_snapshot_id: string | null;
  readonly source_automation_draft_review_snapshot_hash: string | null;
  readonly source_automation_plan_review_snapshot_id: string | null;
  readonly source_automation_plan_review_snapshot_hash: string | null;
  readonly source_case_review_snapshot_id: string | null;
  readonly source_case_review_snapshot_hash: string | null;
  readonly approved_automation_plan_ids: string[];
  readonly approved_test_case_ids: string[];
  readonly approved_automation_draft_ids: string[];
  readonly generated_test_run_ids: string[];
  readonly draft_decisions?: Record<string, unknown>[];
  readonly execution_decisions: Record<string, unknown>[];
}

export interface ExecutionResultReviewWorkflowActionRequest {
  readonly expected_version: number;
  readonly reviewer?: string;
  readonly comment?: string | null;
}

export interface ExecutionResultReviewWorkflowEditRequest extends ExecutionResultReviewWorkflowActionRequest {
  readonly result_decisions: Record<string, unknown>[];
}

export interface ExecutionResultReviewWorkflowContinueRequest {
  readonly expected_version: number;
  readonly approval_decision_id: string;
}

export interface ExecutionResultReviewWorkflowRead {
  readonly project_id: string;
  readonly requirement_review_id: string;
  readonly workflow: {
    readonly run_id: string;
    readonly stage: string;
    readonly state: string;
    readonly lock_version: number;
    readonly snapshot_id: string;
    readonly approval_decision_id: string | null;
    readonly can_submit: boolean;
    readonly can_complete_review: boolean;
    readonly can_edit: boolean;
    readonly can_approve: boolean;
    readonly can_continue: boolean;
  };
  readonly source_execution_approval_snapshot_id: string | null;
  readonly source_execution_approval_snapshot_hash: string | null;
  readonly source_automation_draft_review_snapshot_id: string | null;
  readonly source_automation_draft_review_snapshot_hash: string | null;
  readonly source_automation_plan_review_snapshot_id: string | null;
  readonly source_automation_plan_review_snapshot_hash: string | null;
  readonly source_case_review_snapshot_id: string | null;
  readonly source_case_review_snapshot_hash: string | null;
  readonly approved_automation_draft_ids: string[];
  readonly generated_test_run_ids: string[];
  readonly execution_artifact_ids: string[];
  readonly execution_decisions: Record<string, unknown>[];
  readonly result_decisions: Record<string, unknown>[];
}

export async function createTestRun(data: TestRunCreateRequest): Promise<TestRunRead> {
  return apiClient.postJson<TestRunRead, TestRunCreateRequest>('/test-runs', data);
}

export async function getTestRun(testRunId: string): Promise<TestRunRead> {
  return apiClient.getJson<TestRunRead>(`/test-runs/${testRunId}`);
}

export async function getExecutionApprovalWorkflow(
  projectId: string,
  requirementReviewId: string,
): Promise<ExecutionApprovalWorkflowRead> {
  return apiClient.getJson<ExecutionApprovalWorkflowRead>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-approval`,
  );
}

export async function submitExecutionApprovalWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionApprovalWorkflowActionRequest,
): Promise<ExecutionApprovalWorkflowRead> {
  return apiClient.postJson<ExecutionApprovalWorkflowRead, ExecutionApprovalWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-approval/submit`,
    data,
  );
}

export async function completeExecutionApprovalWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionApprovalWorkflowActionRequest,
): Promise<ExecutionApprovalWorkflowRead> {
  return apiClient.postJson<ExecutionApprovalWorkflowRead, ExecutionApprovalWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-approval/complete-review`,
    data,
  );
}

export async function editExecutionApprovalWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionApprovalWorkflowEditRequest,
): Promise<ExecutionApprovalWorkflowRead> {
  return apiClient.postJson<ExecutionApprovalWorkflowRead, ExecutionApprovalWorkflowEditRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-approval/edit`,
    data,
  );
}

export async function approveExecutionApprovalWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionApprovalWorkflowActionRequest,
): Promise<ExecutionApprovalWorkflowRead> {
  return apiClient.postJson<ExecutionApprovalWorkflowRead, ExecutionApprovalWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-approval/approve`,
    data,
  );
}

export async function rejectExecutionApprovalWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionApprovalWorkflowActionRequest,
): Promise<ExecutionApprovalWorkflowRead> {
  return apiClient.postJson<ExecutionApprovalWorkflowRead, ExecutionApprovalWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-approval/reject`,
    data,
  );
}

export async function continueExecutionApprovalWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionApprovalWorkflowContinueRequest,
): Promise<ExecutionApprovalWorkflowRead> {
  return apiClient.postJson<ExecutionApprovalWorkflowRead, ExecutionApprovalWorkflowContinueRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-approval/continue`,
    data,
  );
}

export async function approveAndContinueExecutionApprovalWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionApprovalWorkflowActionRequest,
): Promise<ExecutionApprovalWorkflowRead> {
  return apiClient.postJson<ExecutionApprovalWorkflowRead, ExecutionApprovalWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-approval/approve-and-continue`,
    data,
  );
}

export async function getExecutionResultReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
): Promise<ExecutionResultReviewWorkflowRead> {
  return apiClient.getJson<ExecutionResultReviewWorkflowRead>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-result-review`,
  );
}

export async function submitExecutionResultReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionResultReviewWorkflowActionRequest,
): Promise<ExecutionResultReviewWorkflowRead> {
  return apiClient.postJson<ExecutionResultReviewWorkflowRead, ExecutionResultReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-result-review/submit`,
    data,
  );
}

export async function completeExecutionResultReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionResultReviewWorkflowActionRequest,
): Promise<ExecutionResultReviewWorkflowRead> {
  return apiClient.postJson<ExecutionResultReviewWorkflowRead, ExecutionResultReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-result-review/complete-review`,
    data,
  );
}

export async function editExecutionResultReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionResultReviewWorkflowEditRequest,
): Promise<ExecutionResultReviewWorkflowRead> {
  return apiClient.postJson<ExecutionResultReviewWorkflowRead, ExecutionResultReviewWorkflowEditRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-result-review/edit`,
    data,
  );
}

export async function approveExecutionResultReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionResultReviewWorkflowActionRequest,
): Promise<ExecutionResultReviewWorkflowRead> {
  return apiClient.postJson<ExecutionResultReviewWorkflowRead, ExecutionResultReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-result-review/approve`,
    data,
  );
}

export async function rejectExecutionResultReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionResultReviewWorkflowActionRequest,
): Promise<ExecutionResultReviewWorkflowRead> {
  return apiClient.postJson<ExecutionResultReviewWorkflowRead, ExecutionResultReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-result-review/reject`,
    data,
  );
}

export async function continueExecutionResultReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionResultReviewWorkflowContinueRequest,
): Promise<ExecutionResultReviewWorkflowRead> {
  return apiClient.postJson<ExecutionResultReviewWorkflowRead, ExecutionResultReviewWorkflowContinueRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-result-review/continue`,
    data,
  );
}

export async function approveAndContinueExecutionResultReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ExecutionResultReviewWorkflowActionRequest,
): Promise<ExecutionResultReviewWorkflowRead> {
  return apiClient.postJson<ExecutionResultReviewWorkflowRead, ExecutionResultReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-result-review/approve-and-continue`,
    data,
  );
}

export function artifactDownloadUrl(artifactId: string): string {
  return `/api/artifacts/${artifactId}/download`;
}
