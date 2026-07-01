import { apiClient } from './client';

export interface PromptVersion {
  readonly id: string;
  readonly name: string;
  readonly version: string;
  readonly hash: string;
  readonly agent_name: string;
  readonly content: string;
  readonly input_schema_json: Record<string, unknown>;
  readonly output_schema_json: Record<string, unknown>;
  readonly status: string;
  readonly created_at: string;
  readonly updated_at: string;
  readonly created_by: string | null;
  readonly updated_by: string | null;
}

export interface SkillVersion {
  readonly id: string;
  readonly name: string;
  readonly version: string;
  readonly hash: string;
  readonly applicable_agents: string[];
  readonly content: string;
  readonly quality_gates_json: string[];
  readonly forbidden_actions_json: string[];
  readonly tool_permissions_json: string[];
  readonly status: string;
  readonly created_at: string;
  readonly updated_at: string;
  readonly created_by: string | null;
  readonly updated_by: string | null;
}

export interface PromptVersionList {
  readonly items: PromptVersion[];
  readonly total: number;
}

export interface SkillVersionList {
  readonly items: SkillVersion[];
  readonly total: number;
}

export async function listPromptVersions(): Promise<PromptVersionList> {
  return apiClient.getJson<PromptVersionList>('/prompt-versions');
}

export async function listSkillVersions(): Promise<SkillVersionList> {
  return apiClient.getJson<SkillVersionList>('/skill-versions');
}
