import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, describe, expect, it, vi } from 'vitest';

import AutomationDraftReviewView from './AutomationDraftReviewView.vue';
import { useAutomationStore } from '../../stores/automation';

describe('AutomationDraftReviewView', () => {
  afterEach(() => {
    window.localStorage.clear();
    vi.unstubAllGlobals();
  });

  it('loads reviewer assets and exposes the four-stage workflow', async () => {
    const latestTestCaseId = '00000000-0000-0000-0000-000000000955';
    const newmanCommandId = '00000000-0000-0000-0000-000000000321';
    window.localStorage.setItem(
      'chtest.latestApprovedTestCase',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        testCaseId: latestTestCaseId,
      }),
    );
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes('/test-cases?project_id=')) {
        return new Response(
          JSON.stringify({
            items: [
              {
                id: latestTestCaseId,
                project_id: '00000000-0000-0000-0000-000000000101',
                module_id: null,
                source_candidate_id: null,
                title: '订单金额优惠规则',
                priority: 'P0',
                test_type: 'functional',
                precondition: null,
                steps: ['提交订单'],
                expected_results: ['金额正确'],
                input_data: {},
                tags: ['reviewed'],
                source_type: 'ai',
                review_status: 'approved',
                status: 'active',
              },
            ],
            total: 1,
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/settings')) {
        return new Response(
          JSON.stringify({
            project: {
              id: '00000000-0000-0000-0000-000000000101',
              name: 'Chtest',
              default_language: 'zh-CN',
              default_test_type: 'functional',
            },
            modules: [],
            repositories: [],
            environments: [],
            test_commands: [
              {
                id: newmanCommandId,
                name: '订单 API 回归',
                command: 'newman run orders.json',
                working_directory: '.',
                command_type: 'newman',
                timeout_seconds: 60,
                parse_junit: true,
                parse_coverage: false,
                status: 'active',
              },
            ],
            tool_definitions: [],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const pinia = createPinia();
    const wrapper = mount(AutomationDraftReviewView, {
      global: {
        plugins: [pinia, ArcoVue],
      },
    });
    const store = useAutomationStore();
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(store.testCases).toEqual([expect.objectContaining({ id: latestTestCaseId, title: '订单金额优惠规则' })]);
    expect(store.testCommands).toEqual([
      expect.objectContaining({ id: newmanCommandId, name: '订单 API 回归', command_type: 'newman' }),
    ]);
    expect(wrapper.find('[data-test="automation-test-case-select"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="automation-draft-workbench"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="automation-execution-empty-state"]').exists()).toBe(false);
    expect(wrapper.findAll('[data-test^="automation-workflow-step-"]')).toHaveLength(4);
    expect(wrapper.text()).toContain('选择用例');
    expect(wrapper.text()).toContain('执行取证');
  });

  it('creates an approved automation plan before generating and approving a draft', async () => {
    const latestTestCaseId = '00000000-0000-0000-0000-000000000955';
    const planId = '00000000-0000-0000-0000-000000000p01'.replace('p', 'a');
    const draftId = '00000000-0000-0000-0000-000000001001';
    const aiTaskId = '00000000-0000-0000-0000-000000001002';
    let planBody: unknown = null;
    let executionBody: unknown = null;

    window.localStorage.setItem(
      'chtest.latestApprovedTestCase',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        testCaseId: latestTestCaseId,
        sourceCandidateId: '00000000-0000-0000-0000-000000000801',
        reviewStatus: 'approved_after_edit',
      }),
    );

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/automation/plans') && init?.method === 'POST') {
        planBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            id: planId,
            project_id: '00000000-0000-0000-0000-000000000101',
            test_case_id: latestTestCaseId,
            requirement_id: '00000000-0000-0000-0000-000000000401',
            requirement_review_id: '00000000-0000-0000-0000-000000000601',
            source_candidate_id: '00000000-0000-0000-0000-000000000801',
            ai_task_id: '00000000-0000-0000-0000-000000000a01',
            knowledge_retrieval_artifact_id: '00000000-0000-0000-0000-000000000e01',
            target_framework: 'pytest',
            title: 'pytest automation plan for expired coupon',
            plan: { source: 'reviewed_test_case' },
            execution_steps: ['Prepare precondition: expired coupon', 'Automate step: submit order'],
            test_data: { coupon_state: 'expired' },
            dependency_notes: 'Requires pytest and project-local fixtures.',
            risk_notes: 'Review selectors and fixtures.',
            used_context_artifact_ids: ['00000000-0000-0000-0000-000000000c01'],
            status: 'plan_generated',
            review_comment: null,
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith(`/automation/plans/${planId}/approve`) && init?.method === 'POST') {
        return new Response(JSON.stringify({ automation_plan_id: planId, status: 'approved' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith(`/automation/plans/${planId}/generate-draft`) && init?.method === 'POST') {
        return new Response(
          JSON.stringify({ automation_draft_id: draftId, ai_task_id: aiTaskId, status: 'draft_generated' }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith(`/automation/drafts/${draftId}`) && (!init?.method || init.method === 'GET')) {
        return new Response(
          JSON.stringify({
            id: draftId,
            project_id: '00000000-0000-0000-0000-000000000101',
            test_case_id: latestTestCaseId,
            requirement_id: '00000000-0000-0000-0000-000000000401',
            ai_task_id: aiTaskId,
            automation_plan_id: planId,
            target_framework: 'pytest',
            title: 'pytest draft for expired coupon',
            draft_code: 'def test_expired_coupon():\n    assert True\n',
            draft_language: 'python',
            suggested_file_path: 'tests/test_expired_coupon.py',
            execution_notes: 'Generated from an approved AutomationPlan.',
            risk_notes: 'Review selectors and fixtures.',
            execution_strategy: 'artifact_runtime_copy',
            approval_required: true,
            status: 'draft_generated',
            review_comment: null,
            runtime_artifact_id: null,
            promoted_artifact_id: null,
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith(`/automation/drafts/${draftId}`) && init?.method === 'PATCH') {
        return new Response(JSON.stringify({ automation_draft_id: draftId, status: 'edited' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith(`/automation/drafts/${draftId}/approve`) && init?.method === 'POST') {
        return new Response(JSON.stringify({ automation_draft_id: draftId, status: 'approved' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/review-history?') && url.includes('entity_type=AutomationPlan')) {
        const hasApproveCall = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith(`/automation/plans/${planId}/approve`) && call[1]?.method === 'POST',
        );
        const hasGenerateCall = fetchMock.mock.calls.some(
          (call) =>
            String(call[0]).endsWith(`/automation/plans/${planId}/generate-draft`) && call[1]?.method === 'POST',
        );
        const items = [];
        if (hasGenerateCall) {
          items.push({
            id: '00000000-0000-0000-0000-000000000h02'.replace('h', 'b'),
            project_id: '00000000-0000-0000-0000-000000000101',
            entity_type: 'AutomationPlan',
            entity_id: planId,
            related_entity_type: 'AutomationDraft',
            related_entity_id: draftId,
            action: 'generate_draft',
            from_status: 'approved',
            to_status: 'draft_generated',
            reviewer: 'Default User',
            comment: 'Generated AutomationDraft from approved AutomationPlan.',
            evidence_artifact_ids: [],
            metadata_json: {},
            created_at: '2026-07-01T02:22:00Z',
          });
        }
        if (hasApproveCall) {
          items.push({
            id: '00000000-0000-0000-0000-000000000h01'.replace('h', 'b'),
            project_id: '00000000-0000-0000-0000-000000000101',
            entity_type: 'AutomationPlan',
            entity_id: planId,
            related_entity_type: null,
            related_entity_id: null,
            action: 'approve',
            from_status: 'plan_generated',
            to_status: 'approved',
            reviewer: 'Default User',
            comment: '前端批准自动化方案',
            evidence_artifact_ids: [],
            metadata_json: {},
            created_at: '2026-07-01T02:20:00Z',
          });
        }
        return new Response(JSON.stringify({ items, total: items.length }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/review-history?') && url.includes('entity_type=AutomationDraft')) {
        const hasApproveCall = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith(`/automation/drafts/${draftId}/approve`) && call[1]?.method === 'POST',
        );
        const hasEditCall = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith(`/automation/drafts/${draftId}`) && call[1]?.method === 'PATCH',
        );
        const items = [];
        if (hasApproveCall) {
          items.push({
            id: '00000000-0000-0000-0000-000000001a02',
            project_id: '00000000-0000-0000-0000-000000000101',
            entity_type: 'AutomationDraft',
            entity_id: draftId,
            related_entity_type: 'AutomationPlan',
            related_entity_id: planId,
            action: 'approve',
            from_status: 'edited',
            to_status: 'approved',
            reviewer: 'Default User',
            comment: '前端批准草稿',
            evidence_artifact_ids: ['00000000-0000-0000-0000-000000001e02'],
            metadata_json: {},
            created_at: '2026-07-01T02:25:00Z',
          });
        }
        if (hasEditCall) {
          items.push({
            id: '00000000-0000-0000-0000-000000001a01',
            project_id: '00000000-0000-0000-0000-000000000101',
            entity_type: 'AutomationDraft',
            entity_id: draftId,
            related_entity_type: 'AutomationPlan',
            related_entity_id: planId,
            action: 'edit',
            from_status: 'draft_generated',
            to_status: 'edited',
            reviewer: 'Default User',
            comment: '前端评审编辑',
            evidence_artifact_ids: ['00000000-0000-0000-0000-000000001e01'],
            metadata_json: {},
            created_at: '2026-07-01T02:23:00Z',
          });
        }
        return new Response(JSON.stringify({ items, total: items.length }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/test-runs') && init?.method === 'POST') {
        executionBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000001301',
            project_id: '00000000-0000-0000-0000-000000000101',
            automation_draft_id: draftId,
            test_command_id: null,
            tool_invocation_id: null,
            name: 'pytest approved draft: pytest draft for expired coupon',
            command: 'pytest tests/test_expired_coupon.py -q',
            working_directory: '/tmp/chtest-test-run',
            runner_mode: 'local_subprocess',
            run_workspace: '/tmp/chtest-test-run',
            repository_readonly: true,
            network_enabled: false,
            runtime_artifact_ids: ['00000000-0000-0000-0000-000000001601'],
            dependency_snapshot_artifact_id: null,
            environment_snapshot_artifact_id: null,
            status: 'passed',
            exit_code: 0,
            duration_ms: 880,
            parsed_result: {
              total: 1,
              passed: 1,
              failed: 0,
              skipped: 0,
              error: 0,
            },
            test_results: [
              {
                id: '00000000-0000-0000-0000-000000001501',
                project_id: '00000000-0000-0000-0000-000000000101',
                test_run_id: '00000000-0000-0000-0000-000000001301',
                test_name: 'generated::test_expired_coupon',
                test_file: 'tests/test_expired_coupon.py',
                status: 'passed',
                duration_ms: 12,
                failure_message: null,
                failure_artifact_ids: [],
                metadata: { source: 'pytest_runner' },
              },
            ],
            artifacts: [
              {
                id: '00000000-0000-0000-0000-000000001601',
                project_id: '00000000-0000-0000-0000-000000000101',
                owner_entity_type: 'TestRun',
                owner_entity_id: '00000000-0000-0000-0000-000000001301',
                artifact_type: 'runtime_manifest',
                file_path: 'test-runs/00000000-0000-0000-0000-000000001301/runtime_manifest.json',
                mime_type: 'application/json',
                size_bytes: 2,
                sha256: 'sha256:runtime',
                metadata_json: { created_by_component: 'PytestRunner' },
              },
              {
                id: '00000000-0000-0000-0000-000000001602',
                project_id: '00000000-0000-0000-0000-000000000101',
                owner_entity_type: 'TestRun',
                owner_entity_id: '00000000-0000-0000-0000-000000001301',
                artifact_type: 'stdout',
                file_path: 'test-runs/00000000-0000-0000-0000-000000001301/stdout.log',
                mime_type: 'text/plain',
                size_bytes: 20,
                sha256: 'sha256:stdout',
                metadata_json: { created_by_component: 'PytestRunner' },
              },
            ],
          }),
          { status: 201, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(AutomationDraftReviewView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    await wrapper.find('form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(planBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        test_case_id: latestTestCaseId,
        target_framework: 'pytest',
        use_knowledge: true,
      }),
    );
    expect(wrapper.text()).toContain('AutomationPlan');
    expect(wrapper.text()).toContain('pytest automation plan for expired coupon');
    expect(wrapper.text()).toContain('Prepare precondition: expired coupon');

    await wrapper.find('[data-test="approve-plan"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('approved');
    expect(wrapper.text()).toContain('方案评审历史');
    expect(wrapper.text()).toContain('前端批准自动化方案');

    await wrapper.find('[data-test="generate-draft-from-plan"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('pytest draft for expired coupon');
    expect(wrapper.text()).toContain('tests/test_expired_coupon.py');
    expect(wrapper.text()).toContain('Generated from an approved AutomationPlan.');
    expect(wrapper.text()).toContain('draft_generated');
    expect(wrapper.text()).toContain('def test_expired_coupon');
    expect(wrapper.text()).toContain('Quality gate');
    expect(wrapper.text()).toContain('fake, stub, placeholder, or assert True-only drafts cannot be approved.');
    expect(wrapper.text()).toContain('自动化执行');
    expect(wrapper.text()).toContain('API / Newman');
    expect(wrapper.text()).toContain('JMeter');

    await wrapper.find('[data-test="edit-draft"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('edited');
    expect(wrapper.text()).toContain('本地评审历史');
    expect(wrapper.text()).toContain('Default User');
    expect(wrapper.text()).toContain('前端评审编辑');
    expect(wrapper.text()).toContain('证据 1');

    await wrapper.find('[data-test="approve-draft"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('approved');
    expect(wrapper.text()).toContain('前端批准草稿');
    expect(JSON.parse(window.localStorage.getItem('chtest.latestAutomationDraft') ?? '{}')).toEqual(
      expect.objectContaining({
        projectId: '00000000-0000-0000-0000-000000000101',
        automationDraftId: draftId,
        status: 'approved',
        targetFramework: 'pytest',
      }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      `/api/review-history?project_id=00000000-0000-0000-0000-000000000101&entity_type=AutomationDraft&entity_id=${draftId}&limit=20`,
      expect.objectContaining({ headers: expect.objectContaining({ Accept: 'application/json' }) }),
    );

    await wrapper.find('.automation-execution-form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(executionBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        automation_draft_id: draftId,
        test_command_id: null,
        runner_mode: 'local_subprocess',
      }),
    );
    expect(wrapper.text()).toContain('pytest approved draft: pytest draft for expired coupon');
    expect(wrapper.text()).toContain('pytest tests/test_expired_coupon.py -q');
    expect(wrapper.text()).toContain('generated::test_expired_coupon');
    expect(wrapper.text()).toContain('stdout');
  });

  it('shows the quality gate error when placeholder draft approval is rejected', async () => {
    const draftId = '00000000-0000-0000-0000-000000001101';
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith(`/automation/drafts/${draftId}/approve`) && init?.method === 'POST') {
        return new Response(
          JSON.stringify({
            error_code: 'AUTOMATION_DRAFT_QUALITY_GATE_FAILED',
            message: 'Automation draft must contain non-placeholder executable test code before approval.',
            details: {},
          }),
          { status: 400, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const pinia = createPinia();
    const wrapper = mount(AutomationDraftReviewView, {
      global: {
        plugins: [pinia, ArcoVue],
      },
    });
    const store = useAutomationStore();
    store.draft = {
      id: draftId,
      project_id: '00000000-0000-0000-0000-000000000101',
      test_case_id: '00000000-0000-0000-0000-000000000955',
      requirement_id: null,
      ai_task_id: '00000000-0000-0000-0000-000000001102',
      automation_plan_id: null,
      target_framework: 'pytest',
      title: 'placeholder draft',
      draft_code: 'def test_placeholder():\n    assert True\n',
      draft_language: 'python',
      suggested_file_path: 'tests/test_placeholder.py',
      execution_notes: 'Generated draft.',
      risk_notes: 'Uses fake adapter.',
      execution_strategy: 'artifact_runtime_copy',
      approval_required: true,
      status: 'draft_generated',
      review_comment: null,
      runtime_artifact_id: null,
      promoted_artifact_id: null,
    };
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('Quality gate');
    expect(wrapper.text()).toContain('fake, stub, placeholder, or assert True-only drafts cannot be approved.');

    await wrapper.find('[data-test="approve-draft"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('Automation draft must contain non-placeholder executable test code before approval.');
    expect(wrapper.text()).toContain('AUTOMATION_DRAFT_QUALITY_GATE_FAILED');
    expect(store.draft.status).toBe('draft_generated');
  });

  it('starts API and JMeter automation from embedded TestCommand execution types', async () => {
    const draftId = '00000000-0000-0000-0000-000000001401';
    const executionBodies: unknown[] = [];
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/test-runs') && init?.method === 'POST') {
        const body = JSON.parse(String(init.body)) as { runner_mode: string; test_command_id: string | null };
        executionBodies.push(body);
        const isJMeter = body.runner_mode === 'jmeter_local';
        return new Response(
          JSON.stringify({
            id: isJMeter ? '00000000-0000-0000-0000-000000001402' : '00000000-0000-0000-0000-000000001401',
            project_id: '00000000-0000-0000-0000-000000000101',
            automation_draft_id: null,
            test_command_id: body.test_command_id,
            tool_invocation_id: null,
            name: isJMeter ? 'jmeter coupon smoke' : 'newman coupon api',
            command: isJMeter
              ? 'jmeter -n -t plans/coupon.jmx -l results.jtl'
              : 'npx newman run collections/coupon.postman_collection.json',
            working_directory: isJMeter ? '/tmp/chtest-jmeter-run' : '/tmp/chtest-newman-run',
            runner_mode: body.runner_mode,
            run_workspace: isJMeter ? '/tmp/chtest-jmeter-run' : '/tmp/chtest-newman-run',
            repository_readonly: true,
            network_enabled: false,
            runtime_artifact_ids: [],
            dependency_snapshot_artifact_id: null,
            environment_snapshot_artifact_id: null,
            status: 'passed',
            exit_code: 0,
            duration_ms: isJMeter ? 1300 : 900,
            parsed_result: isJMeter
              ? {
                  total: 1,
                  passed: 1,
                  failed: 0,
                  skipped: 0,
                  error: 0,
                  sampler_count: 1,
                  assertion_count: 1,
                  average_latency_ms: 82,
                }
              : {
                  total: 1,
                  passed: 1,
                  failed: 0,
                  skipped: 0,
                  error: 0,
                  request_count: 1,
                  assertion_count: 1,
                  collection_name: 'coupon-api',
                },
            test_results: [
              {
                id: isJMeter ? '00000000-0000-0000-0000-000000001512' : '00000000-0000-0000-0000-000000001511',
                project_id: '00000000-0000-0000-0000-000000000101',
                test_run_id: isJMeter
                  ? '00000000-0000-0000-0000-000000001402'
                  : '00000000-0000-0000-0000-000000001401',
                test_name: isJMeter ? 'jmeter/POST /coupons' : 'newman/POST /coupons validates response',
                test_file: null,
                status: 'passed',
                duration_ms: isJMeter ? 82 : 35,
                failure_message: null,
                failure_artifact_ids: [],
                metadata: { source: isJMeter ? 'jmeter_runner' : 'newman_runner' },
              },
            ],
            artifacts: [
              {
                id: isJMeter ? '00000000-0000-0000-0000-000000001612' : '00000000-0000-0000-0000-000000001611',
                project_id: '00000000-0000-0000-0000-000000000101',
                owner_entity_type: 'TestRun',
                owner_entity_id: isJMeter
                  ? '00000000-0000-0000-0000-000000001402'
                  : '00000000-0000-0000-0000-000000001401',
                artifact_type: isJMeter ? 'jmeter_jtl' : 'newman_json',
                file_path: isJMeter ? 'test-runs/jmeter/results.jtl' : 'test-runs/newman/newman-report.json',
                mime_type: isJMeter ? 'text/csv' : 'application/json',
                size_bytes: 12,
                sha256: isJMeter ? 'sha256:jmeter' : 'sha256:newman',
                metadata_json: { created_by_component: isJMeter ? 'JMeterRunner' : 'NewmanRunner' },
              },
            ],
          }),
          { status: 201, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const pinia = createPinia();
    const wrapper = mount(AutomationDraftReviewView, {
      global: {
        plugins: [pinia, ArcoVue],
      },
    });
    const store = useAutomationStore();
    store.draft = {
      id: draftId,
      project_id: '00000000-0000-0000-0000-000000000101',
      test_case_id: '00000000-0000-0000-0000-000000000955',
      requirement_id: null,
      ai_task_id: '00000000-0000-0000-0000-000000001402',
      automation_plan_id: null,
      target_framework: 'pytest',
      title: 'approved pytest draft',
      draft_code: 'def test_coupon_api():\n    assert True\n',
      draft_language: 'python',
      suggested_file_path: 'tests/test_coupon_api.py',
      execution_notes: 'Approved draft.',
      risk_notes: null,
      execution_strategy: 'artifact_runtime_copy',
      approval_required: true,
      status: 'approved',
      review_comment: null,
      runtime_artifact_id: null,
      promoted_artifact_id: null,
    };
    store.testCommands = [
      {
        id: '00000000-0000-0000-0000-000000000321',
        name: '订单 API 回归',
        command: 'newman run collections/coupon.postman_collection.json',
        working_directory: '.',
        command_type: 'newman',
        timeout_seconds: 60,
        parse_junit: true,
        parse_coverage: false,
        status: 'active',
      },
      {
        id: '00000000-0000-0000-0000-000000000331',
        name: '订单性能冒烟',
        command: 'jmeter -n -t plans/coupon.jmx',
        working_directory: '.',
        command_type: 'jmeter',
        timeout_seconds: 60,
        parse_junit: false,
        parse_coverage: false,
        status: 'active',
      },
    ];
    await wrapper.vm.$nextTick();

    await wrapper.find('[data-test="automation-execution-type-api"]').trigger('click');
    const apiCommandSelect = wrapper.find('[data-test="automation-test-command-select"]');
    await apiCommandSelect.trigger('click');
    await wrapper.vm.$nextTick();
    const apiCommandOption = document.querySelector<HTMLElement>(
      '[data-test="automation-test-command-option-00000000-0000-0000-0000-000000000321"]',
    );
    expect(apiCommandOption).not.toBeNull();
    apiCommandOption?.click();
    await wrapper.vm.$nextTick();
    await wrapper.find('.automation-execution-form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(executionBodies[0]).toEqual(
      expect.objectContaining({
        automation_draft_id: null,
        test_command_id: '00000000-0000-0000-0000-000000000321',
        runner_mode: 'newman_local',
      }),
    );
    expect(wrapper.text()).toContain('newman coupon api');
    expect(wrapper.text()).toContain('newman_json');

    await wrapper.find('[data-test="automation-execution-type-jmeter"]').trigger('click');
    const jmeterCommandSelect = wrapper.find('[data-test="automation-test-command-select"]');
    await jmeterCommandSelect.trigger('click');
    await wrapper.vm.$nextTick();
    const jmeterCommandOption = document.querySelector<HTMLElement>(
      '[data-test="automation-test-command-option-00000000-0000-0000-0000-000000000331"]',
    );
    expect(jmeterCommandOption).not.toBeNull();
    jmeterCommandOption?.click();
    await wrapper.vm.$nextTick();
    await wrapper.find('.automation-execution-form').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(executionBodies[1]).toEqual(
      expect.objectContaining({
        automation_draft_id: null,
        test_command_id: '00000000-0000-0000-0000-000000000331',
        runner_mode: 'jmeter_local',
      }),
    );
    expect(wrapper.text()).toContain('jmeter coupon smoke');
    expect(wrapper.text()).toContain('jmeter_jtl');
  });

  it('blocks approving drafts that still reference fake adapters', async () => {
    const draftId = '00000000-0000-0000-0000-000000001201';
    const fetchMock = vi.fn(async () => new Response('not found', { status: 404 }));
    vi.stubGlobal('fetch', fetchMock);

    const pinia = createPinia();
    const wrapper = mount(AutomationDraftReviewView, {
      global: {
        plugins: [pinia, ArcoVue],
      },
    });
    const store = useAutomationStore();
    store.draft = {
      id: draftId,
      project_id: '00000000-0000-0000-0000-000000000101',
      test_case_id: '00000000-0000-0000-0000-000000000955',
      requirement_id: null,
      ai_task_id: '00000000-0000-0000-0000-000000001202',
      automation_plan_id: null,
      target_framework: 'pytest',
      title: 'fake adapter demo draft',
      draft_code:
        'class FakeChargerAppAdapter:\n    pass\n\ndef test_block_master_icon():\n    app = FakeChargerAppAdapter()\n    assert app is not None\n',
      draft_language: 'python',
      suggested_file_path: 'tests/test_block_master_icon.py',
      execution_notes: 'Demo execution with fake adapter.',
      risk_notes: 'Uses FakeChargerAppAdapter.',
      execution_strategy: 'artifact_runtime_copy',
      approval_required: true,
      status: 'draft_generated',
      review_comment: null,
      runtime_artifact_id: null,
      promoted_artifact_id: null,
      quality_gate: {
        status: 'blocked',
        execution_evidence_level: 'blocked',
        approval_blocking_reasons: [
          'Draft code references fake/stub/demo adapters and cannot be approved as real regression evidence.',
        ],
        evidence_warnings: [
          'Draft references fake/stub/demo adapters; replace them with project-local fixtures, selectors, or API hooks.',
        ],
      },
    };
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('Quality gate: blocked');
    expect(wrapper.text()).toContain('Evidence level: blocked');
    expect(wrapper.text()).toContain('cannot be approved as real regression evidence');
    expect(wrapper.find('[data-test="approve-draft"]').attributes('disabled')).toBeDefined();

    await wrapper.find('[data-test="approve-draft"]').trigger('click');
    await flushPromises();

    expect(fetchMock).not.toHaveBeenCalledWith(
      `/api/automation/drafts/${draftId}/approve`,
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('renders the persisted AutomationPlanReview gate and advances it with project-scoped actions', async () => {
    const testCaseId = '00000000-0000-0000-0000-000000000955';
    const requirementReviewId = '00000000-0000-0000-0000-000000000611';
    const planId = '00000000-0000-0000-0000-000000000a01';
    let workflowActionBody: unknown = null;
    window.localStorage.setItem(
      'chtest.latestApprovedTestCase',
      JSON.stringify({
        projectId: '00000000-0000-0000-0000-000000000101',
        testCaseId,
      }),
    );
    const workflowPayload = (state: string, stage = 'automation_plan_review') => ({
      project_id: '00000000-0000-0000-0000-000000000101',
      requirement_review_id: requirementReviewId,
      workflow: {
        run_id: '00000000-0000-0000-0000-000000000b01',
        stage,
        state,
        lock_version: 4,
        snapshot_id: '00000000-0000-0000-0000-000000000b02',
        approval_decision_id: null,
        can_submit: false,
        can_complete_review: false,
        can_edit: true,
        can_approve: true,
        can_continue: false,
      },
      source_case_review_snapshot_id: '00000000-0000-0000-0000-000000000c01',
      source_case_review_snapshot_hash: 'sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
      source_test_plan_review_snapshot_id: '00000000-0000-0000-0000-000000000d01',
      source_test_plan_review_snapshot_hash: 'sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd',
      approved_candidate_ids: ['00000000-0000-0000-0000-000000000801'],
      approved_test_case_ids: [testCaseId],
      generated_plan_ids: [planId],
      plan_decisions: [{ automation_plan_id: planId, status: 'approved' }],
    });
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes('/test-cases?project_id=')) {
        return new Response(
          JSON.stringify({
            items: [
              {
                id: testCaseId,
                project_id: '00000000-0000-0000-0000-000000000101',
                module_id: null,
                source_candidate_id: '00000000-0000-0000-0000-000000000801',
                title: 'Expired coupon cannot submit order',
                priority: 'P0',
                test_type: 'functional',
                precondition: null,
                steps: ['Submit order'],
                expected_results: ['Submit is blocked'],
                input_data: {},
                tags: ['reviewed'],
                source_type: 'ai',
                review_status: 'approved',
                status: 'active',
              },
            ],
            total: 1,
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/settings')) {
        return new Response(
          JSON.stringify({
            project: {
              id: '00000000-0000-0000-0000-000000000101',
              name: 'Chtest',
              default_language: 'zh-CN',
              default_test_type: 'functional',
            },
            modules: [],
            repositories: [],
            environments: [],
            test_commands: [],
            tool_definitions: [],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/automation/plans') && init?.method === 'POST') {
        return new Response(
          JSON.stringify({
            id: planId,
            project_id: '00000000-0000-0000-0000-000000000101',
            test_case_id: testCaseId,
            requirement_id: '00000000-0000-0000-0000-000000000411',
            requirement_review_id: requirementReviewId,
            source_candidate_id: '00000000-0000-0000-0000-000000000801',
            ai_task_id: '00000000-0000-0000-0000-000000000a02',
            knowledge_retrieval_artifact_id: null,
            target_framework: 'pytest',
            title: 'Automate expired coupon checkout',
            plan: { source: 'reviewed_test_case' },
            execution_steps: ['Open checkout', 'Submit expired coupon'],
            test_data: {},
            dependency_notes: 'Use project fixtures.',
            risk_notes: 'Keep coupon state deterministic.',
            used_context_artifact_ids: [],
            status: 'approved',
            review_comment: 'Plan is feasible.',
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith(`/projects/00000000-0000-0000-0000-000000000101/requirement-reviews/${requirementReviewId}/automation-plan-review`)) {
        return new Response(JSON.stringify(workflowPayload('waiting_approval')), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (
        url.endsWith(`/projects/00000000-0000-0000-0000-000000000101/requirement-reviews/${requirementReviewId}/automation-plan-review/approve-and-continue`) &&
        init?.method === 'POST'
      ) {
        workflowActionBody = JSON.parse(String(init.body));
        return new Response(JSON.stringify(workflowPayload('draft', 'automation_draft_review')), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/review-history?')) {
        return new Response(JSON.stringify({ items: [], total: 0 }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(AutomationDraftReviewView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();
    await wrapper.find('[data-test="generate-plan"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.find('[data-test="automation-plan-workflow-panel"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('AutomationPlanReview gate');
    expect(wrapper.text()).toContain('automation_plan_review');

    await wrapper.find('[data-test="automation-plan-review-approve-continue"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(workflowActionBody).toEqual(
      expect.objectContaining({
        expected_version: 4,
        comment: 'Automation plan review approved and advanced.',
      }),
    );
    expect(wrapper.text()).toContain('automation_draft_review');
  });

  it('renders the persisted AutomationDraftReview gate and advances it with project-scoped actions', async () => {
    const requirementReviewId = '00000000-0000-0000-0000-000000000611';
    const draftId = '00000000-0000-0000-0000-000000000d01';
    let workflowActionBody: unknown = null;
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (
        url.endsWith(`/projects/00000000-0000-0000-0000-000000000101/requirement-reviews/${requirementReviewId}/automation-draft-review/approve-and-continue`) &&
        init?.method === 'POST'
      ) {
        workflowActionBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            requirement_review_id: requirementReviewId,
            workflow: {
              run_id: '00000000-0000-0000-0000-000000000e01',
              stage: 'execution_approval',
              state: 'draft',
              lock_version: 8,
              snapshot_id: '00000000-0000-0000-0000-000000000e03',
              approval_decision_id: null,
              can_submit: false,
              can_complete_review: false,
              can_edit: false,
              can_approve: false,
              can_continue: false,
            },
            source_automation_plan_review_snapshot_id: '00000000-0000-0000-0000-000000000b01',
            source_automation_plan_review_snapshot_hash: 'sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            source_case_review_snapshot_id: '00000000-0000-0000-0000-000000000c01',
            source_case_review_snapshot_hash: 'sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
            approved_automation_plan_ids: ['00000000-0000-0000-0000-000000000a01'],
            approved_test_case_ids: ['00000000-0000-0000-0000-000000000955'],
            generated_draft_ids: [draftId],
            draft_decisions: [{ automation_draft_id: draftId, status: 'approved' }],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const pinia = createPinia();
    const wrapper = mount(AutomationDraftReviewView, {
      global: {
        plugins: [pinia, ArcoVue],
      },
    });
    const store = useAutomationStore();
    store.plan = {
      id: '00000000-0000-0000-0000-000000000a01',
      project_id: '00000000-0000-0000-0000-000000000101',
      test_case_id: '00000000-0000-0000-0000-000000000955',
      requirement_id: '00000000-0000-0000-0000-000000000411',
      requirement_review_id: requirementReviewId,
      source_candidate_id: '00000000-0000-0000-0000-000000000801',
      ai_task_id: '00000000-0000-0000-0000-000000000a02',
      knowledge_retrieval_artifact_id: null,
      target_framework: 'pytest',
      title: 'Automate expired coupon checkout',
      plan: {},
      execution_steps: ['Run pytest'],
      test_data: {},
      dependency_notes: null,
      risk_notes: null,
      used_context_artifact_ids: [],
      status: 'draft_generated',
      review_comment: null,
    };
    store.draft = {
      id: draftId,
      project_id: '00000000-0000-0000-0000-000000000101',
      test_case_id: '00000000-0000-0000-0000-000000000955',
      requirement_id: '00000000-0000-0000-0000-000000000411',
      ai_task_id: '00000000-0000-0000-0000-000000000d02',
      automation_plan_id: '00000000-0000-0000-0000-000000000a01',
      target_framework: 'pytest',
      title: 'Automated expired coupon checkout',
      draft_code: 'def test_expired_coupon():\n    assert checkout_expired_coupon() == "blocked"\n',
      draft_language: 'python',
      suggested_file_path: 'tests/test_expired_coupon.py',
      execution_notes: 'Uses project checkout fixture.',
      risk_notes: 'Keep coupon state deterministic.',
      execution_strategy: 'artifact_runtime_copy',
      approval_required: true,
      status: 'approved',
      review_comment: null,
      runtime_artifact_id: null,
      promoted_artifact_id: null,
      quality_gate: {
        status: 'ready_for_approval',
        execution_evidence_level: 'reviewed_candidate',
        approval_blocking_reasons: [],
        evidence_warnings: [],
      },
    };
    store.draftReviewWorkflow = {
      project_id: '00000000-0000-0000-0000-000000000101',
      requirement_review_id: requirementReviewId,
      workflow: {
        run_id: '00000000-0000-0000-0000-000000000e01',
        stage: 'automation_draft_review',
        state: 'waiting_approval',
        lock_version: 7,
        snapshot_id: '00000000-0000-0000-0000-000000000e02',
        approval_decision_id: null,
        can_submit: false,
        can_complete_review: false,
        can_edit: true,
        can_approve: true,
        can_continue: false,
      },
      source_automation_plan_review_snapshot_id: '00000000-0000-0000-0000-000000000b01',
      source_automation_plan_review_snapshot_hash: 'sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
      source_case_review_snapshot_id: '00000000-0000-0000-0000-000000000c01',
      source_case_review_snapshot_hash: 'sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
      approved_automation_plan_ids: ['00000000-0000-0000-0000-000000000a01'],
      approved_test_case_ids: ['00000000-0000-0000-0000-000000000955'],
      generated_draft_ids: [draftId],
      draft_decisions: [{ automation_draft_id: draftId, status: 'approved' }],
    };
    await wrapper.vm.$nextTick();

    expect(wrapper.find('[data-test="automation-draft-workflow-panel"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('AutomationDraftReview gate');
    await wrapper.find('[data-test="automation-draft-review-approve-continue"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(workflowActionBody).toEqual(
      expect.objectContaining({
        expected_version: 7,
        comment: 'Automation draft review approved and advanced.',
      }),
    );
    expect(wrapper.text()).toContain('execution_approval');
  });
});
