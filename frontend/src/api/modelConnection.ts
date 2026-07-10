import { apiClient } from './client';

export interface ModelConnectionConfig {
  readonly configured: boolean;
  readonly provider: string | null;
  readonly model_name: string | null;
  readonly base_url: string | null;
  readonly wire_api: string;
  readonly api_key_configured: boolean;
  readonly api_key_hint: string | null;
}

export interface ModelConnectionConfigUpdate {
  readonly import_config_text?: string | null;
  readonly import_auth_json?: string | null;
  readonly codex_config_toml?: string | null;
  readonly codex_auth_json?: string | null;
  readonly api_key?: string | null;
  readonly provider?: string | null;
  readonly model_name?: string | null;
  readonly base_url?: string | null;
  readonly wire_api?: string | null;
}

export interface ModelConnectionTestResult {
  readonly ok: boolean;
  readonly provider: string | null;
  readonly model_name: string | null;
  readonly base_url: string | null;
  readonly wire_api: string;
  readonly message: string;
  readonly error_code: string | null;
  readonly http_status: number | null;
  readonly diagnostic: string | null;
  readonly suggestion: string | null;
}

export async function getModelConnectionConfig(): Promise<ModelConnectionConfig> {
  return apiClient.getJson<ModelConnectionConfig>('/settings/model-connection');
}

export async function saveModelConnectionConfig(
  data: ModelConnectionConfigUpdate,
): Promise<ModelConnectionConfig> {
  return apiClient.putJson<ModelConnectionConfig, ModelConnectionConfigUpdate>('/settings/model-connection', data);
}

export async function testModelConnectionConfig(
  data: ModelConnectionConfigUpdate = {},
): Promise<ModelConnectionTestResult> {
  return apiClient.postJson<ModelConnectionTestResult, ModelConnectionConfigUpdate>('/settings/model-connection/test', data);
}
