import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import ReportFailureAnalysisView from './ReportFailureAnalysisView.vue';
import { useExecutionStore } from '../../stores/execution';
import { useReportingStore } from '../../stores/reporting';

const projectId = '00000000-0000-0000-0000-000000000101';
const requirementId = '00000000-0000-0000-0000-000000000401';
const requirementReviewId = '00000000-0000-0000-0000-000000000601';
const workflowRunId = '00000000-0000-0000-0000-000000009101';
const routeQuery: Record<string, string | undefined> = {};

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: routeQuery }),
}));

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function exactRequirement() {
  return {
    id: requirementId,
    project_id: projectId,
    module_id: null,
    title: 'Exact ExecutionResultReview requirement',
    content: 'Restore only the authoritative execution result review gate.',
    source_type: 'manual',
    source_ref: 'REQ-EXECUTION-RESULT-EXACT',
    status: 'active',
    created_at: '2026-08-04T00:00:00Z',
    updated_at: '2026-08-04T00:00:00Z',
  };
}

function exactRequirementReview() {
  return {
    id: requirementReviewId,
    requirement_id: requirementId,
    overall_score: 94,
    scores: { completeness: 94, clarity: 94, consistency: 94, testability: 94, feasibility: 94, logic: 94 },
    issues: [],
    clarification_questions: [],
    test_design_notes: [],
    risk_items: [],
    used_knowledge: false,
    used_context_artifact_ids: [],
    context_manifest_artifact_id: null,
    status: 'reviewed',
  };
}

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

