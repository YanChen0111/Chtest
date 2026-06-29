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

  async getJson<T>(path: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      headers: {
        Accept: 'application/json',
      },
    });
    if (!response.ok) {
      throw new ApiError(response.status, `请求失败：${response.status}`);
    }
    return response.json() as Promise<T>;
  }

  async postJson<TResponse, TBody extends Record<string, unknown>>(path: string, body: TBody): Promise<TResponse> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new ApiError(response.status, `请求失败：${response.status}`);
    }
    return response.json() as Promise<TResponse>;
  }
}

export const apiClient = new ApiClient();
