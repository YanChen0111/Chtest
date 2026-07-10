import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, describe, expect, it, vi } from 'vitest';

import KnowledgeBaseView from './KnowledgeBaseView.vue';

describe('KnowledgeBaseView', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('loads context artifacts, adapter state, and MCP-ready tool schema', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/test-knowledge/index')) {
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            total: 1,
            indexed_count: 1,
            embedding_models: ['deterministic-hashing-v1'],
            items: [],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
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
            non_goals: ['no_external_vector_runtime', 'no_online_embedding_provider', 'no_reranking', 'no_external_rag_runtime'],
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
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/test-knowledge/graph')) {
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            nodes: [],
            edges: [],
            coverage: {
              knowledge_coverage_ratio: 0,
              covered_knowledge_card_count: 0,
              vector_index_coverage_ratio: 1,
              embedding_indexed_card_count: 1,
            },
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/test-knowledge/graph')) {
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            nodes: [],
            edges: [],
            coverage: {
              knowledge_coverage_ratio: 0,
              covered_knowledge_card_count: 0,
              vector_index_coverage_ratio: 1,
              embedding_indexed_card_count: 1,
            },
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/test-knowledge/graph')) {
        const hasReview = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith('/test-knowledge/cards/card-uploaded'),
        );
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            nodes: [],
            edges: [],
            coverage: {
              knowledge_coverage_ratio: hasReview ? 1 : 0,
              covered_knowledge_card_count: hasReview ? 1 : 0,
              vector_index_coverage_ratio: 1,
              embedding_indexed_card_count: 1,
            },
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/test-knowledge/cards')) {
        return new Response(
          JSON.stringify({
            total: 1,
            items: [
              {
                id: 'card1',
                project_id: '00000000-0000-0000-0000-000000000101',
                source_artifact_id: 'ctx1',
                source_document_version: 'v1',
                source_section: 'section:1',
                source_quote_hash: 'hash1',
                knowledge_type: 'BoundaryCondition',
                title: 'BoundaryCondition: expired coupon checkout',
                content: 'Expired coupon validation blocks checkout.',
                module_key: 'coupon',
                api_endpoint: null,
                risk_type: 'boundary',
                case_type_hint: 'negative',
                applicability: 'case_generation',
                confidence: 80,
                safe_to_show: true,
                allowed_for_prompt: true,
                status: 'extracted',
                created_at: '2026-06-30T10:00:00Z',
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
    expect(wrapper.text()).toContain('Vector Index');
    expect(wrapper.text()).toContain('Vector Coverage');
    expect(wrapper.text()).toContain('no_external_vector_runtime');
    expect(wrapper.text()).not.toContain('Provider 配置');
    expect(wrapper.text()).not.toContain('向量检索');
  });

  it('keeps the page useful when no retrieval evidence exists', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/test-knowledge/index')) {
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            total: 0,
            indexed_count: 0,
            embedding_models: [],
            items: [],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
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
            non_goals: ['no_external_vector_runtime'],
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
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/test-knowledge/graph')) {
        const hasReview = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith('/test-knowledge/cards/card-uploaded'),
        );
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            nodes: [],
            edges: [],
            coverage: {
              knowledge_coverage_ratio: hasReview ? 1 : 0,
              covered_knowledge_card_count: hasReview ? 1 : 0,
              vector_index_coverage_ratio: 0,
              embedding_indexed_card_count: 0,
            },
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/test-knowledge/cards')) {
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

  it('uploads context artifacts, enables local retrieval, and runs retrieval tests', async () => {
    let uploadedBody: unknown = null;
    let adapterBody: unknown = null;
    let retrievalBody: unknown = null;
    let extractionBody: unknown = null;
    let knowledgeCardRetrievalBody: unknown = null;
    let reviewBody: unknown = null;
    let indexRebuildBody: unknown = null;
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/test-knowledge/index/rebuild') && init?.method === 'POST') {
        indexRebuildBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            indexed_count: 1,
            skipped_count: 0,
            embedding_model: 'deterministic-hashing-v1',
            embedding_dim: 64,
            items: [],
          }),
          { status: 201, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/test-knowledge/index')) {
        const hasIndexRebuild = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith('/test-knowledge/index/rebuild') && call[1]?.method === 'POST',
        );
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            total: hasIndexRebuild ? 1 : 0,
            indexed_count: hasIndexRebuild ? 1 : 0,
            embedding_models: hasIndexRebuild ? ['deterministic-hashing-v1'] : [],
            items: [],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/knowledge-base')) {
        const hasUpload = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith('/context-artifacts') && call[1]?.method === 'POST',
        );
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            knowledge_adapter: {
              project_id: '00000000-0000-0000-0000-000000000101',
              adapter_name: 'default',
              status: 'configured_stub',
              provider_type: 'deterministic_local',
              retrieval_mode: 'deterministic_local',
              config: {},
              safety_policy: {},
              last_checked_at: null,
              notes: null,
              used_knowledge: false,
            },
            context_artifacts: hasUpload
              ? [
                  {
                    id: 'ctx-uploaded',
                    title: 'checkout-runbook.txt',
                    artifact_type: 'context_text',
                    mime_type: 'text/plain',
                    source_ref: 'file:checkout-runbook.txt',
                    safe_to_show: true,
                    redaction_applied: false,
                    allowed_for_prompt: true,
                    usage_count: 0,
                    latest_used_at: null,
                    retrieved_count: 0,
                    latest_retrieved_at: null,
                  },
                ]
              : [],
            latest_retrievals: [],
            non_goals: ['no_external_vector_runtime'],
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
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/test-knowledge/graph')) {
        const hasReview = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith('/test-knowledge/cards/card-uploaded') && call[1]?.method === 'PATCH',
        );
        const hasIndexRebuild = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith('/test-knowledge/index/rebuild') && call[1]?.method === 'POST',
        );
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            nodes: [],
            edges: [],
            coverage: {
              knowledge_coverage_ratio: hasReview ? 1 : 0,
              covered_knowledge_card_count: hasReview ? 1 : 0,
              vector_index_coverage_ratio: hasIndexRebuild ? 1 : 0,
              embedding_indexed_card_count: hasIndexRebuild ? 1 : 0,
            },
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/test-knowledge/cards')) {
        const hasExtraction = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith('/test-knowledge/cards/extract-batch') && call[1]?.method === 'POST',
        );
        const hasReview = fetchMock.mock.calls.some(
          (call) => String(call[0]).endsWith('/test-knowledge/cards/card-uploaded') && call[1]?.method === 'PATCH',
        );
        return new Response(
          JSON.stringify({
            total: hasExtraction ? 1 : 0,
            items: hasExtraction
              ? [
                  {
                    id: 'card-uploaded',
                    project_id: '00000000-0000-0000-0000-000000000101',
                    source_artifact_id: 'ctx-uploaded',
                    source_document_version: 'v1',
                    source_section: 'section:1',
                    source_quote_hash: 'hash-uploaded',
                    knowledge_type: 'BoundaryCondition',
                    title: 'BoundaryCondition: expired coupon checkout',
                    content: 'Expired coupon validation blocks checkout.',
                    module_key: 'coupon',
                    api_endpoint: null,
                    risk_type: 'boundary',
                    case_type_hint: 'negative',
                    applicability: 'case_generation',
                    confidence: 80,
                    safe_to_show: true,
                    allowed_for_prompt: true,
                    status: hasReview ? 'approved' : 'extracted',
                    created_at: '2026-06-30T10:00:00Z',
                  },
                ]
              : [],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/context-artifacts') && init?.method === 'POST') {
        uploadedBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            id: 'ctx-uploaded',
            project_id: '00000000-0000-0000-0000-000000000101',
            owner_entity_type: 'Project',
            owner_entity_id: '00000000-0000-0000-0000-000000000101',
            artifact_type: 'context_markdown',
            file_path: 'projects/ctx/content.md',
            mime_type: 'text/markdown',
            size_bytes: 42,
            sha256: 'sha256:uploaded',
            title: 'coupon-api-notes.md',
            source_ref: 'manual:coupon-api-notes.md',
            safe_to_show: true,
            redaction_applied: false,
            allowed_for_prompt: true,
          }),
          { status: 201, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/test-knowledge/cards/extract-batch') && init?.method === 'POST') {
        extractionBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            source_artifact_ids: ['ctx-uploaded'],
            created_count: 1,
            skipped_count: 0,
            items: [],
          }),
          { status: 201, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/test-knowledge/cards/card-uploaded') && init?.method === 'PATCH') {
        reviewBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            id: 'card-uploaded',
            project_id: '00000000-0000-0000-0000-000000000101',
            source_artifact_id: 'ctx-uploaded',
            source_document_version: 'v1',
            source_section: 'section:1',
            source_quote_hash: 'hash-uploaded',
            knowledge_type: 'BoundaryCondition',
            title: 'BoundaryCondition: expired coupon checkout',
            content: 'Expired coupon validation blocks checkout.',
            module_key: 'coupon',
            api_endpoint: null,
            risk_type: 'boundary',
            case_type_hint: 'negative',
            applicability: 'case_generation',
            confidence: 80,
            safe_to_show: true,
            allowed_for_prompt: true,
            status: 'approved',
            created_at: '2026-06-30T10:00:00Z',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/test-knowledge/cards/retrieve') && init?.method === 'POST') {
        knowledgeCardRetrievalBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            query_text: 'coupon expired checkout',
            approved_only: false,
            total: 1,
            items: [
              {
                evidence_id: 'evidence-card-uploaded',
                knowledge_card_id: 'card-uploaded',
                source_artifact_id: 'ctx-uploaded',
                knowledge_type: 'BoundaryCondition',
                title: 'BoundaryCondition: expired coupon checkout',
                snippet: 'Expired coupon validation blocks checkout.',
                score: 3,
                matched_terms: ['coupon', 'expired', 'checkout'],
                retrieval_reason: 'deterministic_hybrid_keyword_vector',
                semantic_score: 0.92,
                embedding_model: 'deterministic-hashing-v1',
                safe_to_show: true,
                allowed_for_prompt: true,
                status: 'approved',
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/knowledge-adapter') && init?.method === 'PUT') {
        adapterBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            project_id: '00000000-0000-0000-0000-000000000101',
            adapter_name: 'default',
            status: 'configured_stub',
            provider_type: 'deterministic_local',
            retrieval_mode: 'deterministic_local',
            config: {},
            safety_policy: {},
            last_checked_at: null,
            notes: null,
            used_knowledge: false,
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/projects/00000000-0000-0000-0000-000000000101/knowledge-adapter/retrieve') && init?.method === 'POST') {
        retrievalBody = JSON.parse(String(init.body));
        return new Response(
          JSON.stringify({
            adapter_name: 'default',
            retrieval_mode: 'deterministic_local',
            query_text: 'coupon expired checkout',
            query_terms: ['coupon', 'expired', 'checkout'],
            used_knowledge: true,
            used_context_artifact_ids: ['ctx-uploaded'],
            results: [
              {
                context_artifact_id: 'ctx-uploaded',
                title: 'coupon-api-notes.md',
                source_ref: 'manual:coupon-api-notes.md',
                score: 3,
                matched_terms: ['coupon', 'expired', 'checkout'],
                snippet: 'Expired coupon validation blocks checkout.',
                sha256: 'sha256:uploaded',
                redaction_applied: false,
                allowed_for_prompt: true,
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

    const file = new File(['expired coupon checkout notes'], 'checkout-runbook.txt', { type: 'text/plain' });
    Object.defineProperty(file, 'text', {
      value: vi.fn().mockResolvedValue('expired coupon checkout notes'),
    });
    const fileInput = wrapper.find('[data-test="knowledge-file"]');
    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
    });
    await fileInput.trigger('change');
    await flushPromises();
    await wrapper.vm.$nextTick();

    await wrapper.findAll('form')[0].trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(uploadedBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        title: 'checkout-runbook.txt',
        artifact_type: 'context_text',
        mime_type: 'text/plain',
        source_ref: 'file:checkout-runbook.txt',
        content: 'expired coupon checkout notes',
      }),
    );

    await wrapper.find('[data-test="extract-knowledge-cards"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(extractionBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        source_artifact_ids: ['ctx-uploaded'],
      }),
    );
    expect(wrapper.text()).toContain('BoundaryCondition: expired coupon checkout');
    expect(wrapper.text()).toContain('新增 1，跳过 0');

    await wrapper.find('[data-test="approve-knowledge-card"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(reviewBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        status: 'approved',
      }),
    );
    expect(wrapper.text()).toContain('approved');

    await wrapper.find('[data-test="rebuild-knowledge-index"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(indexRebuildBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        embedding_model: 'deterministic-hashing-v1',
        embedding_dim: 64,
      }),
    );
    expect(wrapper.text()).toContain('Vector Index');

    await wrapper.find('[data-test="knowledge-card-retrieval-form"]').trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(knowledgeCardRetrievalBody).toEqual(
      expect.objectContaining({
        project_id: '00000000-0000-0000-0000-000000000101',
        query_text: 'coupon expired checkout',
        limit: 5,
        approved_only: false,
      }),
    );
    expect(wrapper.text()).toContain('score 3');
    expect(wrapper.text()).toContain('vector 0.92');
    expect(wrapper.text()).toContain('coupon, expired, checkout');

    await wrapper.find('[data-test="enable-local-retrieval"]').trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(adapterBody).toEqual(
      expect.objectContaining({
        adapter_name: 'default',
        status: 'configured_stub',
        provider_type: 'deterministic_local',
      }),
    );

    await wrapper.findAll('form')[1].trigger('submit');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(retrievalBody).toEqual(
      expect.objectContaining({
        query_text: 'coupon expired checkout',
        adapter_name: 'default',
      }),
    );
    expect(wrapper.text()).toContain('检索词');
    expect(wrapper.text()).toContain('得分 3');
    expect(wrapper.text()).toContain('Expired coupon validation blocks checkout.');
  });
});
