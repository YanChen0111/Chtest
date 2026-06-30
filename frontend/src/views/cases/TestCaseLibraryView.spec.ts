import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import TestCaseLibraryView from './TestCaseLibraryView.vue';

describe('TestCaseLibraryView', () => {
  it('lists reviewed test cases and shows selected case detail', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/test-cases?project_id=00000000-0000-0000-0000-000000000101')) {
        return new Response(
          JSON.stringify({
            total: 2,
            items: [
              {
                id: '00000000-0000-0000-0000-000000000901',
                project_id: '00000000-0000-0000-0000-000000000101',
                module_id: null,
                source_candidate_id: '00000000-0000-0000-0000-000000000801',
                title: '过期优惠券不可用于结算',
                priority: 'P0',
                test_type: 'functional',
                precondition: '用户存在一张已过期优惠券',
                steps: ['准备已过期优惠券', '进入结算页', '提交订单'],
                expected_results: ['提交被阻断', '页面提示优惠券已过期'],
                input_data: { coupon_state: 'expired' },
                tags: ['coupon', 'boundary'],
                source_type: 'ai',
                review_status: 'approved_after_edit',
                status: 'active',
              },
              {
                id: '00000000-0000-0000-0000-000000000902',
                project_id: '00000000-0000-0000-0000-000000000101',
                module_id: null,
                source_candidate_id: null,
                title: '可用优惠券可成功抵扣订单金额',
                priority: 'P1',
                test_type: 'ui',
                precondition: '用户存在一张可用优惠券',
                steps: ['进入结算页', '选择优惠券', '提交订单'],
                expected_results: ['最终支付金额已抵扣'],
                input_data: { coupon_state: 'valid' },
                tags: ['coupon', 'ui'],
                source_type: 'ai',
                review_status: 'approved',
                status: 'active',
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(TestCaseLibraryView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('用例库');
    expect(wrapper.text()).toContain('已评审用例');
    expect(wrapper.text()).toContain('过期优惠券不可用于结算');
    expect(wrapper.text()).toContain('可用优惠券可成功抵扣订单金额');
    expect(wrapper.text()).toContain('准备已过期优惠券');
    expect(wrapper.text()).toContain('页面提示优惠券已过期');
    expect(wrapper.text()).toContain('编辑后通过');
    expect(wrapper.text()).toContain('coupon, boundary');
    expect(wrapper.text()).not.toContain('生成自动化草稿');
    expect(wrapper.text()).not.toContain('执行用例');
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/test-cases?project_id=00000000-0000-0000-0000-000000000101',
      expect.objectContaining({ headers: expect.objectContaining({ Accept: 'application/json' }) }),
    );
  });
});
