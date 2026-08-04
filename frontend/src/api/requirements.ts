import { apiClient } from './client';

export interface RequirementCreateRequest {
  readonly project_id: string;
  readonly module_id?: string | null;
  readonly title: string;
  readonly content: string;
  readonly source_type?: string;
  readonly source_ref?: string | null;
}

export interface RequirementRead {
  readonly id: string;
  readonly project_id: string;
  readonly module_id: string | null;
  readonly title: string;
  readonly content: string;
  readonly source_type: string;
  readonly source_ref: string | null;
  readonly status: string;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface RequirementListRead {
  readonly items: RequirementRead[];
  readonly total: number;
}

export interface RequirementReviewStartRequest {
  readonly prompt_version: 'requirement_review:v1';
  readonly skill_version: 'requirement-review-skill:v1';
  readonly model_provider?: string | null;
  readonly model_name?: string | null;
  readonly use_knowledge: boolean;
  readonly context_artifact_ids: string[];
  readonly supplement_text?: string | null;
  readonly clarification_answers?: ClarificationAnswer[];
}

export interface RequirementReviewStartRead {
  readonly ai_task_id: string;
  readonly requirement_id: string;
  readonly status: string;
  readonly next_poll_url: string;
  readonly used_knowledge: boolean;
  readonly used_context_artifact_ids: string[];
}

export interface RequirementReviewIssue {
  readonly type: string;
  readonly text: string;
  readonly severity: string;
}

export interface RequirementRiskItem {
  readonly id?: string;
  readonly title: string;
  readonly risk_level: string;
  readonly category?: string;
  readonly impact?: string;
  readonly suggestion: string;
  readonly status?: string;
}

export interface RequirementReviewRead {
  readonly id: string;
  readonly requirement_id: string;
  readonly overall_score: number;
  readonly scores: {
    readonly completeness: number;
    readonly clarity: number;
    readonly consistency: number;
    readonly testability: number;
    readonly feasibility: number;
    readonly logic: number;
  };
  readonly issues: RequirementReviewIssue[];
  readonly clarification_questions: string[];
  readonly test_design_notes: unknown[];
  readonly test_plan_strategy?: string | null;
  readonly test_plan_items?: TestPlanItem[];
  readonly risk_items: RequirementRiskItem[];
  readonly used_knowledge: boolean;
  readonly used_context_artifact_ids: string[];
  readonly context_manifest_artifact_id: string | null;
  readonly status: string;
  readonly workflow: RequirementWorkflow | null;
}

export interface RequirementWorkflow {
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
}

export interface RequirementWorkflowActionRequest {
  readonly expected_version: number;
  readonly reviewer?: string;
  readonly comment?: string | null;
}

export interface RequirementWorkflowEditRequest extends RequirementWorkflowActionRequest {
  readonly issues: RequirementReviewIssue[];
  readonly clarification_questions: string[];
  readonly test_design_notes: unknown[];
  readonly risk_items: RequirementRiskItem[];
}

export interface RiskReviewEditRequest extends RequirementWorkflowActionRequest {
  readonly risk_items: RequirementRiskItem[];
}

export interface TestPlanItem {
  readonly risk_title?: string;
  readonly risk_level?: string;
  readonly strategy?: string;
  readonly included?: boolean;
}

export interface TestPlanReviewEditRequest extends RequirementWorkflowActionRequest {
  readonly test_strategy?: string | null;
  readonly plan_items: TestPlanItem[];
}

export interface ClarificationAnswer {
  readonly question: string;
  readonly answer: string;
}

export interface RequirementDocumentCreateRequest {
  readonly requirement_review_id: string;
  readonly version?: string;
  readonly status?: 'draft' | 'confirmed';
}

export interface RequirementDocumentRead {
  readonly id: string;
  readonly project_id: string;
  readonly requirement_id: string;
  readonly requirement_review_id: string;
  readonly document_number: string;
  readonly version: string;
  readonly title: string;
  readonly status: string;
  readonly artifact_id: string;
  readonly download_url: string;
  readonly created_at: string;
}

export interface RequirementDocumentListRead {
  readonly items: RequirementDocumentRead[];
  readonly total: number;
}

export async function createRequirement(data: RequirementCreateRequest): Promise<RequirementRead> {
  return apiClient.postJson<RequirementRead, RequirementCreateRequest>('/requirements', data);
}

export async function listRequirements(projectId: string): Promise<RequirementListRead> {
  return apiClient.getJson<RequirementListRead>(`/projects/${projectId}/requirements`);
}

export async function getRequirement(requirementId: string): Promise<RequirementRead> {
  return apiClient.getJson<RequirementRead>(`/requirements/${requirementId}`);
}

export async function startRequirementReview(
  requirementId: string,
  data: RequirementReviewStartRequest,
): Promise<RequirementReviewStartRead> {
  return apiClient.postJson<RequirementReviewStartRead, RequirementReviewStartRequest>(
    `/requirements/${requirementId}/review`,
    data,
  );
}

export async function getRequirementReview(requirementId: string): Promise<RequirementReviewRead> {
  return apiClient.getJson<RequirementReviewRead>(`/requirements/${requirementId}/review`);
}

export async function completeRequirementReview(projectId: string, reviewId: string, data: RequirementWorkflowActionRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/complete-review`, data,
  );
}

export async function editRequirementReview(projectId: string, reviewId: string, data: RequirementWorkflowEditRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowEditRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/edit`, data,
  );
}

