import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { useExecutionStore } from '../../stores/execution';
import PytestExecutionView from './PytestExecutionView.vue';

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
    title: 'Exact ExecutionApproval requirement',
    content: 'Restore only the authoritative execution approval gate.',
    source_type: 'manual',
    source_ref: 'REQ-EXECUTION-EXACT',
    status: 'active',
    created_at: '2026-08-04T00:00:00Z',
    updated_at: '2026-08-04T00:00:00Z',
  };
}

function exactRequirementReview() {
  return {
    id: requirementReviewId,
    requirement_id: requirementId,
    overall_score: 93,
    scores: { completeness: 93, clarity: 93, consistency: 93, testability: 93, feasibility: 93, logic: 93 },
    issues: [],
    clarification_questions: [],
    test_design_notes: [],
    risk_items: [],
    used_knowledge: false,
    used_context_artifact_ids: [],
    context_manifest_artifact_id: null,
    status: 'reviewed',
  };
}

function exactExecutionApproval(overrides: {
  project_id?: string;
  requirement_review_id?: string;
  stage?: string;
  run_id?: string;
  state?: string;
} = {}) {
  return {
    ...executionApprovalBody(),
    project_id: overrides.project_id ?? projectId,
    requirement_review_id: overrides.requirement_review_id ?? requirementReviewId,
    workflow: {
      ...executionApprovalBody().workflow,
      run_id: overrides.run_id ?? workflowRunId,
      stage: overrides.stage ?? 'execution_approval',
      state: overrides.state ?? 'waiting_approval',
      lock_version: 4,
      approval_decision_id: null,
      can_approve: true,
      can_continue: false,
    },
  };
}

function testRunBody() {
  return {
    id: '00000000-0000-0000-0000-000000001301',
    project_id: '00000000-0000-0000-0000-000000000101',
    automation_draft_id: '00000000-0000-0000-0000-000000001001',
    test_command_id: null,
    tool_invocation_id: null,
    name: 'pytest approved draft',
    command: 'pytest tests/test_generated_ok.py -q',
    working_directory: '/tmp/chtest-test-run',
    runner_mode: 'local_subprocess',
    run_workspace: '/tmp/chtest-test-run',
    repository_readonly: true,
    network_enabled: false,
    runtime_artifact_ids: [
      '00000000-0000-0000-0000-000000001201',
      '00000000-0000-0000-0000-000000001202',
    ],
    dependency_snapshot_artifact_id: '00000000-0000-0000-0000-000000001402',
    environment_snapshot_artifact_id: null,
    status: 'passed',
    exit_code: 0,
    duration_ms: 518,
    parsed_result: {
      total: 1,
      passed: 1,
      failed: 0,
      skipped: 0,
      error: 0,
    },
    test_results: [
      {
        id: '00000000-0000-0000-0000-000000001331',
        project_id: '00000000-0000-0000-0000-000000000101',
        test_run_id: '00000000-0000-0000-0000-000000001301',
        test_name: 'generated::test_generated_ok',
        test_file: 'generated',
        status: 'passed',
        duration_ms: null,
        failure_message: null,
        failure_artifact_ids: [],
        metadata: { source: 'pytest_runner' },
      },
    ],
    artifacts: [
      {
        id: '00000000-0000-0000-0000-000000001201',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001301',
        artifact_type: 'automation_draft_code',
        file_path: 'automation-drafts/00000000-0000-0000-0000-000000001001/runtime/test_from_draft.py',
        mime_type: 'text/plain',
        size_bytes: 128,
        sha256: 'sha256:runtime',
        metadata_json: { created_by_component: 'PytestRunner' },
      },
      {
        id: '00000000-0000-0000-0000-000000001401',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001301',
        artifact_type: 'stdout',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001301/stdout.log',
        mime_type: 'text/plain',
        size_bytes: 64,
        sha256: 'sha256:stdout',
        metadata_json: { created_by_component: 'PytestRunner' },
      },
      {
        id: '00000000-0000-0000-0000-000000001402',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001301',
        artifact_type: 'dependency_snapshot',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001301/dependency_snapshot.json',
        mime_type: 'application/json',
        size_bytes: 96,
        sha256: 'sha256:dependency',
        metadata_json: { created_by_component: 'PytestRunner' },
      },
      {
        id: '00000000-0000-0000-0000-000000001404',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001301',
        artifact_type: 'parsed_output',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001301/parsed_result.json',
        mime_type: 'application/json',
        size_bytes: 80,
        sha256: 'sha256:parsed',
        metadata_json: { created_by_component: 'PytestRunner' },
      },
    ],
  };
}

