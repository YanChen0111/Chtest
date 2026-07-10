import { describe, expect, it } from 'vitest';

import { executionRunDurationLabel, executionRunStatusLabel } from './executionDisplay';

describe('executionDisplay', () => {
  it('maps known run statuses and preserves unknown status text', () => {
    expect(executionRunStatusLabel('passed')).toBe('通过');
    expect(executionRunStatusLabel('failed')).toBe('失败');
    expect(executionRunStatusLabel('running')).toBe('运行中');
    expect(executionRunStatusLabel('pending')).toBe('排队中');
    expect(executionRunStatusLabel('error')).toBe('错误');
    expect(executionRunStatusLabel('timeout')).toBe('超时');
    expect(executionRunStatusLabel('cancelled')).toBe('cancelled');
  });

  it('formats run duration labels', () => {
    expect(executionRunDurationLabel(null)).toBe('运行中');
    expect(executionRunDurationLabel(0)).toBe('0 ms');
    expect(executionRunDurationLabel(812)).toBe('812 ms');
  });
});
