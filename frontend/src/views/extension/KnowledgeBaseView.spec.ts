import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import KnowledgeBaseView from './KnowledgeBaseView.vue';

describe('KnowledgeBaseView', () => {
  it('loads context artifacts, adapter state, and MCP-ready tool schema', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/knowledge-base')) {
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            knowledge_adapter: {
              project_id: '00000000-0000-0000-0000-000000000101',
              adapter_name: 'default',
              status: 'not_configured',
              provider_type: 'deterministic_local',
              retrieval_mode: 'deterministic_local',
              config: {},
              safety_policy: {},
              last_checked_at: null,
              notes: null,
              used_knowledge: false,
            },
            context_artifacts: [
              {
                id: 'ctx1',
                title: 'coupon-api-notes.md',
                artifact_type: 'context_markdown',
                mime_type: 'text/markdown',
                source_ref: 'manual:coupon-api-notes.md',
                safe_to_show: true,
                redaction_applied: false,
                allowed_for_prompt: true,
                usage_count: 2,
                latest_used_at: '2026-06-30T10:00:00Z',
                retrieved_count: 1,
                latest_retrieved_at: '2026-06-30T10:30:00Z',
              },
            ],
            latest_retrievals: [
              {
                ai_task_id: 'task1',
                retrieval_evidence_artifact_id: 'artifact1',
                query_terms: ['coupon', 'expired'],
                used_context_artifact_ids: ['ctx1'],
                snippet_count: 1,
                created_at: '2026-06-30T10:30:00Z',
                results: [
                  {
                    context_artifact_id: 'ctx1',
                    title: 'coupon-api-notes.md',
                    source_ref: 'manual:coupon-api-notes.md',
                    score: 2,
                    matched_terms: ['coupon', 'expired'],
                    snippet: 'Expired coupon validation blocks checkout.',
                    sha256: 'sha256:ctx1',
                    redaction_applied: false,
                    allowed_for_prompt: true,
                  },
                ],
              },
            ],
            non_goals: ['no_vector_index', 'no_embedding', 'no_reranking', 'no_external_rag_runtime'],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/tool-definitions')) {
        return new Response(
          JSON.stringify({
            total: 1,
            items: [
              {
                id: 'tool1',
                project_id: '00000000-0000-0000-0000-000000000101',
                name: 'pytest_runner',
                description: 'Run allowlisted pytest commands',
                tool_type: 'test_runner',
                input_schema: { type: 'object' },
                output_schema: { type: 'object' },
                risk_level: 'medium',
                approval_required: false,
                timeout_seconds: 600,
                command_allowlist: ['pytest {path}'],
                allowed_working_directories: ['/workspace'],
                forbidden_shell_operators: [';', '&&'],
                max_stdout_bytes: 1048576,
                max_stderr_bytes: 1048576,
                artifact_policy: { stdout: true },
                is_mcp_ready: true,
                mcp_metadata: { schema_version: 'v1', capability_name: 'pytest_runner' },
                status: 'active',
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(KnowledgeBaseView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('RAG 知识库');
    expect(wrapper.text()).toContain('ContextArtifact');
    expect(wrapper.text()).toContain('KnowledgeAdapter');
    expect(wrapper.text()).toContain('允许进入提示词');
    expect(wrapper.text()).toContain('未配置');
    expect(wrapper.text()).toContain('使用知识=否');
    expect(wrapper.text()).toContain('确定性本地检索');
    expect(wrapper.text()).toContain('coupon-api-notes.md');
    expect(wrapper.text()).toContain('manual:coupon-api-notes.md');
    expect(wrapper.text()).toContain('允许');
    expect(wrapper.text()).toContain('检索证据');
    expect(wrapper.text()).toContain('2026-06-30T10:30:00Z');
    expect(wrapper.text()).toContain('pytest_runner');
    expect(wrapper.text()).toContain('MCP-ready');
    expect(wrapper.text()).toContain('最近检索证据');
    expect(wrapper.text()).toContain('命中词');
    expect(wrapper.text()).toContain('coupon');
    expect(wrapper.text()).toContain('expired');
    expect(wrapper.text()).toContain('得分 2');
    expect(wrapper.text()).toContain('Expired coupon validation blocks checkout.');
    expect(wrapper.text()).toContain('no_vector_index');
    expect(wrapper.text()).not.toContain('Embedding');
    expect(wrapper.text()).not.toContain('Provider 配置');
    expect(wrapper.text()).not.toContain('向量检索');
  });

  it('keeps the page useful when no retrieval evidence exists', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/knowledge-base')) {
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            knowledge_adapter: {
              project_id: '00000000-0000-0000-0000-000000000101',
              adapter_name: 'default',
              status: 'configured_stub',
              provider_type: 'deterministic_local',
              config: {},
              safety_policy: {},
              last_checked_at: null,
              notes: null,
              used_knowledge: false,
            },
            context_artifacts: [],
            non_goals: ['no_vector_index'],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/tool-definitions')) {
        return new Response(JSON.stringify({ total: 0, items: [] }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(KnowledgeBaseView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('最近检索证据');
    expect(wrapper.text()).toContain('暂无 deterministic retrieval evidence');
    expect(wrapper.text()).toContain('ContextArtifact');
    expect(wrapper.text()).toContain('MCP-ready');
    expect(wrapper.text()).not.toContain('向量检索');
  });
});
