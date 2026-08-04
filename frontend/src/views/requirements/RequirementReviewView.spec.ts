import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { useRequirementsStore } from '../../stores/requirements';
import RequirementReviewView from './RequirementReviewView.vue';

const projectId = '00000000-0000-0000-0000-000000000101';
const requirementId = '00000000-0000-0000-0000-000000000401';
const reviewId = '00000000-0000-0000-0000-000000000601';
const workflowRunId = '00000000-0000-0000-0000-000000000701';
const routeQuery: Record<string, string | undefined> = {};

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: routeQuery }),
}));

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function exactRequirement(id = requirementId) {
  return {
    id,
    project_id: projectId,
    module_id: null,
    title: 'Exact queue requirement',
    content: 'Restore only this requirement review.',
    source_type: 'manual',
    source_ref: 'REQ-EXACT-1',
    status: 'active',
    created_at: '2026-08-04T00:00:00Z',
    updated_at: '2026-08-04T00:00:00Z',
  };
}

function exactReview(id = reviewId, runId = workflowRunId, stage = 'requirement_review') {
  return {
    id,
    requirement_id: requirementId,
    overall_score: 91,
    scores: { completeness: 90, clarity: 91, consistency: 92, testability: 93, feasibility: 89, logic: 91 },
    issues: [],
    clarification_questions: [],
    test_design_notes: [],
    risk_items: [],
    used_knowledge: false,
    used_context_artifact_ids: [],
    context_manifest_artifact_id: null,
    status: 'reviewed',
    workflow: {
      run_id: runId,
      stage,
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
}

describe('RequirementReviewView', () => {
  beforeEach(() => {
    window.localStorage.clear();
    Object.keys(routeQuery).forEach((key) => delete routeQuery[key]);
  });
  afterEach(() => vi.unstubAllGlobals());

  it('loads the exact requirement review and workflow run requested by the queue route', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = reviewId;
    routeQuery.workflow_run_id = workflowRunId;
    const requestedUrls: string[] = [];
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      requestedUrls.push(url);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/requirements/${requirementId}/review`)) return jsonResponse(exactReview());
      if (url.endsWith(`/projects/${projectId}/requirement-documents`)) {
        return jsonResponse({ items: [], total: 0 });
      }
      return new Response('not found', { status: 404 });
    }));

    const wrapper = mount(RequirementReviewView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });
    await flushPromises();

    expect(requestedUrls.some((url) => url.endsWith(`/requirements/${requirementId}`))).toBe(true);
    expect(requestedUrls.some((url) => url.endsWith(`/requirements/${requirementId}/review`))).toBe(true);
    expect(requestedUrls.some((url) => url.endsWith(`/projects/${projectId}/requirements`))).toBe(false);
    expect((wrapper.find('input').element as HTMLInputElement).value).toBe('Exact queue requirement');
    expect(wrapper.text()).toContain('91');
    expect(wrapper.find('[data-test="review-next-step"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="start-review"]').attributes('disabled')).toBeDefined();
    const persisted = JSON.parse(window.localStorage.getItem('chtest.latestRequirementReview') ?? '{}');
    expect(persisted).toEqual(expect.objectContaining({
      requirementId,
      requirementReviewId: reviewId,
      review: expect.objectContaining({ workflow: expect.objectContaining({ run_id: workflowRunId }) }),
    }));
  });

  it('loads an exact risk review through the project-scoped stage API', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = reviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'risk_review';
    const requestedUrls: string[] = [];
    const pinia = createPinia();
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      requestedUrls.push(url);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${reviewId}/risk-review`)) {
        return jsonResponse(exactReview(reviewId, workflowRunId, 'risk_review'));
      }
      if (url.endsWith(`/projects/${projectId}/requirement-documents`)) {
        return jsonResponse({ items: [], total: 0 });
      }
      return new Response('not found', { status: 404 });
    }));

    const wrapper = mount(RequirementReviewView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    expect(requestedUrls.some(
      (url) => url.endsWith(`/projects/${projectId}/requirement-reviews/${reviewId}/risk-review`),
    )).toBe(true);
    expect(requestedUrls.some((url) => url.endsWith(`/requirements/${requirementId}/review`))).toBe(false);
    expect(useRequirementsStore(pinia).review?.workflow?.stage).toBe('risk_review');
    expect(wrapper.find('[data-test="review-next-step"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="start-review"]').attributes('disabled')).toBeDefined();
  });

  it('fails closed when a risk route returns a different workflow stage', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = reviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'risk_review';
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${reviewId}/risk-review`)) {
        return jsonResponse(exactReview());
      }
      return new Response('not found', { status: 404 });
    }));

    const wrapper = mount(RequirementReviewView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });
    await flushPromises();

    expect(wrapper.find('[data-test="exact-review-restore-failed"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="review-next-step"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="start-review"]').attributes('disabled')).toBeDefined();
  });

  it('loads an exact test plan review through the project-scoped stage API', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = reviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'test_plan_review';
    const requestedUrls: string[] = [];
    const pinia = createPinia();
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      requestedUrls.push(url);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${reviewId}/test-plan-review`)) {
        return jsonResponse(exactReview(reviewId, workflowRunId, 'test_plan_review'));
      }
      if (url.endsWith(`/projects/${projectId}/requirement-documents`)) {
        return jsonResponse({ items: [], total: 0 });
      }
      return new Response('not found', { status: 404 });
    }));

    const wrapper = mount(RequirementReviewView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    expect(requestedUrls.some(
      (url) => url.endsWith(`/projects/${projectId}/requirement-reviews/${reviewId}/test-plan-review`),
    )).toBe(true);
    expect(requestedUrls.some(
      (url) => url.endsWith(`/projects/${projectId}/requirement-reviews/${reviewId}/risk-review`),
    )).toBe(false);
    expect(useRequirementsStore(pinia).review?.workflow?.stage).toBe('test_plan_review');
    expect(wrapper.find('[data-test="test-plan-review-panel"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="start-review"]').attributes('disabled')).toBeDefined();
  });

  it('fails closed when a test plan route returns a different workflow stage', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = reviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'test_plan_review';
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${reviewId}/test-plan-review`)) {
        return jsonResponse(exactReview(reviewId, workflowRunId, 'risk_review'));
      }
      return new Response('not found', { status: 404 });
    }));

    const wrapper = mount(RequirementReviewView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });
    await flushPromises();

    expect(wrapper.find('[data-test="exact-review-restore-failed"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="test-plan-review-panel"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="start-review"]').attributes('disabled')).toBeDefined();
  });

  it('fails closed without restoring stale browser context when explicit ids are invalid', async () => {
    routeQuery.requirement_id = 'not-a-uuid';
    routeQuery.requirement_review_id = reviewId;
    routeQuery.workflow_run_id = workflowRunId;
    window.localStorage.setItem('chtest.latestRequirementReview', JSON.stringify({
      projectId,
      requirementId,
      requirementReviewId: reviewId,
      requirement: exactRequirement(),
      review: exactReview(),
    }));
    const requestedUrls: string[] = [];
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      requestedUrls.push(url);
      return jsonResponse({ error_code: 'VALIDATION_ERROR', message: 'Requirement id is invalid.', details: {} }, 422);
    }));

    const wrapper = mount(RequirementReviewView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });
    await flushPromises();

    expect(requestedUrls.some((url) => url.endsWith('/requirements/not-a-uuid'))).toBe(true);
    expect(requestedUrls.some((url) => url.endsWith(`/requirements/${requirementId}`))).toBe(false);
    expect(wrapper.find('[data-test="exact-review-restore-failed"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="review-next-step"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="start-review"]').attributes('disabled')).toBeDefined();
    expect(wrapper.text()).not.toContain('Exact queue requirement');
  });

  it('fails closed when the restored review belongs to a different workflow run', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = reviewId;
    routeQuery.workflow_run_id = '00000000-0000-0000-0000-000000000799';
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/requirements/${requirementId}/review`)) return jsonResponse(exactReview());
      return new Response('not found', { status: 404 });
    }));

    const wrapper = mount(RequirementReviewView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });
    await flushPromises();

    expect(wrapper.find('[data-test="exact-review-restore-failed"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="review-next-step"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="start-review"]').attributes('disabled')).toBeDefined();
  });

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
