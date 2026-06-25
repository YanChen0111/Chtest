const DEFAULT_API_BASE_URL = '/api';

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export interface ApiClientOptions {
  readonly baseUrl?: string;
}

export class ApiClient {
  private readonly baseUrl: string;

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = options.baseUrl ?? DEFAULT_API_BASE_URL;
  }

  async getText(path: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}${path}`);
    if (!response.ok) {
      throw new ApiError(response.status, `请求失败：${response.status}`);
    }
    return response.text();
  }
}

export const apiClient = new ApiClient();
