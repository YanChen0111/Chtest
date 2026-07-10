import type { ExecutionRunManifestOutputArtifact } from './executionRunManifest';

export const standardOutputArtifact = { artifactType: 'stdout', label: '标准输出' } as const;
export const standardErrorArtifact = { artifactType: 'stderr', label: '标准错误' } as const;
export const parsedOutputArtifact = { artifactType: 'parsed_output', label: '解析结果' } as const;
export const junitOutputArtifact = { artifactType: 'junit', label: 'JUnit 结果' } as const;

export const pytestOutputArtifacts = [
  standardOutputArtifact,
  standardErrorArtifact,
  parsedOutputArtifact,
  junitOutputArtifact,
  { artifactType: 'coverage', label: '覆盖率结果' },
] as const satisfies readonly ExecutionRunManifestOutputArtifact[];

export const playwrightOutputArtifacts = [
  standardOutputArtifact,
  standardErrorArtifact,
  parsedOutputArtifact,
  junitOutputArtifact,
  { artifactType: 'playwright_trace', label: 'Playwright Trace' },
  { artifactType: 'screenshot', label: '截图' },
] as const satisfies readonly ExecutionRunManifestOutputArtifact[];

export const newmanOutputArtifacts = [
  standardOutputArtifact,
  standardErrorArtifact,
  { artifactType: 'newman_json', label: 'Newman JSON' },
  parsedOutputArtifact,
  junitOutputArtifact,
] as const satisfies readonly ExecutionRunManifestOutputArtifact[];

export const jmeterOutputArtifacts = [
  standardOutputArtifact,
  standardErrorArtifact,
  parsedOutputArtifact,
  { artifactType: 'jmeter_jtl', label: 'JMeter JTL' },
] as const satisfies readonly ExecutionRunManifestOutputArtifact[];
