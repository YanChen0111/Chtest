export type ReadinessStatus = 'ready' | 'degraded' | 'not_ready';

export interface ReadinessCheckRead {
  readonly status: string;
  readonly error_code: string | null;
  readonly message: string;
  readonly details: Record<string, unknown>;
}

export interface ReadinessRead {
  readonly status: ReadinessStatus;
  readonly error_code: string | null;
  readonly message: string;
  readonly checks: Record<string, ReadinessCheckRead>;
}

export async function getReadiness(): Promise<ReadinessRead> {
  const response = await fetch('/api/ready', { headers: { Accept: 'application/json' } });
  const payload = (await response.json()) as ReadinessRead;
  if (!payload || !['ready', 'degraded', 'not_ready'].includes(payload.status)) {
    throw new Error(`Readiness response is invalid (${response.status}).`);
  }
  return payload;
}
