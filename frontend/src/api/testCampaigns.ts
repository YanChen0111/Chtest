import { apiClient } from './client';

export type CampaignCoverageKind = 'requirement' | 'risk' | 'test_plan' | 'approved_case';
export type CampaignCoverageStatus = 'covered' | 'gap';

export interface CampaignCoverageRow {
  readonly kind: CampaignCoverageKind;
  readonly target_id: string;
  readonly label: string;
  readonly coverage_status: CampaignCoverageStatus;
  readonly evidence_case_ids: string[];
  readonly evidence_snapshot_id: string | null;
  readonly gap_reason: string | null;
}

export interface TestCampaignWorkflowRead {
  readonly run_id: string;
  readonly stage: string;
  readonly state: string;
  readonly lock_version: number;
  readonly snapshot_id: string;
  readonly snapshot_hash: string;
  readonly snapshot_iteration: number;
  readonly approval_decision_id: string | null;
  readonly can_continue: boolean;
}

export interface TestCampaignRead {
  readonly id: string;
  readonly project_id: string;
  readonly name: string;
  readonly scope_statement: string;
  readonly target_environment_id: string;
  readonly target_version_ref: string;
  readonly exit_conditions: string[];
  readonly requirement_ids: string[];
  readonly risk_ids: string[];
  readonly test_plan_snapshot_ids: string[];
  readonly approved_case_ids: string[];
  readonly coverage_rows: CampaignCoverageRow[];
  readonly status: string;
  readonly workflow: TestCampaignWorkflowRead;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface TestCampaignScopeInput {
  readonly name: string;
  readonly scope_statement: string;
  readonly target_environment_id: string;
  readonly target_version_ref: string;
  readonly exit_conditions: string[];
  readonly requirement_ids: string[];
  readonly risk_ids: string[];
  readonly test_plan_snapshot_ids: string[];
  readonly approved_case_ids: string[];
}

export interface TestCampaignActionInput {
  readonly expected_version: number;
  readonly reviewer?: string;
  readonly comment?: string | null;
}

export async function listTestCampaigns(projectId: string): Promise<TestCampaignRead[]> {
  return apiClient.getJson<TestCampaignRead[]>(`/projects/${projectId}/test-campaigns`);
}

export async function getTestCampaign(projectId: string, campaignId: string): Promise<TestCampaignRead> {
  return apiClient.getJson<TestCampaignRead>(`/projects/${projectId}/test-campaigns/${campaignId}`);
}

export async function createTestCampaign(
  projectId: string,
  input: TestCampaignScopeInput & { readonly created_by?: string },
): Promise<TestCampaignRead> {
  return apiClient.postJson<TestCampaignRead, typeof input>(`/projects/${projectId}/test-campaigns`, input);
}

export async function editTestCampaign(
  projectId: string,
  campaignId: string,
  input: TestCampaignScopeInput & TestCampaignActionInput,
): Promise<TestCampaignRead> {
  return apiClient.postJson<TestCampaignRead, typeof input>(
    `/projects/${projectId}/test-campaigns/${campaignId}/edit`,
    input,
  );
}

export async function submitTestCampaign(
  projectId: string,
  campaignId: string,
  input: TestCampaignActionInput,
): Promise<TestCampaignRead> {
  return campaignAction(projectId, campaignId, 'submit', input);
}

export async function completeTestCampaignReview(
  projectId: string,
  campaignId: string,
  input: TestCampaignActionInput,
): Promise<TestCampaignRead> {
  return campaignAction(projectId, campaignId, 'complete-review', input);
}

export async function approveTestCampaign(
  projectId: string,
  campaignId: string,
  input: TestCampaignActionInput,
): Promise<TestCampaignRead> {
  return campaignAction(projectId, campaignId, 'approve', input);
}

export async function rejectTestCampaign(
  projectId: string,
  campaignId: string,
  input: TestCampaignActionInput,
): Promise<TestCampaignRead> {
  return campaignAction(projectId, campaignId, 'reject', input);
}

export async function continueTestCampaign(
  projectId: string,
  campaignId: string,
  expectedVersion: number,
  approvalDecisionId: string,
): Promise<TestCampaignRead> {
  return apiClient.postJson<TestCampaignRead, { expected_version: number; approval_decision_id: string }>(
    `/projects/${projectId}/test-campaigns/${campaignId}/continue`,
    { expected_version: expectedVersion, approval_decision_id: approvalDecisionId },
  );
}

function campaignAction(
  projectId: string,
  campaignId: string,
  action: 'submit' | 'complete-review' | 'approve' | 'reject',
  input: TestCampaignActionInput,
): Promise<TestCampaignRead> {
  return apiClient.postJson<TestCampaignRead, TestCampaignActionInput>(
    `/projects/${projectId}/test-campaigns/${campaignId}/${action}`,
    input,
  );
}
