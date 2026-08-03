import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, describe, expect, it, vi } from 'vitest';

import TestCampaignScopeView from './TestCampaignScopeView.vue';

const pushMock = vi.fn();

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock }),
}));

const projectId = '00000000-0000-0000-0000-000000000101';
const environmentId = '00000000-0000-0000-0000-000000000201';
const campaignId = '00000000-0000-0000-0000-000000000701';
const requirementId = '00000000-0000-0000-0000-000000000301';
const riskId = '00000000-0000-0000-0000-000000000302';
const caseId = '00000000-0000-0000-0000-000000000401';
const approvalId = '00000000-0000-0000-0000-000000000501';

const settingsResponse = {
  project: { id: projectId, name: 'Checkout', default_language: 'python', default_test_type: 'functional' },
  modules: [],
  repositories: [],
  environments: [{ id: environmentId, name: 'staging', variables_json: {}, status: 'active' }],
  test_commands: [],
  tool_definitions: [],
};

describe('TestCampaignScopeView', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    pushMock.mockReset();
  });

  it('creates a scope draft with explicit environment, version, and exit conditions', async () => {
    let createBody: Record<string, unknown> | null = null;
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith(`/projects/${projectId}/settings`)) return jsonResponse(settingsResponse);
      if (url.endsWith(`/projects/${projectId}/test-campaigns`) && (init?.method ?? 'GET') === 'GET') {
        return jsonResponse([]);
      }
      if (url.endsWith(`/projects/${projectId}/test-campaigns`) && init?.method === 'POST') {
        createBody = JSON.parse(String(init.body));
        return jsonResponse(campaignResponse('draft', 0));
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);
    const wrapper = mountView();
    await flushPromises();

    expect(wrapper.text()).toContain('Scope');
    expect(wrapper.text()).toContain('未创建');

    await wrapper.find('[data-test="campaign-name"] input').setValue('Checkout 2026.08');
    await wrapper.find('[data-test="campaign-version"] input').setValue('release/2026.08');
    await wrapper.find('[data-test="campaign-scope"] textarea').setValue('验证支付与重试，排除营销页面。');
    await wrapper.find('[data-test="campaign-exit-conditions"] textarea').setValue('无严重缺陷\n高风险均有批准用例');
    await wrapper.find('[data-test="campaign-requirements"]').setValue(requirementId);
    await wrapper.find('[data-test="campaign-risks"]').setValue(riskId);
    await wrapper.find('[data-test="campaign-save"]').trigger('click');
    await flushPromises();

    expect(createBody).toEqual({
      name: 'Checkout 2026.08',
      scope_statement: '验证支付与重试，排除营销页面。',
      target_environment_id: environmentId,
      target_version_ref: 'release/2026.08',
      exit_conditions: ['无严重缺陷', '高风险均有批准用例'],
      requirement_ids: [requirementId],
      risk_ids: [riskId],
      test_plan_snapshot_ids: [],
      approved_case_ids: [],
      created_by: 'Default User',
    });
    expect(wrapper.text()).toContain('Snapshot 1');
    expect((wrapper.find('[data-test="campaign-name"] input').element as HTMLInputElement).value)
      .toBe('Checkout release 2026.08');
  });

  it('renders persisted coverage and sends exact workflow versions through continue', async () => {
    const requests: Array<{ url: string; body: Record<string, unknown> }> = [];
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? 'GET';
      if (url.endsWith(`/projects/${projectId}/settings`)) return jsonResponse(settingsResponse);
      if (url.endsWith(`/projects/${projectId}/test-campaigns`) && method === 'GET') {
        return jsonResponse([campaignResponse('draft', 0)]);
      }
      if (method === 'POST') {
        const body = JSON.parse(String(init?.body)) as Record<string, unknown>;
        requests.push({ url, body });
        if (url.endsWith('/submit')) return jsonResponse(campaignResponse('waiting_review', 1));
        if (url.endsWith('/complete-review')) return jsonResponse(campaignResponse('waiting_approval', 2));
        if (url.endsWith('/approve')) return jsonResponse(campaignResponse('approved', 3, approvalId));
        if (url.endsWith('/continue')) return jsonResponse(campaignResponse('draft', 4, null, 'requirement_review'));
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);
    const wrapper = mountView();
    await flushPromises();

    expect(wrapper.text()).toContain('Checkout succeeds');
    expect(wrapper.text()).toContain('已覆盖');
    expect(wrapper.text()).toContain('No selected approved case cites this requirement.');
    expect(wrapper.text()).toContain('缺口');

    await wrapper.find('[data-test="campaign-submit"]').trigger('click');
    await flushPromises();
    await wrapper.find('[data-test="campaign-complete"]').trigger('click');
    await flushPromises();
    await wrapper.find('[data-test="campaign-approve"]').trigger('click');
    await flushPromises();
    await wrapper.find('[data-test="campaign-continue"]').trigger('click');
    await flushPromises();

    expect(requests.map((request) => request.body.expected_version)).toEqual([0, 1, 2, 3]);
    expect(requests[3].body.approval_decision_id).toBe(approvalId);
    expect(pushMock).toHaveBeenCalledWith({ name: 'requirement-review' });
  });

  it('locks mutations after a workflow conflict until refresh', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith(`/projects/${projectId}/settings`)) return jsonResponse(settingsResponse);
      if (url.endsWith(`/projects/${projectId}/test-campaigns`) && (init?.method ?? 'GET') === 'GET') {
        return jsonResponse([campaignResponse('draft', 0)]);
      }
      if (url.endsWith('/submit')) {
        return jsonResponse(
          { error_code: 'WORKFLOW_CONCURRENT_MODIFICATION', message: 'Workflow action was rejected.', details: {} },
          409,
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);
    const wrapper = mountView();
    await flushPromises();

    await wrapper.find('[data-test="campaign-submit"]').trigger('click');
    await flushPromises();

    expect(wrapper.text()).toContain('刷新后才能继续操作');
    expect(wrapper.find('[data-test="campaign-save"]').attributes('disabled')).toBeDefined();
    expect(wrapper.find('[data-test="campaign-submit"]').attributes('disabled')).toBeDefined();
  });
});

