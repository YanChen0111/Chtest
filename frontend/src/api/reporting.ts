import { apiClient } from './client';
import type { TestRunArtifactRead } from './execution';

export interface FailureAnalysisCreateRequest {
  readonly prompt_version?: string;
  readonly skill_version?: string;
  readonly model_provider?: string;
  readonly model_name?: string;
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
