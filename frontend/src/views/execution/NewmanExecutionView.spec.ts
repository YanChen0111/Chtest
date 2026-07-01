import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import NewmanExecutionView from './NewmanExecutionView.vue';

function newmanRunBody() {
  return {
    id: '00000000-0000-0000-0000-000000001421',
    project_id: '00000000-0000-0000-0000-000000000101',
    automation_draft_id: null,
    test_command_id: '00000000-0000-0000-0000-000000000322',
    tool_invocation_id: null,
    name: 'newman coupon api',
    command:
      'npx newman run collections/coupon.postman_collection.json --reporters json --reporter-json-export newman-report.json',
    working_directory: '/tmp/chtest-newman-run',
    runner_mode: 'newman_local',
    run_workspace: '/tmp/chtest-newman-run',
    repository_readonly: true,
    network_enabled: false,
    runtime_artifact_ids: ['00000000-0000-0000-0000-000000001521'],
    dependency_snapshot_artifact_id: null,
    environment_snapshot_artifact_id: null,
    status: 'failed',
    exit_code: 0,
    duration_ms: 812,
    parsed_result: {
      total: 4,
      passed: 3,
      failed: 1,
      skipped: 0,
      error: 0,
      request_count: 2,
      assertion_count: 4,
      collection_name: 'coupon-api',
    },
    test_results: [
      {
        id: '00000000-0000-0000-0000-000000001431',
        project_id: '00000000-0000-0000-0000-000000000101',
        test_run_id: '00000000-0000-0000-0000-000000001421',
        test_name: 'coupon-api/Reject expired coupon::message is explicit',
        test_file: null,
        status: 'failed',
        duration_ms: null,
        failure_message: 'expected clear message',
        failure_artifact_ids: [],
        metadata: { source: 'newman_runner' },
      },
    ],
    artifacts: [
      {
        id: '00000000-0000-0000-0000-000000001601',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001421',
        artifact_type: 'newman_json',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001421/newman-report.json',
        mime_type: 'application/json',
        size_bytes: 512,
        sha256: 'sha256:newman',
        metadata_json: { created_by_component: 'NewmanRunner' },
      },
      {
        id: '00000000-0000-0000-0000-000000001602',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001421',
        artifact_type: 'parsed_output',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001421/parsed_result.json',
        mime_type: 'application/json',
        size_bytes: 128,
        sha256: 'sha256:parsed',
        metadata_json: { created_by_component: 'NewmanRunner' },
      },
    ],
  };
}

describe('NewmanExecutionView', () => {
  it('starts and refreshes a Newman run with API assertion evidence', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/test-runs') && init?.method === 'POST') {
        const body = JSON.parse(String(init.body));
        expect(body.runner_mode).toBe('newman_local');
        expect(body.automation_draft_id).toBeNull();
        return new Response(JSON.stringify(newmanRunBody()), {
          status: 202,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/test-runs/00000000-0000-0000-0000-000000001421')) {
        return new Response(JSON.stringify({ ...newmanRunBody(), duration_ms: 900 }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(NewmanExecutionView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    expect(wrapper.text()).toContain('API 执行');
    expect(wrapper.text()).toContain('TestCommand ID');
    expect(wrapper.text()).not.toContain('AutomationDraft ID');
    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('失败');
    expect(wrapper.text()).toContain('coupon-api');
    expect(wrapper.text()).toContain('newman_local');
    expect(wrapper.text()).toContain('newman_json');
    expect(wrapper.text()).toContain('parsed_output');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001601/download"]').text()).toBe('打开');
    expect(wrapper.text()).toContain('coupon-api/Reject expired coupon::message is explicit');
    expect(wrapper.text()).toContain('expected clear message');
    expect(wrapper.text()).toContain('总断言');
    expect(wrapper.text()).toContain('请求数');

    await wrapper.find('[data-test="refresh-newman-run"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('900 ms');
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