function executionApprovalBody() {
  return {
    project_id: '00000000-0000-0000-0000-000000000101',
    requirement_review_id: '00000000-0000-0000-0000-000000000601',
    workflow: {
      run_id: '00000000-0000-0000-0000-000000009001',
      stage: 'execution_approval',
      state: 'approved',
      lock_version: 8,
      snapshot_id: '00000000-0000-0000-0000-000000009002',
      approval_decision_id: '00000000-0000-0000-0000-000000009003',
      can_submit: false,
      can_complete_review: false,
      can_edit: true,
      can_approve: false,
      can_execute: true,
      can_continue: true,
    },
    source_automation_draft_review_snapshot_id: '00000000-0000-0000-0000-000000008002',
    source_automation_draft_review_snapshot_hash: 'sha256:draft-review',
    source_automation_plan_review_snapshot_id: '00000000-0000-0000-0000-000000007002',
    source_automation_plan_review_snapshot_hash: 'sha256:plan-review',
    source_case_review_snapshot_id: '00000000-0000-0000-0000-000000006002',
    source_case_review_snapshot_hash: 'sha256:case-review',
    approved_automation_plan_ids: ['00000000-0000-0000-0000-000000001101'],
    approved_test_case_ids: ['00000000-0000-0000-0000-000000000955'],
    approved_automation_draft_ids: ['00000000-0000-0000-0000-000000001001'],
    generated_test_run_ids: [],
    draft_decisions: [],
    execution_decisions: [],
  };
}