function mountView() {
  return mount(TestCampaignScopeView, {
    global: { plugins: [createPinia(), ArcoVue] },
  });
}

function campaignResponse(
  state: string,
  version: number,
  currentApprovalId: string | null = null,
  stage = 'scope',
) {
  return {
    id: campaignId,
    project_id: projectId,
    name: 'Checkout release 2026.08',
    scope_statement: 'Validate checkout payment and retry behavior.',
    target_environment_id: environmentId,
    target_version_ref: 'release/2026.08',
    exit_conditions: ['No open critical defects'],
    requirement_ids: [requirementId],
    risk_ids: [],
    test_plan_snapshot_ids: [],
    approved_case_ids: [caseId],
    coverage_rows: [
      {
        kind: 'requirement',
        target_id: requirementId,
        label: 'Checkout succeeds',
        coverage_status: 'covered',
        evidence_case_ids: [caseId],
        evidence_snapshot_id: null,
        gap_reason: null,
      },
      {
        kind: 'risk',
        target_id: '00000000-0000-0000-0000-000000000302',
        label: 'Duplicate charge',
        coverage_status: 'gap',
        evidence_case_ids: [],
        evidence_snapshot_id: null,
        gap_reason: 'No selected approved case cites this requirement.',
      },
    ],
    status: 'active',
    workflow: {
      run_id: '00000000-0000-0000-0000-000000000801',
      stage,
      state,
      lock_version: version,
      snapshot_id: `00000000-0000-0000-0000-00000000090${version}`,
      snapshot_hash: `sha256:${String(version).padStart(64, '0')}`,
      snapshot_iteration: version === 0 ? 1 : version,
      approval_decision_id: currentApprovalId,
      can_continue: state === 'approved' && Boolean(currentApprovalId),
    },
    created_at: '2026-08-03T08:00:00+00:00',
    updated_at: '2026-08-03T08:00:00+00:00',
  };
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
