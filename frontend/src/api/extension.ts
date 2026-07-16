import { apiClient } from './client';

export interface KnowledgeAdapterRead {
  readonly project_id: string;
  readonly adapter_name: string;
  readonly status: string;
  readonly provider_type: string;
  readonly retrieval_mode?: string;
  readonly config: Record<string, unknown>;
  readonly safety_policy: Record<string, unknown>;
  readonly last_checked_at: string | null;
  readonly notes: string | null;
  readonly used_knowledge: boolean;
}

export interface KnowledgeBaseContextArtifactRead {
  readonly id: string;
  readonly title: string;
  readonly artifact_type: string;
  readonly mime_type: string;
  readonly source_ref: string;
  readonly safe_to_show: boolean;
  readonly redaction_applied: boolean;
  readonly allowed_for_prompt: boolean;
  readonly usage_count: number;
  readonly latest_used_at: string | null;
  readonly retrieved_count?: number;
  readonly latest_retrieved_at?: string | null;
}

export interface KnowledgeRetrievalResultRead {
  readonly context_artifact_id: string;
  readonly title: string;
  readonly source_ref: string;
  readonly score: number;
  readonly matched_terms: string[];
  readonly snippet: string;
  readonly sha256: string;
  readonly redaction_applied: boolean;
  readonly allowed_for_prompt: boolean;
}

export interface KnowledgeRetrievalSummaryRead {
  readonly ai_task_id: string;
  readonly retrieval_evidence_artifact_id: string;
  readonly query_terms: string[];
  readonly used_context_artifact_ids: string[];
  readonly snippet_count: number;
  readonly created_at: string;
  readonly results?: KnowledgeRetrievalResultRead[];
}

export interface KnowledgeBaseRead {
  readonly project_id: string;
  readonly knowledge_adapter: KnowledgeAdapterRead;
  readonly context_artifacts: KnowledgeBaseContextArtifactRead[];
  readonly latest_retrievals?: KnowledgeRetrievalSummaryRead[];
  readonly non_goals: string[];
}

export interface EvidenceTraceArtifactRefRead {
  readonly id: string;
  readonly artifact_type: string;
  readonly mime_type: string;
  readonly safe_to_show: boolean;
  readonly download_url: string;
}

export interface EvidenceTraceNodeRead {
  readonly stage: string;
  readonly entity_type: string;
  readonly entity_id: string;
  readonly status: string;
  readonly timestamp: string;
  readonly summary: string;
  readonly artifact_refs: EvidenceTraceArtifactRefRead[];
  readonly evidence_ids: string[];
  readonly source_locator: Record<string, unknown>;
  readonly provider_type?: string | null;
  readonly requested_retrieval_mode?: string | null;
  readonly retrieval_mode?: string | null;
  readonly degraded?: boolean | null;
  readonly fallback_reason?: string | null;
  readonly latency_ms?: number | null;
}

export interface EvidenceTraceStageRead {
  readonly name: string;
  readonly items: EvidenceTraceNodeRead[];
}

export interface EvidenceTraceRead {
  readonly project_id: string;
  readonly entity_type?: string | null;
  readonly entity_id?: string | null;
  readonly query?: string | null;
  readonly stages: EvidenceTraceStageRead[];
  readonly total: number;
}

export interface TestKnowledgeCardRead {
  readonly id: string;
  readonly project_id: string;
  readonly source_artifact_id: string;
  readonly source_document_version: string;
  readonly source_section: string | null;
  readonly source_quote_hash: string;
  readonly knowledge_type: string;
  readonly title: string;
  readonly content: string;
  readonly module_key: string | null;
  readonly api_endpoint: string | null;
  readonly risk_type: string | null;
  readonly case_type_hint: string | null;
  readonly applicability: string | null;
  readonly confidence: number;
  readonly safe_to_show: boolean;
  readonly allowed_for_prompt: boolean;
  readonly status: string;
  readonly created_at: string;
}

export interface TestKnowledgeCardListRead {
  readonly items: TestKnowledgeCardRead[];
  readonly total: number;
}

export interface TestKnowledgeCardExtractRequest {
  readonly project_id: string;
  readonly source_artifact_id: string;
}

export interface TestKnowledgeCardExtractRead {
  readonly source_artifact_id: string;
  readonly created_count: number;
  readonly skipped_count: number;
  readonly items: TestKnowledgeCardRead[];
}

export interface TestKnowledgeCardExtractBatchRequest {
  readonly project_id: string;
  readonly source_artifact_ids?: string[];
}

export interface TestKnowledgeCardExtractBatchRead {
  readonly project_id: string;
  readonly source_artifact_ids: string[];
  readonly created_count: number;
  readonly skipped_count: number;
  readonly items: TestKnowledgeCardRead[];
}

