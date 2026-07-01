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

export interface RequirementReviewStartRequest {
  readonly prompt_version: 'requirement_review:v1';
  readonly skill_version: 'requirement-review-skill:v1';
  readonly model_provider: 'mock';
  readonly model_name: 'mock-requirement-review';
  readonly use_knowledge: boolean;
  readonly context_artifact_ids: string[];
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
  readonly title: string;
  readonly risk_level: string;
  readonly suggestion: string;
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
  readonly risk_items: RequirementRiskItem[];
  readonly used_knowledge: boolean;
  readonly used_context_artifact_ids: string[];
  readonly context_manifest_artifact_id: string | null;
  readonly status: string;
}

export async function createRequirement(data: RequirementCreateRequest): Promise<RequirementRead> {
  return apiClient.postJson<RequirementRead, RequirementCreateRequest>('/requirements', data);
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
