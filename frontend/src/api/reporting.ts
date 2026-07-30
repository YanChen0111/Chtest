import { apiClient } from './client';
import type { TestRunArtifactRead } from './execution';

export interface FailureAnalysisCreateRequest {
  readonly prompt_version?: string;
  readonly skill_version?: string;
  readonly model_provider?: string;
  readonly model_name?: string;
  readonly execution_result_review_decision_id?: string;
}

export interface FailureAnalysisCreateRead {
  readonly ai_task_id: string;
  readonly failure_analysis_id: string;
  readonly status: string;
}

export interface FailureAnalysisRead {
  readonly id: string;
  readonly project_id: string;
  readonly test_run_id: string | null;
  readonly test_result_id: string | null;
  readonly ai_task_id: string;
  readonly classification: string;
  readonly confidence: number;
  readonly evidence_artifact_ids: string[];
  readonly summary: string;
  readonly root_cause: string | null;
  readonly suggested_actions: unknown[];
  readonly status: string;
}

export interface ReportCreateRequest {
  readonly project_id: string;
  readonly report_type: string;
  readonly related_entity_type: string;
  readonly related_entity_id: string;
  readonly execution_result_review_decision_id?: string;
}

export interface ReportCreateRead {
  readonly report_id: string;
  readonly status: string;
  readonly evidence_manifest_artifact_id: string | null;
}

export interface EvidenceManifestItem {
  readonly artifact_id?: string;
  readonly artifact_type?: string;
  readonly metric?: string;
  readonly test_result_id?: string;
  readonly supports_claim: string;
  readonly required: boolean;
}

export interface EvidenceManifest {
  readonly report_id?: string;
  readonly conclusion?: string;
  readonly evidence?: EvidenceManifestItem[];
  readonly missing_evidence?: string[];
}

export interface ReportRead {
  readonly id: string;
  readonly project_id: string;
  readonly report_type: string;
  readonly title: string;
  readonly related_entity_type: string | null;
  readonly related_entity_id: string | null;
  readonly status: string;
  readonly conclusion: string | null;
  readonly summary: string | null;
  readonly metrics: Record<string, number>;
  readonly artifact_ids: string[];
  readonly evidence_manifest: EvidenceManifest;
  readonly artifacts: TestRunArtifactRead[];
}

export interface ReportReviewWorkflowActionRequest {
  readonly expected_version: number;
  readonly reviewer?: string;
  readonly comment?: string | null;
}

export interface ReportReviewWorkflowEditRequest extends ReportReviewWorkflowActionRequest {
  readonly report_decisions: Record<string, unknown>[];
}

export interface ReportReviewWorkflowContinueRequest {
  readonly expected_version: number;
  readonly approval_decision_id: string;
}

export interface ReportReviewWorkflowRead {
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
    readonly published?: boolean;
  };
  readonly source_execution_result_review_snapshot_id: string | null;
  readonly source_execution_result_review_snapshot_hash: string | null;
  readonly source_execution_approval_snapshot_id: string | null;
  readonly source_execution_approval_snapshot_hash: string | null;
  readonly generated_test_run_ids: string[];
  readonly execution_artifact_ids: string[];
  readonly generated_report_ids: string[];
  readonly report_artifact_ids: string[];
  readonly execution_decisions: Record<string, unknown>[];
  readonly result_decisions: Record<string, unknown>[];
  readonly report_decisions: Record<string, unknown>[];
}

export async function createFailureAnalysis(
  testRunId: string,
  data: FailureAnalysisCreateRequest = {},
): Promise<FailureAnalysisCreateRead> {
  return apiClient.postJson<FailureAnalysisCreateRead, FailureAnalysisCreateRequest>(
    `/test-runs/${testRunId}/failure-analysis`,
    data,
  );
}

export async function getFailureAnalysis(testRunId: string): Promise<FailureAnalysisRead> {
  return apiClient.getJson<FailureAnalysisRead>(`/test-runs/${testRunId}/failure-analysis`);
}

export async function createReport(data: ReportCreateRequest): Promise<ReportCreateRead> {
  return apiClient.postJson<ReportCreateRead, ReportCreateRequest>('/reports', data);
}

export async function getReport(reportId: string): Promise<ReportRead> {
  return apiClient.getJson<ReportRead>(`/reports/${reportId}`);
}

export async function getReportReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
): Promise<ReportReviewWorkflowRead> {
  return apiClient.getJson<ReportReviewWorkflowRead>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/report-review`,
  );
}

export async function submitReportReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ReportReviewWorkflowActionRequest,
): Promise<ReportReviewWorkflowRead> {
  return apiClient.postJson<ReportReviewWorkflowRead, ReportReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/report-review/submit`,
    data,
  );
}

export async function completeReportReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ReportReviewWorkflowActionRequest,
): Promise<ReportReviewWorkflowRead> {
  return apiClient.postJson<ReportReviewWorkflowRead, ReportReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/report-review/complete-review`,
    data,
  );
}

export async function editReportReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ReportReviewWorkflowEditRequest,
): Promise<ReportReviewWorkflowRead> {
  return apiClient.postJson<ReportReviewWorkflowRead, ReportReviewWorkflowEditRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/report-review/edit`,
    data,
  );
}

export async function approveReportReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ReportReviewWorkflowActionRequest,
): Promise<ReportReviewWorkflowRead> {
  return apiClient.postJson<ReportReviewWorkflowRead, ReportReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/report-review/approve`,
    data,
  );
}

export async function rejectReportReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ReportReviewWorkflowActionRequest,
): Promise<ReportReviewWorkflowRead> {
  return apiClient.postJson<ReportReviewWorkflowRead, ReportReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/report-review/reject`,
    data,
  );
}

export async function continueReportReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ReportReviewWorkflowContinueRequest,
): Promise<ReportReviewWorkflowRead> {
  return apiClient.postJson<ReportReviewWorkflowRead, ReportReviewWorkflowContinueRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/report-review/continue`,
    data,
  );
}

export async function approveAndContinueReportReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: ReportReviewWorkflowActionRequest,
): Promise<ReportReviewWorkflowRead> {
  return apiClient.postJson<ReportReviewWorkflowRead, ReportReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/report-review/approve-and-continue`,
    data,
  );
}
