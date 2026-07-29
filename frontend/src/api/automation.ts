import { apiClient } from './client';

export interface AutomationDraftCreateRequest {
  readonly project_id: string;
  readonly test_case_id: string | null;
  readonly requirement_id: string | null;
  readonly automation_plan_id?: string | null;
  readonly target_framework: string;
  readonly prompt_version: string;
  readonly skill_version: string;
  readonly model_provider?: string | null;
  readonly model_name?: string | null;
}

export interface AutomationPlanCreateRequest {
  readonly project_id: string;
  readonly test_case_id: string;
  readonly target_framework: string;
  readonly use_knowledge: boolean;
  readonly context_artifact_ids: string[];
  readonly prompt_version: string;
  readonly skill_version: string;
  readonly model_provider?: string | null;
  readonly model_name?: string | null;
}

export interface AutomationPlanRead {
  readonly id: string;
  readonly project_id: string;
  readonly test_case_id: string;
  readonly requirement_id: string | null;
  readonly requirement_review_id: string | null;
  readonly source_candidate_id: string | null;
  readonly ai_task_id: string;
  readonly knowledge_retrieval_artifact_id: string | null;
  readonly target_framework: string;
  readonly title: string;
  readonly plan: Record<string, unknown>;
  readonly execution_steps: string[];
  readonly test_data: Record<string, unknown>;
  readonly dependency_notes: string | null;
  readonly risk_notes: string | null;
  readonly used_context_artifact_ids: string[];
  readonly status: string;
  readonly review_comment: string | null;
}

export interface AutomationPlanReviewRead {
  readonly automation_plan_id: string;
  readonly status: string;
}

export interface AutomationPlanReviewWorkflowActionRequest {
  readonly expected_version: number;
  readonly reviewer?: string;
  readonly comment?: string | null;
}

export interface AutomationPlanReviewWorkflowEditRequest extends AutomationPlanReviewWorkflowActionRequest {
  readonly plan_decisions: Record<string, unknown>[];
}

export interface AutomationPlanReviewWorkflowContinueRequest {
  readonly expected_version: number;
  readonly approval_decision_id: string;
}

export interface AutomationPlanReviewWorkflowRead {
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
  readonly source_case_review_snapshot_id: string | null;
  readonly source_case_review_snapshot_hash: string | null;
  readonly source_test_plan_review_snapshot_id: string | null;
  readonly source_test_plan_review_snapshot_hash: string | null;
  readonly approved_candidate_ids: string[];
  readonly approved_test_case_ids: string[];
  readonly generated_plan_ids: string[];
  readonly plan_decisions: Record<string, unknown>[];
}

export interface AutomationDraftCreateRead {
  readonly automation_draft_id: string;
  readonly ai_task_id: string;
  readonly status: string;
}

export interface AutomationDraftQualityGateRead {
  readonly status: string;
  readonly execution_evidence_level: string;
  readonly approval_blocking_reasons: string[];
  readonly evidence_warnings: string[];
}

export interface AutomationDraftRead {
  readonly id: string;
  readonly project_id: string;
  readonly test_case_id: string | null;
  readonly requirement_id: string | null;
  readonly ai_task_id: string;
  readonly automation_plan_id: string | null;
  readonly target_framework: string;
  readonly title: string;
  readonly draft_code: string;
  readonly draft_language: string;
  readonly suggested_file_path: string | null;
  readonly execution_notes: string | null;
  readonly risk_notes: string | null;
  readonly execution_strategy: string;
  readonly approval_required: boolean;
  readonly status: string;
  readonly review_comment: string | null;
  readonly runtime_artifact_id: string | null;
  readonly promoted_artifact_id: string | null;
  readonly quality_gate?: AutomationDraftQualityGateRead;
}

export interface AutomationDraftEditRequest {
  readonly draft_code: string;
  readonly suggested_file_path: string | null;
  readonly execution_notes: string | null;
  readonly risk_notes: string | null;
  readonly review_comment: string | null;
}

export interface AutomationDraftReviewRead {
  readonly automation_draft_id: string;
  readonly status: string;
}

