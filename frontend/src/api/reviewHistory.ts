import { apiClient } from './client';

export interface ReviewHistoryItem {
  readonly id: string;
  readonly project_id: string;
  readonly entity_type: string;
  readonly entity_id: string;
  readonly related_entity_type: string | null;
  readonly related_entity_id: string | null;
  readonly action: string;
  readonly from_status: string | null;
  readonly to_status: string | null;
  readonly reviewer: string;
  readonly comment: string | null;
  readonly evidence_artifact_ids: string[];
  readonly metadata_json: Record<string, unknown>;
  readonly created_at: string;
}

export interface ReviewHistoryListRead {
  readonly items: ReviewHistoryItem[];
  readonly total: number;
}

export interface ReviewHistoryQuery {
  readonly projectId: string;
  readonly entityType?: string;
  readonly entityId?: string;
  readonly relatedEntityType?: string;
  readonly relatedEntityId?: string;
  readonly limit?: number;
}

export async function listReviewHistory(query: ReviewHistoryQuery): Promise<ReviewHistoryListRead> {
  const params = new URLSearchParams({ project_id: query.projectId });
  if (query.entityType && query.entityId) {
    params.set('entity_type', query.entityType);
    params.set('entity_id', query.entityId);
  }
  if (query.relatedEntityType && query.relatedEntityId) {
    params.set('related_entity_type', query.relatedEntityType);
    params.set('related_entity_id', query.relatedEntityId);
  }
  if (query.limit) {
    params.set('limit', String(query.limit));
  }
  return apiClient.getJson<ReviewHistoryListRead>(`/review-history?${params.toString()}`);
}
