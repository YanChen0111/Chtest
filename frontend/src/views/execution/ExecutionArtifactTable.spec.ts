import { enableAutoUnmount, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { afterEach, describe, expect, it } from 'vitest';

import ExecutionArtifactTable from './ExecutionArtifactTable.vue';

enableAutoUnmount(afterEach);

function artifactRows() {
  return [
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
  ];
}

describe('ExecutionArtifactTable', () => {
  it('renders artifact metadata and local open links', () => {
    const wrapper = mount(ExecutionArtifactTable, {
      props: {
        title: '工件',
        titleId: 'pytest-artifacts-title',
        artifacts: artifactRows(),
      },
      global: {
        plugins: [ArcoVue],
      },
    });

    expect(wrapper.find('#pytest-artifacts-title').text()).toBe('工件');
    expect(wrapper.text()).toContain('类型');
    expect(wrapper.text()).toContain('路径');
    expect(wrapper.text()).toContain('MIME');
    expect(wrapper.text()).toContain('大小');
    expect(wrapper.text()).toContain('stdout');
    expect(wrapper.text()).toContain('parsed_output');
    expect(wrapper.text()).toContain('text/plain');
    expect(wrapper.text()).toContain('application/json');
    expect(wrapper.text()).toContain('64');
    expect(wrapper.text()).toContain('80');

    const stdoutLink = wrapper.find(
      'a[href="/api/artifacts/00000000-0000-0000-0000-000000001401/download"]',
    );
    expect(stdoutLink.text()).toBe('打开');
    expect(stdoutLink.attributes('aria-label')).toBe('打开 stdout 工件');
    expect(stdoutLink.attributes('title')).toBe('打开 stdout 工件');

    expect(
      wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001404/download"]').exists(),
    ).toBe(true);
  });
});
