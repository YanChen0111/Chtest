import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import ExecutionMetricsPanel from './ExecutionMetricsPanel.vue';

describe('ExecutionMetricsPanel', () => {
  it('renders page-owned metric labels and values', () => {
    const wrapper = mount(ExecutionMetricsPanel, {
      props: {
        items: [
          { label: '总数', value: 8 },
          { label: '通过', value: 7 },
          { label: '平均延迟', value: '32 ms' },
        ],
      },
    });

    expect(wrapper.attributes('aria-label')).toBe('执行指标');
    expect(wrapper.text()).toContain('总数');
    expect(wrapper.text()).toContain('8');
    expect(wrapper.text()).toContain('通过');
    expect(wrapper.text()).toContain('7');
    expect(wrapper.text()).toContain('平均延迟');
    expect(wrapper.text()).toContain('32 ms');
    expect(wrapper.findAll('.metric-tile')).toHaveLength(3);
  });
});
