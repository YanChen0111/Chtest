import { describe, expect, it } from 'vitest';

import { evidenceAvailabilityLabels, type EvidenceAvailabilityState } from './evidenceAvailability';

describe('evidenceAvailabilityLabels', () => {
  it('returns stable user-facing labels for evidence availability states', () => {
    const cases: Array<[EvidenceAvailabilityState, string, string, boolean]> = [
      ['local_artifact', '可打开', '打开', true],
      ['unavailable', '不可用', '不可打开', false],
      ['external_reference', '外部引用', '不可本地打开', false],
      ['metadata_only', '仅元数据', '不可直接打开', false],
    ];

    for (const [state, stateLabel, actionLabel, isOpenable] of cases) {
      expect(evidenceAvailabilityLabels(state)).toMatchObject({
        state,
        stateLabel,
        actionLabel,
        isOpenable,
      });
    }
  });

  it('keeps local-openable evidence as the only openable state', () => {
    expect(evidenceAvailabilityLabels('local_artifact').isOpenable).toBe(true);
    expect(evidenceAvailabilityLabels('unavailable').isOpenable).toBe(false);
    expect(evidenceAvailabilityLabels('external_reference').isOpenable).toBe(false);
    expect(evidenceAvailabilityLabels('metadata_only').isOpenable).toBe(false);
  });
});
