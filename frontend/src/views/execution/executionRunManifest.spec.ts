import { describe, expect, it } from 'vitest';

import { buildExecutionRunManifestRows, runnerModeLabel } from './executionRunManifest';

function artifact(id: string, artifactType: string, filePath: string) {
  return {
    id,
    project_id: '00000000-0000-0000-0000-000000000101',
    owner_entity_type: 'TestRun',
    owner_entity_id: '00000000-0000-0000-0000-000000001301',
    artifact_type: artifactType,
    file_path: filePath,
    mime_type: 'application/json',
    size_bytes: 64,
    sha256: `sha256:${artifactType}`,
    metadata_json: {},
  };
}

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
    dependency_snapshot_artifact_id: '00000000-0000-0000-0000-000000001402',
    environment_snapshot_artifact_id: null,
    status: 'passed',
    exit_code: 0,
    duration_ms: 518,
    parsed_result: {},
    test_results: [],
    artifacts: [
      artifact(
        '00000000-0000-0000-0000-000000001201',
        'runtime_manifest',
        'test-runs/00000000-0000-0000-0000-000000001301/runtime_manifest.json',
      ),
      artifact(
        '00000000-0000-0000-0000-000000001402',
        'dependency_snapshot',
        'test-runs/00000000-0000-0000-0000-000000001301/dependency_snapshot.json',
      ),
      artifact(
        '00000000-0000-0000-0000-000000001401',
        'stdout',
        'test-runs/00000000-0000-0000-0000-000000001301/stdout.log',
      ),
    ],
  };
}

describe('buildExecutionRunManifestRows', () => {
  it('builds openable rows only from persisted local artifact metadata', () => {
    const rows = buildExecutionRunManifestRows(runBody(), [
      { artifactType: 'stdout', label: '标准输出' },
      { artifactType: 'stderr', label: '标准错误' },
    ]);

    expect(rows.map((row) => row.label)).toEqual([
      '运行时文件 1',
      '运行时文件 2',
      '依赖快照',
      '环境快照',
      '标准输出',
      '标准错误',
    ]);

    expect(rows.find((row) => row.key === 'runtime-00000000-0000-0000-0000-000000001201')).toMatchObject({
      available: true,
      artifactId: '00000000-0000-0000-0000-000000001201',
      stateLabel: '可打开',
      artifactLabel: '打开',
    });
    expect(rows.find((row) => row.key === 'runtime-00000000-0000-0000-0000-000000001202')).toMatchObject({
      available: false,
      artifactId: null,
      stateLabel: '不可用',
      artifactLabel: '不可打开',
      description: '运行时文件未返回本地元数据',
    });
    expect(rows.find((row) => row.key === 'environment-snapshot')).toMatchObject({
      available: false,
      artifactId: null,
      description: '未生成环境快照',
    });
    expect(rows.find((row) => row.key === 'output-stdout')).toMatchObject({
      available: true,
      artifactId: '00000000-0000-0000-0000-000000001401',
    });
    expect(rows.find((row) => row.key === 'output-stderr')).toMatchObject({
      available: false,
      artifactId: null,
      description: '标准错误不可用',
    });
  });

  it('keeps an empty runtime list visible as unavailable evidence', () => {
    const rows = buildExecutionRunManifestRows({ ...runBody(), runtime_artifact_ids: [] }, []);

    expect(rows[0]).toMatchObject({
      key: 'runtime-missing',
      label: '运行时文件',
      available: false,
      artifactId: null,
      description: '暂无运行时文件',
    });
  });

  it('returns no rows before a run is loaded', () => {
    expect(buildExecutionRunManifestRows(null, [])).toEqual([]);
  });
});

describe('runnerModeLabel', () => {
  it('labels known runner modes while preserving the raw mode', () => {
    expect(runnerModeLabel('playwright_local')).toBe('Playwright 本地 (playwright_local)');
    expect(runnerModeLabel('custom_runner')).toBe('custom_runner');
  });
});
