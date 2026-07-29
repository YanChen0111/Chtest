import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import PytestExecutionView from './PytestExecutionView.vue';

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
  beforeEach(() => window.localStorage.clear());
  afterEach(() => vi.unstubAllGlobals());

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
