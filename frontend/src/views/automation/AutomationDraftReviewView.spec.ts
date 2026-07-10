import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, describe, expect, it, vi } from 'vitest';

import AutomationDraftReviewView from './AutomationDraftReviewView.vue';
import { useAutomationStore } from '../../stores/automation';

describe('AutomationDraftReviewView', () => {
  afterEach(() => {
    window.localStorage.clear();
    vi.unstubAllGlobals();
  });

  it('creates an approved automation plan before generating and approving a draft', async () => {
    const latestTestCaseId = '00000000-0000-0000-0000-000000000955';
    const planId = '00000000-0000-0000-0000-000000000p01'.replace('p', 'a');
    const draftId = '00000000-0000-0000-0000-000000001001';
    const aiTaskId = '00000000-0000-0000-0000-000000001002';
    let planBody: unknown = null;

    window.localStorage.setItem(
      'chtest.latestApprovedTestCase',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        testCaseId: latestTestCaseId,
        sourceCandidateId: '00000000-0000-0000-0000-000000000801',
        reviewStatus: 'approved_after_edit',
      }),
    );

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/automation/plans') && init?.method === 'POST') {
        planBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            id: planId,
            project_id: '00000000-0000-0000-0000-000000000101',
            test_case_id: latestTestCaseId,
            requirement_id: '00000000-0000-0000-0000-000000000401',
            requirement_review_id: '00000000-0000-0000-0000-000000000601',
            source_candidate_id: '00000000-0000-0000-0000-000000000801',
            ai_task_id: '00000000-0000-0000-0000-000000000a01',
            knowledge_retrieval_artifact_id: '00000000-0000-0000-0000-000000000e01',
            target_framework: 'pytest',
            title: 'pytest automation plan for expired coupon',
            plan: { source: 'reviewed_test_case' },
            execution_steps: ['Prepare precondition: expired coupon', 'Automate step: submit order'],
            test_data: { coupon_state: 'expired' },
            dependency_notes: 'Requires pytest and project-local fixtures.',
            risk_notes: 'Review selectors and fixtures.',
            used_context_artifact_ids: ['00000000-0000-0000-0000-000000000c01'],
            status: 'plan_generated',
            review_comment: null,
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith(`/automation/plans/${planId}/approve`) && init?.method === 'POST') {
        return new Response(JSON.stringify({ automation_plan_id: planId, status: 'approved' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith(`/automation/plans/${planId}/generate-draft`) && init?.method === 'POST') {
        return new Response(
          JSON.stringify({ automation_draft_id: draftId, ai_task_id: aiTaskId, status: 'draft_generated' }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith(`/automation/drafts/${draftId}`) && (!init?.method || init.method === 'GET')) {
        return new Response(
          JSON.stringify({
            id: draftId,
            project_id: '00000000-0000-0000-0000-000000000101',
            test_case_id: latestTestCaseId,
            requirement_id: '00000000-0000-0000-0000-000000000401',
            ai_task_id: aiTaskId,
            automation_plan_id: planId,
            target_framework: 'pytest',
            title: 'pytest draft for expired coupon',
            draft_code: 'def test_expired_coupon():\n    assert True\n',
            draft_language: 'python',
            suggested_file_path: 'tests/test_expired_coupon.py',
            execution_notes: 'Generated from an approved AutomationPlan.',
            risk_notes: 'Review selectors and fixtures.',
            execution_strategy: 'artifact_runtime_copy',
            approval_required: true,
            status: 'draft_generated',
            review_comment: null,
            runtime_artifact_id: null,
            promoted_artifact_id: null,
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith(`/automation/drafts/${draftId}`) && init?.method === 'PATCH') {
        return new Response(JSON.stringify({ automation_draft_id: draftId, status: 'edited' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith(`/automation/drafts/${draftId}/approve`) && init?.method === 'POST') {
        return new Response(JSON.stringify({ automation_draft_id: draftId, status: 'approved' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/review-history?') && url.includes('entity_type=AutomationPlan')) {
        const hasApproveCall = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith(`/automation/plans/${planId}/approve`) && call[1]?.method === 'POST',
        );
        const hasGenerateCall = fetchMock.mock.calls.some(
          (call) =>
            String(call[0]).endsWith(`/automation/plans/${planId}/generate-draft`) && call[1]?.method === 'POST',
        );
        const items = [];
        if (hasGenerateCall) {
          items.push({
            id: '00000000-0000-0000-0000-000000000h02'.replace('h', 'b'),
            project_id: '00000000-0000-0000-0000-000000000101',
            entity_type: 'AutomationPlan',
            entity_id: planId,
            related_entity_type: 'AutomationDraft',
            related_entity_id: draftId,
            action: 'generate_draft',
            from_status: 'approved',
            to_status: 'draft_generated',
            reviewer: 'Default User',
            comment: 'Generated AutomationDraft from approved AutomationPlan.',
            evidence_artifact_ids: [],
            metadata_json: {},
            created_at: '2026-07-01T02:22:00Z',
          });
        }
        if (hasApproveCall) {
          items.push({
            id: '00000000-0000-0000-0000-000000000h01'.replace('h', 'b'),
            project_id: '00000000-0000-0000-0000-000000000101',
            entity_type: 'AutomationPlan',
            entity_id: planId,
            related_entity_type: null,
            related_entity_id: null,
            action: 'approve',
            from_status: 'plan_generated',
            to_status: 'approved',
            reviewer: 'Default User',
            comment: '前端批准自动化方案',
            evidence_artifact_ids: [],
            metadata_json: {},
            created_at: '2026-07-01T02:20:00Z',
          });
        }
        return new Response(JSON.stringify({ items, total: items.length }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/review-history?') && url.includes('entity_type=AutomationDraft')) {
        const hasApproveCall = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith(`/automation/drafts/${draftId}/approve`) && call[1]?.method === 'POST',
        );
        const hasEditCall = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith(`/automation/drafts/${draftId}`) && call[1]?.method === 'PATCH',
        );
        const items = [];
        if (hasApproveCall) {
          items.push({
            id: '00000000-0000-0000-0000-000000001a02',
            project_id: '00000000-0000-0000-0000-000000000101',
            entity_type: 'AutomationDraft',
            entity_id: draftId,
            related_entity_type: 'AutomationPlan',
            related_entity_id: planId,
            action: 'approve',
            from_status: 'edited',
            to_status: 'approved',
            reviewer: 'Default User',
            comment: '前端批准草稿',
            evidence_artifact_ids: ['00000000-0000-0000-0000-000000001e02'],
            metadata_json: {},
            created_at: '2026-07-01T02:25:00Z',
          });
        }
        if (hasEditCall) {
          items.push({
            id: '00000000-0000-0000-0000-000000001a01',
            project_id: '00000000-0000-0000-0000-000000000101',
            entity_type: 'AutomationDraft',
            entity_id: draftId,
            related_entity_type: 'AutomationPlan',
            related_entity_id: planId,
            action: 'edit',
            from_status: 'draft_generated',
            to_status: 'edited',
            reviewer: 'Default User',
            comment: '前端评审编辑',
            evidence_artifact_ids: ['00000000-0000-0000-0000-000000001e01'],
            metadata_json: {},
            created_at: '2026-07-01T02:23:00Z',
          });
        }
        return new Response(JSON.stringify({ items, total: items.length }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(AutomationDraftReviewView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(planBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        test_case_id: latestTestCaseId,
        target_framework: 'pytest',
        use_knowledge: true,
      }),
    );
    expect(wrapper.text()).toContain('AutomationPlan');
    expect(wrapper.text()).toContain('pytest automation plan for expired coupon');
    expect(wrapper.text()).toContain('Prepare precondition: expired coupon');

    await wrapper.find('[data-test="approve-plan"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('approved');
    expect(wrapper.text()).toContain('方案评审历史');
    expect(wrapper.text()).toContain('前端批准自动化方案');

    await wrapper.find('[data-test="generate-draft-from-plan"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('pytest draft for expired coupon');
    expect(wrapper.text()).toContain('tests/test_expired_coupon.py');
    expect(wrapper.text()).toContain('Generated from an approved AutomationPlan.');
    expect(wrapper.text()).toContain('draft_generated');
    expect(wrapper.text()).toContain('def test_expired_coupon');
    expect(wrapper.text()).toContain('Quality gate');
    expect(wrapper.text()).toContain('fake, stub, placeholder, or assert True-only drafts cannot be approved.');
    expect(wrapper.text()).not.toContain('执行草稿');
    expect(wrapper.text()).not.toContain('运行测试');

    await wrapper.find('[data-test="edit-draft"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('edited');
    expect(wrapper.text()).toContain('本地评审历史');
    expect(wrapper.text()).toContain('Default User');
    expect(wrapper.text()).toContain('前端评审编辑');
    expect(wrapper.text()).toContain('证据 1');

    await wrapper.find('[data-test="approve-draft"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('approved');
    expect(wrapper.text()).toContain('前端批准草稿');
    expect(fetchMock).toHaveBeenCalledWith(
      `/api/review-history?project_id=00000000-0000-0000-0000-000000000101&entity_type=AutomationDraft&entity_id=${draftId}&limit=20`,
      expect.objectContaining({ headers: expect.objectContaining({ Accept: 'application/json' }) }),
    );
  });

  it('shows the quality gate error when placeholder draft approval is rejected', async () => {
    const draftId = '00000000-0000-0000-0000-000000001101';
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith(`/automation/drafts/${draftId}/approve`) && init?.method === 'POST') {
        return new Response(
          JSON.stringify({
            error_code: 'AUTOMATION_DRAFT_QUALITY_GATE_FAILED',
            message: 'Automation draft must contain non-placeholder executable test code before approval.',
            details: {},
          }),
          { status: 400, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const pinia = createPinia();
    const wrapper = mount(AutomationDraftReviewView, {
      global: {
        plugins: [pinia, ArcoVue],
      },
    });
    const store = useAutomationStore();
    store.draft = {
      id: draftId,
      project_id: '00000000-0000-0000-0000-000000000101',
      test_case_id: '00000000-0000-0000-0000-000000000955',
      requirement_id: null,
      ai_task_id: '00000000-0000-0000-0000-000000001102',
      automation_plan_id: null,
      target_framework: 'pytest',
      title: 'placeholder draft',
      draft_code: 'def test_placeholder():\n    assert True\n',
      draft_language: 'python',
      suggested_file_path: 'tests/test_placeholder.py',
      execution_notes: 'Generated draft.',
      risk_notes: 'Uses fake adapter.',
      execution_strategy: 'artifact_runtime_copy',
      approval_required: true,
      status: 'draft_generated',
      review_comment: null,
      runtime_artifact_id: null,
      promoted_artifact_id: null,
    };
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('Quality gate');
    expect(wrapper.text()).toContain('fake, stub, placeholder, or assert True-only drafts cannot be approved.');

    await wrapper.find('[data-test="approve-draft"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('Automation draft must contain non-placeholder executable test code before approval.');
    expect(wrapper.text()).toContain('AUTOMATION_DRAFT_QUALITY_GATE_FAILED');
    expect(store.draft.status).toBe('draft_generated');
  });
});