export interface AutomationDraftReviewWorkflowActionRequest {
  readonly expected_version: number;
  readonly reviewer?: string;
  readonly comment?: string | null;
}

export interface AutomationDraftReviewWorkflowEditRequest extends AutomationDraftReviewWorkflowActionRequest {
  readonly draft_decisions: Record<string, unknown>[];
}

export interface AutomationDraftReviewWorkflowContinueRequest {
  readonly expected_version: number;
  readonly approval_decision_id: string;
}

export interface AutomationDraftReviewWorkflowRead {
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
  readonly source_automation_plan_review_snapshot_id: string | null;
  readonly source_automation_plan_review_snapshot_hash: string | null;
  readonly source_case_review_snapshot_id: string | null;
  readonly source_case_review_snapshot_hash: string | null;
  readonly approved_automation_plan_ids: string[];
  readonly approved_test_case_ids: string[];
  readonly generated_draft_ids: string[];
  readonly draft_decisions: Record<string, unknown>[];
}

export async function createAutomationDraft(data: AutomationDraftCreateRequest): Promise<AutomationDraftCreateRead> {
  return apiClient.postJson<AutomationDraftCreateRead, AutomationDraftCreateRequest>('/automation/drafts', data);
}

export async function createAutomationPlan(data: AutomationPlanCreateRequest): Promise<AutomationPlanRead> {
  return apiClient.postJson<AutomationPlanRead, AutomationPlanCreateRequest>('/automation/plans', data);
}

export async function getAutomationPlan(planId: string): Promise<AutomationPlanRead> {
  return apiClient.getJson<AutomationPlanRead>(`/automation/plans/${planId}`);
}

export async function approveAutomationPlan(planId: string, reviewComment: string): Promise<AutomationPlanReviewRead> {
  return apiClient.postJson<AutomationPlanReviewRead, { action: 'approve'; review_comment: string }>(
    `/automation/plans/${planId}/approve`,
    { action: 'approve', review_comment: reviewComment },
  );
}

export async function generateAutomationDraftFromPlan(planId: string): Promise<AutomationDraftCreateRead> {
  return apiClient.postJson<AutomationDraftCreateRead, Record<string, never>>(
    `/automation/plans/${planId}/generate-draft`,
    {},
  );
}

export async function getAutomationPlanReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
): Promise<AutomationPlanReviewWorkflowRead> {
  return apiClient.getJson<AutomationPlanReviewWorkflowRead>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-plan-review`,
  );
}

export async function submitAutomationPlanReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationPlanReviewWorkflowActionRequest,
): Promise<AutomationPlanReviewWorkflowRead> {
  return apiClient.postJson<AutomationPlanReviewWorkflowRead, AutomationPlanReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-plan-review/submit`,
    data,
  );
}

export async function completeAutomationPlanReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationPlanReviewWorkflowActionRequest,
): Promise<AutomationPlanReviewWorkflowRead> {
  return apiClient.postJson<AutomationPlanReviewWorkflowRead, AutomationPlanReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-plan-review/complete-review`,
    data,
  );
}

export async function editAutomationPlanReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationPlanReviewWorkflowEditRequest,
): Promise<AutomationPlanReviewWorkflowRead> {
  return apiClient.postJson<AutomationPlanReviewWorkflowRead, AutomationPlanReviewWorkflowEditRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-plan-review/edit`,
    data,
  );
}

export async function approveAutomationPlanReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationPlanReviewWorkflowActionRequest,
): Promise<AutomationPlanReviewWorkflowRead> {
  return apiClient.postJson<AutomationPlanReviewWorkflowRead, AutomationPlanReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-plan-review/approve`,
    data,
  );
}

export async function rejectAutomationPlanReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationPlanReviewWorkflowActionRequest,
): Promise<AutomationPlanReviewWorkflowRead> {
  return apiClient.postJson<AutomationPlanReviewWorkflowRead, AutomationPlanReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-plan-review/reject`,
    data,
  );
}

