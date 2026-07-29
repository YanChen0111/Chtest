import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import ReportFailureAnalysisView from './ReportFailureAnalysisView.vue';
import { useExecutionStore } from '../../stores/execution';
import { useReportingStore } from '../../stores/reporting';

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

function executionResultReviewBody(state = 'waiting_approval') {
  return {
    project_id: '00000000-0000-0000-0000-000000000101',
    requirement_review_id: '00000000-0000-0000-0000-000000000601',
    workflow: {
      run_id: '00000000-0000-0000-0000-000000009101',
      stage: 'execution_result_review',
      state,
      lock_version: state === 'approved' ? 11 : 10,
      snapshot_id: '00000000-0000-0000-0000-000000009102',
      approval_decision_id: state === 'approved' ? '00000000-0000-0000-0000-000000009103' : null,
      can_submit: false,
      can_complete_review: false,
      can_edit: true,
      can_approve: state === 'waiting_approval',
      can_continue: state === 'approved',
    },
    source_execution_approval_snapshot_id: '00000000-0000-0000-0000-000000009002',
    source_execution_approval_snapshot_hash: 'sha256:execution-approval',
    source_automation_draft_review_snapshot_id: '00000000-0000-0000-0000-000000008002',
    source_automation_draft_review_snapshot_hash: 'sha256:draft-review',
    source_automation_plan_review_snapshot_id: '00000000-0000-0000-0000-000000007002',
    source_automation_plan_review_snapshot_hash: 'sha256:plan-review',
    source_case_review_snapshot_id: '00000000-0000-0000-0000-000000006002',
    source_case_review_snapshot_hash: 'sha256:case-review',
    approved_automation_draft_ids: ['00000000-0000-0000-0000-000000001001'],
    generated_test_run_ids: ['00000000-0000-0000-0000-000000001301'],
    execution_artifact_ids: ['00000000-0000-0000-0000-000000001601'],
    execution_decisions: [],
    result_decisions: [],
  };
}

describe('ReportFailureAnalysisView', () => {
  it('offers a named resume action for recent test runs', async () => {
    const pinia = createPinia();
    const executionStore = useExecutionStore(pinia);
    executionStore.recentRunsHydrated = true;
    executionStore.recentRuns = [
      {
        id: '00000000-0000-0000-0000-000000001399',
        project_id: '00000000-0000-0000-0000-000000000101',
        automation_draft_id: null,
        test_command_id: '00000000-0000-0000-0000-000000000302',
        tool_invocation_id: null,
        name: 'pytest coupon regression',
        command: 'pytest tests/test_coupon.py',
        working_directory: '.',
        runner_mode: 'local_subprocess',
        run_workspace: null,
        repository_readonly: true,
        network_enabled: false,
        runtime_artifact_ids: [],
        dependency_snapshot_artifact_id: null,
        environment_snapshot_artifact_id: null,
        status: 'failed',
        exit_code: 1,
        duration_ms: 1200,
        parsed_result: {},
        test_results: [],
        artifacts: [],
      },
    ];
    const wrapper = mount(ReportFailureAnalysisView, {
      global: { plugins: [pinia, ArcoVue] },
    });

    expect(wrapper.find('[data-test="reporting-recent-runs-list"]').exists()).toBe(true);
    await wrapper.find('[data-test="resume-reporting-run-00000000-0000-0000-0000-000000001399"]').trigger('click');
    await wrapper.vm.$nextTick();

    expect(useReportingStore(pinia).testRunId).toBe('00000000-0000-0000-0000-000000001399');
    expect((wrapper.find('[data-test="reporting-test-run-id"] input').element as HTMLInputElement).value).toBe(
      '00000000-0000-0000-0000-000000001399',
    );
  });

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
    expect(wrapper.text()).toContain('当前分析对象');

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
    expect(renderedText).not.toContain('evidence_manifest.json');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001601/download"]').text()).toBe('打开');
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000001701/download"]').text()).toBe('打开');
    expect(fetchMock).toHaveBeenCalledTimes(4);
  });

  it('requires ExecutionResultReview approval before workflow-backed analysis and report generation', async () => {
    const pinia = createPinia();
    const reportingStore = useReportingStore(pinia);
    reportingStore.requirementReviewId = '00000000-0000-0000-0000-000000000601';
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirement-reviews/00000000-0000-0000-0000-000000000601/execution-result-review')) {
        return new Response(JSON.stringify(executionResultReviewBody()), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/execution-result-review/approve') && init?.method === 'POST') {
        const payload = JSON.parse(String(init.body));
        expect(payload.expected_version).toBe(10);
        return new Response(JSON.stringify(executionResultReviewBody('approved')), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/failure-analysis') && init?.method === 'POST') {
        const payload = JSON.parse(String(init.body));
        expect(payload.execution_result_review_decision_id).toBe('00000000-0000-0000-0000-000000009103');
        return new Response(JSON.stringify({
          ai_task_id: '00000000-0000-0000-0000-000000001501',
          failure_analysis_id: '00000000-0000-0000-0000-000000001502',
          status: 'draft',
        }), { status: 202, headers: { 'Content-Type': 'application/json' } });
      }
      if (url.includes('/failure-analysis')) {
        return new Response(JSON.stringify(failureAnalysisBody()), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/reports') && init?.method === 'POST') {
        const payload = JSON.parse(String(init.body));
        expect(payload.execution_result_review_decision_id).toBe('00000000-0000-0000-0000-000000009103');
        return new Response(JSON.stringify({
          report_id: '00000000-0000-0000-0000-000000001701',
          status: 'ready',
          evidence_manifest_artifact_id: '00000000-0000-0000-0000-000000001703',
        }), { status: 202, headers: { 'Content-Type': 'application/json' } });
      }
      if (url.includes('/reports/')) {
        return new Response(JSON.stringify(reportBody()), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(ReportFailureAnalysisView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    expect(wrapper.find('[data-test="execution-result-review-panel"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('ExecutionResultReview gate');
    expect(wrapper.find('[data-test="reporting-test-run-id"] input').element).toHaveProperty(
      'value',
      '00000000-0000-0000-0000-000000001301',
    );

    await wrapper.find('[data-test="start-failure-analysis"]').trigger('click');
    await flushPromises();
    expect(reportingStore.errorMessage).toContain('ExecutionResultReview gate');
    await wrapper.find('[data-test="start-report"]').trigger('click');
    await flushPromises();
    expect(reportingStore.errorMessage).toContain('ExecutionResultReview gate');

    await wrapper.find('[data-test="execution-result-review-approve"]').trigger('click');
    await flushPromises();
    await wrapper.find('[data-test="start-failure-analysis"]').trigger('click');
    await flushPromises();
    await wrapper.find('[data-test="start-report"]').trigger('click');
    await flushPromises();

    expect(wrapper.text()).toContain('test_script_issue');
    expect(reportingStore.report?.id).toBe('00000000-0000-0000-0000-000000001401');
    expect(fetchMock).toHaveBeenCalledTimes(6);
  });
});
