import { apiClient } from './client';

export interface AutomationDraftCreateRequest {
  readonly project_id: string;
  readonly test_case_id: string | null;
  readonly requirement_id: string | null;
  readonly target_framework: string;
  readonly prompt_version: string;
  readonly skill_version: string;
  readonly model_provider: string;
  readonly model_name: string;
}

export interface AutomationDraftCreateRead {
  readonly automation_draft_id: string;
  readonly ai_task_id: string;
  readonly status: string;
}

export interface AutomationDraftRead {
  readonly id: string;
  readonly project_id: string;
  readonly test_case_id: string | null;
  readonly requirement_id: string | null;
  readonly ai_task_id: string;
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

export async function createAutomationDraft(data: AutomationDraftCreateRequest): Promise<AutomationDraftCreateRead> {
  return apiClient.postJson<AutomationDraftCreateRead, AutomationDraftCreateRequest>('/automation/drafts', data);
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
