import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import ReportFailureAnalysisView from './ReportFailureAnalysisView.vue';

function failureAnalysisBody() {
  return {
    id: '00000000-0000-0000-0000-000000001502',
    project_id: '00000000-0000-0000-0000-000000000101',
    test_run_id: '00000000-0000-0000-0000-000000001301',
    test_result_id: '00000000-0000-0000-0000-000000001331',
    ai_task_id: '00000000-0000-0000-0000-000000001501',
    classification: 'test_script_issue',
    confidence: 0.82,
    evidence_artifact_ids: ['00000000-0000-0000-0000-000000001601'],
    summary: 'Fixture lookup failed before business assertion.',
    root_cause: 'fixture coupon_client not found',
    suggested_actions: ['Add or fix the missing test fixture before rerunning the suite.'],
    status: 'draft',
  };
}

function reportBody() {
  return {
    id: '00000000-0000-0000-0000-000000001401',
    project_id: '00000000-0000-0000-0000-000000000101',
    report_type: 'automation_execution',
    title: 'Automation execution report',
    related_entity_type: 'TestRun',
    related_entity_id: '00000000-0000-0000-0000-000000001301',
    status: 'ready',
    conclusion: 'failed',
    summary: '1 of 1 tests failed with 1 execution artifact(s).',
    metrics: {
      total: 1,
      passed: 0,
      failed: 1,
      skipped: 0,
    },
    artifact_ids: [
      '00000000-0000-0000-0000-000000001701',
      '00000000-0000-0000-0000-000000001702',
      '00000000-0000-0000-0000-000000001703',
    ],
    evidence_manifest: {
      report_id: '00000000-0000-0000-0000-000000001401',
      conclusion: 'failed',
      evidence: [
        {
          artifact_id: '00000000-0000-0000-0000-000000001601',
          artifact_type: 'stderr',
          supports_claim: 'pytest failed run includes stderr evidence',
          required: true,
        },
        {
          metric: 'test_result:failed',
          test_result_id: '00000000-0000-0000-0000-000000001331',
          supports_claim: 'fixture coupon_client not found',
          required: true,
        },
      ],
      missing_evidence: ['environment_snapshot'],
    },
    artifacts: [
      {
        id: '00000000-0000-0000-0000-000000001701',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'Report',
        owner_entity_id: '00000000-0000-0000-0000-000000001401',
        artifact_type: 'report_md',
        file_path: 'projects/00000000-0000-0000-0000-000000000101/reports/00000000-0000-0000-0000-000000001401/report.md',
        mime_type: 'text/markdown',
        size_bytes: 0,
        sha256: 'sha256:report_md',
        metadata_json: { report_kind: 'automation_execution' },
      },
      {
        id: '00000000-0000-0000-0000-000000001703',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'Report',
        owner_entity_id: '00000000-0000-0000-0000-000000001401',
        artifact_type: 'report_json',
        file_path: 'projects/00000000-0000-0000-0000-000000000101/reports/00000000-0000-0000-0000-000000001401/evidence_manifest.json',
        mime_type: 'application/json',
        size_bytes: 0,
        sha256: 'sha256:evidence_manifest',
        metadata_json: { manifest_kind: 'evidence_manifest' },
      },
    ],
  };
}

describe('ReportFailureAnalysisView', () => {
  it('starts failure analysis and report generation with evidence first details', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes('/failure-analysis') && init?.method === 'POST') {
        return new Response(
          JSON.stringify({
            ai_task_id: '00000000-0000-0000-0000-000000001501',
            failure_analysis_id: '00000000-0000-0000-0000-000000001502',
            status: 'draft',
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.includes('/failure-analysis')) {
        return new Response(JSON.stringify(failureAnalysisBody()), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/reports') && init?.method === 'POST') {
        return new Response(
          JSON.stringify({
            report_id: '00000000-0000-0000-0000-000000001401',
            status: 'ready',
            evidence_manifest_artifact_id: '00000000-0000-0000-0000-000000001703',
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/reports/00000000-0000-0000-0000-000000001401')) {
        return new Response(JSON.stringify(reportBody()), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(ReportFailureAnalysisView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    expect(wrapper.text()).toContain('报告与失败分析');
    expect(wrapper.text()).toContain('TestRun ID');

    await wrapper.find('[data-test="start-failure-analysis"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('test_script_issue');
    expect(wrapper.text()).toContain('82%');
    expect(wrapper.text()).toContain('fixture coupon_client not found');

    await wrapper.find('[data-test="start-report"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    const renderedText = wrapper.text();
    expect(renderedText.indexOf('证据清单')).toBeLessThan(renderedText.indexOf('test_script_issue'));
    expect(renderedText).toContain('failed');
    expect(renderedText).toContain('stderr');
    expect(renderedText).toContain('pytest failed run includes stderr evidence');
    expect(renderedText).toContain('environment_snapshot');
    expect(renderedText).toContain('缺失不可打开');
    expect(renderedText).toContain('report_md');
    expect(renderedText).toContain('evidence_manifest.json');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001601/download"]').text()).toBe('打开');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001701/download"]').text()).toBe('打开');
    expect(fetchMock).toHaveBeenCalledTimes(4);
  });
});
