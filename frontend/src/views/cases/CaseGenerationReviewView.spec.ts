import { flushPromises, mount, type VueWrapper } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { useCasesStore } from '../../stores/cases';
import CaseGenerationReviewView from './CaseGenerationReviewView.vue';

const projectId = '00000000-0000-0000-0000-000000000101';
const requirementId = '00000000-0000-0000-0000-000000000411';
const requirementReviewId = '00000000-0000-0000-0000-000000000611';
const workflowRunId = '00000000-0000-0000-0000-000000000c01';
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

function exactRequirement() {
  return {
    id: requirementId,
    project_id: projectId,
    module_id: null,
    title: 'Exact CaseReview requirement',
    content: 'Restore this exact case review only.',
    source_type: 'manual',
    source_ref: 'REQ-CASE-EXACT',
    status: 'active',
    created_at: '2026-08-04T00:00:00Z',
    updated_at: '2026-08-04T00:00:00Z',
  };
}

function exactRequirementReview() {
  return {
    id: requirementReviewId,
    requirement_id: requirementId,
    overall_score: 90,
    scores: { completeness: 90, clarity: 90, consistency: 90, testability: 90, feasibility: 90, logic: 90 },
    issues: [],
    clarification_questions: [],
    test_design_notes: [],
    risk_items: [{ title: 'Exact queue risk', risk_level: 'high', suggestion: 'Review it.' }],
    used_knowledge: false,
    used_context_artifact_ids: [],
    context_manifest_artifact_id: null,
    status: 'reviewed',
  };
}

