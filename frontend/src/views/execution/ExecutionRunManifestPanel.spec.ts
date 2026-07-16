import { mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { describe, expect, it } from 'vitest';

import ExecutionRunManifestPanel from './ExecutionRunManifestPanel.vue';
import { buildExecutionRunManifestRows } from './executionRunManifest';

function runBody() {
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
    dependency_snapshot_artifact_id: null,
    environment_snapshot_artifact_id: null,
    status: 'passed',
    exit_code: 0,
    duration_ms: 518,
    parsed_result: {},
    test_results: [],
    artifacts: [
      {
        id: '00000000-0000-0000-0000-000000001201',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'TestRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001301',
        artifact_type: 'runtime_manifest',
        file_path: 'test-runs/00000000-0000-0000-0000-000000001301/runtime_manifest.json',
        mime_type: 'application/json',
        size_bytes: 64,
        sha256: 'sha256:runtime',
        metadata_json: {},
      },
    ],
  };
}

describe('ExecutionRunManifestPanel', () => {
  it('renders run context, local links, and unavailable rows', () => {
    const run = runBody();
    const wrapper = mount(ExecutionRunManifestPanel, {
      props: {
        run,
        titleId: 'test-run-manifest-title',
        rows: buildExecutionRunManifestRows(run, [{ artifactType: 'stderr', label: '标准错误' }]),
      },
      global: {
        plugins: [ArcoVue],
      },
    });

    expect(wrapper.text()).toContain('执行运行清单');
    expect(wrapper.text()).toContain('pytest tests/test_generated_ok.py -q');
    expect(wrapper.text()).toContain('/tmp/chtest-test-run');
    expect(wrapper.text()).toContain('本地子进程 (local_subprocess)');
    expect(wrapper.text()).toContain('只读挂载');
    expect(wrapper.text()).toContain('网络关闭');
    expect(wrapper.text()).toContain('运行时文件 1');
    expect(wrapper.text()).toContain('运行时文件 2');
    expect(wrapper.text()).toContain('运行时文件未返回本地元数据');
    expect(wrapper.text()).toContain('标准错误不可用');
    const runtimeLink = wrapper.find(
      'a[href="/api/artifacts/00000000-0000-0000-0000-000000001201/download"]',
    );
    expect(runtimeLink.text()).toBe('打开');
    expect(runtimeLink.attributes('aria-label')).toBe('打开 运行时文件 1 工件');
    expect(runtimeLink.attributes('title')).toBe('打开 运行时文件 1 工件');
    expect(
      wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001202/download"]').exists(),
    ).toBe(false);
  });
});
