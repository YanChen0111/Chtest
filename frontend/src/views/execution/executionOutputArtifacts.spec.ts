import { describe, expect, it } from 'vitest';

import {
  jmeterOutputArtifacts,
  newmanOutputArtifacts,
  playwrightOutputArtifacts,
  pytestOutputArtifacts,
} from './executionOutputArtifacts';

function pairs(items: readonly { readonly artifactType: string; readonly label: string }[]) {
  return items.map((item) => [item.artifactType, item.label]);
}

describe('executionOutputArtifacts', () => {
  it('keeps pytest manifest output definitions ordered', () => {
    expect(pairs(pytestOutputArtifacts)).toEqual([
      ['stdout', '标准输出'],
      ['stderr', '标准错误'],
      ['parsed_output', '解析结果'],
      ['junit', 'JUnit 结果'],
      ['coverage', '覆盖率结果'],
    ]);
  });

  it('keeps Playwright manifest output definitions ordered', () => {
    expect(pairs(playwrightOutputArtifacts)).toEqual([
      ['stdout', '标准输出'],
      ['stderr', '标准错误'],
      ['parsed_output', '解析结果'],
      ['junit', 'JUnit 结果'],
      ['playwright_trace', 'Playwright Trace'],
      ['screenshot', '截图'],
    ]);
  });

  it('keeps Newman manifest output definitions ordered', () => {
    expect(pairs(newmanOutputArtifacts)).toEqual([
      ['stdout', '标准输出'],
      ['stderr', '标准错误'],
      ['newman_json', 'Newman JSON'],
      ['parsed_output', '解析结果'],
      ['junit', 'JUnit 结果'],
    ]);
  });

  it('keeps JMeter manifest output definitions ordered', () => {
    expect(pairs(jmeterOutputArtifacts)).toEqual([
      ['stdout', '标准输出'],
      ['stderr', '标准错误'],
      ['parsed_output', '解析结果'],
      ['jmeter_jtl', 'JMeter JTL'],
    ]);
  });
});
