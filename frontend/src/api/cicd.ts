import { apiClient } from './client';
import type { TestRunArtifactRead } from './execution';

export interface CICDRunCreateRequest {
  readonly project_id: string;
  readonly repository_id?: string | null;
  readonly source_type?: string;
  readonly trigger_type?: string;
  readonly provider?: string;
  readonly pipeline_name?: string | null;
  readonly base_ref?: string | null;
  readonly head_ref?: string | null;
  readonly diff_text?: string | null;
}

export interface CICDRunCreateRead {
  readonly cicd_run_id: string;
  readonly status: string;
}

export interface CICDRunAnalyzeRequest {
  readonly prompt_version?: string;
  readonly skill_version?: string;
  readonly model_provider?: string;
  readonly model_name?: string;
}

export interface CICDRunAnalyzeRead {
  readonly cicd_run_id: string;
  readonly ai_task_id: string;
  readonly risk_analysis_artifact_id: string;
  readonly status: string;
}

export interface UnitTestPatchRead {
  readonly id: string;
  readonly cicd_run_id: string;
  readonly ai_task_id: string;
  readonly patch_text: string;
  readonly target_framework: string;
  readonly scope_gate_result: {
    readonly allowed?: boolean;
    readonly checked_paths?: string[];
    readonly blocked_paths?: string[];
    readonly forbidden_patterns?: string[];
    readonly risk_level?: string;
    readonly reason?: string;
  };
  readonly test_intent: string;
  readonly coverage_target: Array<{ readonly path?: string; readonly reason?: string }>;
  readonly status: string;
  readonly review_comment: string | null;
}

export interface UnitTestPatchReviewRead {
  readonly unit_test_patch_id: string;
  readonly status: string;
}

export interface CICDRunNewTestsRead {
  readonly test_run_id: string;
  readonly cicd_run_id: string;
  readonly status: string;
}

export interface CICDRegressionSelectRead {
  readonly cicd_run_id: string;
  readonly regression_plan_artifact_id: string;
  readonly recommended_test_command_ids: string[];
  readonly reasons: string[];
}

export interface CICDRegressionRunRead {
  readonly cicd_run_id: string;
  readonly test_run_ids: string[];
  readonly status: string;
}

export interface QualityGateDecisionRead {
  readonly id: string;
  readonly project_id: string;
  readonly cicd_run_id: string;
  readonly status: string;
  readonly summary: string;
  readonly blocking_reasons: string[];
  readonly evidence_artifact_ids: string[];
  readonly decided_by: string;
  readonly status_detail: Record<string, unknown>;
}

export interface CICDQualityReportRead {
  readonly report_id: string;
  readonly cicd_run_id: string;
  readonly status: string;
  readonly evidence_manifest_artifact_id: string | null;
}

export interface CICDChangedFileRead {
  readonly id: string;
  readonly cicd_run_id: string;
  readonly path: string;
  readonly old_path: string | null;
  readonly change_type: string;
  readonly language: string | null;
  readonly file_role: string;
  readonly risk_level: string;
  readonly risk_reasons: string[];
  readonly lines_added: number;
  readonly lines_deleted: number;
}

export interface CICDRunRead {
  readonly id: string;
  readonly project_id: string;
  readonly repository_id: string | null;
  readonly source_type: string;
  readonly trigger_type: string;
  readonly provider: string;
  readonly pipeline_name: string | null;
  readonly base_ref: string | null;
  readonly head_ref: string | null;
  readonly summary: string | null;
  readonly overall_risk: string;
  readonly quality_gate_status: string;
  readonly status: string;
  readonly changed_files: CICDChangedFileRead[];
  readonly analysis_artifacts: TestRunArtifactRead[];
}

export interface CICDRunListRead {
  readonly items: CICDRunRead[];
  readonly total: number;
}

export async function createCICDRun(data: CICDRunCreateRequest): Promise<CICDRunCreateRead> {
  return apiClient.postJson<CICDRunCreateRead, CICDRunCreateRequest>('/cicd/runs', data);
}

export async function getCICDRun(cicdRunId: string): Promise<CICDRunRead> {
  return apiClient.getJson<CICDRunRead>(`/cicd/runs/${cicdRunId}`);
}

export async function listCICDRuns(): Promise<CICDRunListRead> {
  return apiClient.getJson<CICDRunListRead>('/cicd/runs');
}

export async function analyzeCICDRun(
  cicdRunId: string,
  data: CICDRunAnalyzeRequest = {},
): Promise<CICDRunAnalyzeRead> {
  return apiClient.postJson<CICDRunAnalyzeRead, CICDRunAnalyzeRequest>(`/cicd/runs/${cicdRunId}/analyze`, data);
}

export async function generateUnitTestPatch(cicdRunId: string): Promise<UnitTestPatchRead> {
  return apiClient.postJson<UnitTestPatchRead, Record<string, unknown>>(`/cicd/runs/${cicdRunId}/unit-test-patches`, {});
}

export async function approveUnitTestPatch(patchId: string, reviewComment: string): Promise<UnitTestPatchReviewRead> {
  return apiClient.postJson<UnitTestPatchReviewRead, { review_comment: string }>(
    `/cicd/unit-test-patches/${patchId}/approve`,
    { review_comment: reviewComment },
  );
}

export async function rejectUnitTestPatch(patchId: string, reviewComment: string): Promise<UnitTestPatchReviewRead> {
  return apiClient.postJson<UnitTestPatchReviewRead, { review_comment: string }>(
    `/cicd/unit-test-patches/${patchId}/reject`,
    { review_comment: reviewComment },
  );
}

export async function runNewTests(cicdRunId: string, unitTestPatchId: string): Promise<CICDRunNewTestsRead> {
  return apiClient.postJson<CICDRunNewTestsRead, { unit_test_patch_id: string; test_command_id: string }>(
    `/cicd/runs/${cicdRunId}/run-new-tests`,
    {
      unit_test_patch_id: unitTestPatchId,
      test_command_id: '00000000-0000-0000-0000-000000000302',
    },
  );
}

export async function selectRegression(cicdRunId: string): Promise<CICDRegressionSelectRead> {
  return apiClient.postJson<CICDRegressionSelectRead, { candidate_test_command_ids: string[] }>(
    `/cicd/runs/${cicdRunId}/select-regression`,
    { candidate_test_command_ids: ['00000000-0000-0000-0000-000000000302'] },
  );
}

export async function runRegression(
  cicdRunId: string,
  regressionPlanArtifactId: string,
  testCommandIds: string[],
): Promise<CICDRegressionRunRead> {
  return apiClient.postJson<CICDRegressionRunRead, { regression_plan_artifact_id: string; test_command_ids: string[] }>(
    `/cicd/runs/${cicdRunId}/run-regression`,
    { regression_plan_artifact_id: regressionPlanArtifactId, test_command_ids: testCommandIds },
  );
}

export async function computeQualityGate(cicdRunId: string): Promise<QualityGateDecisionRead> {
  return apiClient.postJson<QualityGateDecisionRead, Record<string, unknown>>(`/cicd/runs/${cicdRunId}/quality-gate`, {});
}

export async function generateCICDQualityReport(cicdRunId: string): Promise<CICDQualityReportRead> {
  return apiClient.postJson<CICDQualityReportRead, { report_format: string[] }>(`/cicd/runs/${cicdRunId}/generate-report`, {
    report_format: ['json'],
  });
}
