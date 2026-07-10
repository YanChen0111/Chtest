import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, describe, expect, it, vi } from 'vitest';

import CaseGenerationReviewView from './CaseGenerationReviewView.vue';

describe('CaseGenerationReviewView', () => {
  afterEach(() => {
    window.localStorage.clear();
    vi.unstubAllGlobals();
  });

  it('starts case generation, lists candidates, and submits a review action', async () => {
    let metricsRequestCount = 0;
    let generationBody: unknown = null;
    window.localStorage.setItem(
      'chtest.latestRequirementReview',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        requirementId: '00000000-0000-0000-0000-000000000411',
        requirementReviewId: '00000000-0000-0000-0000-000000000611',
      }),
    );
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirement-documents')) {
        return new Response(JSON.stringify({ items: [], total: 0 }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/case-generation/tasks') && init?.method === 'POST') {
        generationBody = JSON.parse(String(init.body));
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
      if (url.endsWith('/case-generation/tasks/00000000-0000-0000-0000-000000000701/metrics')) {
        metricsRequestCount += 1;
        return new Response(
          JSON.stringify({
            generation_task_id: '00000000-0000-0000-0000-000000000701',
            generated_count: 2,
            approved_count: metricsRequestCount > 1 ? 1 : 0,
            edited_count: metricsRequestCount > 1 ? 1 : 0,
            rejected_count: 0,
            optimization_count: 0,
            reviewed_count: metricsRequestCount > 1 ? 1 : 0,
            acceptance_rate: metricsRequestCount > 1 ? 0.5 : 0,
            edit_rate: metricsRequestCount > 1 ? 0.5 : 0,
            rejection_rate: 0,
            optimization_rate: 0,
            review_progress: metricsRequestCount > 1 ? 0.5 : 0,
            field_complete_rate: 1,
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
      if (url.includes('/review-history?')) {
        return new Response(
          JSON.stringify({
            total: 1,
            items: [
              {
                id: '00000000-0000-0000-0000-000000000a01',
                project_id: '00000000-0000-0000-0000-000000000101',
                entity_type: 'GeneratedCaseCandidate',
                entity_id: '00000000-0000-0000-0000-000000000801',
                related_entity_type: 'TestCase',
                related_entity_id: '00000000-0000-0000-0000-000000000901',
                action: 'approve_after_edit',
                from_status: 'generated',
                to_status: 'approved_after_edit',
                reviewer: 'Default User',
                comment: '前端评审动作',
                evidence_artifact_ids: ['00000000-0000-0000-0000-000000000e01', '00000000-0000-0000-0000-000000000e02'],
                metadata_json: {},
                created_at: '2026-07-01T02:15:00Z',
              },
            ],
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

    expect(generationBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        requirement_id: '00000000-0000-0000-0000-000000000411',
        requirement_review_id: '00000000-0000-0000-0000-000000000611',
        requirement_document_artifact_id: null,
      }),
    );
    expect(wrapper.text()).toContain('候选用例');
    expect(wrapper.text()).toContain('过期优惠券不可用于结算');
    expect(wrapper.text()).toContain('优惠券金额不能超过订单应付金额');
    expect(wrapper.text()).toContain('覆盖有效期边界');
    expect(wrapper.text()).toContain('进入结算页');
    expect(wrapper.text()).toContain('页面提示优惠券已过期');
    expect(wrapper.text()).toContain('批次指标');
    expect(wrapper.text()).toContain('生成总数');
    expect(wrapper.text()).toContain('字段完整率');
    expect(wrapper.text()).toContain('100%');

    await wrapper.find('[data-test="approve-after-edit"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('编辑后通过');
    expect(wrapper.text()).toContain('00000000-0000-0000-0000-000000000901');
    expect(wrapper.text()).toContain('采纳率');
    expect(wrapper.text()).toContain('编辑率');
    expect(wrapper.text()).toContain('评审进度');
    expect(wrapper.text()).toContain('50%');
    expect(wrapper.text()).toContain('本地评审历史');
    expect(wrapper.text()).toContain('Default User');
    expect(wrapper.text()).toContain('已生成 -> 编辑后通过');
    expect(wrapper.text()).toContain('前端评审动作');
    expect(wrapper.text()).toContain('证据 2');
    expect(JSON.parse(window.localStorage.getItem('chtest.latestApprovedTestCase') ?? '{}')).toEqual({
      projectId: '00000000-0000-0000-0000-000000000101',
      testCaseId: '00000000-0000-0000-0000-000000000901',
      sourceCandidateId: '00000000-0000-0000-0000-000000000801',
      reviewStatus: 'approved_after_edit',
    });
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/case-review/items/00000000-0000-0000-0000-000000000801/approve',
      expect.objectContaining({ method: 'POST' }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/review-history?project_id=00000000-0000-0000-0000-000000000101&entity_type=GeneratedCaseCandidate&entity_id=00000000-0000-0000-0000-000000000801&limit=20',
      expect.objectContaining({ headers: expect.objectContaining({ Accept: 'application/json' }) }),
    );
  });

  it('uses a generated requirement document as the case generation source', async () => {
    let generationBody: unknown = null;
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirement-documents')) {
        return new Response(
          JSON.stringify({
            total: 1,
            items: [
              {
                id: '00000000-0000-0000-0000-000000000d01',
                project_id: '00000000-0000-0000-0000-000000000101',
                requirement_id: '00000000-0000-0000-0000-000000000421',
                requirement_review_id: '00000000-0000-0000-0000-000000000621',
                document_number: 'RD-CHECKOUT-SYSTEM-20260709-0001',
                version: 'v1',
                title: '优惠券结算规则',
                status: 'confirmed',
                artifact_id: '00000000-0000-0000-0000-000000000d01',
                download_url: '/api/artifacts/00000000-0000-0000-0000-000000000d01/download',
                created_at: '2026-07-09T10:00:00Z',
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/case-generation/tasks') && init?.method === 'POST') {
        generationBody = JSON.parse(String(init.body));
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
        return new Response(JSON.stringify({ total: 0, items: [] }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/case-generation/tasks/00000000-0000-0000-0000-000000000701/metrics')) {
        return new Response(
          JSON.stringify({
            generation_task_id: '00000000-0000-0000-0000-000000000701',
            generated_count: 0,
            approved_count: 0,
            edited_count: 0,
            rejected_count: 0,
            optimization_count: 0,
            reviewed_count: 0,
            acceptance_rate: 0,
            edit_rate: 0,
            rejection_rate: 0,
            optimization_rate: 0,
            review_progress: 0,
            field_complete_rate: 0,
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

    expect(wrapper.text()).toContain('RD-CHECKOUT-SYSTEM-20260709-0001');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000000d01/download"]').exists()).toBe(true);

    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(generationBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        requirement_id: '00000000-0000-0000-0000-000000000421',
        requirement_review_id: '00000000-0000-0000-0000-000000000621',
        requirement_document_artifact_id: '00000000-0000-0000-0000-000000000d01',
      }),
    );
  });

  it('does not submit case generation without a review or document source', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirement-documents')) {
        return new Response(JSON.stringify({ items: [], total: 0 }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
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
    await wrapper.find('form').trigger('submit');
    await flushPromises();

    expect(wrapper.text()).toContain('请先完成需求评审，或选择一份正式需求文档。');
    expect(fetchMock).not.toHaveBeenCalledWith('/api/case-generation/tasks', expect.objectContaining({ method: 'POST' }));
  });
});