function exactCaseReview(overrides: {
  project_id?: string;
  requirement_review_id?: string;
  stage?: string;
  run_id?: string;
} = {}) {
  return {
    project_id: overrides.project_id ?? projectId,
    requirement_review_id: overrides.requirement_review_id ?? requirementReviewId,
    workflow: {
      run_id: overrides.run_id ?? workflowRunId,
      stage: overrides.stage ?? 'case_review',
      state: 'waiting_approval',
      lock_version: 3,
      snapshot_id: '00000000-0000-0000-0000-000000000c02',
      approval_decision_id: null,
      can_submit: false,
      can_complete_review: false,
      can_edit: true,
      can_approve: true,
      can_continue: false,
    },
    source_test_plan_review_snapshot_id: '00000000-0000-0000-0000-000000000b01',
    source_test_plan_review_snapshot_hash: 'sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    test_strategy: 'Cover the exact queue risk.',
    plan_items: [{ title: 'Exact coverage', risk_level: 'high' }],
    generated_candidate_ids: ['00000000-0000-0000-0000-000000000801'],
    candidate_decisions: [],
  };
}

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
    Object.keys(routeQuery).forEach((key) => delete routeQuery[key]);
    vi.unstubAllGlobals();
  });

  it('restores the exact CaseReview and WorkflowRun requested by the queue route', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'case_review';
    window.localStorage.setItem('chtest.latestRequirementReview', JSON.stringify({
      projectId: '00000000-0000-0000-0000-000000000199',
      requirementId: '00000000-0000-0000-0000-000000000499',
      requirementReviewId: '00000000-0000-0000-0000-000000000699',
    }));
    const requestedUrls: string[] = [];
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      requestedUrls.push(url);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/requirements/${requirementId}/review`)) return jsonResponse(exactRequirementReview());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${requirementReviewId}/case-review`)) {
        return jsonResponse(exactCaseReview());
      }
      return new Response('not found', { status: 404 });
    }));
    const pinia = createPinia();

    const wrapper = mount(CaseGenerationReviewView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    const store = useCasesStore(pinia);
    expect(store.projectId).toBe(projectId);
    expect(store.requirementId).toBe(requirementId);
    expect(store.requirementReviewId).toBe(requirementReviewId);
    expect(store.caseReviewWorkflow?.workflow.run_id).toBe(workflowRunId);
    expect(store.caseReviewWorkflow?.workflow.stage).toBe('case_review');
    expect(wrapper.find('[data-test="case-review-workflow-panel"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="start-case-generation"]').attributes('disabled')).toBeDefined();
    expect(requestedUrls.some((url) => url.includes('00000000-0000-0000-0000-000000000499'))).toBe(false);
    expect(requestedUrls.some((url) => url.endsWith(`/projects/${projectId}/requirements`))).toBe(false);
  });

  it.each([
    ['project identity', { project_id: '00000000-0000-0000-0000-000000000199' }],
    ['review identity', { requirement_review_id: '00000000-0000-0000-0000-000000000699' }],
    ['workflow stage', { stage: 'automation_plan_review' }],
    ['workflow run', { run_id: '00000000-0000-0000-0000-000000000c99' }],
  ])('fails closed when the restored CaseReview has a mismatched %s', async (_label, gateOverrides) => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'case_review';
    window.localStorage.setItem('chtest.latestRequirementReview', JSON.stringify({
      projectId,
      requirementId: '00000000-0000-0000-0000-000000000499',
      requirementReviewId: '00000000-0000-0000-0000-000000000699',
    }));
    const requestedUrls: string[] = [];
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      requestedUrls.push(url);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/requirements/${requirementId}/review`)) return jsonResponse(exactRequirementReview());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${requirementReviewId}/case-review`)) {
        return jsonResponse(exactCaseReview(gateOverrides));
      }
      return new Response('not found', { status: 404 });
    }));
    const pinia = createPinia();
    const store = useCasesStore(pinia);
    store.selectedCandidateId = '00000000-0000-0000-0000-000000000899';
    store.caseReviewWorkflow = exactCaseReview();

    const wrapper = mount(CaseGenerationReviewView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    expect(store.exactRestoreFailed).toBe(true);
    expect(store.requirementId).toBe('');
    expect(store.requirementReviewId).toBe('');
    expect(store.caseReviewWorkflow).toBeNull();
    expect(store.candidates).toEqual([]);
    expect(store.selectedCandidateId).toBe('');
    expect(wrapper.find('[data-test="exact-case-review-restore-failed"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="case-review-workflow-panel"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="start-case-generation"]').attributes('disabled')).toBeDefined();
    expect(requestedUrls.some((url) => url.includes('00000000-0000-0000-0000-000000000499'))).toBe(false);
    expect(requestedUrls.some((url) => url.endsWith(`/projects/${projectId}/requirements`))).toBe(false);
  });

  it('fails closed without network or browser-context fallback when an exact route parameter is missing', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_stage = 'case_review';
    window.localStorage.setItem('chtest.latestRequirementReview', JSON.stringify({
      projectId,
      requirementId: '00000000-0000-0000-0000-000000000499',
      requirementReviewId: '00000000-0000-0000-0000-000000000699',
    }));
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    const pinia = createPinia();

    const wrapper = mount(CaseGenerationReviewView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    const store = useCasesStore(pinia);
    expect(fetchMock).not.toHaveBeenCalled();
    expect(store.exactRestoreFailed).toBe(true);
    expect(store.requirementId).toBe('');
    expect(store.requirementReviewId).toBe('');
    expect(store.caseReviewWorkflow).toBeNull();
    expect(wrapper.find('[data-test="exact-case-review-restore-failed"]').exists()).toBe(true);
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
        review: {
          risk_items: [{ title: '结算互斥规则' }, { title: '金额边界' }],
          clarification_questions: ['优惠券是否支持叠加？'],
        },
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
    expect(wrapper.text()).toContain('风险：结算互斥规则、金额边界，以及 1 个待澄清项已纳入本次生成范围');
    expect(wrapper.text()).not.toContain('插枪');

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
        use_knowledge: true,
        context_artifact_ids: [],
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
    expect(wrapper.find('[data-test="case-generation-review-page"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="recent-generation-run"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="resume-generation-review"]').exists()).toBe(true);
    await wrapper.find('[data-test="resume-generation-review"]').trigger('click');

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
        use_knowledge: true,
        context_artifact_ids: [],
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
    expect(wrapper.text()).toContain('需要从需求评审页进入，系统才能自动带入完整评审结果。');
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

  it('recovers the latest reviewed requirement when browser workflow context is absent', async () => {
    window.localStorage.setItem(
      'chtest.latestRequirementReview',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        requirementId: '00000000-0000-0000-0000-000000000499',
        requirementReviewId: '00000000-0000-0000-0000-000000000699',
      }),
    );
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirements')) {
        return new Response(
          JSON.stringify({
            items: [
              {
                id: '00000000-0000-0000-0000-000000000411',
                project_id: '00000000-0000-0000-0000-000000000101',
                module_id: null,
                title: 'Recovered reviewed requirement',
                content: 'A reviewed requirement available from the project.',
                source_type: 'manual',
                source_ref: null,
                status: 'active',
                created_at: '2026-07-24T10:00:00Z',
                updated_at: '2026-07-24T10:00:00Z',
              },
            ],
            total: 1,
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/requirements/00000000-0000-0000-0000-000000000411/review')) {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000000611',
            requirement_id: '00000000-0000-0000-0000-000000000411',
            overall_score: 82,
            scores: { completeness: 80, clarity: 80, consistency: 80, testability: 80, feasibility: 80, logic: 80 },
            issues: [],
            clarification_questions: [],
            risk_items: [{ title: 'Recovered risk', risk_level: 'high', suggestion: 'Cover the risk.' }],
            used_knowledge: false,
            used_context_artifact_ids: [],
            context_manifest_artifact_id: null,
            status: 'reviewed',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
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
      global: { plugins: [createPinia(), ArcoVue] },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect((wrapper.find('[data-test="requirement-id-input"] input').element as HTMLInputElement).value).toBe(
      '00000000-0000-0000-0000-000000000411',
    );
    expect((wrapper.find('[data-test="requirement-review-id-input"] input').element as HTMLInputElement).value).toBe(
      '00000000-0000-0000-0000-000000000611',
    );
  });

  it('renders the persisted CaseReview gate and advances it with project-scoped actions', async () => {
    let caseReviewActionBody: unknown = null;
    window.localStorage.setItem(
      'chtest.latestRequirementReview',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        requirementId: '00000000-0000-0000-0000-000000000411',
        requirementReviewId: '00000000-0000-0000-0000-000000000611',
        review: {
          risk_items: [{ title: 'High-risk coupon boundary' }],
          clarification_questions: [],
        },
      }),
    );
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirements')) {
        return new Response(
          JSON.stringify({
            items: [
              {
                id: '00000000-0000-0000-0000-000000000411',
                project_id: '00000000-0000-0000-0000-000000000101',
                module_id: null,
                title: 'Coupon checkout rules',
                content: 'Coupon cannot be used with points.',
                source_type: 'manual',
                source_ref: null,
                status: 'active',
                created_at: '2026-07-29T10:00:00Z',
                updated_at: '2026-07-29T10:00:00Z',
              },
            ],
            total: 1,
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/requirements/00000000-0000-0000-0000-000000000411/review')) {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000000611',
            requirement_id: '00000000-0000-0000-0000-000000000411',
            overall_score: 88,
            scores: { completeness: 90, clarity: 90, consistency: 88, testability: 88, feasibility: 88, logic: 88 },
            issues: [],
            clarification_questions: [],
            risk_items: [{ title: 'High-risk coupon boundary', risk_level: 'high', suggestion: 'Cover the risk.' }],
            used_knowledge: false,
            used_context_artifact_ids: [],
            context_manifest_artifact_id: null,
            status: 'reviewed',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirement-documents')) {
        return new Response(JSON.stringify({ items: [], total: 0 }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirement-reviews/00000000-0000-0000-0000-000000000611/case-review')) {
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            requirement_review_id: '00000000-0000-0000-0000-000000000611',
            workflow: {
              run_id: '00000000-0000-0000-0000-000000000c01',
              stage: 'case_review',
              state: 'waiting_approval',
              lock_version: 3,
              snapshot_id: '00000000-0000-0000-0000-000000000c02',
              approval_decision_id: null,
              can_submit: false,
              can_complete_review: false,
              can_edit: true,
              can_approve: true,
              can_continue: false,
            },
            source_test_plan_review_snapshot_id: '00000000-0000-0000-0000-000000000b01',
            source_test_plan_review_snapshot_hash: 'sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            test_strategy: 'Cover the high-risk coupon boundary.',
            plan_items: [{ title: 'Boundary coverage', risk_level: 'high' }],
            generated_candidate_ids: [
              '00000000-0000-0000-0000-000000000801',
              '00000000-0000-0000-0000-000000000802',
            ],
            candidate_decisions: [
              {
                candidate_id: '00000000-0000-0000-0000-000000000801',
                status: 'approved',
                review_comment: 'Promote this candidate.',
                test_case_id: '00000000-0000-0000-0000-000000000901',
              },
              {
                candidate_id: '00000000-0000-0000-0000-000000000802',
                status: 'rejected',
                review_comment: 'Outside scope.',
                test_case_id: null,
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (
        url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirement-reviews/00000000-0000-0000-0000-000000000611/case-review/approve-and-continue') &&
        init?.method === 'POST'
      ) {
        caseReviewActionBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            requirement_review_id: '00000000-0000-0000-0000-000000000611',
            workflow: {
              run_id: '00000000-0000-0000-0000-000000000c01',
              stage: 'automation_plan_review',
              state: 'draft',
              lock_version: 4,
              snapshot_id: '00000000-0000-0000-0000-000000000c03',
              approval_decision_id: '00000000-0000-0000-0000-000000000d01',
              can_submit: false,
              can_complete_review: false,
              can_edit: false,
              can_approve: false,
              can_continue: false,
            },
            source_test_plan_review_snapshot_id: '00000000-0000-0000-0000-000000000b01',
            source_test_plan_review_snapshot_hash: 'sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            test_strategy: 'Cover the high-risk coupon boundary.',
            plan_items: [{ title: 'Boundary coverage', risk_level: 'high' }],
            generated_candidate_ids: [
              '00000000-0000-0000-0000-000000000801',
              '00000000-0000-0000-0000-000000000802',
            ],
            candidate_decisions: [],
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

    expect(wrapper.find('[data-test="case-review-workflow-panel"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('CaseReview gate');
    expect(wrapper.text()).toContain('case_review');
    await wrapper.find('[data-test="case-review-approve-continue"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(caseReviewActionBody).toEqual(
      expect.objectContaining({
        expected_version: 3,
        comment: 'Case review approved and advanced.',
      }),
    );
    expect(wrapper.text()).toContain('automation_plan_review');
  });
});
