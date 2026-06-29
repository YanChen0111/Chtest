import { apiClient } from './client';

export interface CaseGenerationStartRequest {
  readonly project_id: string;
  readonly requirement_id: string;
  readonly requirement_review_id?: string | null;
  readonly target_test_types: string[];
  readonly prompt_version: 'case_generation:v1';
  readonly skill_version: 'test-case-generation-skill:v1';
  readonly model_provider: 'mock';
  readonly model_name: 'mock-case-generator';
  readonly use_knowledge: boolean;
  readonly context_artifact_ids: string[];
}

export interface CaseGenerationStartRead {
  readonly case_generation_task_id: string;
  readonly ai_task_id: string;
  readonly status: string;
  readonly used_knowledge: boolean;
  readonly used_context_artifact_ids: string[];
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
  readonly ai_reason: string;
  readonly status: string;
}

export interface GeneratedCaseCandidateListRead {
  readonly items: GeneratedCaseCandidateListItem[];
  readonly total: number;
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

export async function startCaseGeneration(data: CaseGenerationStartRequest): Promise<CaseGenerationStartRead> {
  return apiClient.postJson<CaseGenerationStartRead, CaseGenerationStartRequest>('/case-generation/tasks', data);
}

export async function listCaseCandidates(generationTaskId: string): Promise<GeneratedCaseCandidateListRead> {
  return apiClient.getJson<GeneratedCaseCandidateListRead>(`/case-generation/tasks/${generationTaskId}/candidates`);
}

export async function reviewCaseCandidate(candidateId: string, data: CaseReviewRequest): Promise<CaseReviewRead> {
  return apiClient.postJson<CaseReviewRead, CaseReviewRequest>(`/case-review/items/${candidateId}/approve`, data);
}
