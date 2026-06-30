import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import AiWorkbenchView from './AiWorkbenchView.vue';

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

  it('loads recent AI tasks and shows selected task evidence details', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/health')) {
        return new Response('ok', { status: 200 });
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
                schema_validation_artifact_id: null,
                token_usage_json: { prompt_tokens: 128, completion_tokens: 256 },
                latency_ms: 42,
                error_json: null,
                started_at: '2026-06-29T10:00:00Z',
                finished_at: '2026-06-29T10:00:05Z',
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
    expect(wrapper.text()).toContain('需求评审智能体');
    expect(wrapper.text()).toContain('模拟模型 · requirement review');
    expect(wrapper.text()).toContain('任务详情');
    expect(wrapper.text()).toContain('提示词版本');
    expect(wrapper.text()).toContain('技能版本');
    expect(wrapper.text()).toContain('令牌用量');
    expect(wrapper.text()).toContain('上下文工件');
    expect(wrapper.text()).toContain('00000000-0000-0000-0000-000000000371');
    expect(wrapper.text()).toContain('工件摘要');
    expect(wrapper.text()).toContain('raw_llm_output');
    expect(wrapper.text()).toContain('application/json');
    expect(wrapper.text()).toContain('sha256:aaaaaaaa');
    expect(wrapper.text()).toContain('不可直接展示');
    expect(wrapper.text()).toContain('未脱敏');
    expect(wrapper.text()).toContain('大模型调用日志');
    expect(wrapper.text()).toContain('提示词令牌');
    expect(wrapper.text()).toContain('00000000-0000-0000-0000-000000000901');
    expect(wrapper.text()).toContain('42 ms');
    expect(wrapper.text()).not.toContain('raw content');
  });
});
