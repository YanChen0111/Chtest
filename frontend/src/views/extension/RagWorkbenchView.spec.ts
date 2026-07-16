import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia, setActivePinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import { describe, expect, it, vi } from 'vitest';

import RagWorkbenchView from './RagWorkbenchView.vue';
import * as extensionApi from '../../api/extension';
import { useExtensionStore } from '../../stores/extension';

describe('RagWorkbenchView', () => {
  it('surfaces tester-first health, gaps, coverage, and trace search actions', async () => {
    const pinia = createPinia();
    setActivePinia(pinia);
    const store = useExtensionStore();
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', component: RagWorkbenchView }] });
    store.knowledgeBase = {
      project_id: store.projectId,
      knowledge_adapter: {
        project_id: store.projectId,
        adapter_name: 'default',
        status: 'degraded',
        provider_type: 'postgres_hybrid',
        retrieval_mode: 'keyword',
        config: {},
        safety_policy: {},
        last_checked_at: null,
        notes: null,
        used_knowledge: true,
      },
      context_artifacts: [],
      latest_retrievals: [
        {
          ai_task_id: 'task-1',
          retrieval_evidence_artifact_id: 'artifact-1',
          query_terms: ['expired', 'coupon'],
          used_context_artifact_ids: [],
          snippet_count: 2,
          created_at: '2026-07-15T10:00:00Z',
        },
      ],
      non_goals: [],
    };
    store.testKnowledgeCards = [
      {
        id: 'card-1',
        project_id: store.projectId,
        source_artifact_id: 'artifact-source',
        source_document_version: 'v1',
        source_section: '1',
        source_quote_hash: 'hash',
        knowledge_type: 'Rule',
        title: 'Expired coupon',
        content: 'Expired coupon is rejected.',
        module_key: null,
        api_endpoint: null,
        risk_type: null,
        case_type_hint: null,
        applicability: 'case_generation',
        confidence: 90,
        safe_to_show: true,
        allowed_for_prompt: true,
        status: 'extracted',
        created_at: '2026-07-15T10:00:00Z',
      },
    ];
    store.testKnowledgeGraph = {
      project_id: store.projectId,
      nodes: [{ id: 'card:1', node_type: 'knowledge_card' }],
      edges: [{ source: 'case:1', target: 'card:1', edge_type: 'covers' }],
      coverage: { knowledge_coverage_ratio: 0.5 },
    };

    const traceSpy = vi.spyOn(extensionApi, 'searchEvidenceTrace').mockResolvedValue({
      project_id: store.projectId,
      query: 'expired',
      stages: [{ name: 'evidence', items: [{ stage: 'evidence', entity_type: 'KnowledgeEvidence', entity_id: 'evidence-1', status: 'eligible', timestamp: '2026-07-15T10:00:00Z', summary: 'expired coupon rule', artifact_refs: [], evidence_ids: ['evidence-1'], source_locator: { section: '1' }, provider_type: 'postgres_hybrid', retrieval_mode: 'keyword', latency_ms: 12 }] }],
      total: 1,
    });
    const wrapper = mount(RagWorkbenchView, { global: { plugins: [pinia, ArcoVue, router] } });

    expect(wrapper.text()).toContain('Knowledge Workbench');
    expect(wrapper.text()).toContain('Prompt-ready cards');
    expect(wrapper.text()).toContain('Index gap');
    expect(wrapper.text()).toContain('Provider health');
    expect(wrapper.text()).toContain('postgres_hybrid');
    expect(wrapper.text()).toContain('degraded');
    expect(wrapper.text()).toContain('keyword fallback');
    expect(wrapper.text()).toContain('Global evidence trace');
    expect(wrapper.text()).toContain('expired');
    expect(wrapper.text()).toContain('50%');
    expect(wrapper.find('[data-test="knowledge-workbench-page"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="recent-retrieval-runs"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="resume-retrieval-run"]').exists()).toBe(true);
    await wrapper.find('input[placeholder="Search card, retrieval, feedback, or case evidence"]').setValue('expired');
    const searchButton = wrapper.findAll('button').find((button) => button.text().includes('Search trace'));
    expect(searchButton).toBeDefined();
    await searchButton!.trigger('click');
    await flushPromises();
    expect(traceSpy).toHaveBeenCalledWith(store.projectId, { q: 'expired', limit: 50 });
    expect(wrapper.text()).toContain('expired coupon rule');
    expect(wrapper.text()).toContain('12 ms');
    await wrapper.find('.trace-row').trigger('click');
    expect(wrapper.find('.trace-row').exists()).toBe(true);
    expect(wrapper.find('[data-test="evidence-trace-row"]').exists()).toBe(true);
    traceSpy.mockRestore();
  });
});
