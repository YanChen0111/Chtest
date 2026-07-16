const RUN_STATUS_LABELS: Record<string, string> = {
  passed: '通过',
  failed: '失败',
  running: '运行中',
  pending: '排队中',
  error: '错误',
  timeout: '超时',
};

export function executionRunStatusLabel(status: string): string {
  return RUN_STATUS_LABELS[status] ?? status;
}

export function executionRunDurationLabel(durationMs: number | null): string {
  return durationMs === null ? '运行中' : `${durationMs} ms`;
}
