import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import { useCICDStore } from '../../stores/cicd';
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

function importedCicdRunBody() {
  return {
    ...cicdRunBody('imported'),
    source_type: 'ci_import',
    trigger_type: 'imported',
    provider: 'github_actions',
    pipeline_name: 'CI',
    base_ref: 'main',
    head_ref: 'feature/coupon-boundary',
    quality_gate_status: 'pending',
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
        lines_added: 12,
        lines_deleted: 4,
      },
      {
        id: '00000000-0000-0000-0000-000000001112',
        cicd_run_id: '00000000-0000-0000-0000-000000001101',
        path: 'tests/test_coupon.py',
        old_path: null,
        change_type: 'added',
        language: 'python',
        file_role: 'test',
        risk_level: 'low',
        risk_reasons: ['test file changed'],
        lines_added: 8,
        lines_deleted: 0,
      },
    ],
    analysis_artifacts: [
      {
        id: '00000000-0000-0000-0000-000000001122',
        project_id: '00000000-0000-0000-0000-000000000101',
        owner_entity_type: 'CICDRun',
        owner_entity_id: '00000000-0000-0000-0000-000000001101',
        artifact_type: 'ci_run_metadata',
        file_path:
          'artifacts/projects/00000000-0000-0000-0000-000000000101/cicd-quality/00000000-0000-0000-0000-000000001101/ci_run_metadata.json',
        mime_type: 'application/json',
        size_bytes: 0,
        sha256: 'sha256:ci_run_metadata',
        metadata_json: {
          provider_is_inert_label: true,
          remote_fetch_performed: false,
          quality_gate_auto_decision: false,
          content_json: {
            provider: 'github_actions',
            conclusion: 'success',
            status: 'completed',
            external_run_id: '123456',
            job_name: 'pytest',
            commit_sha: 'abc123',
            external_url: 'https://example.invalid/runs/123456',
            started_at: '2026-07-01T01:00:00Z',
            finished_at: '2026-07-01T01:05:00Z',
            duration_ms: 300000,
            artifact_references: [
              {
                name: 'pytest report',
                kind: 'test_report',
                external_url: 'https://example.invalid/artifacts/1',
                inert_reference: true,
              },
            ],
          },
        },
      },
    ],
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
  it('shows imported CI evidence without remote provider controls', async () => {
    const pinia = createPinia();
    const store = useCICDStore(pinia);
    store.run = importedCicdRunBody();
    store.runs = [importedCicdRunBody()];

    const wrapper = mount(CicdQualityCenterView, {
      global: {
        plugins: [pinia, ArcoVue],
      },
    });

    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('导入 CI 证据');
    expect(wrapper.text()).toContain('GitHub Actions');
    expect(wrapper.text()).toContain('CI 结论');
    expect(wrapper.text()).toContain('成功');
    expect(wrapper.text()).toContain('QualityGateDecision');
    expect(wrapper.text()).toContain('待处理');
    expect(wrapper.text()).toContain('pytest report');
    expect(wrapper.text()).toContain('test_report');
    expect(wrapper.text()).toContain('仅保存引用');
    expect(wrapper.text()).toContain('不可本地打开');
    expect(wrapper.text()).toContain('未远程拉取');
    expect(wrapper.text()).toContain('app/coupon.py');
    expect(wrapper.text()).toContain('tests/test_coupon.py');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001122/download"]').exists()).toBe(false);
    expect(wrapper.text()).not.toContain('重新运行');
    expect(wrapper.text()).not.toContain('取消流水线');
    expect(wrapper.text()).not.toContain('Webhook');
    expect(wrapper.text()).not.toContain('Token');
    expect(wrapper.text()).not.toContain('部署');
    expect(wrapper.text()).not.toContain('发布');
  });

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
            status: 'needs_review',
            summary: 'CI/CD quality gate needs review because new-test evidence is missing.',
            blocking_reasons: ['missing new-test evidence'],
            evidence_artifact_ids: ['00000000-0000-0000-0000-000000001211'],
            decided_by: 'system',
            status_detail: {
              patch_scope_gate: { allowed: true },
              unit_test_patch: { id: '00000000-0000-0000-0000-000000001201', status: 'applied' },
              new_tests: { status: 'missing', test_run_ids: [] },
              regression: { status: 'succeeded' },
            },
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.includes('/review-history?')) {
        if (url.includes('entity_type=UnitTestPatch')) {
          const hasRejectCall = fetchMock.mock.calls.some((call) =>
            String(call[0]).endsWith('/cicd/unit-test-patches/00000000-0000-0000-0000-000000001201/reject'),
          );
          const hasApproveCall = fetchMock.mock.calls.some((call) =>
            String(call[0]).endsWith('/cicd/unit-test-patches/00000000-0000-0000-0000-000000001201/approve'),
          );
          const items = [];
          if (hasRejectCall) {
            items.push({
              id: '00000000-0000-0000-0000-000000001a12',
              project_id: '00000000-0000-0000-0000-000000000101',
              entity_type: 'UnitTestPatch',
              entity_id: '00000000-0000-0000-0000-000000001201',
              related_entity_type: 'CICDRun',
              related_entity_id: '00000000-0000-0000-0000-000000001101',
              action: 'reject',
              from_status: 'approved',
              to_status: 'rejected',
              reviewer: 'Default User',
              comment: '前端拒绝 UnitTestPatch',
              evidence_artifact_ids: [],
              metadata_json: {},
              created_at: '2026-07-01T02:50:00Z',
            });
          }
          if (hasApproveCall) {
            items.push({
              id: '00000000-0000-0000-0000-000000001a11',
              project_id: '00000000-0000-0000-0000-000000000101',
              entity_type: 'UnitTestPatch',
              entity_id: '00000000-0000-0000-0000-000000001201',
              related_entity_type: 'CICDRun',
              related_entity_id: '00000000-0000-0000-0000-000000001101',
              action: 'approve',
              from_status: 'scope_validated',
              to_status: 'approved',
              reviewer: 'Default User',
              comment: '前端批准 UnitTestPatch',
              evidence_artifact_ids: ['00000000-0000-0000-0000-000000001211'],
              metadata_json: {},
              created_at: '2026-07-01T02:45:00Z',
            });
          }
          return new Response(JSON.stringify({ items, total: items.length }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          });
        }
        if (url.includes('related_entity_type=CICDRun')) {
          return new Response(
            JSON.stringify({
              total: 1,
              items: [
                {
                  id: '00000000-0000-0000-0000-000000001a21',
                  project_id: '00000000-0000-0000-0000-000000000101',
                  entity_type: 'QualityGateDecision',
                  entity_id: '00000000-0000-0000-0000-000000001401',
                  related_entity_type: 'CICDRun',
                  related_entity_id: '00000000-0000-0000-0000-000000001101',
                  action: 'compute_quality_gate',
                  from_status: 'pending',
                  to_status: 'passed',
                  reviewer: 'Default User',
                  comment: '本地质量门禁计算',
                  evidence_artifact_ids: ['00000000-0000-0000-0000-000000001211', '00000000-0000-0000-0000-000000001221'],
                  metadata_json: {},
                  created_at: '2026-07-01T02:55:00Z',
                },
              ],
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } },
          );
        }
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
    expect(wrapper.text()).toContain('本地评审历史');
    expect(wrapper.text()).toContain('Default User');
    expect(wrapper.text()).toContain('范围已验证 -> 已批准');
    expect(wrapper.text()).toContain('前端批准 UnitTestPatch');
    expect(wrapper.text()).toContain('证据 1');

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
    expect(wrapper.text()).toContain('需要复核');
    expect(wrapper.text()).toContain('门禁证据摘要');
    expect(wrapper.text()).toContain('UnitTestPatch / PatchScopeGate');
    expect(wrapper.text()).toContain('新增测试证据');
    expect(wrapper.text()).toContain('缺失不可打开');
    expect(wrapper.text()).toContain('回归证据');
    expect(wrapper.text()).toContain('阻塞原因');
    expect(wrapper.text()).toContain('缺少新增测试证据');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001211/download"]').exists()).toBe(true);
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001221/download"]').exists()).toBe(false);
    expect(wrapper.text()).toContain('计算门禁');
    expect(wrapper.text()).toContain('待处理 -> 通过');
    expect(wrapper.text()).toContain('本地质量门禁计算');
    expect(wrapper.text()).toContain('证据 2');
    expect(wrapper.text()).toContain('报告');
    expect(wrapper.text()).toContain('00000000-0000-0000-0000-000000001501');

    await wrapper.find('[data-test="reject-unit-test-patch"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('已拒绝');
    expect(wrapper.text()).toContain('已批准 -> 已拒绝');
    expect(wrapper.text()).toContain('前端拒绝 UnitTestPatch');
    expect(wrapper.text()).toContain('证据 0');
    expect(wrapper.text()).not.toContain('重新运行流水线');
    expect(wrapper.text()).not.toContain('PR 评论');
    expect(wrapper.text()).not.toContain('部署');
    expect(wrapper.text()).not.toContain('发布');
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/review-history?project_id=00000000-0000-0000-0000-000000000101&entity_type=UnitTestPatch&entity_id=00000000-0000-0000-0000-000000001201&limit=20',
      expect.objectContaining({ headers: expect.objectContaining({ Accept: 'application/json' }) }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/review-history?project_id=00000000-0000-0000-0000-000000000101&related_entity_type=CICDRun&related_entity_id=00000000-0000-0000-0000-000000001101&limit=20',
      expect.objectContaining({ headers: expect.objectContaining({ Accept: 'application/json' }) }),
    );
  });
});
