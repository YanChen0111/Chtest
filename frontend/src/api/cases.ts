import { apiClient } from './client';

export interface CaseGenerationStartRequest {
  readonly project_id: string;
  readonly requirement_id: string;
  readonly requirement_review_id?: string | null;
  readonly requirement_document_artifact_id?: string | null;
  readonly target_test_types: string[];
  readonly prompt_version: 'case_generation:v1' | 'case_generation:v2';
  readonly skill_version: 'test-case-generation-skill:v1' | 'test-case-generation-skill:v2';
  readonly model_provider?: string | null;
  readonly model_name?: string | null;
  readonly use_knowledge: boolean;
  readonly context_artifact_ids: string[];
  readonly decision_table_acknowledged?: boolean;
}

export interface CaseGenerationStartRead {
  readonly case_generation_task_id: string;
  readonly ai_task_id: string;
  readonly status: string;
  readonly used_knowledge: boolean;
  readonly used_context_artifact_ids: string[];
}

export interface CaseGenerationTaskRead {
  readonly id: string;
  readonly project_id: string;
  readonly requirement_id: string;
  readonly requirement_review_id: string | null;
  readonly ai_task_id: string;
  readonly target_test_types: string[];
  readonly status: string;
  readonly generated_count: number;
  readonly ai_task_status: string | null;
  readonly error_code: string | null;
  readonly error_message: string | null;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface GeneratedCaseCandidateListItem {
  readonly id: string;
  readonly title: string;
  readonly priority: string;
  readonly test_type: string;
  readonly precondition: string | null;
  readonly steps: string[];
  readonly expected_results: string[];
  readonly input_data: Record<string, unknown>;
  readonly requirement_refs: string[];
  readonly risk_refs: string[];
  readonly source_knowledge_evidence: Record<string, unknown>[];
  readonly coverage_dimensions: CaseCoverageDimension[];
  readonly ai_reason: string;
  readonly status: string;
}

export interface CaseCoverageDimension {
  readonly key: string;
  readonly label: string;
  readonly evidence?: string;
  readonly source?: string;
}

export interface GeneratedCaseCandidateListRead {
  readonly items: GeneratedCaseCandidateListItem[];
  readonly total: number;
}

export interface CaseMetricsRead {
  readonly generation_task_id: string;
  readonly generated_count: number;
  readonly approved_count: number;
  readonly edited_count: number;
  readonly rejected_count: number;
  readonly optimization_count: number;
  readonly reviewed_count: number;
  readonly acceptance_rate: number;
  readonly edit_rate: number;
  readonly rejection_rate: number;
  readonly optimization_rate: number;
  readonly review_progress: number;
  readonly field_complete_rate: number;
}

export interface TestCaseListItem {
  readonly id: string;
  readonly project_id: string;
  readonly module_id: string | null;
  readonly source_candidate_id: string | null;
  readonly title: string;
  readonly priority: string;
  readonly test_type: string;
  readonly precondition: string | null;
  readonly steps: string[];
  readonly expected_results: string[];
  readonly input_data: Record<string, unknown>;
  readonly tags: string[];
  readonly source_type: string;
  readonly review_status: string;
  readonly status: string;
}

export interface TestCaseListRead {
  readonly items: TestCaseListItem[];
  readonly total: number;
}

export interface TestCaseImportItem {
  readonly title: string;
  readonly priority?: string;
  readonly test_type?: string;
  readonly precondition?: string | null;
  readonly steps?: string[];
  readonly expected_results?: string[];
  readonly input_data?: Record<string, unknown>;
  readonly tags?: string[];
}

export interface TestCaseImportRead {
  readonly project_id: string;
  readonly imported_count: number;
  readonly skipped_count: number;
  readonly items: TestCaseListItem[];
}

export type CaseReviewAction = 'approve' | 'approve_after_edit' | 'reject' | 'needs_optimization';

export interface CaseReviewEditedCase {
  readonly title: string;
  readonly priority: string;
  readonly test_type: string;
  readonly precondition: string | null;
  readonly steps: string[];
  readonly expected_results: string[];
  readonly input_data: Record<string, unknown>;
  readonly tags: string[];
}

export interface CaseReviewRequest {
  readonly action: CaseReviewAction;
  readonly edited_case?: CaseReviewEditedCase;
  readonly review_comment?: string | null;
}

export interface CaseReviewRead {
  readonly candidate_id: string;
  readonly status: string;
  readonly test_case_id: string | null;
}

export interface CaseReviewWorkflowActionRequest {
  readonly expected_version: number;
  readonly reviewer?: string;
  readonly comment?: string | null;
}

export interface CaseReviewWorkflowEditRequest extends CaseReviewWorkflowActionRequest {
  readonly candidate_decisions: Record<string, unknown>[];
}

export interface CaseReviewWorkflowContinueRequest {
  readonly expected_version: number;
  readonly approval_decision_id: string;
}

export interface CaseReviewWorkflowRead {
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
  readonly source_test_plan_review_snapshot_id: string | null;
  readonly source_test_plan_review_snapshot_hash: string | null;
  readonly source_case_review_snapshot_id?: string | null;
  readonly source_case_review_snapshot_hash?: string | null;
  readonly test_strategy: string | null;
  readonly plan_items: Record<string, unknown>[];
  readonly generated_candidate_ids: string[];
  readonly approved_candidate_ids?: string[];
  readonly approved_test_case_ids?: string[];
  readonly candidate_decisions: Record<string, unknown>[];
}

export async function startCaseGeneration(data: CaseGenerationStartRequest): Promise<CaseGenerationStartRead> {
  return apiClient.postJson<CaseGenerationStartRead, CaseGenerationStartRequest>('/case-generation/tasks', data);
}

export async function getCaseGenerationTask(generationTaskId: string): Promise<CaseGenerationTaskRead> {
  return apiClient.getJson<CaseGenerationTaskRead>(`/case-generation/tasks/${generationTaskId}`);
}

export async function listCaseCandidates(generationTaskId: string): Promise<GeneratedCaseCandidateListRead> {
  return apiClient.getJson<GeneratedCaseCandidateListRead>(`/case-generation/tasks/${generationTaskId}/candidates`);
}

export async function getCaseMetrics(generationTaskId: string): Promise<CaseMetricsRead> {
  return apiClient.getJson<CaseMetricsRead>(`/case-generation/tasks/${generationTaskId}/metrics`);
}

export async function listTestCases(projectId: string): Promise<TestCaseListRead> {
  return apiClient.getJson<TestCaseListRead>(`/test-cases?project_id=${projectId}`);
}

export async function importTestCases(projectId: string, items: TestCaseImportItem[]): Promise<TestCaseImportRead> {
  return apiClient.postJson<TestCaseImportRead, { project_id: string; items: TestCaseImportItem[] }>(
    '/test-cases/import',
    { project_id: projectId, items },
  );
}

export async function updateTestCaseStatus(
  projectId: string,
  caseId: string,
  status: 'active' | 'archived',
): Promise<{ id: string; status: string }> {
  return apiClient.patchJson<{ id: string; status: string }, { project_id: string; status: 'active' | 'archived' }>(
    `/test-cases/${caseId}`,
    { project_id: projectId, status },
  );
}

export async function reviewCaseCandidate(candidateId: string, data: CaseReviewRequest): Promise<CaseReviewRead> {
  return apiClient.postJson<CaseReviewRead, CaseReviewRequest>(`/case-review/items/${candidateId}/approve`, data);
}

export async function getCaseReviewWorkflow(projectId: string, requirementReviewId: string): Promise<CaseReviewWorkflowRead> {
  return apiClient.getJson<CaseReviewWorkflowRead>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/case-review`,
  );
}

export async function submitCaseReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: CaseReviewWorkflowActionRequest,
): Promise<CaseReviewWorkflowRead> {
  return apiClient.postJson<CaseReviewWorkflowRead, CaseReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/case-review/submit`,
    data,
  );
}

