import { mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { describe, expect, it } from 'vitest';

import ExecutionResultTable from './ExecutionResultTable.vue';

describe('ExecutionResultTable', () => {
  it('renders page-owned result columns and rows', () => {
    const wrapper = mount(ExecutionResultTable, {
      props: {
        title: '测试结果',
        titleId: 'pytest-results-title',
        columns: [
          { title: '测试', dataIndex: 'test_name' },
          { title: '状态', dataIndex: 'status' },
          { title: '耗时', dataIndex: 'duration_label' },
        ],
        rows: [
          {
            id: 'result-1',
            test_name: 'generated::test_ok',
            status: 'passed',
            duration_label: '32 ms',
          },
        ],
      },
      global: {
        plugins: [ArcoVue],
      },
    });

    expect(wrapper.find('#pytest-results-title').text()).toBe('测试结果');
    expect(wrapper.text()).toContain('测试');
    expect(wrapper.text()).toContain('状态');
    expect(wrapper.text()).toContain('耗时');
    expect(wrapper.text()).toContain('generated::test_ok');
    expect(wrapper.text()).toContain('passed');
    expect(wrapper.text()).toContain('32 ms');
  });
});
