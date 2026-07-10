import type { TestRunArtifactRead, TestRunRead } from '../../api/execution';
import { evidenceAvailabilityLabels } from './evidenceAvailability';

export interface ExecutionRunManifestOutputArtifact {
  readonly artifactType: string;
  readonly label: string;
  readonly missingLabel?: string;
}

export interface ExecutionRunManifestRow {
  readonly key: string;
  readonly label: string;
  readonly available: boolean;
  readonly stateLabel: string;
  readonly tagColor: 'green' | 'gray' | 'orange' | 'blue';
  readonly artifactId: string | null;
  readonly artifactLabel: string;
  readonly description: string;
}

export function buildExecutionRunManifestRows(
  run: TestRunRead | null | undefined,
  outputArtifacts: readonly ExecutionRunManifestOutputArtifact[],
): ExecutionRunManifestRow[] {
  if (!run) {
    return [];
  }

  const artifactsById = new Map(run.artifacts.map((artifact) => [artifact.id, artifact]));
  const artifactByType = new Map(run.artifacts.map((artifact) => [artifact.artifact_type, artifact]));

  return [
    ...runtimeArtifactRows(run, artifactsById),
    manifestArtifactRow({
      key: 'dependency-snapshot',
      label: '依赖快照',
      artifact: artifactFromId(artifactsById, run.dependency_snapshot_artifact_id),
      missingLabel: '未生成依赖快照',
    }),
    manifestArtifactRow({
      key: 'environment-snapshot',
      label: '环境快照',
      artifact: artifactFromId(artifactsById, run.environment_snapshot_artifact_id),
      missingLabel: '未生成环境快照',
    }),
    ...outputArtifacts.map((outputArtifact) => {
      const artifact = artifactByType.get(outputArtifact.artifactType) ?? null;
      return manifestArtifactRow({
        key: `output-${outputArtifact.artifactType}`,
        label: outputArtifact.label,
        artifact,
        missingLabel: outputArtifact.missingLabel ?? `${outputArtifact.label}不可用`,
      });
    }),
  ];
}

export function runnerModeLabel(mode: string): string {
  const labels: Record<string, string> = {
    local_subprocess: '本地子进程',
    playwright_local: 'Playwright 本地',
    newman_local: 'Newman 本地',
    jmeter_local: 'JMeter 本地',
    docker_runner: 'Docker Runner',
  };
  return labels[mode] ? `${labels[mode]} (${mode})` : mode;
}

function runtimeArtifactRows(
  run: TestRunRead,
  artifactsById: Map<string, TestRunArtifactRead>,
): ExecutionRunManifestRow[] {
  if (run.runtime_artifact_ids.length === 0) {
    return [
      manifestArtifactRow({
        key: 'runtime-missing',
        label: '运行时文件',
        artifact: null,
        missingLabel: '暂无运行时文件',
      }),
    ];
  }

  return run.runtime_artifact_ids.map((artifactId, index) =>
    manifestArtifactRow({
      key: `runtime-${artifactId}`,
      label: `运行时文件 ${index + 1}`,
      artifact: artifactsById.get(artifactId) ?? null,
      missingLabel: '运行时文件未返回本地元数据',
    }),
  );
}

function artifactFromId(
  artifactsById: Map<string, TestRunArtifactRead>,
  artifactId: string | null,
): TestRunArtifactRead | null {
  return artifactId ? (artifactsById.get(artifactId) ?? null) : null;
}

function manifestArtifactRow(options: {
  readonly key: string;
  readonly label: string;
  readonly artifact: TestRunArtifactRead | null;
  readonly missingLabel: string;
}): ExecutionRunManifestRow {
  const availability = evidenceAvailabilityLabels(options.artifact ? 'local_artifact' : 'unavailable');

  return {
    key: options.key,
    label: options.label,
    available: availability.isOpenable,
    stateLabel: availability.stateLabel,
    tagColor: availability.tagColor,
    artifactId: availability.isOpenable ? options.artifact?.id ?? null : null,
    artifactLabel: availability.actionLabel,
    description: options.artifact
      ? `${options.artifact.artifact_type} · ${options.artifact.file_path}`
      : options.missingLabel,
  };
}
