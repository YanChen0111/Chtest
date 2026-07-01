import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import JMeterExecutionView from './JMeterExecutionView.vue';

function jmeterRunBody() {
  return {
    id: '00000000-0000-0000-0000-000000001621',
    project_id: '00000000-0000-0000-0000-000000000101',
    automation_draft_id: null,
    test_command_id: '00000000-0000-0000-0000-000000000333',
    tool_invocation_id: null,
    name: 'jmeter coupon smoke',
    command: 'jmeter -n -t plans/coupon.jmx -l results.jtl',
    working_directory: '/tmp/chtest-jmeter-run',
    runner_mode: 'jmeter_local',
    run_workspace: '/tmp/chtest-jmeter-run',
    repository_readonly: true,
    network_enabled: false,
    runtime_artifact_ids: ['00000000-0000-0000-0000-000000001721'],
    dependency_snapshot_artifact_id: null,
    environment_snapshot_artifact_id: null,
    status: 'failed',
    exit_code: 0,
    duration_ms: 1240,
    parsed_result: {
      total: 3,
      passed: 2,
      failed: 1,
      skipped: 0,
      error: 0,
      sampler_count: 3,
      assertion_count: 3,
      duration_ms: 450,
      average_latency_ms: 103,
    },
    test_results: [
      {
        id: '00000000-0000-0000-0000-000000001631',
        project_id: '00000000-0000-0000-0000-000000000101',
        test_run_id: '00000000-0000-0000-0000-000000001621',
        test_name: 'jmeter/POST /coupons',
        test_file: null,
        status: 'failed',
        duration_ms: 240,
        failure_message: '500 Internal Server Error',
        failure_artifact_ids: [],
        metadata: { source: 'jmeter_runner', response_code: '500' },
      },
    ],
    artifacts: [
      {
        id: '00000000-0000-0000-0000-000000001701',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001621',
        artifact_type: 'jmeter_jtl',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001621/results.jtl',
        mime_type: 'text/csv',
        size_bytes: 512,
        sha256: 'sha256:jtl',
        metadata_json: { created_by_component: 'JMeterRunner' },
      },
      {
        id: '00000000-0000-0000-0000-000000001702',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001621',
        artifact_type: 'parsed_output',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001621/parsed_result.json',
        mime_type: 'application/json',
        size_bytes: 128,
        sha256: 'sha256:parsed',
        metadata_json: { created_by_component: 'JMeterRunner' },
      },
    ],
  };
}

describe('JMeterExecutionView', () => {
  it('starts and refreshes a JMeter run with sampler and JTL evidence', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/test-runs') && init?.method === 'POST') {
        const body = JSON.parse(String(init.body));
        expect(body.runner_mode).toBe('jmeter_local');
        expect(body.automation_draft_id).toBeNull();
        return new Response(JSON.stringify(jmeterRunBody()), {
          status: 202,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/test-runs/00000000-0000-0000-0000-000000001621')) {
        return new Response(JSON.stringify({ ...jmeterRunBody(), duration_ms: 1300 }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(JMeterExecutionView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    expect(wrapper.text()).toContain('JMeter 执行');
    expect(wrapper.text()).toContain('TestCommand ID');
    expect(wrapper.text()).not.toContain('AutomationDraft ID');
    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('失败');
    expect(wrapper.text()).toContain('jmeter_local');
    expect(wrapper.text()).toContain('jmeter_jtl');
    expect(wrapper.text()).toContain('parsed_output');
    expect(wrapper.text()).toContain('jmeter/POST /coupons');
    expect(wrapper.text()).toContain('500 Internal Server Error');
    expect(wrapper.text()).toContain('总样本');
    expect(wrapper.text()).toContain('Sampler 数');
    expect(wrapper.text()).toContain('断言数');
    expect(wrapper.text()).toContain('平均延迟');
    expect(wrapper.text()).toContain('103 ms');

    await wrapper.find('[data-test="refresh-jmeter-run"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('1300 ms');
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
