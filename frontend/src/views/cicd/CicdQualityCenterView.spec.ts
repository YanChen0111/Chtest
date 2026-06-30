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

const unitTestPatchBody = {
  id: '00000000-0000-0000-0000-000000001201',
  cicd_run_id: '00000000-0000-0000-0000-000000001101',
  ai_task_id: '00000000-0000-0000-0000-000000001131',
  patch_text: 'diff --git a/tests/test_coupon.py b/tests/test_coupon.py\n+def test_coupon_boundary():\n+    assert True\n',
  target_framework: 'pytest',
  scope_gate_result: {
    allowed: true,
    checked_paths: ['tests/test_coupon.py'],
    blocked_paths: [],
    forbidden_patterns: [],
    risk_level: 'low',
  },
  test_intent: 'Cover coupon boundary change',
  coverage_target: [{ path: 'app/coupon.py', reason: 'changed source' }],
  status: 'scope_validated',
  review_comment: null,
};

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
      if (url.endsWith('/cicd/runs/00000000-0000-0000-0000-000000001101/unit-test-patches')) {
        return new Response(JSON.stringify(unitTestPatchBody), {
          status: 202,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/cicd/unit-test-patches/00000000-0000-0000-0000-000000001201/approve')) {
        return new Response(
          JSON.stringify({ unit_test_patch_id: '00000000-0000-0000-0000-000000001201', status: 'approved' }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/cicd/unit-test-patches/00000000-0000-0000-0000-000000001201/reject')) {
        return new Response(
          JSON.stringify({ unit_test_patch_id: '00000000-0000-0000-0000-000000001201', status: 'rejected' }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/cicd/runs/00000000-0000-0000-0000-000000001101/run-new-tests')) {
        return new Response(
          JSON.stringify({
            test_run_id: '00000000-0000-0000-0000-000000001301',
            cicd_run_id: '00000000-0000-0000-0000-000000001101',
            status: 'queued',
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/cicd/runs/00000000-0000-0000-0000-000000001101/select-regression')) {
        return new Response(
          JSON.stringify({
            cicd_run_id: '00000000-0000-0000-0000-000000001101',
            regression_plan_artifact_id: '00000000-0000-0000-0000-000000001221',
            recommended_test_command_ids: ['00000000-0000-0000-0000-000000000302'],
            reasons: ['Selected active pytest regression command.'],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/cicd/runs/00000000-0000-0000-0000-000000001101/run-regression')) {
        return new Response(
          JSON.stringify({
            cicd_run_id: '00000000-0000-0000-0000-000000001101',
            test_run_ids: ['00000000-0000-0000-0000-000000001302'],
            status: 'tests_running',
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/cicd/runs/00000000-0000-0000-0000-000000001101/quality-gate')) {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000001401',
            project_id: '00000000-0000-0000-0000-000000000101',
            cicd_run_id: '00000000-0000-0000-0000-000000001101',
            status: 'passed',
            summary: 'CI/CD quality gate passed with patch, new-test, and regression evidence.',
            blocking_reasons: [],
            evidence_artifact_ids: ['00000000-0000-0000-0000-000000001211'],
            decided_by: 'system',
            status_detail: {
              patch_scope_gate: { allowed: true },
              new_tests: { status: 'succeeded' },
              regression: { status: 'succeeded' },
            },
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/cicd/runs/00000000-0000-0000-0000-000000001101/generate-report')) {
        return new Response(
          JSON.stringify({
            report_id: '00000000-0000-0000-0000-000000001501',
            cicd_run_id: '00000000-0000-0000-0000-000000001101',
            status: 'generating',
            evidence_manifest_artifact_id: '00000000-0000-0000-0000-000000001511',
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
    expect(wrapper.text()).toContain('统一 diff');

    await wrapper.find('[data-test="create-cicd-run"]').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('app/coupon.py');
    expect(wrapper.text()).toContain('源码');
    expect(wrapper.text()).toContain('中');
    expect(wrapper.text()).toContain('源码文件变更');

    await wrapper.find('[data-test="analyze-cicd-run"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('已分析');
    expect(wrapper.text()).toContain('risk_analysis');
    expect(wrapper.text()).toContain('risk_analysis.json');
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/cicd/runs'), expect.objectContaining({ method: 'POST' }));
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/cicd/runs/00000000-0000-0000-0000-000000001101/analyze'),
      expect.objectContaining({ method: 'POST' }),
    );

    await wrapper.find('[data-test="generate-unit-test-patch"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('覆盖优惠券边界变更');
    expect(wrapper.text()).toContain('tests/test_coupon.py');
    expect(wrapper.text()).toContain('app/coupon.py');
    expect(wrapper.text()).toContain('范围已验证');
    expect(wrapper.text()).toContain('PatchScopeGate：通过');

    await wrapper.find('[data-test="approve-unit-test-patch"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('已批准');

    await wrapper.find('[data-test="run-new-tests"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    await wrapper.find('[data-test="select-regression"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    await wrapper.find('[data-test="run-regression"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    await wrapper.find('[data-test="compute-quality-gate"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    await wrapper.find('[data-test="generate-cicd-report"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('新增 TestRun');
    expect(wrapper.text()).toContain('回归计划');
    expect(wrapper.text()).toContain('QualityGateDecision');
    expect(wrapper.text()).toContain('通过');
    expect(wrapper.text()).toContain('报告');
    expect(wrapper.text()).toContain('00000000-0000-0000-0000-000000001501');

    await wrapper.find('[data-test="reject-unit-test-patch"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('已拒绝');
  });
});
