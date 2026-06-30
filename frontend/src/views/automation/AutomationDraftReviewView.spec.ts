import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import AutomationDraftReviewView from './AutomationDraftReviewView.vue';

describe('AutomationDraftReviewView', () => {
  it('creates, edits, and approves an automation draft without execution actions', async () => {
    const draftId = '00000000-0000-0000-0000-000000001001';
    const aiTaskId = '00000000-0000-0000-0000-000000001002';
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/automation/drafts') && init?.method === 'POST') {
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
            test_case_id: '00000000-0000-0000-0000-000000000901',
            requirement_id: null,
            ai_task_id: aiTaskId,
            target_framework: 'pytest',
            title: 'pytest draft for expired coupon',
            draft_code: 'def test_expired_coupon():\n    assert True\n',
            draft_language: 'python',
            suggested_file_path: 'tests/test_expired_coupon.py',
            execution_notes: 'Review and approve this draft before execution.',
            risk_notes: 'Mock fixture names need confirmation.',
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

    expect(wrapper.text()).toContain('自动化草稿');
    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('pytest draft for expired coupon');
    expect(wrapper.text()).toContain('tests/test_expired_coupon.py');
    expect(wrapper.text()).toContain('Mock fixture names need confirmation.');
    expect(wrapper.text()).toContain('draft_generated');
    expect(wrapper.text()).toContain('需要审批');
    expect(wrapper.text()).toContain('def test_expired_coupon');
    expect(wrapper.text()).not.toContain('执行草稿');
    expect(wrapper.text()).not.toContain('运行测试');

    await wrapper.find('[data-test="edit-draft"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('edited');

    await wrapper.find('[data-test="approve-draft"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('approved');
  });
});