export interface TestKnowledgeCardReviewRequest {
  readonly project_id: string;
  readonly status: string;
}

export interface TestKnowledgeCardEvidenceRead {
  readonly evidence_id: string;
  readonly knowledge_card_id: string;
  readonly source_artifact_id: string;
  readonly knowledge_type: string;
  readonly title: string;
  readonly snippet: string;
  readonly score: number;
  readonly matched_terms: string[];
  readonly retrieval_reason: string;
  readonly safe_to_show: boolean;
  readonly allowed_for_prompt: boolean;
  readonly status: string;
  readonly semantic_score?: number;
  readonly embedding_model?: string;
}

export interface TestKnowledgeCardRetrievalRequest {
  readonly project_id: string;
  readonly query_text: string;
  readonly limit?: number;
  readonly approved_only?: boolean;
}

export interface TestKnowledgeCardRetrievalRead {
  readonly project_id: string;
  readonly query_text: string;
  readonly approved_only: boolean;
  readonly items: TestKnowledgeCardEvidenceRead[];
  readonly total: number;
}

export interface TestKnowledgeGraphRead {
  readonly project_id: string;
  readonly nodes: Record<string, unknown>[];
  readonly edges: Record<string, unknown>[];
  readonly coverage: Record<string, unknown>;
}

export interface TestKnowledgeIndexItemRead {
  readonly id: string;
  readonly project_id: string;
  readonly knowledge_card_id: string;
  readonly index_kind: string;
  readonly embedding_provider: string;
  readonly embedding_model: string;
  readonly embedding_dim: number;
  readonly content_hash: string;
  readonly status: string;
  readonly metadata: Record<string, unknown>;
  readonly created_at: string | null;
}

export interface TestKnowledgeIndexRead {
  readonly project_id: string;
  readonly total: number;
  readonly indexed_count: number;
  readonly embedding_models: string[];
  readonly items: TestKnowledgeIndexItemRead[];
}

export interface TestKnowledgeIndexRebuildRequest {
  readonly project_id: string;
  readonly knowledge_card_ids?: string[];
  readonly embedding_model?: string;
  readonly embedding_dim?: number;
}

export interface TestKnowledgeIndexRebuildRead {
  readonly project_id: string;
  readonly indexed_count: number;
  readonly skipped_count: number;
  readonly embedding_model: string;
  readonly embedding_dim: number;
  readonly items: TestKnowledgeIndexItemRead[];
}

export interface ContextArtifactCreateRequest {
  readonly project_id: string;
  readonly title: string;
  readonly artifact_type: 'context_markdown' | 'context_text' | 'context_pdf' | 'context_xlsx' | 'context_image';
  readonly mime_type: string;
  readonly content?: string;
  readonly content_base64?: string;
  readonly source_ref: string;
  readonly ocr_language?: string;
}

export interface ContextArtifactRead {
  readonly id: string;
  readonly project_id: string;
  readonly owner_entity_type: string;
  readonly owner_entity_id: string;
  readonly artifact_type: string;
  readonly file_path: string;
  readonly mime_type: string;
  readonly size_bytes: number;
  readonly sha256: string;
  readonly title: string;
  readonly source_ref: string;
  readonly safe_to_show: boolean;
  readonly redaction_applied: boolean;
  readonly allowed_for_prompt: boolean;
}

export interface KnowledgeAdapterUpdateRequest {
  readonly adapter_name: string;
  readonly status: 'not_configured' | 'disabled' | 'configured_stub';
  readonly provider_type: 'none' | 'stub' | 'deterministic_local';
  readonly config: Record<string, unknown>;
  readonly safety_policy: Record<string, unknown>;
  readonly notes?: string | null;
}

export interface KnowledgeRetrievalRequest {
  readonly query_text: string;
  readonly adapter_name?: string;
  readonly max_results?: number;
  readonly max_snippet_chars?: number;
}

export interface KnowledgeRetrievalRead {
  readonly adapter_name: string;
  readonly retrieval_mode: string;
  readonly query_text: string;
  readonly query_terms: string[];
  readonly used_knowledge: boolean;
  readonly used_context_artifact_ids: string[];
  readonly results: KnowledgeRetrievalResultRead[];
}

export interface ToolDefinitionRead {
  readonly id: string;
  readonly project_id: string | null;
  readonly name: string;
  readonly description: string | null;
  readonly tool_type: string;
  readonly input_schema: Record<string, unknown>;
  readonly output_schema: Record<string, unknown>;
  readonly risk_level: string;
  readonly approval_required: boolean;
  readonly timeout_seconds: number;
  readonly command_allowlist: unknown[];
  readonly allowed_working_directories: unknown[];
  readonly forbidden_shell_operators: unknown[];
  readonly max_stdout_bytes: number;
  readonly max_stderr_bytes: number;
  readonly artifact_policy: Record<string, unknown>;
  readonly is_mcp_ready: boolean;
  readonly mcp_metadata: Record<string, unknown>;
  readonly status: string;
}

