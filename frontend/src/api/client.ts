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
      throw await this.errorFromResponse(response);
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
      throw await this.errorFromResponse(response);
    }
    return response.json() as Promise<T>;
  }

  async postJson<TResponse, TBody extends object>(path: string, body: TBody): Promise<TResponse> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw await this.errorFromResponse(response);
    }
    return response.json() as Promise<TResponse>;
  }

  async putJson<TResponse, TBody extends object>(path: string, body: TBody): Promise<TResponse> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'PUT',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw await this.errorFromResponse(response);
    }
    return response.json() as Promise<TResponse>;
  }

  async patchJson<TResponse, TBody extends object>(path: string, body: TBody): Promise<TResponse> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'PATCH',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw await this.errorFromResponse(response);
    }
    return response.json() as Promise<TResponse>;
  }

  async delete(path: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}${path}`, { method: 'DELETE', headers: { Accept: 'application/json' } });
    if (!response.ok) {
      throw await this.errorFromResponse(response);
    }
  }

  private async errorFromResponse(response: Response): Promise<ApiError> {
    let message = `请求失败：${response.status}`;
    try {
      const payload = (await response.clone().json()) as unknown;
      const record = isRecord(payload) ? payload : null;
      const payloadMessage =
        typeof record?.message === 'string'
          ? record.message
          : typeof record?.detail === 'string'
            ? record.detail
            : '';
      const errorCode = typeof record?.error_code === 'string' ? record.error_code : '';
      if (payloadMessage) {
        message = `${message} (${payloadMessage})`;
      }
      if (errorCode) {
        message = `${message}（${errorCode}）`;
      }
    } catch {
      try {
        const text = (await response.clone().text()).trim();
        if (text) {
          message = `${message} (${text.slice(0, 300)})`;
        }
      } catch {
        // Keep the status-only fallback.
      }
    }
    return new ApiError(response.status, message);
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

export const apiClient = new ApiClient();
