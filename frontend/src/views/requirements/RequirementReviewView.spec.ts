import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { useRequirementsStore } from '../../stores/requirements';
import RequirementReviewView from './RequirementReviewView.vue';

describe('RequirementReviewView', () => {
  beforeEach(() => window.localStorage.clear());
  afterEach(() => vi.unstubAllGlobals());

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
      if (url.endsWith('/test-knowledge/cards/retrieve') && init?.method === 'POST') {
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            query_text: '优惠券不可与积分同时使用。过期优惠券不可使用。',
            approved_only: true,
            total: 1,
            items: [
              {
                evidence_id: 'evidence-coupon-1',
                knowledge_card_id: 'card-coupon-1',
                source_artifact_id: 'artifact-coupon-1',
                knowledge_type: 'BoundaryCondition',
                title: '优惠券过期与互斥规则',
                snippet: '过期优惠券不可使用，优惠券与积分不能同时使用。',
                score: 4,
                matched_terms: ['优惠券', '过期'],
                retrieval_reason: 'keyword_overlap',
                safe_to_show: true,
                allowed_for_prompt: true,
                status: 'approved',
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
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
            used_knowledge: true,
            used_context_artifact_ids: ['artifact-coupon-1'],
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
            test_design_notes: [],
            risk_items: [
              {
                title: '优惠券与积分互斥规则',
                risk_level: 'high',
                suggestion: '覆盖同时选择优惠券和积分时的提交阻断',
              },
            ],
            used_knowledge: true,
            used_context_artifact_ids: ['artifact-coupon-1'],
            context_manifest_artifact_id: '00000000-0000-0000-0000-000000000372',
            status: 'reviewed',
            workflow: {
              run_id: '00000000-0000-0000-0000-000000000701',
              stage: 'requirement_review',
              state: 'approved',
              lock_version: 3,
              snapshot_id: '00000000-0000-0000-0000-000000000702',
              approval_decision_id: '00000000-0000-0000-0000-000000000703',
              can_submit: false,
              can_complete_review: false,
              can_edit: true,
              can_approve: false,
              can_continue: true,
            },
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
    expect(wrapper.text()).toContain('评审前先检索项目知识');

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
    expect(wrapper.text()).toContain('已自动使用 1 条项目知识证据');
    expect(wrapper.text()).toContain('已找到 1 条相关知识');
    expect(wrapper.find('[data-test="review-next-step"]').exists()).toBe(true);
    expect(reviewBodies[0]).toEqual(expect.objectContaining({ use_knowledge: true, context_artifact_ids: ['artifact-coupon-1'] }));

    const persistedContext = JSON.parse(window.localStorage.getItem('chtest.latestRequirementReview') ?? '{}');
    expect(persistedContext).toEqual(
      expect.objectContaining({
        requirementId: '00000000-0000-0000-0000-000000000401',
        requirementReviewId: '00000000-0000-0000-0000-000000000601',
        requirement: expect.objectContaining({ title: '优惠券结算规则' }),
        review: expect.objectContaining({ overall_score: 82 }),
      }),
    );

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

    wrapper.unmount();
    const restoredWrapper = mount(RequirementReviewView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });
    await flushPromises();
    await restoredWrapper.vm.$nextTick();
    expect(restoredWrapper.text()).toContain('综合评分');
    expect(restoredWrapper.text()).toContain('82');
    expect(restoredWrapper.find('input').element.value).toBe('优惠券结算规则');
  });

  it('fails closed for formal assets and downstream navigation before approval', async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL) => new Response(JSON.stringify({ items: [], total: 0 }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }));
    vi.stubGlobal('fetch', fetchMock);
    const pinia = createPinia();
    const store = useRequirementsStore(pinia);
    store.requirement = {
      id: '00000000-0000-0000-0000-000000000401',
      project_id: store.projectId,
      module_id: null,
      title: '优惠券结算规则',
      content: '候选输入',
      source_type: 'manual',
      source_ref: 'REQ-1',
      status: 'active',
      created_at: '2026-07-29T00:00:00Z',
      updated_at: '2026-07-29T00:00:00Z',
    };
    store.review = {
      id: '00000000-0000-0000-0000-000000000601',
      requirement_id: store.requirement.id,
      overall_score: 80,
      scores: { completeness: 80, clarity: 80, consistency: 80, testability: 80, feasibility: 80, logic: 80 },
      issues: [],
      clarification_questions: [],
      test_design_notes: [],
      risk_items: [],
      used_knowledge: false,
      used_context_artifact_ids: [],
      context_manifest_artifact_id: null,
      status: 'reviewed',
      workflow: {
        run_id: '00000000-0000-0000-0000-000000000701',
        stage: 'requirement_review',
        state: 'waiting_review',
        lock_version: 1,
        snapshot_id: '00000000-0000-0000-0000-000000000702',
        approval_decision_id: null,
        can_submit: false,
        can_complete_review: true,
        can_edit: true,
        can_approve: false,
        can_continue: false,
      },
    };

    const wrapper = mount(RequirementReviewView, { global: { plugins: [pinia, ArcoVue] } });
    await flushPromises();

    const documentButton = wrapper.find('[data-test="generate-document"]');
    expect(documentButton.attributes('disabled')).toBeDefined();
    expect(wrapper.find('[data-test="continue-workflow"]').exists()).toBe(false);
    await documentButton.trigger('click');
    expect(fetchMock.mock.calls.some(([input]) => String(input).includes('/documents'))).toBe(false);
  });
});
