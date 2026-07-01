import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

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
    runtime_artifact_ids: ['00000000-0000-0000-0000-000000001201'],
    dependency_snapshot_artifact_id: null,
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
    ],
  };
}

describe('PytestExecutionView', () => {
  it('starts and refreshes a pytest run with evidence details', async () => {
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
    expect(wrapper.text()).toContain('AutomationDraft ID');
    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('通过');
    expect(wrapper.text()).toContain('pytest tests/test_generated_ok.py -q');
    expect(wrapper.text()).toContain('/tmp/chtest-test-run');
    expect(wrapper.text()).toContain('local_subprocess');
    expect(wrapper.text()).toContain('关闭');
    expect(wrapper.text()).toContain('stdout');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001401/download"]').text()).toBe('打开');
    expect(wrapper.text()).toContain('generated::test_generated_ok');
    expect(wrapper.text()).toContain('通过');
    expect(wrapper.text()).toContain('1');

    await wrapper.find('[data-test="refresh-run"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('620 ms');
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
