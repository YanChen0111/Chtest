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
