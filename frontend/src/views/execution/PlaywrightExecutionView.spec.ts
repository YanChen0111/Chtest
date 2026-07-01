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
    runtime_artifact_ids: ['00000000-0000-0000-0000-000000001501'],
    dependency_snapshot_artifact_id: null,
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
    ],
  };
}

describe('PlaywrightExecutionView', () => {
  it('starts and refreshes a Playwright run with trace and screenshot evidence', async () => {
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
    expect(wrapper.text()).toContain('AutomationDraft ID');
    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('通过');
    expect(wrapper.text()).toContain('npx playwright test tests/checkout.spec.ts');
    expect(wrapper.text()).toContain('playwright_local');
    expect(wrapper.text()).toContain('playwright_trace');
    expect(wrapper.text()).toContain('screenshot');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001601/download"]').text()).toBe('打开');
    expect(wrapper.text()).toContain('generated::checkout smoke');
    expect(wrapper.text()).toContain('通过');
    expect(wrapper.text()).toContain('1');

    await wrapper.find('[data-test="refresh-playwright-run"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('900 ms');
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
