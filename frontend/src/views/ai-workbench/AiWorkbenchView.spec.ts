import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import AiWorkbenchView from './AiWorkbenchView.vue';

function workflowQueueBody() {
  return {
    project_id: '00000000-0000-0000-0000-000000000101',
    total: 3,
    groups: {
      waiting_review: [
        {
          id: '00000000-0000-0000-0000-000000009001',
          project_id: '00000000-0000-0000-0000-000000000101',
          workflow_kind: 'requirement_to_execution',
          subject_ref: '00000000-0000-0000-0000-000000000601',
          current_stage: 'risk_review',
          gate_state: 'waiting_review',
          bucket: 'waiting_review',
          lock_version: 4,
          current_snapshot_id: '00000000-0000-0000-0000-000000009101',
          input_snapshot_hash: 'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
          approval_decision_id: null,
          can_continue: false,
          route_path: null,
          created_at: '2026-07-30T08:00:00Z',
          updated_at: '2026-07-30T08:01:00Z',
        },
      ],
      waiting_approval: [
        {
          id: '00000000-0000-0000-0000-000000009002',
          project_id: '00000000-0000-0000-0000-000000000101',
          workflow_kind: 'requirement_to_execution',
          subject_ref: '00000000-0000-0000-0000-000000000602',
          current_stage: 'case_review',
          gate_state: 'waiting_approval',
          bucket: 'waiting_approval',
          lock_version: 8,
          current_snapshot_id: '00000000-0000-0000-0000-000000009102',
          input_snapshot_hash: 'sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
          approval_decision_id: null,
          can_continue: false,
          route_path: null,
          created_at: '2026-07-30T08:02:00Z',
          updated_at: '2026-07-30T08:03:00Z',
        },
      ],
      can_continue: [
        {
          id: '00000000-0000-0000-0000-000000009003',
          project_id: '00000000-0000-0000-0000-000000000101',
          workflow_kind: 'requirement_to_execution',
          subject_ref: '00000000-0000-0000-0000-000000000603',
          current_stage: 'report_review',
          gate_state: 'approved',
          bucket: 'can_continue',
          lock_version: 15,
          current_snapshot_id: '00000000-0000-0000-0000-000000009103',
          input_snapshot_hash: 'sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
          approval_decision_id: '00000000-0000-0000-0000-000000009203',
          can_continue: true,
          route_path: null,
          created_at: '2026-07-30T08:04:00Z',
          updated_at: '2026-07-30T08:05:00Z',
        },
      ],
    },
    items: [],
  };
}

