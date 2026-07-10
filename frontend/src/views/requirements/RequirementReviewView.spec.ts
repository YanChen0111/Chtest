import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import RequirementReviewView from './RequirementReviewView.vue';

describe('RequirementReviewView', () => {
  it('creates a requirement and shows review scores, risks, and context usage', async () => {
    const reviewBodies: unknown[] = [];
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirement-documents')) {
        return new Response(JSON.stringify({ items: [], total: 0 }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/projects')) {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000000101',
            name: 'Checkout System',
            default_language: 'python',
            default_test_type: 'functional',
            status: 'active',
            created_at: '2026-06-29T10:00:00Z',
          }),
          { status: 201, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/requirements') && init?.method === 'POST') {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000000401',
            project_id: '00000000-0000-0000-0000-000000000101',
            module_id: null,
            title: '优惠券结算规则',
            content: '优惠券不可与积分同时使用。过期优惠券不可使用。',
            source_type: 'manual',
            source_ref: 'REQ-COUPON-001',
            status: 'active',
            created_at: '2026-06-29T10:00:00Z',
            updated_at: '2026-06-29T10:00:00Z',
          }),
          { status: 201, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/requirements/00000000-0000-0000-0000-000000000401/review') && init?.method === 'POST') {
        reviewBodies.push(JSON.parse(String(init.body)));
        return new Response(
          JSON.stringify({
            ai_task_id: '00000000-0000-0000-0000-000000000501',
            requirement_id: '00000000-0000-0000-0000-000000000401',
            status: 'pending',
            next_poll_url: '/api/ai-tasks/00000000-0000-0000-0000-000000000501',
            used_knowledge: false,
            used_context_artifact_ids: [],
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/requirements/00000000-0000-0000-0000-000000000401/review')) {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000000601',
            requirement_id: '00000000-0000-0000-0000-000000000401',
            overall_score: 82,
            scores: {
              completeness: 78,
              clarity: 85,
              consistency: 88,
              testability: 84,
              feasibility: 82,
              logic: 75,
            },
            issues: [{ type: 'missing_boundary', text: '未说明优惠券金额等于订单应付金额时是否允许支付金额为 0', severity: 'medium' }],
            clarification_questions: ['优惠券是否可以与平台活动叠加？'],
            risk_items: [
              {
                title: '优惠券与积分互斥规则',
                risk_level: 'high',
                suggestion: '覆盖同时选择优惠券和积分时的提交阻断',
              },
            ],
            used_knowledge: false,
            used_context_artifact_ids: [],
            context_manifest_artifact_id: '00000000-0000-0000-0000-000000000372',
            status: 'reviewed',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/requirements/00000000-0000-0000-0000-000000000401/documents') && init?.method === 'POST') {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000000d01',
            project_id: '00000000-0000-0000-0000-000000000101',
            requirement_id: '00000000-0000-0000-0000-000000000401',
            requirement_review_id: '00000000-0000-0000-0000-000000000601',
            document_number: 'RD-CHECKOUT-SYSTEM-20260709-0001',
            version: 'v1',
            title: '优惠券结算规则',
            status: 'draft',
            artifact_id: '00000000-0000-0000-0000-000000000d01',
            download_url: '/api/artifacts/00000000-0000-0000-0000-000000000d01/download',
            created_at: '2026-07-09T10:00:00Z',
          }),
          { status: 201, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(RequirementReviewView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('需求评审');
    expect(wrapper.text()).toContain('开始评审');

    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('综合评分');
    expect(wrapper.text()).toContain('优惠券结算规则');
    expect(wrapper.text()).toContain('82');
    expect(wrapper.text()).toContain('完整性');
    expect(wrapper.text()).toContain('78');
    expect(wrapper.text()).toContain('未说明优惠券金额等于订单应付金额');
    expect(wrapper.text()).toContain('优惠券是否可以与平台活动叠加');
    expect(wrapper.text()).toContain('优惠券与积分互斥规则');
    expect(wrapper.text()).toContain('覆盖同时选择优惠券和积分时的提交阻断');
    expect(wrapper.text()).toContain('外部知识库未使用');
    expect(wrapper.text()).toContain('上下文清单');

    await wrapper.find('[data-test="supplement-text"] textarea').setValue('平台活动可以叠加，但积分不可同时使用。');
    await wrapper.find('[data-test="clarification-answer"] input').setValue('可以与平台活动叠加。');
    await wrapper.find('[data-test="submit-supplement"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(reviewBodies[1]).toEqual(
      expect.objectContaining({
        supplement_text: '平台活动可以叠加，但积分不可同时使用。',
        clarification_answers: [
          {
            question: '优惠券是否可以与平台活动叠加？',
            answer: '可以与平台活动叠加。',
          },
        ],
      }),
    );

    await wrapper.find('[data-test="generate-document"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('正式需求文档');
    expect(wrapper.text()).toContain('RD-CHECKOUT-SYSTEM-20260709-0001');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000000d01/download"]').exists()).toBe(true);
  });
});