export interface ToolDefinitionListRead {
  readonly items: ToolDefinitionRead[];
  readonly total: number;
}

export async function getKnowledgeBase(projectId: string): Promise<KnowledgeBaseRead> {
  return apiClient.getJson<KnowledgeBaseRead>(`/projects/${projectId}/knowledge-base`);
}

export async function searchEvidenceTrace(
  projectId: string,
  params: { q?: string; entity_type?: string; entity_id?: string; limit?: number } = {},
): Promise<EvidenceTraceRead> {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') query.set(key, String(value));
  }
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return apiClient.getJson<EvidenceTraceRead>(`/projects/${projectId}/evidence-trace${suffix}`);
}

export async function listTestKnowledgeCards(projectId: string): Promise<TestKnowledgeCardListRead> {
  return apiClient.getJson<TestKnowledgeCardListRead>(`/projects/${projectId}/test-knowledge/cards`);
}

export async function getTestKnowledgeGraph(projectId: string): Promise<TestKnowledgeGraphRead> {
  return apiClient.getJson<TestKnowledgeGraphRead>(`/projects/${projectId}/test-knowledge/graph`);
}

export async function getTestKnowledgeIndex(projectId: string): Promise<TestKnowledgeIndexRead> {
  return apiClient.getJson<TestKnowledgeIndexRead>(`/projects/${projectId}/test-knowledge/index`);
}

export async function rebuildTestKnowledgeIndex(
  data: TestKnowledgeIndexRebuildRequest,
): Promise<TestKnowledgeIndexRebuildRead> {
  return apiClient.postJson<TestKnowledgeIndexRebuildRead, TestKnowledgeIndexRebuildRequest>(
    '/test-knowledge/index/rebuild',
    data,
  );
}

export async function extractTestKnowledgeCards(
  data: TestKnowledgeCardExtractRequest,
): Promise<TestKnowledgeCardExtractRead> {
  return apiClient.postJson<TestKnowledgeCardExtractRead, TestKnowledgeCardExtractRequest>(
    '/test-knowledge/cards/extract',
    data,
  );
}

export async function extractAllTestKnowledgeCards(
  data: TestKnowledgeCardExtractBatchRequest,
): Promise<TestKnowledgeCardExtractBatchRead> {
  return apiClient.postJson<TestKnowledgeCardExtractBatchRead, TestKnowledgeCardExtractBatchRequest>(
    '/test-knowledge/cards/extract-batch',
    data,
  );
}

export async function reviewTestKnowledgeCard(
  cardId: string,
  data: TestKnowledgeCardReviewRequest,
): Promise<TestKnowledgeCardRead> {
  return apiClient.patchJson<TestKnowledgeCardRead, TestKnowledgeCardReviewRequest>(
    `/test-knowledge/cards/${cardId}`,
    data,
  );
}

export async function retrieveTestKnowledgeCards(
  data: TestKnowledgeCardRetrievalRequest,
): Promise<TestKnowledgeCardRetrievalRead> {
  return apiClient.postJson<TestKnowledgeCardRetrievalRead, TestKnowledgeCardRetrievalRequest>(
    '/test-knowledge/cards/retrieve',
    data,
  );
}

export async function createContextArtifact(data: ContextArtifactCreateRequest): Promise<ContextArtifactRead> {
  return apiClient.postJson<ContextArtifactRead, ContextArtifactCreateRequest>('/context-artifacts', data);
}

export async function updateKnowledgeAdapter(
  projectId: string,
  data: KnowledgeAdapterUpdateRequest,
): Promise<KnowledgeAdapterRead> {
  return apiClient.putJson<KnowledgeAdapterRead, KnowledgeAdapterUpdateRequest>(
    `/projects/${projectId}/knowledge-adapter`,
    data,
  );
}

export async function retrieveKnowledge(
  projectId: string,
  data: KnowledgeRetrievalRequest,
): Promise<KnowledgeRetrievalRead> {
  return apiClient.postJson<KnowledgeRetrievalRead, KnowledgeRetrievalRequest>(
    `/projects/${projectId}/knowledge-adapter/retrieve`,
    data,
  );
}

export async function listToolDefinitions(projectId: string): Promise<ToolDefinitionListRead> {
  return apiClient.getJson<ToolDefinitionListRead>(`/projects/${projectId}/tool-definitions`);
}