describe('AiWorkbenchView', () => {
  it('shows the backend health result', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('ok', { status: 200 })));

    const wrapper = mount(AiWorkbenchView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('后端健康');
    expect(wrapper.text()).toContain('正常');
  });

  it('shows a failure state when the backend health call fails', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('bad gateway', { status: 502 })));

    const wrapper = mount(AiWorkbenchView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('后端健康');
    expect(wrapper.text()).toContain('失败');
    expect(wrapper.text()).toContain('请求失败：502');
  });

  it('keeps workflow queue failures scoped to the queue panel', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/health')) {
        return new Response('ok', { status: 200 });
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/workflow-runs')) {
        return new Response('workflow unavailable', { status: 502 });
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/ai-tasks')) {
        return new Response(JSON.stringify({ total: 0, items: [] }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not configured', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(AiWorkbenchView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    const queueError = wrapper.find('[data-test="workflow-queue-error"]');
    expect(queueError.exists()).toBe(true);
    expect(queueError.text()).toContain('502');
    expect(wrapper.find('[data-test="workflow-queue-panel"]').exists()).toBe(true);
  });

  it('loads recent AI tasks and shows selected task evidence details', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/health')) {
        return new Response('ok', { status: 200 });
      }
      if (url.endsWith('/settings/model-connection')) {
        return new Response(
          JSON.stringify({
            configured: true,
            provider: 'OpenAI Compatible',
            model_name: 'gpt-5.5',
            base_url: 'https://gateway.example.test/v1',
            wire_api: 'responses',
            api_key_configured: true,
            api_key_hint: '***cret',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/workflow-runs')) {
        return new Response(JSON.stringify(workflowQueueBody()), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/ai-tasks')) {
        return new Response(
          JSON.stringify({
            total: 1,
            items: [
              {
                id: '00000000-0000-0000-0000-000000000501',
                project_id: '00000000-0000-0000-0000-000000000101',
                agent_name: 'RequirementReviewAgent',
                task_type: 'requirement_review',
                status: 'succeeded',
                model_provider: 'mock',
                model_name: 'mock-requirement-review',
                context_artifact_ids: ['00000000-0000-0000-0000-000000000371'],
                started_at: '2026-06-29T10:00:00Z',
                finished_at: '2026-06-29T10:00:05Z',
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/ai-tasks/00000000-0000-0000-0000-000000000501')) {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000000501',
            project_id: '00000000-0000-0000-0000-000000000101',
            agent_name: 'RequirementReviewAgent',
            task_type: 'requirement_review',
            status: 'succeeded',
            prompt_version_id: '00000000-0000-0000-0000-000000000601',
            skill_version_id: '00000000-0000-0000-0000-000000000701',
            model_provider: 'mock',
            model_name: 'mock-requirement-review',
            token_usage: { prompt_tokens: 128, completion_tokens: 256 },
            used_knowledge: false,
            context_artifact_ids: ['00000000-0000-0000-0000-000000000371'],
            used_context_artifact_ids: ['00000000-0000-0000-0000-000000000371'],
            context_manifest_artifact_id: '00000000-0000-0000-0000-000000000801',
            artifacts: [
              {
                id: '00000000-0000-0000-0000-000000000901',
                artifact_type: 'raw_llm_output',
                file_path:
                  'projects/00000000-0000-0000-0000-000000000101/ai-tasks/00000000-0000-0000-0000-000000000501/raw_output.json',
                mime_type: 'application/json',
                size_bytes: 320,
                sha256: 'sha256:aaaaaaaa',
                safe_to_show: false,
                redaction_applied: false,
              },
              {
                id: '00000000-0000-0000-0000-000000000800',
                artifact_type: 'input_json',
                file_path:
                  'projects/00000000-0000-0000-0000-000000000101/ai-tasks/00000000-0000-0000-0000-000000000501/input.json',
                mime_type: 'application/json',
                size_bytes: 210,
                sha256: 'sha256:eeeeeeee',
                safe_to_show: true,
                redaction_applied: false,
              },
              {
                id: '00000000-0000-0000-0000-000000000902',
                artifact_type: 'parsed_output',
                file_path:
                  'projects/00000000-0000-0000-0000-000000000101/ai-tasks/00000000-0000-0000-0000-000000000501/parsed_output.json',
                mime_type: 'application/json',
                size_bytes: 260,
                sha256: 'sha256:bbbbbbbb',
                safe_to_show: true,
                redaction_applied: false,
              },
              {
                id: '00000000-0000-0000-0000-000000000903',
                artifact_type: 'schema_validation',
                file_path:
                  'projects/00000000-0000-0000-0000-000000000101/ai-tasks/00000000-0000-0000-0000-000000000501/schema_validation.json',
                mime_type: 'application/json',
                size_bytes: 180,
                sha256: 'sha256:cccccccc',
                safe_to_show: true,
                redaction_applied: false,
              },
              {
                id: '00000000-0000-0000-0000-000000000801',
                artifact_type: 'context_manifest',
                file_path:
                  'projects/00000000-0000-0000-0000-000000000101/ai-tasks/00000000-0000-0000-0000-000000000501/context_manifest.json',
                mime_type: 'application/json',
                size_bytes: 220,
                sha256: 'sha256:dddddddd',
                safe_to_show: true,
                redaction_applied: false,
              },
            ],
            llm_call_logs: [
              {
                id: '00000000-0000-0000-0000-000000001001',
                provider: 'mock',
                model_name: 'mock-requirement-review',
                call_index: 1,
                status: 'succeeded',
                request_artifact_id: '00000000-0000-0000-0000-000000000800',
                response_artifact_id: '00000000-0000-0000-0000-000000000901',
                parsed_artifact_id: '00000000-0000-0000-0000-000000000902',
                schema_validation_artifact_id: '00000000-0000-0000-0000-000000000903',
                token_usage_json: { prompt_tokens: 128, completion_tokens: 256 },
                latency_ms: 42,
                error_json: null,
                started_at: '2026-06-29T10:00:00Z',
                finished_at: '2026-06-29T10:00:05Z',
              },
              {
                id: '00000000-0000-0000-0000-000000001002',
                provider: 'mock',
                model_name: 'mock-requirement-review',
                call_index: 2,
                status: 'succeeded',
                request_artifact_id: '00000000-0000-0000-0000-000000000901',
                response_artifact_id: null,
                parsed_artifact_id: null,
                schema_validation_artifact_id: null,
                token_usage_json: {},
                latency_ms: null,
                error_json: null,
                started_at: '2026-06-29T10:00:06Z',
                finished_at: '2026-06-29T10:00:07Z',
              },
              {
                id: '00000000-0000-0000-0000-000000001003',
                provider: 'mock',
                model_name: 'mock-requirement-review',
                call_index: 3,
                status: 'succeeded',
                request_artifact_id: null,
                response_artifact_id: null,
                parsed_artifact_id: null,
                schema_validation_artifact_id: null,
                token_usage_json: {},
                latency_ms: null,
                error_json: null,
                started_at: '2026-06-29T10:00:08Z',
                finished_at: '2026-06-29T10:00:09Z',
              },
            ],
            started_at: '2026-06-29T10:00:00Z',
            finished_at: '2026-06-29T10:00:05Z',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(AiWorkbenchView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('最近 AI 任务');
    expect(wrapper.text()).toContain('模型服务');
    expect(wrapper.text()).toContain('流程待办');
    expect(wrapper.text()).toContain('待人工评审');
    expect(wrapper.text()).toContain('待批准');
    expect(wrapper.text()).toContain('已批准，可继续');
    expect(wrapper.text()).toContain('风险评审');
    expect(wrapper.text()).toContain('用例评审');
    expect(wrapper.text()).toContain('报告评审');
    expect(wrapper.text()).toContain('15');
    expect(wrapper.find('[data-test="workflow-queue-panel"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="workflow-queue-can_continue"]').text()).toContain(
      '00000000-0000-0000-0000-000000009103',
    );
    expect(wrapper.find('[data-test="workflow-queue-open"]').exists()).toBe(false);
    expect(wrapper.text()).toContain('暂无入口');
    expect(wrapper.text()).toContain('OpenAI Compatible');
    expect(wrapper.text()).toContain('OpenAI Compatible · gpt-5.5');
    expect(wrapper.text()).toContain('需求评审智能体');
    expect(wrapper.text()).toContain('本地模型 · requirement review');
    expect(wrapper.text()).toContain('任务详情');
    expect(wrapper.text()).toContain('提示词版本');
    expect(wrapper.text()).toContain('技能版本');
    expect(wrapper.text()).toContain('令牌用量');
    expect(wrapper.text()).toContain('上下文工件');
    expect(wrapper.text()).toContain('本次使用 1 个上下文工件');
    expect(wrapper.text()).toContain('上下文清单证据');
    const contextManifestLink = wrapper.find(
      'a[href="/api/artifacts/00000000-0000-0000-0000-000000000801/download"]',
    );
    expect(contextManifestLink.exists()).toBe(true);
    expect(contextManifestLink.attributes('aria-label')).toBe(
      '打开上下文清单证据工件 00000000-0000-0000-0000-000000000801',
    );
    expect(wrapper.text()).toContain('工件摘要');
    expect(wrapper.text()).toContain('raw_llm_output');
    expect(wrapper.text()).toContain('application/json');
    expect(wrapper.text()).not.toContain('sha256:aaaaaaaa');
    expect(wrapper.text()).toContain('不可直接展示');
    expect(wrapper.text()).toContain('不可直接打开');
    expect(wrapper.text()).toContain('打开');
    expect(wrapper.text()).not.toContain('未脱敏');
    const parsedOutputLink = wrapper.find(
      'a[href="/api/artifacts/00000000-0000-0000-0000-000000000902/download"]',
    );
    expect(parsedOutputLink.exists()).toBe(true);
    expect(parsedOutputLink.attributes('aria-label')).toBe(
      '打开 parsed_output 工件 00000000-0000-0000-0000-000000000902',
    );
    expect(parsedOutputLink.attributes('title')).toBe(
      '打开 parsed_output 工件 00000000-0000-0000-0000-000000000902',
    );
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000000901/download"]').exists()).toBe(false);
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000000903/download"]').exists()).toBe(true);
    expect(wrapper.find('a[href="/api/artifacts/00000000-0000-0000-0000-000000000903/download"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('大模型调用日志');
    expect(wrapper.text()).toContain('提示词令牌');
    const llmCallRows = wrapper
      .findAll('tr')
      .filter((row) =>
        row.findAll('td').some((cell) => cell.text() === 'mock-requirement-review'),
      );
    expect(llmCallRows).toHaveLength(3);
    expect(
      llmCallRows.map((row) => {
        const cells = row.findAll('td');
        return cells[cells.length - 1]?.text();
      }),
    ).toEqual([
      '提示词令牌: 128, 输出令牌: 256',
      '未记录',
      '未记录',
    ]);
    expect(wrapper.text()).toContain('证据');
    expect(wrapper.text()).toContain('3 项');
    expect(wrapper.text()).toContain('1 项');
    expect(wrapper.text()).toContain('42 ms');
    expect(wrapper.text()).not.toContain('raw content');
    expect(wrapper.text()).not.toContain('重新运行');
    expect(wrapper.text()).not.toContain('Prompt 编辑');
    expect(wrapper.text()).not.toContain('Provider 控制');
  });

  it('shows explicit evidence empty states for a selected task without artifacts or LLM calls', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/health')) {
        return new Response('ok', { status: 200 });
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/workflow-runs')) {
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            total: 0,
            groups: { waiting_review: [], waiting_approval: [], can_continue: [] },
            items: [],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/ai-tasks')) {
        return new Response(
          JSON.stringify({
            total: 1,
            items: [
              {
                id: '00000000-0000-0000-0000-000000000502',
                project_id: '00000000-0000-0000-0000-000000000101',
                agent_name: 'CaseGenerationAgent',
                task_type: 'case_generation',
                status: 'pending',
                model_provider: 'mock',
                model_name: 'mock-empty-evidence',
                context_artifact_ids: [],
                started_at: null,
                finished_at: null,
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/ai-tasks/00000000-0000-0000-0000-000000000502')) {
        return new Response(
          JSON.stringify({
            id: '00000000-0000-0000-0000-000000000502',
            project_id: '00000000-0000-0000-0000-000000000101',
            agent_name: 'CaseGenerationAgent',
            task_type: 'case_generation',
            status: 'pending',
            prompt_version_id: '00000000-0000-0000-0000-000000000602',
            skill_version_id: '00000000-0000-0000-0000-000000000702',
            model_provider: 'mock',
            model_name: 'mock-empty-evidence',
            token_usage: {},
            used_knowledge: false,
            context_artifact_ids: [],
            used_context_artifact_ids: [],
            context_manifest_artifact_id: null,
            artifacts: [],
            llm_call_logs: [],
            started_at: null,
            finished_at: null,
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(AiWorkbenchView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('用例生成智能体');
    expect(wrapper.text()).toContain('暂无工件证据');
    expect(wrapper.text()).toContain('暂无大模型调用日志');
    expect(wrapper.text()).not.toContain('raw content');
  });
});
