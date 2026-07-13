import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, describe, expect, it, vi } from 'vitest';

import CaseGenerationReviewView from './CaseGenerationReviewView.vue';

async function confirmDecisionTable(wrapper: VueWrapper): Promise<void> {
  for (const selector of [
    '[data-test="decision-source-confirmed"]',
    '[data-test="decision-risk-confirmed"]',
    '[data-test="decision-review-ready"]',
  ]) {
    const input = wrapper.find(`${selector} input[type="checkbox"]`);
    if (input.exists()) {
      await input.setValue(true);
    } else {
      await wrapper.find(selector).trigger('click');
    }
  }
  await flushPromises();
  await wrapper.vm.$nextTick();
}

describe('CaseGenerationReviewView', () => {
  afterEach(() => {
    window.localStorage.clear();
    vi.unstubAllGlobals();
  });

  it('starts case generation, lists candidates, and submits a review action', async () => {
    let metricsRequestCount = 0;
    let generationBody: unknown = null;
    let reviewBody: unknown = null;
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
      if (url.endsWith('/case-generation/tasks/00000000-0000-0000-0000-000000000701')) {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000000701',
            project_id: '00000000-0000-0000-0000-000000000101',
            requirement_id: '00000000-0000-0000-0000-000000000411',
            requirement_review_id: '00000000-0000-0000-0000-000000000611',
            ai_task_id: '00000000-0000-0000-0000-000000000702',
            target_test_types: ['functional', 'ui'],
            status: 'succeeded',
            generated_count: 2,
            ai_task_status: 'succeeded',
            error_code: null,
            error_message: null,
            created_at: '2026-07-01T02:00:00Z',
            updated_at: '2026-07-01T02:00:01Z',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
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
                coverage_dimensions: [
                  {
                    key: 'negative',
                    label: '异常/负向',
                    evidence: 'Expired coupon is blocked during checkout.',
                    source: 'model',
                  },
                  {
                    key: 'boundary',
                    label: '边界值',
                    evidence: 'Expiration date boundary is covered.',
                    source: 'model',
                  },
                ],
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
                coverage_dimensions: [
                  {
                    key: 'boundary',
                    label: '边界值',
                    evidence: 'Coupon amount boundary is covered.',
                    source: 'model',
                  },
                ],
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
        reviewBody = JSON.parse(String(init.body));
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
        const hasReviewCall = fetchMock.mock.calls.some(
          (call) =>
            String(call[0]).endsWith('/case-review/items/00000000-0000-0000-0000-000000000801/approve') &&
            call[1]?.method === 'POST',
        );
        const items =
          url.includes('entity_id=00000000-0000-0000-0000-000000000801') && hasReviewCall
            ? [
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
                  comment: '前端评审编辑后通过',
                  evidence_artifact_ids: [
                    '00000000-0000-0000-0000-000000000e01',
                    '00000000-0000-0000-0000-000000000e02',
                  ],
                  metadata_json: {},
                  created_at: '2026-07-01T02:15:00Z',
                },
              ]
            : [];
        return new Response(
          JSON.stringify({
            total: items.length,
            items,
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

    await confirmDecisionTable(wrapper);
    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(generationBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        requirement_id: '00000000-0000-0000-0000-000000000411',
        requirement_review_id: '00000000-0000-0000-0000-000000000611',
        requirement_document_artifact_id: null,
        decision_table_acknowledged: true,
      }),
    );
    expect(wrapper.text()).toContain('候选用例');
    expect(wrapper.text()).toContain('过期优惠券不可用于结算');
    expect(wrapper.text()).toContain('优惠券金额不能超过订单应付金额');
    expect(wrapper.text()).toContain('覆盖有效期边界');
    expect(wrapper.text()).toContain('覆盖维度');
    expect(wrapper.text()).toContain('Expiration date boundary is covered.');
    expect(wrapper.text()).toContain('进入结算页');
    expect(wrapper.text()).toContain('页面提示优惠券已过期');
    expect(wrapper.text()).toContain('批次指标');
    expect(wrapper.text()).toContain('生成总数');
    expect(wrapper.text()).toContain('字段完整率');
    expect(wrapper.text()).toContain('100%');

    await wrapper.find('[data-test="edit-case-title"] input').setValue('过期优惠券不可用于结算（已编辑）');
    await wrapper.find('[data-test="edit-case-steps"] textarea').setValue('准备一张已过期优惠券\n提交结算订单');
    await wrapper
      .find('[data-test="edit-case-expected-results"] textarea')
      .setValue('系统阻止订单提交\n页面提示优惠券已过期');

    await wrapper.find('[data-test="approve-after-edit"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(reviewBody).toEqual(
      expect.objectContaining({
        action: 'approve_after_edit',
        review_comment: '前端评审编辑后通过',
        edited_case: expect.objectContaining({
          title: '过期优惠券不可用于结算（已编辑）',
          steps: ['准备一张已过期优惠券', '提交结算订单'],
          expected_results: ['系统阻止订单提交', '页面提示优惠券已过期'],
        }),
      }),
    );
    expect(wrapper.text()).toContain('编辑后通过');
    expect(wrapper.text()).toContain('00000000-0000-0000-0000-000000000901');
    expect(wrapper.text()).toContain('采纳率');
    expect(wrapper.text()).toContain('编辑率');
    expect(wrapper.text()).toContain('评审进度');
    expect(wrapper.text()).toContain('50%');
    expect(wrapper.text()).toContain('本地评审历史');
    expect(wrapper.text()).toContain('Default User');
    expect(wrapper.text()).toContain('已生成 -> 编辑后通过');
    expect(wrapper.text()).toContain('前端评审编辑后通过');
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

    await wrapper.findAll('[data-test="candidate-list-item"]')[1].trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('优惠券金额不能超过订单应付金额');
    expect(wrapper.text()).toContain('Coupon amount boundary is covered.');
    expect(wrapper.find('[data-test="review-result"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="review-history"]').exists()).toBe(false);
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/review-history?project_id=00000000-0000-0000-0000-000000000101&entity_type=GeneratedCaseCandidate&entity_id=00000000-0000-0000-0000-000000000802&limit=20',
      expect.objectContaining({ headers: expect.objectContaining({ Accept: 'application/json' }) }),
    );
  });

  it('uses a generated requirement document as the case generation source', async () => {
    let generationBody: unknown = null;
    window.localStorage.setItem(
      'chtest.latestRequirementDocument',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        requirementId: '00000000-0000-0000-0000-000000000421',
        requirementReviewId: '00000000-0000-0000-0000-000000000621',
        requirementDocumentArtifactId: '00000000-0000-0000-0000-000000000d01',
        documentNumber: 'RD-CHECKOUT-SYSTEM-20260709-0001',
        downloadUrl: '/api/artifacts/00000000-0000-0000-0000-000000000d01/download',
      }),
    );
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
      if (url.endsWith('/case-generation/tasks/00000000-0000-0000-0000-000000000701')) {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000000701',
            project_id: '00000000-0000-0000-0000-000000000101',
            requirement_id: '00000000-0000-0000-0000-000000000421',
            requirement_review_id: '00000000-0000-0000-0000-000000000621',
            ai_task_id: '00000000-0000-0000-0000-000000000702',
            target_test_types: ['functional'],
            status: 'succeeded',
            generated_count: 0,
            ai_task_status: 'succeeded',
            error_code: null,
            error_message: null,
            created_at: '2026-07-01T02:00:00Z',
            updated_at: '2026-07-01T02:00:01Z',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
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

    await confirmDecisionTable(wrapper);
    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(generationBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        requirement_id: '00000000-0000-0000-0000-000000000421',
        requirement_review_id: '00000000-0000-0000-0000-000000000621',
        requirement_document_artifact_id: '00000000-0000-0000-0000-000000000d01',
        decision_table_acknowledged: true,
      }),
    );
  });

  it('does not auto-select the first requirement document without saved context', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirement-documents')) {
        return new Response(
          JSON.stringify({
            total: 1,
            items: [
              {
                id: '00000000-0000-0000-0000-000000000d02',
                project_id: '00000000-0000-0000-0000-000000000101',
                requirement_id: '00000000-0000-0000-0000-000000000422',
                requirement_review_id: '00000000-0000-0000-0000-000000000622',
                document_number: 'RD-CHECKOUT-SYSTEM-20260709-0002',
                version: 'v1',
                title: 'Coupon stacking rule',
                status: 'confirmed',
                artifact_id: '00000000-0000-0000-0000-000000000d02',
                download_url: '/api/artifacts/00000000-0000-0000-0000-000000000d02/download',
                created_at: '2026-07-09T11:00:00Z',
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

    expect(
      wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000000d02/download"]').exists(),
    ).toBe(false);

    await wrapper.find('form').trigger('submit');
    await flushPromises();

    expect(fetchMock).not.toHaveBeenCalledWith('/api/case-generation/tasks', expect.objectContaining({ method: 'POST' }));
  });

  it('resets the decision table acknowledgement when the generation source changes', async () => {
    window.localStorage.setItem(
      'chtest.latestRequirementReview',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        requirementId: '00000000-0000-0000-0000-000000000411',
        requirementReviewId: '00000000-0000-0000-0000-000000000611',
      }),
    );
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
    await confirmDecisionTable(wrapper);
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined();

    await wrapper.find('[data-test="requirement-id-input"] input').setValue('00000000-0000-0000-0000-000000000412');
    await flushPromises();
    await wrapper.vm.$nextTick();
    await wrapper.find('form').trigger('submit');
    await flushPromises();

    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined();
    expect(wrapper.text()).toContain('请先确认生成前决策表，避免直接把未澄清需求送入最终用例生成。');
    expect(fetchMock).not.toHaveBeenCalledWith('/api/case-generation/tasks', expect.objectContaining({ method: 'POST' }));
  });

  it('surfaces failed generation task errors before loading candidates', async () => {
    window.localStorage.setItem(
      'chtest.latestRequirementReview',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        requirementId: '00000000-0000-0000-0000-000000000431',
        requirementReviewId: '00000000-0000-0000-0000-000000000631',
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
        return new Response(
          JSON.stringify({
            case_generation_task_id: '00000000-0000-0000-0000-000000000731',
            ai_task_id: '00000000-0000-0000-0000-000000000732',
            status: 'pending',
            used_knowledge: false,
            used_context_artifact_ids: [],
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/case-generation/tasks/00000000-0000-0000-0000-000000000731')) {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000000731',
            project_id: '00000000-0000-0000-0000-000000000101',
            requirement_id: '00000000-0000-0000-0000-000000000431',
            requirement_review_id: '00000000-0000-0000-0000-000000000631',
            ai_task_id: '00000000-0000-0000-0000-000000000732',
            target_test_types: ['functional'],
            status: 'failed',
            generated_count: 0,
            ai_task_status: 'failed',
            error_code: 'CASE_GENERATION_DOMAIN_MISMATCH',
            error_message: 'Generated cases do not match the requirement domain.',
            created_at: '2026-07-01T02:00:00Z',
            updated_at: '2026-07-01T02:02:00Z',
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
    await confirmDecisionTable(wrapper);
    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('CASE_GENERATION_DOMAIN_MISMATCH');
    expect(wrapper.text()).toContain('Generated cases do not match the requirement domain.');
    expect(fetchMock).not.toHaveBeenCalledWith(
      '/api/case-generation/tasks/00000000-0000-0000-0000-000000000731/candidates',
      expect.anything(),
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