export async function continueAutomationPlanReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationPlanReviewWorkflowContinueRequest,
): Promise<AutomationPlanReviewWorkflowRead> {
  return apiClient.postJson<AutomationPlanReviewWorkflowRead, AutomationPlanReviewWorkflowContinueRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-plan-review/continue`,
    data,
  );
}

export async function approveAndContinueAutomationPlanReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationPlanReviewWorkflowActionRequest,
): Promise<AutomationPlanReviewWorkflowRead> {
  return apiClient.postJson<AutomationPlanReviewWorkflowRead, AutomationPlanReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-plan-review/approve-and-continue`,
    data,
  );
}

export async function getAutomationDraft(draftId: string): Promise<AutomationDraftRead> {
  return apiClient.getJson<AutomationDraftRead>(`/automation/drafts/${draftId}`);
}

export async function editAutomationDraft(
  draftId: string,
  data: AutomationDraftEditRequest,
): Promise<AutomationDraftReviewRead> {
  return apiClient.patchJson<AutomationDraftReviewRead, AutomationDraftEditRequest>(`/automation/drafts/${draftId}`, data);
}

export async function approveAutomationDraft(draftId: string, reviewComment: string): Promise<AutomationDraftReviewRead> {
  return apiClient.postJson<AutomationDraftReviewRead, { action: 'approve'; review_comment: string }>(
    `/automation/drafts/${draftId}/approve`,
    { action: 'approve', review_comment: reviewComment },
  );
}

export async function getAutomationDraftReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
): Promise<AutomationDraftReviewWorkflowRead> {
  return apiClient.getJson<AutomationDraftReviewWorkflowRead>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-draft-review`,
  );
}

export async function submitAutomationDraftReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationDraftReviewWorkflowActionRequest,
): Promise<AutomationDraftReviewWorkflowRead> {
  return apiClient.postJson<AutomationDraftReviewWorkflowRead, AutomationDraftReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-draft-review/submit`,
    data,
  );
}

export async function completeAutomationDraftReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationDraftReviewWorkflowActionRequest,
): Promise<AutomationDraftReviewWorkflowRead> {
  return apiClient.postJson<AutomationDraftReviewWorkflowRead, AutomationDraftReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-draft-review/complete-review`,
    data,
  );
}

export async function editAutomationDraftReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationDraftReviewWorkflowEditRequest,
): Promise<AutomationDraftReviewWorkflowRead> {
  return apiClient.postJson<AutomationDraftReviewWorkflowRead, AutomationDraftReviewWorkflowEditRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-draft-review/edit`,
    data,
  );
}

export async function approveAutomationDraftReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationDraftReviewWorkflowActionRequest,
): Promise<AutomationDraftReviewWorkflowRead> {
  return apiClient.postJson<AutomationDraftReviewWorkflowRead, AutomationDraftReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-draft-review/approve`,
    data,
  );
}

export async function rejectAutomationDraftReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationDraftReviewWorkflowActionRequest,
): Promise<AutomationDraftReviewWorkflowRead> {
  return apiClient.postJson<AutomationDraftReviewWorkflowRead, AutomationDraftReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-draft-review/reject`,
    data,
  );
}

export async function continueAutomationDraftReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationDraftReviewWorkflowContinueRequest,
): Promise<AutomationDraftReviewWorkflowRead> {
  return apiClient.postJson<AutomationDraftReviewWorkflowRead, AutomationDraftReviewWorkflowContinueRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-draft-review/continue`,
    data,
  );
}

export async function approveAndContinueAutomationDraftReviewWorkflow(
  projectId: string,
  requirementReviewId: string,
  data: AutomationDraftReviewWorkflowActionRequest,
): Promise<AutomationDraftReviewWorkflowRead> {
  return apiClient.postJson<AutomationDraftReviewWorkflowRead, AutomationDraftReviewWorkflowActionRequest>(
    `/projects/${projectId}/requirement-reviews/${requirementReviewId}/automation-draft-review/approve-and-continue`,
    data,
  );
}
