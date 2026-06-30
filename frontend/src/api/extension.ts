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

export async function listToolDefinitions(projectId: string): Promise<ToolDefinitionListRead> {
  return apiClient.getJson<ToolDefinitionListRead>(`/projects/${projectId}/tool-definitions`);
}
