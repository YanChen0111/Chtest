import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import CicdQualityCenterView from './CicdQualityCenterView.vue';

function cicdRunBody(status = 'created') {
  return {
    id: '00000000-0000-0000-0000-000000001101',
    project_id: '00000000-0000-0000-0000-000000000101',
    repository_id: '00000000-0000-0000-0000-000000000301',
    source_type: 'local_diff',
    trigger_type: 'manual',
    provider: 'local',
    pipeline_name: null,
    base_ref: 'main',
    head_ref: 'HEAD',
    summary: null,
    overall_risk: 'medium',
    quality_gate_status: 'pending',
    status,
    changed_files: [
      {
        id: '00000000-0000-0000-0000-000000001111',
        cicd_run_id: '00000000-0000-0000-0000-000000001101',
        path: 'app/coupon.py',
        old_path: null,
        change_type: 'modified',
        language: 'python',
        file_role: 'source',
        risk_level: 'medium',
        risk_reasons: ['source file changed'],
        lines_added: 1,
        lines_deleted: 1,
      },
    ],
    analysis_artifacts:
      status === 'analyzed'
        ? [
            {
              id: '00000000-0000-0000-0000-000000001121',
              project_id: '00000000-0000-0000-0000-000000000101',
              owner_entity_type: 'CICDRun',
              owner_entity_id: '00000000-0000-0000-0000-000000001101',
              artifact_type: 'risk_analysis',
              file_path:
                'artifacts/projects/00000000-0000-0000-0000-000000000101/cicd-quality/00000000-0000-0000-0000-000000001101/risk_analysis.json',
              mime_type: 'application/json',
              size_bytes: 0,
              sha256: 'sha256:risk_analysis',
              metadata_json: { overall_risk: 'medium' },
            },
          ]
        : [],
  };
}

describe('CicdQualityCenterView', () => {
  it('creates and analyzes a local diff run with changed file evidence', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/cicd/runs') && init?.method === 'POST') {
        return new Response(
          JSON.stringify({
            cicd_run_id: '00000000-0000-0000-0000-000000001101',
            status: 'created',
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/cicd/runs') && !init?.method) {
        return new Response(JSON.stringify({ items: [cicdRunBody()], total: 1 }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/cicd/runs/00000000-0000-0000-0000-000000001101/analyze')) {
        return new Response(
          JSON.stringify({
            cicd_run_id: '00000000-0000-0000-0000-000000001101',
            ai_task_id: '00000000-0000-0000-0000-000000001131',
            risk_analysis_artifact_id: '00000000-0000-0000-0000-000000001121',
            status: 'analyzed',
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/cicd/runs/00000000-0000-0000-0000-000000001101')) {
        const body = fetchMock.mock.calls.some((call) => String(call[0]).endsWith('/analyze'))
          ? cicdRunBody('analyzed')
          : cicdRunBody();
        return new Response(JSON.stringify(body), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(CicdQualityCenterView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    expect(wrapper.text()).toContain('CI/CD 质量中心');
    expect(wrapper.text()).toContain('Unified Diff');

    await wrapper.find('[data-test="create-cicd-run"]').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('app/coupon.py');
    expect(wrapper.text()).toContain('source');
    expect(wrapper.text()).toContain('medium');
    expect(wrapper.text()).toContain('source file changed');

    await wrapper.find('[data-test="analyze-cicd-run"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('analyzed');
    expect(wrapper.text()).toContain('risk_analysis');
    expect(wrapper.text()).toContain('risk_analysis.json');
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/cicd/runs'), expect.objectContaining({ method: 'POST' }));
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/cicd/runs/00000000-0000-0000-0000-000000001101/analyze'),
      expect.objectContaining({ method: 'POST' }),
    );
  });
});
