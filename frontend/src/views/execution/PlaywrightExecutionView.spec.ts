import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import PlaywrightExecutionView from './PlaywrightExecutionView.vue';

function playwrightRunBody() {
  return {
    id: '00000000-0000-0000-0000-000000001411',
    project_id: '00000000-0000-0000-0000-000000000101',
    automation_draft_id: '00000000-0000-0000-0000-000000001011',
    test_command_id: null,
    tool_invocation_id: null,
    name: 'playwright approved draft',
    command: 'npx playwright test tests/checkout.spec.ts',
    working_directory: '/tmp/chtest-playwright-run',
    runner_mode: 'playwright_local',
    run_workspace: '/tmp/chtest-playwright-run',
    repository_readonly: true,
    network_enabled: false,
    runtime_artifact_ids: [
      '00000000-0000-0000-0000-000000001501',
      '00000000-0000-0000-0000-000000001502',
    ],
    dependency_snapshot_artifact_id: '00000000-0000-0000-0000-000000001603',
    environment_snapshot_artifact_id: null,
    status: 'passed',
    exit_code: 0,
    duration_ms: 812,
    parsed_result: {
      total: 1,
      passed: 1,
      failed: 0,
      skipped: 0,
      error: 0,
    },
    test_results: [
      {
        id: '00000000-0000-0000-0000-000000001431',
        project_id: '00000000-0000-0000-0000-000000000101',
        test_run_id: '00000000-0000-0000-0000-000000001411',
        test_name: 'generated::checkout smoke',
        test_file: 'generated',
        status: 'passed',
        duration_ms: null,
        failure_message: null,
        failure_artifact_ids: [],
        metadata: { source: 'playwright_runner' },
      },
    ],
    artifacts: [
      {
        id: '00000000-0000-0000-0000-000000001501',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001411',
        artifact_type: 'automation_draft_code',
        file_path: 'automation-drafts/00000000-0000-0000-0000-000000001011/runtime/test_from_draft.spec.ts',
        mime_type: 'text/plain',
        size_bytes: 118,
        sha256: 'sha256:runtime',
        metadata_json: { created_by_component: 'PlaywrightRunner' },
      },
      {
        id: '00000000-0000-0000-0000-000000001601',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001411',
        artifact_type: 'playwright_trace',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001411/playwright-report/trace.zip',
        mime_type: 'application/zip',
        size_bytes: 128,
        sha256: 'sha256:trace',
        metadata_json: { created_by_component: 'PlaywrightRunner' },
      },
      {
        id: '00000000-0000-0000-0000-000000001602',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001411',
        artifact_type: 'screenshot',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001411/playwright-report/screenshot.png',
        mime_type: 'image/png',
        size_bytes: 256,
        sha256: 'sha256:screenshot',
        metadata_json: { created_by_component: 'PlaywrightRunner' },
      },
      {
        id: '00000000-0000-0000-0000-000000001603',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001411',
        artifact_type: 'dependency_snapshot',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001411/dependency_snapshot.json',
        mime_type: 'application/json',
        size_bytes: 96,
        sha256: 'sha256:dependency',
        metadata_json: { created_by_component: 'PlaywrightRunner' },
      },
      {
        id: '00000000-0000-0000-0000-000000001604',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001411',
        artifact_type: 'stdout',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001411/stdout.log',
        mime_type: 'text/plain',
        size_bytes: 64,
        sha256: 'sha256:stdout',
        metadata_json: { created_by_component: 'PlaywrightRunner' },
      },
    ],
  };
}

describe('PlaywrightExecutionView', () => {
  it('starts and refreshes a Playwright run with trace and screenshot evidence', async () => {
    window.localStorage.setItem(
      'chtest.latestAutomationDraft',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        testCaseId: '00000000-0000-0000-0000-000000000955',
        automationDraftId: '00000000-0000-0000-0000-000000001001',
        status: 'approved',
        targetFramework: 'playwright',
      }),
    );
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/test-runs') && init?.method === 'POST') {
        expect(JSON.parse(String(init.body)).runner_mode).toBe('playwright_local');
        return new Response(JSON.stringify(playwrightRunBody()), {
          status: 202,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/test-runs/00000000-0000-0000-0000-000000001411')) {
        return new Response(JSON.stringify({ ...playwrightRunBody(), duration_ms: 900 }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(PlaywrightExecutionView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    expect(wrapper.text()).toContain('Playwright 执行');
    expect(wrapper.text()).toContain('已批准 Playwright 草稿');
    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('通过');
    expect(wrapper.text()).toContain('npx playwright test tests/checkout.spec.ts');
    expect(wrapper.text()).toContain('/tmp/chtest-playwright-run');
    expect(wrapper.text()).toContain('playwright_local');
    expect(wrapper.text()).toContain('执行运行清单');
    expect(wrapper.text()).toContain('执行命令');
    expect(wrapper.text()).toContain('工作目录');
    expect(wrapper.text()).toContain('运行器模式');
    expect(wrapper.text()).toContain('运行工作区');
    expect(wrapper.text()).toContain('仓库只读策略');
    expect(wrapper.text()).toContain('网络策略');
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
    expect(wrapper.text()).toContain('解析结果不可用');
    expect(wrapper.text()).toContain('JUnit 结果不可用');
    expect(wrapper.text()).toContain('playwright_trace');
    expect(wrapper.text()).toContain('screenshot');
    expect(
      wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001501/download"]').text(),
    ).toBe('打开');
    expect(
      wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001502/download"]').exists(),
    ).toBe(false);
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001601/download"]').text()).toBe('打开');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001602/download"]').text()).toBe('打开');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001603/download"]').text()).toBe('打开');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001604/download"]').text()).toBe('打开');
    expect(wrapper.text()).toContain('generated::checkout smoke');
    expect(wrapper.text()).toContain('通过');
    expect(wrapper.text()).toContain('1');
    expect(wrapper.text()).not.toContain('重新运行');
    expect(wrapper.text()).not.toContain('生成报告');
    expect(wrapper.text()).not.toContain('远程执行');
    expect(wrapper.text()).not.toContain('远程控制');

    await wrapper.find('[data-test="refresh-playwright-run"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('900 ms');
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
