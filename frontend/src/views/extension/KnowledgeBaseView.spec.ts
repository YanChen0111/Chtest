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
              provider_type: 'none',
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
    expect(wrapper.text()).toContain('not_configured');
    expect(wrapper.text()).toContain('used_knowledge=false');
    expect(wrapper.text()).toContain('coupon-api-notes.md');
    expect(wrapper.text()).toContain('manual:coupon-api-notes.md');
    expect(wrapper.text()).toContain('allowed');
    expect(wrapper.text()).toContain('pytest_runner');
    expect(wrapper.text()).toContain('MCP-ready');
    expect(wrapper.text()).toContain('no_vector_index');
    expect(wrapper.text()).not.toContain('Vector Search');
  });
});
