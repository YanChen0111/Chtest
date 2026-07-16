import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia, setActivePinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import ExecutionRecentRuns from './ExecutionRecentRuns.vue';
import { useExecutionStore } from '../../stores/execution';

const run = {
  id: 'run-1', project_id: 'project-1', automation_draft_id: null, test_command_id: 'command-1',
  tool_invocation_id: null, name: 'pytest smoke', command: 'pytest -q', working_directory: '/tmp/run',
  runner_mode: 'local_subprocess', run_workspace: '/tmp/run', repository_readonly: true, network_enabled: false,
  runtime_artifact_ids: [], dependency_snapshot_artifact_id: null, environment_snapshot_artifact_id: null,
  status: 'passed', exit_code: 0, duration_ms: 120, parsed_result: {}, test_results: [], artifacts: [],
};

describe('ExecutionRecentRuns', () => {
  it('shows an actionable empty state', () => {
    setActivePinia(createPinia());
    const wrapper = mount(ExecutionRecentRuns, { global: { plugins: [ArcoVue] } });
    expect(wrapper.find('[data-test="recent-runs"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="recent-runs-empty-state"]').exists()).toBe(true);
  });

  it('resumes a cached run through the shared store', async () => {
    setActivePinia(createPinia());
    const store = useExecutionStore();
    store.recentRuns = [run];
    store.recentRunsHydrated = true;
    vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify(run), {
      status: 200, headers: { 'Content-Type': 'application/json' },
    })));
    const wrapper = mount(ExecutionRecentRuns, { global: { plugins: [ArcoVue] } });
    await wrapper.find('[data-test="resume-run-run-1"]').trigger('click');
    await flushPromises();
    expect(store.run?.id).toBe('run-1');
    expect(wrapper.find('[data-test="recent-runs-list"]').exists()).toBe(true);
  });
});
