export type EvidenceAvailabilityState =
  | 'local_artifact'
  | 'unavailable'
  | 'external_reference'
  | 'metadata_only';

export interface EvidenceAvailabilityLabels {
  readonly state: EvidenceAvailabilityState;
  readonly stateLabel: string;
  readonly actionLabel: string;
  readonly tagColor: 'green' | 'gray' | 'orange' | 'blue';
  readonly isOpenable: boolean;
}

const EVIDENCE_AVAILABILITY_LABELS: Record<EvidenceAvailabilityState, EvidenceAvailabilityLabels> = {
  local_artifact: {
    state: 'local_artifact',
    stateLabel: '可打开',
    actionLabel: '打开',
    tagColor: 'green',
    isOpenable: true,
  },
  unavailable: {
    state: 'unavailable',
    stateLabel: '不可用',
    actionLabel: '不可打开',
    tagColor: 'gray',
    isOpenable: false,
  },
  external_reference: {
    state: 'external_reference',
    stateLabel: '外部引用',
    actionLabel: '不可本地打开',
    tagColor: 'orange',
    isOpenable: false,
  },
  metadata_only: {
    state: 'metadata_only',
    stateLabel: '仅元数据',
    actionLabel: '不可直接打开',
    tagColor: 'blue',
    isOpenable: false,
  },
};

export function evidenceAvailabilityLabels(state: EvidenceAvailabilityState): EvidenceAvailabilityLabels {
  return EVIDENCE_AVAILABILITY_LABELS[state];
}
