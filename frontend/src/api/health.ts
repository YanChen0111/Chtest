import { apiClient, ApiError } from './client';

export type BackendHealthState = '正常' | '失败';

export interface BackendHealthResult {
  readonly state: BackendHealthState;
  readonly rawText: string;
}

export async function getBackendHealth(): Promise<BackendHealthResult> {
  try {
    const rawText = await apiClient.getText('/health');
    return {
      state: '正常',
      rawText,
    };
  } catch (error: unknown) {
    const rawText = error instanceof ApiError ? error.message : '请求失败';
    return {
      state: '失败',
      rawText,
    };
  }
}