export async function approveRequirementReview(projectId: string, reviewId: string, data: RequirementWorkflowActionRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/approve`, data,
  );
}

export async function rejectRequirementReview(projectId: string, reviewId: string, data: RequirementWorkflowActionRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/reject`, data,
  );
}

export async function continueRequirementReview(projectId: string, reviewId: string, expectedVersion: number, approvalDecisionId: string): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, { expected_version: number; approval_decision_id: string }>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/continue`,
    { expected_version: expectedVersion, approval_decision_id: approvalDecisionId },
  );
}

export async function getRiskReview(projectId: string, reviewId: string): Promise<RequirementReviewRead> {
  return apiClient.getJson<RequirementReviewRead>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/risk-review`,
  );
}

export async function submitRiskReview(projectId: string, reviewId: string, data: RequirementWorkflowActionRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/risk-review/submit`, data,
  );
}

export async function completeRiskReview(projectId: string, reviewId: string, data: RequirementWorkflowActionRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/risk-review/complete-review`, data,
  );
}

export async function editRiskReview(projectId: string, reviewId: string, data: RiskReviewEditRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RiskReviewEditRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/risk-review/edit`, data,
  );
}

export async function approveRiskReview(projectId: string, reviewId: string, data: RequirementWorkflowActionRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/risk-review/approve`, data,
  );
}

export async function rejectRiskReview(projectId: string, reviewId: string, data: RequirementWorkflowActionRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/risk-review/reject`, data,
  );
}

export async function continueRiskReview(projectId: string, reviewId: string, expectedVersion: number, approvalDecisionId: string): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, { expected_version: number; approval_decision_id: string }>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/risk-review/continue`,
    { expected_version: expectedVersion, approval_decision_id: approvalDecisionId },
  );
}

export async function getTestPlanReview(projectId: string, reviewId: string): Promise<RequirementReviewRead> {
  return apiClient.getJson<RequirementReviewRead>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/test-plan-review`,
  );
}

export async function submitTestPlanReview(projectId: string, reviewId: string, data: RequirementWorkflowActionRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/test-plan-review/submit`, data,
  );
}

export async function completeTestPlanReview(projectId: string, reviewId: string, data: RequirementWorkflowActionRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/test-plan-review/complete-review`, data,
  );
}

export async function editTestPlanReview(projectId: string, reviewId: string, data: TestPlanReviewEditRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, TestPlanReviewEditRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/test-plan-review/edit`, data,
  );
}

export async function approveTestPlanReview(projectId: string, reviewId: string, data: RequirementWorkflowActionRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/test-plan-review/approve`, data,
  );
}

export async function rejectTestPlanReview(projectId: string, reviewId: string, data: RequirementWorkflowActionRequest): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, RequirementWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/test-plan-review/reject`, data,
  );
}

export async function continueTestPlanReview(projectId: string, reviewId: string, expectedVersion: number, approvalDecisionId: string): Promise<RequirementReviewRead> {
  return apiClient.postJson<RequirementReviewRead, { expected_version: number; approval_decision_id: string }>(
    `/projects/${projectId}/requirement-reviews/${reviewId}/test-plan-review/continue`,
    { expected_version: expectedVersion, approval_decision_id: approvalDecisionId },
  );
}

export async function createRequirementDocument(
  requirementId: string,
  data: RequirementDocumentCreateRequest,
): Promise<RequirementDocumentRead> {
  return apiClient.postJson<RequirementDocumentRead, RequirementDocumentCreateRequest>(
    `/requirements/${requirementId}/documents`,
    data,
  );
}

export async function listRequirementDocuments(projectId: string): Promise<RequirementDocumentListRead> {
  return apiClient.getJson<RequirementDocumentListRead>(`/projects/${projectId}/requirement-documents`);
}
