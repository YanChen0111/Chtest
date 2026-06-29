import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import CaseGenerationReviewView from './CaseGenerationReviewView.vue';

describe('CaseGenerationReviewView', () => {
  it('starts case generation, lists candidates, and submits a review action', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/case-generation/tasks') && init?.method === 'POST') {
        return new Response(
          JSON.stringify({
            case_generation_task_id: '00000000-0000-0000-0000-000000000701',
            ai_task_id: '00000000-0000-0000-0000-000000000702',
            status: 'pending',
            used_knowledge: false,
            used_context_artifact_ids: [],
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/case-generation/tasks/00000000-0000-0000-0000-000000000701/candidates')) {
        return new Response(
          JSON.stringify({
            total: 2,
            items: [
              {
                id: '00000000-0000-0000-0000-000000000801',
                title: '过期优惠券不可用于结算',
                priority: 'P0',
                test_type: 'functional',
                precondition: '用户存在一张已过期优惠券',
                steps: ['进入结算页', '查看优惠券列表', '尝试选择已过期优惠券', '提交订单'],
                expected_results: ['已过期优惠券不可选或提交失败', '页面提示优惠券已过期'],
                input_data: {},
                requirement_refs: ['过期优惠券不可使用'],
                risk_refs: [],
                ai_reason: '覆盖有效期边界',
                status: 'generated',
              },
              {
                id: '00000000-0000-0000-0000-000000000802',
                title: '优惠券金额不能超过订单应付金额',
                priority: 'P1',
                test_type: 'functional',
                precondition: '订单应付金额小于优惠券金额',
                steps: ['进入结算页', '选择金额大于订单应付金额的优惠券', '提交订单'],
                expected_results: ['系统按规则阻断或限制抵扣', '最终支付金额不会为负数'],
                input_data: {},
                requirement_refs: ['优惠券金额不能超过订单应付金额'],
                risk_refs: [],
                ai_reason: '覆盖金额边界',
                status: 'generated',
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/case-review/items/00000000-0000-0000-0000-000000000801/approve') && init?.method === 'POST') {
        return new Response(
          JSON.stringify({
            candidate_id: '00000000-0000-0000-0000-000000000801',
            status: 'approved_after_edit',
            test_case_id: '00000000-0000-0000-0000-000000000901',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(CaseGenerationReviewView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('用例生成评审');
    expect(wrapper.text()).toContain('开始生成候选用例');

    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('候选用例');
    expect(wrapper.text()).toContain('过期优惠券不可用于结算');
    expect(wrapper.text()).toContain('优惠券金额不能超过订单应付金额');
    expect(wrapper.text()).toContain('覆盖有效期边界');
    expect(wrapper.text()).toContain('进入结算页');
    expect(wrapper.text()).toContain('页面提示优惠券已过期');

    await wrapper.find('[data-test="approve-after-edit"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('approved_after_edit');
    expect(wrapper.text()).toContain('00000000-0000-0000-0000-000000000901');
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/case-review/items/00000000-0000-0000-0000-000000000801/approve',
      expect.objectContaining({ method: 'POST' }),
    );
  });
});