function reportBody(status = 'ready') {
  return {
    id: '00000000-0000-0000-0000-000000001401',
    project_id: '00000000-0000-0000-0000-000000000101',
    report_type: 'automation_execution',
    title: 'Automation execution report',
    related_entity_type: 'TestRun',
    related_entity_id: '00000000-0000-0000-0000-000000001301',
    status,
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

function exactExecutionResultReview(overrides: {
  project_id?: string;
  requirement_review_id?: string;
  stage?: string;
  run_id?: string;
  state?: string;
} = {}) {
  const state = overrides.state ?? 'waiting_approval';
  const body = executionResultReviewBody(state);
  return {
    ...body,
    project_id: overrides.project_id ?? projectId,
    requirement_review_id: overrides.requirement_review_id ?? requirementReviewId,
    workflow: {
      ...body.workflow,
      run_id: overrides.run_id ?? workflowRunId,
      stage: overrides.stage ?? 'execution_result_review',
    },
  };
}

function reportReviewBody(state = 'draft', published = false) {
  return {
    project_id: '00000000-0000-0000-0000-000000000101',
    requirement_review_id: '00000000-0000-0000-0000-000000000601',
    workflow: {
      run_id: '00000000-0000-0000-0000-000000009101',
      stage: 'report_review',
      state,
      lock_version: state === 'draft' ? 12 : state === 'waiting_review' ? 13 : state === 'waiting_approval' ? 14 : published ? 16 : 15,
      snapshot_id: '00000000-0000-0000-0000-000000009202',
      approval_decision_id: state === 'approved' && !published ? '00000000-0000-0000-0000-000000009203' : null,
      can_submit: state === 'draft',
      can_complete_review: state === 'waiting_review',
      can_edit: ['waiting_review', 'waiting_approval', 'approved', 'rejected'].includes(state),
      can_approve: state === 'waiting_approval',
      can_continue: state === 'approved' && !published,
      published,
    },
    source_execution_result_review_snapshot_id: '00000000-0000-0000-0000-000000009102',
    source_execution_result_review_snapshot_hash: 'sha256:execution-result-review',
    source_execution_approval_snapshot_id: '00000000-0000-0000-0000-000000009002',
    source_execution_approval_snapshot_hash: 'sha256:execution-approval',
    generated_test_run_ids: ['00000000-0000-0000-0000-000000001301'],
    execution_artifact_ids: ['00000000-0000-0000-0000-000000001601'],
    generated_report_ids: ['00000000-0000-0000-0000-000000001401'],
    report_artifact_ids: [
      '00000000-0000-0000-0000-000000001701',
      '00000000-0000-0000-0000-000000001702',
      '00000000-0000-0000-0000-000000001703',
    ],
    execution_decisions: [],
    result_decisions: [],
    report_decisions: [],
  };
}

function exactReportReview(overrides: {
  project_id?: string;
  requirement_review_id?: string;
  stage?: string;
  run_id?: string;
  state?: string;
} = {}) {
  const state = overrides.state ?? 'waiting_approval';
  const body = reportReviewBody(state);
  return {
    ...body,
    project_id: overrides.project_id ?? projectId,
    requirement_review_id: overrides.requirement_review_id ?? requirementReviewId,
    workflow: {
      ...body.workflow,
      run_id: overrides.run_id ?? workflowRunId,
      stage: overrides.stage ?? 'report_review',
    },
  };
}

function exactReport(overrides: { project_id?: string; related_entity_id?: string } = {}) {
  return {
    ...reportBody(),
    project_id: overrides.project_id ?? projectId,
    related_entity_id: overrides.related_entity_id ?? '00000000-0000-0000-0000-000000001301',
  };
}

describe('ReportFailureAnalysisView', () => {
  beforeEach(() => {
    window.localStorage.clear();
    Object.keys(routeQuery).forEach((key) => delete routeQuery[key]);
  });

  afterEach(() => vi.unstubAllGlobals());

  it('restores the exact ExecutionResultReview and uses its server lock for actions', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'execution_result_review';
    window.localStorage.setItem('chtest.execution.recent-runs', JSON.stringify([{
      id: '00000000-0000-0000-0000-000000001399',
      project_id: projectId,
      name: 'stale recent run',
      command: 'pytest stale',
      status: 'failed',
    }]));
    let actionBody: unknown = null;
    const requestedUrls: string[] = [];
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      requestedUrls.push(url);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/requirements/${requirementId}/review`)) return jsonResponse(exactRequirementReview());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-result-review`) && !init?.method) {
        return jsonResponse(exactExecutionResultReview());
      }
      if (url.endsWith('/execution-result-review/approve') && init?.method === 'POST') {
        actionBody = JSON.parse(String(init.body));
        return jsonResponse(exactExecutionResultReview({ state: 'approved' }));
      }
      return new Response('not found', { status: 404 });
    }));
    const pinia = createPinia();

    const wrapper = mount(ReportFailureAnalysisView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    const reportingStore = useReportingStore(pinia);
    const executionStore = useExecutionStore(pinia);
    expect(reportingStore.requirementReviewId).toBe(requirementReviewId);
    expect(reportingStore.testRunId).toBe('00000000-0000-0000-0000-000000001301');
    expect(reportingStore.reportReviewWorkflow).toBeNull();
    expect(reportingStore.failureAnalysis).toBeNull();
    expect(reportingStore.report).toBeNull();
    expect(executionStore.recentRuns).toEqual([]);
    expect(wrapper.find('[data-test="reporting-recent-runs"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="start-failure-analysis"]').attributes('disabled')).toBeDefined();
    expect(wrapper.find('[data-test="start-report"]').attributes('disabled')).toBeDefined();
    expect(requestedUrls.some((url) => url.includes('/report-review'))).toBe(false);

    await wrapper.find('[data-test="execution-result-review-approve"]').trigger('click');
    await flushPromises();
    expect(actionBody).toEqual(expect.objectContaining({
      expected_version: 10,
      comment: 'Execution result evidence reviewed.',
    }));
    expect(wrapper.find('[data-test="start-failure-analysis"]').attributes('disabled')).toBeUndefined();
    expect(wrapper.find('[data-test="start-report"]').attributes('disabled')).toBeUndefined();
  });

  it.each([
    ['project identity', { project_id: '00000000-0000-0000-0000-000000000199' }],
    ['review identity', { requirement_review_id: '00000000-0000-0000-0000-000000000699' }],
    ['workflow stage', { stage: 'report_review' }],
    ['workflow run', { run_id: '00000000-0000-0000-0000-000000009199' }],
  ])('fails closed when the restored ExecutionResultReview has a mismatched %s', async (_label, overrides) => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'execution_result_review';
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/requirements/${requirementId}/review`)) return jsonResponse(exactRequirementReview());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${requirementReviewId}/execution-result-review`)) {
        return jsonResponse(exactExecutionResultReview(overrides));
      }
      return new Response('not found', { status: 404 });
    }));
    const pinia = createPinia();
    const reportingStore = useReportingStore(pinia);
    reportingStore.testRunId = '00000000-0000-0000-0000-000000001399';
    reportingStore.requirementReviewId = requirementReviewId;
    reportingStore.executionResultReviewWorkflow = executionResultReviewBody();
    reportingStore.reportReviewWorkflow = reportReviewBody();
    reportingStore.failureAnalysis = failureAnalysisBody();
    reportingStore.report = reportBody();

    const wrapper = mount(ReportFailureAnalysisView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    expect(reportingStore.exactRestoreFailed).toBe(true);
    expect(reportingStore.requirementReviewId).toBe('');
    expect(reportingStore.testRunId).toBe('');
    expect(reportingStore.executionResultReviewWorkflow).toBeNull();
    expect(reportingStore.reportReviewWorkflow).toBeNull();
    expect(reportingStore.failureAnalysis).toBeNull();
    expect(reportingStore.report).toBeNull();
    expect(wrapper.find('[data-test="exact-execution-result-review-restore-failed"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="execution-result-review-panel"]').exists()).toBe(false);
  });

  it('fails closed without network or recent context when an ExecutionResultReview route parameter is missing', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_stage = 'execution_result_review';
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(ReportFailureAnalysisView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });
    await flushPromises();

    expect(fetchMock).not.toHaveBeenCalled();
    expect(wrapper.find('[data-test="exact-execution-result-review-restore-failed"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="reporting-recent-runs"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="start-failure-analysis"]').attributes('disabled')).toBeDefined();
    expect(wrapper.find('[data-test="start-report"]').attributes('disabled')).toBeDefined();
  });

  it('restores the exact ReportReview, report evidence, and server-owned publication lock', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'report_review';
    let approveBody: unknown = null;
    let continueBody: unknown = null;
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/requirements/${requirementId}/review`)) return jsonResponse(exactRequirementReview());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${requirementReviewId}/report-review`) && !init?.method) {
        return jsonResponse(exactReportReview());
      }
      if (url.endsWith('/reports/00000000-0000-0000-0000-000000001401') && !init?.method) {
        return jsonResponse(exactReport());
      }
      if (url.endsWith('/report-review/approve') && init?.method === 'POST') {
        approveBody = JSON.parse(String(init.body));
        return jsonResponse(exactReportReview({ state: 'approved' }));
      }
      if (url.endsWith('/report-review/continue') && init?.method === 'POST') {
        continueBody = JSON.parse(String(init.body));
        return jsonResponse(reportReviewBody('approved', true));
      }
      return new Response('not found', { status: 404 });
    }));
    const pinia = createPinia();

    const wrapper = mount(ReportFailureAnalysisView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    const reportingStore = useReportingStore(pinia);
    expect(reportingStore.requirementReviewId).toBe(requirementReviewId);
    expect(reportingStore.executionResultReviewWorkflow).toBeNull();
    expect(reportingStore.reportReviewWorkflow?.workflow.run_id).toBe(workflowRunId);
    expect(reportingStore.report?.id).toBe('00000000-0000-0000-0000-000000001401');
    expect(wrapper.find('[data-test="execution-result-review-panel"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="report-review-panel"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="reporting-recent-runs"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="start-failure-analysis"]').attributes('disabled')).toBeDefined();
    expect(wrapper.find('[data-test="start-report"]').attributes('disabled')).toBeDefined();

    await wrapper.find('[data-test="report-review-approve"]').trigger('click');
    await flushPromises();
    expect(approveBody).toEqual(expect.objectContaining({
      expected_version: 14,
      comment: 'Report evidence reviewed.',
    }));

    await wrapper.find('[data-test="report-review-continue"]').trigger('click');
    await flushPromises();
    expect(continueBody).toEqual({
      expected_version: 15,
      approval_decision_id: '00000000-0000-0000-0000-000000009203',
    });
    expect(wrapper.text()).toContain('published');
  });

  it.each([
    ['project identity', { project_id: '00000000-0000-0000-0000-000000000199' }],
    ['review identity', { requirement_review_id: '00000000-0000-0000-0000-000000000699' }],
    ['workflow stage', { stage: 'execution_result_review' }],
    ['workflow run', { run_id: '00000000-0000-0000-0000-000000009199' }],
  ])('fails closed when the restored ReportReview has a mismatched %s', async (_label, overrides) => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'report_review';
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/requirements/${requirementId}/review`)) return jsonResponse(exactRequirementReview());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${requirementReviewId}/report-review`)) {
        return jsonResponse(exactReportReview(overrides));
      }
      return new Response('not found', { status: 404 });
    }));

    const wrapper = mount(ReportFailureAnalysisView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });
    await flushPromises();

    expect(wrapper.find('[data-test="exact-report-review-restore-failed"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="report-review-panel"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="start-report"]').attributes('disabled')).toBeDefined();
  });

  it('fails closed when the exact ReportReview report belongs to another TestRun', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_run_id = workflowRunId;
    routeQuery.workflow_stage = 'report_review';
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith(`/requirements/${requirementId}`)) return jsonResponse(exactRequirement());
      if (url.endsWith(`/requirements/${requirementId}/review`)) return jsonResponse(exactRequirementReview());
      if (url.endsWith(`/projects/${projectId}/requirement-reviews/${requirementReviewId}/report-review`)) {
        return jsonResponse(exactReportReview());
      }
      if (url.endsWith('/reports/00000000-0000-0000-0000-000000001401')) {
        return jsonResponse(exactReport({ related_entity_id: '00000000-0000-0000-0000-000000001399' }));
      }
      return new Response('not found', { status: 404 });
    }));
    const pinia = createPinia();
    const reportingStore = useReportingStore(pinia);

    const wrapper = mount(ReportFailureAnalysisView, {
      global: { plugins: [pinia, ArcoVue] },
    });
    await flushPromises();

    expect(reportingStore.testRunId).toBe('');
    expect(reportingStore.reportReviewWorkflow).toBeNull();
    expect(reportingStore.report).toBeNull();
    expect(wrapper.find('[data-test="exact-report-review-restore-failed"]').exists()).toBe(true);
  });

  it('fails closed without network when a ReportReview route parameter is missing', async () => {
    routeQuery.requirement_id = requirementId;
    routeQuery.requirement_review_id = requirementReviewId;
    routeQuery.workflow_stage = 'report_review';
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(ReportFailureAnalysisView, {
      global: { plugins: [createPinia(), ArcoVue] },
    });
    await flushPromises();

    expect(fetchMock).not.toHaveBeenCalled();
    expect(wrapper.find('[data-test="exact-report-review-restore-failed"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="reporting-recent-runs"]').exists()).toBe(false);
  });

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
    let reportStatus = 'draft';
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
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/requirement-reviews/00000000-0000-0000-0000-000000000601/report-review')) {
        return new Response(JSON.stringify(reportReviewBody('draft')), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/report-review/submit') && init?.method === 'POST') {
        return new Response(JSON.stringify(reportReviewBody('waiting_review')), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/report-review/complete-review') && init?.method === 'POST') {
        return new Response(JSON.stringify(reportReviewBody('waiting_approval')), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/report-review/edit') && init?.method === 'POST') {
        const payload = JSON.parse(String(init.body));
        expect(payload.report_decisions[0].report_id).toBe('00000000-0000-0000-0000-000000001401');
        return new Response(JSON.stringify(reportReviewBody('draft')), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/report-review/approve') && init?.method === 'POST') {
        return new Response(JSON.stringify(reportReviewBody('approved')), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/report-review/continue') && init?.method === 'POST') {
        const payload = JSON.parse(String(init.body));
        expect(payload.approval_decision_id).toBe('00000000-0000-0000-0000-000000009203');
        reportStatus = 'ready';
        return new Response(JSON.stringify(reportReviewBody('approved', true)), {
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
          report_id: '00000000-0000-0000-0000-000000001401',
          status: 'draft',
          evidence_manifest_artifact_id: '00000000-0000-0000-0000-000000001703',
        }), { status: 202, headers: { 'Content-Type': 'application/json' } });
      }
      if (url.includes('/reports/')) {
        return new Response(JSON.stringify(reportBody(reportStatus)), {
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
    expect(reportingStore.report?.status).toBe('draft');
    expect(wrapper.find('[data-test="report-review-panel"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('ReportReview gate');

    await wrapper.find('[data-test="report-review-submit"]').trigger('click');
    await flushPromises();
    await wrapper.find('[data-test="report-review-complete"]').trigger('click');
    await flushPromises();
    await wrapper.find('[data-test="report-review-edit"]').trigger('click');
    await flushPromises();
    await wrapper.find('[data-test="report-review-submit"]').trigger('click');
    await flushPromises();
    await wrapper.find('[data-test="report-review-complete"]').trigger('click');
    await flushPromises();
    await wrapper.find('[data-test="report-review-approve"]').trigger('click');
    await flushPromises();
    await wrapper.find('[data-test="report-review-continue"]').trigger('click');
    await flushPromises();

    expect(reportingStore.report?.status).toBe('ready');
    expect(wrapper.text()).toContain('published');
    expect(fetchMock).toHaveBeenCalled();
  });
});