describe('PytestExecutionView', () => {
  beforeEach(() => {
    window.localStorage.clear();
    Object.keys(routeQuery).forEach((key) => delete routeQuery[key]);
  });
  afterEach(() => vi.unstubAllGlobals());

  it('restores the exact ExecutionApproval and uses its server lock for actions', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'execution_approval';
    window.localStorage.setItem('chtest.latestAutomationDraft', JSON.stringify({
      projectId,
      requirementReviewId: '00000000-0000-0000-0000-000000000699',
      automationDraftId: '00000000-0000-0000-0000-000000001999',
      status: 'approved',
      targetFramework: 'pytest',
    }));
    window.localStorage.setItem('chtest.execution.recent-runs', JSON.stringify([testRunBody()]));
    let actionBody: unknown = null;
    const requestedUrls: string[] = [];
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      requestedUrls.push(url);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/requirements/${requirementId}/review`)) return jsonResponse(exactRequirementReview());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-approval`) && !init?.method) {
        return jsonResponse(exactExecutionApproval());
      }
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-approval/approve`) && init?.method === 'POST') {
        actionBody = JSON.parse(String(init.body));
        return jsonResponse(exactExecutionApproval({ state: 'approved' }));
      }
      return new Response('not found', { status: 404 });
    }));
    const pinia = createPinia();

    const wrapper = mount(PytestExecutionView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    const store = useExecutionStore(pinia);
    expect(store.requirementReviewId).toBe(requirementReviewId);
    expect(store.automationDraftId).toBe('');
    expect(store.testCommandId).toBe('');
    expect(store.run).toBeNull();
    expect(store.recentRuns).toEqual([]);
    expect(store.executionApprovalWorkflow?.workflow.run_id).toBe(workflowRunId);
    expect(wrapper.find('[data-test="execution-approval-panel"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="execution-approval-edit"]').attributes('disabled')).toBeDefined();
    expect(wrapper.find('[data-test="start-run"]').attributes('disabled')).toBeDefined();
    expect(wrapper.find('[data-test="execution-recent-runs"]').exists()).toBe(false);
    expect(requestedUrls.some((url) => url.includes('00000000-0000-0000-0000-000000001999'))).toBe(false);

    await wrapper.find('[data-test="execution-approval-approve"]').trigger('click');
    await flushPromises();
    expect(actionBody).toEqual(expect.objectContaining({
      expected_version: 4,
      comment: 'Approved for controlled local pytest execution.',
    }));
  });

  it.each([
    ['project identity', { project_id: '00000000-0000-0000-0000-000000000199' }],
    ['review identity', { requirement_review_id: '00000000-0000-0000-0000-000000000699' }],
    ['workflow stage', { stage: 'execution_result_review' }],
    ['workflow run', { run_id: '00000000-0000-0000-0000-000000000c99' }],
  ])('fails closed when the restored ExecutionApproval has a mismatched %s', async (_label, gateOverrides) => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'execution_approval';
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/requirements/${requirementId}/review`)) return jsonResponse(exactRequirementReview());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-approval`)) {
        return jsonResponse(exactExecutionApproval(gateOverrides));
      }
      return new Response('not found', { status: 404 });
    }));
    const pinia = createPinia();
    const store = useExecutionStore(pinia);
    store.automationDraftId = '00000000-0000-0000-0000-000000001999';
    store.run = testRunBody();

    const wrapper = mount(PytestExecutionView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    expect(store.exactRestoreFailed).toBe(true);
    expect(store.requirementReviewId).toBe('');
    expect(store.automationDraftId).toBe('');
    expect(store.testCommandId).toBe('');
    expect(store.run).toBeNull();
    expect(store.executionApprovalWorkflow).toBeNull();
    expect(wrapper.find('[data-test="exact-execution-approval-restore-failed"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="execution-approval-panel"]').exists()).toBe(false);
  });

  it('fails closed without network or recent context when an ExecutionApproval route parameter is missing', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_stage = 'execution_approval';
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(PytestExecutionView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });
    await flushPromises();

    expect(fetchMock).not.toHaveBeenCalled();
    expect(wrapper.find('[data-test="exact-execution-approval-restore-failed"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="execution-approval-panel"]').exists()).toBe(false);
  });

  it('starts and refreshes a pytest run with evidence details', async () => {
    window.localStorage.setItem(
      'chtest.latestAutomationDraft',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        testCaseId: '00000000-0000-0000-0000-000000000955',
        automationDraftId: '00000000-0000-0000-0000-000000001001',
        status: 'approved',
        targetFramework: 'pytest',
      }),
    );
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/test-runs') && init?.method === 'POST') {
        return new Response(JSON.stringify(testRunBody()), {
          status: 202,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/test-runs/00000000-0000-0000-0000-000000001301')) {
        return new Response(JSON.stringify({ ...testRunBody(), duration_ms: 620 }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(PytestExecutionView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    expect(wrapper.text()).toContain('执行中心');
    expect(wrapper.text()).toContain('已批准自动化草稿');
    expect((wrapper.find('[data-test="execution-source-id"] input').element as HTMLInputElement).value).toBe(
      '00000000-0000-0000-0000-000000001001',
    );
    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('通过');
    expect(wrapper.text()).toContain('pytest tests/test_generated_ok.py -q');
    expect(wrapper.text()).toContain('/tmp/chtest-test-run');
    expect(wrapper.text()).toContain('local_subprocess');
    expect(wrapper.text()).toContain('执行命令');
    expect(wrapper.text()).toContain('工作目录');
    expect(wrapper.text()).toContain('运行器模式');
    expect(wrapper.text()).toContain('仓库只读策略');
    expect(wrapper.text()).toContain('网络策略');
    expect(wrapper.text()).toContain('关闭');
    expect(wrapper.text()).toContain('执行运行清单');
    expect(wrapper.text()).toContain('运行工作区');
    expect(wrapper.text()).toContain('只读挂载');
    expect(wrapper.text()).toContain('网络关闭');
    expect(wrapper.text()).toContain('运行时文件 1');
    expect(wrapper.text()).toContain('运行时文件 2');
    expect(wrapper.text()).toContain('运行时文件未返回本地元数据');
    expect(wrapper.text()).toContain('依赖快照');
    expect(wrapper.text()).toContain('环境快照');
    expect(wrapper.text()).toContain('未生成环境快照');
    expect(wrapper.text()).toContain('不可用');
    expect(wrapper.text()).toContain('标准输出');
    expect(wrapper.text()).toContain('标准错误不可用');
    expect(wrapper.text()).toContain('解析结果');
    expect(wrapper.text()).toContain('stdout');
    expect(
      wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001201/download"]').text(),
    ).toBe('打开');
    expect(
      wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001202/download"]').exists(),
    ).toBe(false);
    expect(
      wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001402/download"]').text(),
    ).toBe('打开');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001401/download"]').text()).toBe('打开');
    expect(wrapper.text()).toContain('generated::test_generated_ok');
    expect(wrapper.text()).toContain('通过');
    expect(wrapper.text()).toContain('1');
    expect(wrapper.text()).not.toContain('重新运行');
    expect(wrapper.text()).not.toContain('生成报告');
    expect(wrapper.text()).not.toContain('远程执行');
    expect(wrapper.text()).not.toContain('远程控制');

    await wrapper.find('[data-test="refresh-run"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('620 ms');
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it('requires the server ExecutionApproval gate for workflow-backed draft execution', async () => {
    window.localStorage.setItem(
      'chtest.latestAutomationDraft',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        requirementReviewId: '00000000-0000-0000-0000-000000000601',
        testCaseId: '00000000-0000-0000-0000-000000000955',
        automationDraftId: '00000000-0000-0000-0000-000000001001',
        status: 'approved',
        targetFramework: 'pytest',
      }),
    );
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirement-reviews/00000000-0000-0000-0000-000000000601/execution-approval')) {
        return new Response(JSON.stringify(executionApprovalBody()), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/test-runs') && init?.method === 'POST') {
        const payload = JSON.parse(String(init.body));
        expect(payload.execution_approval_decision_id).toBe('00000000-0000-0000-0000-000000009003');
        return new Response(JSON.stringify(testRunBody()), {
          status: 202,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(PytestExecutionView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.find('[data-test="execution-approval-panel"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('ExecutionApproval gate');
    expect(wrapper.text()).toContain('00000000-0000-0000-0000-000000009003');
    expect(wrapper.find('[data-test="start-run"]').attributes('disabled')).toBeUndefined();

    await wrapper.find('form').trigger('submit');
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(wrapper.text()).toContain('pytest tests/test_generated_ok.py -q');
  });

  it('does not expose a fabricated draft id when no approved workflow context exists', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(PytestExecutionView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });

    expect((wrapper.find('[data-test="execution-source-id"] input').element as HTMLInputElement).value).toBe('');
    expect(wrapper.find('[data-test="start-run"]').attributes('disabled')).toBeDefined();
    expect(wrapper.find('[data-test="execution-start-hint"]').text()).toContain('自动化草稿页');
    await wrapper.find('form').trigger('submit');
    await flushPromises();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