export async function completeCaseReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: CaseReviewWorkflowActionRequest,
): Promise<CaseReviewWorkflowRead> {
  return apiClient.postJson<CaseReviewWorkflowRead, CaseReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/case-review/complete-review`,
    data,
  );
}

export async function editCaseReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: CaseReviewWorkflowEditRequest,
): Promise<CaseReviewWorkflowRead> {
  return apiClient.postJson<CaseReviewWorkflowRead, CaseReviewWorkflowEditRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/case-review/edit`,
    data,
  );
}

export async function approveCaseReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: CaseReviewWorkflowActionRequest,
): Promise<CaseReviewWorkflowRead> {
  return apiClient.postJson<CaseReviewWorkflowRead, CaseReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/case-review/approve`,
    data,
  );
}

export async function rejectCaseReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: CaseReviewWorkflowActionRequest,
): Promise<CaseReviewWorkflowRead> {
  return apiClient.postJson<CaseReviewWorkflowRead, CaseReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/case-review/reject`,
    data,
  );
}

export async function continueCaseReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: CaseReviewWorkflowContinueRequest,
): Promise<CaseReviewWorkflowRead> {
  return apiClient.postJson<CaseReviewWorkflowRead, CaseReviewWorkflowContinueRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/case-review/continue`,
    data,
  );
}

export async function approveAndContinueCaseReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: CaseReviewWorkflowActionRequest,
): Promise<CaseReviewWorkflowRead> {
  return apiClient.postJson<CaseReviewWorkflowRead, CaseReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/case-review/approve-and-continue`,
    data,
  );
}
