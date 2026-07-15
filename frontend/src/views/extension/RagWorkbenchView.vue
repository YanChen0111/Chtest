<template>
  <section class="rag-workbench" aria-labelledby="rag-workbench-title" data-test="knowledge-workbench-page">
    <header class="rag-hero">
      <div>
        <p class="eyebrow">Evidence operations</p>
        <h2 id="rag-workbench-title">Knowledge Workbench</h2>
        <p class="rag-subtitle">Review prompt-safe knowledge, inspect retrieval quality, and trace every result back to evidence.</p>
      </div>
      <div class="rag-hero-actions">
        <a-button data-test="open-knowledge-base" type="primary" @click="go('knowledge-base')">Open knowledge base</a-button>
        <a-button data-test="refresh-knowledge-workbench" @click="refresh" :loading="store.loading">Refresh data</a-button>
      </div>
    </header>

    <a-alert v-if="store.errorMessage" data-test="knowledge-workbench-error" type="error" show-icon :content="store.errorMessage" />

    <div class="rag-kpis" aria-label="Knowledge health metrics">
      <article v-for="metric in metrics" :key="metric.label" class="rag-kpi">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
        <small :class="`tone-${metric.tone}`">{{ metric.note }}</small>
      </article>
    </div>

    <div class="rag-grid">
      <a-card class="rag-panel rag-next" :bordered="false">
        <template #title>Next actions</template>
        <div class="action-list">
          <button v-for="action in actions" :key="action.route" class="action-row" @click="go(action.route)">
            <span class="action-icon">{{ action.icon }}</span>
            <span><strong>{{ action.title }}</strong><small>{{ action.description }}</small></span>
            <span class="action-arrow" aria-hidden="true">-&gt;</span>
          </button>
        </div>
      </a-card>

      <a-card class="rag-panel" :bordered="false">
        <template #title>Provider health</template>
        <div class="provider-summary">
          <div>
            <span class="muted-label">Provider</span>
            <strong>{{ adapter.provider_type || 'none' }}</strong>
          </div>
          <a-tag :color="statusColor(adapter.status)">{{ adapter.status || 'not_configured' }}</a-tag>
        </div>
        <dl class="provider-details">
          <div><dt>Mode</dt><dd>{{ adapter.retrieval_mode || 'not configured' }}</dd></div>
          <div><dt>Last checked</dt><dd>{{ adapter.last_checked_at || 'Not checked' }}</dd></div>
          <div><dt>Usage</dt><dd>{{ adapter.used_knowledge ? 'Evidence used' : 'No evidence used' }}</dd></div>
        </dl>
        <a-alert v-if="isDegraded" type="warning" show-icon content="Provider is degraded. Retrieval remains available through the local fallback." />
      </a-card>
    </div>

    <a-card class="rag-panel trace-panel" :bordered="false" data-test="evidence-trace-panel">
      <template #title>Global evidence trace</template>
      <div class="trace-toolbar">
        <a-input v-model="traceQuery" allow-clear placeholder="Search card, retrieval, feedback, or case evidence" @press-enter="searchTrace" />
        <a-select v-model="traceStage" :options="[{ label: 'All stages', value: 'all' }, ...traceStages.map((stage) => ({ label: stage, value: stage }))]" />
        <a-button type="primary" :loading="traceLoading" @click="searchTrace">Search trace</a-button>
      </div>
      <a-alert v-if="traceError" data-test="evidence-trace-error" type="error" show-icon :content="traceError" />
      <a-empty v-if="!traceLoading && traceQuery && !visibleTraceNodes.length" data-test="evidence-trace-empty" description="No evidence trace matches" />
      <div v-else class="trace-list" aria-label="Evidence trace results" data-test="evidence-trace-results">
        <button v-for="node in visibleTraceNodes" :key="`${node.entity_type}-${node.entity_id}-${node.stage}`" class="trace-row" data-test="evidence-trace-row" @click="selectTrace(node)">
          <span class="trace-stage">{{ node.stage }}</span>
          <span class="trace-main"><strong>{{ node.summary }}</strong><small>{{ node.entity_type }} · {{ node.status }} · {{ node.timestamp }}</small></span>
          <span class="trace-diagnostics">{{ node.provider_type || 'local' }} / {{ node.retrieval_mode || 'n/a' }} · {{ node.latency_ms == null ? 'latency n/a' : `${node.latency_ms} ms` }}</span>
          <span class="trace-arrow" aria-hidden="true">-&gt;</span>
        </button>
      </div>
    </a-card>

    <a-drawer v-model:visible="traceDrawerVisible" title="Evidence trace details" :width="420">
      <template v-if="selectedTrace">
        <dl class="trace-details">
          <div><dt>Entity</dt><dd>{{ selectedTrace.entity_type }} / {{ selectedTrace.entity_id }}</dd></div>
          <div><dt>Status</dt><dd>{{ selectedTrace.status }}</dd></div>
          <div><dt>Provider / mode</dt><dd>{{ selectedTrace.provider_type || 'local' }} / {{ selectedTrace.retrieval_mode || 'n/a' }}</dd></div>
          <div><dt>Fallback</dt><dd>{{ selectedTrace.fallback_reason || 'none' }}</dd></div>
          <div><dt>Latency</dt><dd>{{ selectedTrace.latency_ms == null ? 'not recorded' : `${selectedTrace.latency_ms} ms` }}</dd></div>
          <div><dt>Evidence ids</dt><dd>{{ selectedTrace.evidence_ids.join(', ') || 'none' }}</dd></div>
          <div><dt>Source locator</dt><dd><code>{{ JSON.stringify(selectedTrace.source_locator) }}</code></dd></div>
          <div><dt>Safe artifacts</dt><dd>{{ selectedTrace.artifact_refs.map((artifact) => artifact.id).join(', ') || 'none' }}</dd></div>
        </dl>
        <a-button type="primary" @click="navigateTrace(selectedTrace)">Open originating record</a-button>
      </template>
    </a-drawer>

    <a-card class="rag-panel rag-table-panel" :bordered="false" data-test="recent-retrieval-runs">
      <template #title>
        <div class="panel-title-row"><span>Recent retrievals</span><a-button size="small" @click="go('knowledge-base')">View all logs</a-button></div>
      </template>
      <div class="table-toolbar">
        <a-input v-model="query" allow-clear placeholder="Filter by query terms" />
        <a-tag color="blue">{{ filteredRetrievals.length }} runs</a-tag>
      </div>
      <a-table data-test="recent-retrieval-table" :data="filteredRetrievals" :pagination="false" :scroll="{ x: 1120 }" row-key="retrieval_evidence_artifact_id" size="small">
        <template #columns>
          <a-table-column title="Query" data-index="query" />
          <a-table-column title="Provider" data-index="provider" :width="140" />
          <a-table-column title="Mode" data-index="mode" :width="110" />
          <a-table-column title="Fallback" data-index="fallback" :width="120" />
          <a-table-column title="Latency" data-index="latency" :width="110" />
          <a-table-column title="Evidence" data-index="snippet_count" :width="110" />
          <a-table-column title="Created" data-index="created_at" :width="210" />
          <a-table-column title="Trace" :width="110">
            <template #cell="{ record }"><a-button data-test="resume-retrieval-run" size="mini" @click="resumeRetrieval(record.query)">{{ record.retrieval_evidence_artifact_id.slice(0, 8) }}</a-button></template>
          </a-table-column>
        </template>
        <template #empty><a-empty description="No retrieval runs yet" /></template>
      </a-table>
      <div v-if="filteredRetrievals.length" class="retrieval-rows" aria-label="Retrieval log summary">
        <div v-for="row in filteredRetrievals" :key="`summary-${row.retrieval_evidence_artifact_id}`" class="retrieval-row">
          <strong>{{ row.query }}</strong><span>{{ row.provider }} / {{ row.mode }} / {{ row.fallback }}</span><small>{{ row.snippet_count }} evidence · {{ row.latency }} · {{ row.created_at }}</small><a-button data-test="resume-retrieval-run" size="mini" @click="resumeRetrieval(row.query)">Resume</a-button>
        </div>
      </div>
    </a-card>

    <a-card class="rag-panel" :bordered="false">
      <template #title>Coverage and trace</template>
      <div class="coverage-row">
        <div class="coverage-ring" :style="{ '--coverage': `${coveragePercent}%` }"><strong>{{ coveragePercent }}%</strong><span>knowledge covered</span></div>
        <div class="coverage-copy"><h3>Evidence path is visible</h3><p>{{ graphNodes }} nodes and {{ graphEdges }} typed edges are available for impact and gap analysis.</p><a-button @click="go('knowledge-base')">Open graph view</a-button></div>
      </div>
    </a-card>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

import { searchEvidenceTrace, type EvidenceTraceNodeRead } from '../../api/extension';
import { useExtensionStore } from '../../stores/extension';

const router = useRouter();
const store = useExtensionStore();
const query = ref('');
const traceQuery = ref('');
const traceStage = ref('all');
const traceLoading = ref(false);
const traceError = ref('');
const traceNodes = ref<EvidenceTraceNodeRead[]>([]);
const selectedTrace = ref<EvidenceTraceNodeRead | null>(null);
const traceDrawerVisible = ref(false);

const adapter = computed(() => store.knowledgeBase?.knowledge_adapter ?? {
  provider_type: 'none', status: 'not_configured', retrieval_mode: undefined, last_checked_at: null, used_knowledge: false,
});
const isDegraded = computed(() => ['degraded', 'failed'].includes(adapter.value.status));
const coveragePercent = computed(() => Math.round(store.knowledgeCoverageRatio * 100));
const graphNodes = computed(() => store.testKnowledgeGraph?.nodes.length ?? 0);
const graphEdges = computed(() => store.testKnowledgeGraph?.edges.length ?? 0);
const filteredRetrievals = computed(() => {
  const needle = query.value.trim().toLowerCase();
  return store.latestRetrievals
    .filter((item) => !needle || item.query_terms.some((term) => term.toLowerCase().includes(needle)))
    .map((item) => ({
      ...item,
      query: item.query_terms.join(' '),
      provider: adapter.value.provider_type || 'none',
      mode: adapter.value.retrieval_mode || 'unknown',
      fallback: isDegraded.value ? 'keyword fallback' : 'none',
      latency: 'not recorded',
    }));
});
const metrics = computed(() => [
  { label: 'Prompt-ready cards', value: store.promptReadyKnowledgeCardCount, note: `${store.pendingKnowledgeCardCount} awaiting review`, tone: store.pendingKnowledgeCardCount ? 'warning' : 'good' },
  { label: 'Index gap', value: store.knowledgeIndexGapCount, note: store.knowledgeIndexGapCount ? 'Rebuild recommended' : 'Index is aligned', tone: store.knowledgeIndexGapCount ? 'warning' : 'good' },
  { label: 'Knowledge coverage', value: `${coveragePercent.value}%`, note: `${store.coveredKnowledgeCardCount} cards linked`, tone: coveragePercent.value >= 80 ? 'good' : 'warning' },
  { label: 'Retrieval runs', value: store.latestRetrievals.length, note: 'Evidence artifacts retained', tone: 'neutral' },
]);
const actions = [
  { icon: '+', title: 'Review extracted cards', description: 'Approve only prompt-safe evidence', route: 'knowledge-base' },
  { icon: '?', title: 'Run a retrieval check', description: 'Compare query, score, and source', route: 'knowledge-base' },
  { icon: '#', title: 'Inspect case rationale', description: 'See evidence behind generated cases', route: 'case-generation-review' },
];

const visibleTraceNodes = computed(() => traceNodes.value.filter((node) => traceStage.value === 'all' || node.stage === traceStage.value));
const traceStages = computed(() => [...new Set(traceNodes.value.map((node) => node.stage))]);

function go(routeName: string) { router.push({ name: routeName }); }
function resumeRetrieval(retrievalQuery: string) {
  window.sessionStorage.setItem('chtest:knowledge-retrieval-query', retrievalQuery);
  router.push({ name: 'knowledge-base' });
}
function refresh() { return store.loadExtensionSurface(); }
function statusColor(status: string) { return status === 'ready' ? 'green' : ['degraded', 'failed'].includes(status) ? 'orange' : 'gray'; }
async function searchTrace() {
  const text = traceQuery.value.trim();
  if (!text) return;
  traceLoading.value = true;
  traceError.value = '';
  try {
    const result = await searchEvidenceTrace(store.projectId, { q: text, limit: 50 });
    traceNodes.value = result.stages.flatMap((stage) => stage.items);
  } catch (error) {
    traceError.value = error instanceof Error ? error.message : 'Trace search failed';
    traceNodes.value = [];
  } finally {
    traceLoading.value = false;
  }
}
function selectTrace(node: EvidenceTraceNodeRead) {
  selectedTrace.value = node;
  traceDrawerVisible.value = true;
}
function navigateTrace(node: EvidenceTraceNodeRead) {
  const routeName = node.entity_type === 'GeneratedCaseCandidate' ? 'case-generation-review' : 'knowledge-base';
  router.push({ name: routeName, query: { entityType: node.entity_type, entityId: node.entity_id } });
  traceDrawerVisible.value = false;
}

onMounted(() => { if (!store.knowledgeBase) void store.loadExtensionSurface(); });
</script>

<style scoped>
.rag-workbench { display: grid; gap: 18px; }
.rag-hero { display: flex; justify-content: space-between; gap: 20px; align-items: flex-start; padding: 24px; border: 1px solid #dbe3ef; border-radius: 8px; background: linear-gradient(135deg, #ffffff 0%, #f7fbff 100%); }
.rag-hero h2 { margin: 0; color: #152238; font-size: 30px; }
.rag-subtitle { max-width: 680px; margin: 10px 0 0; color: #5b6b82; line-height: 1.6; }
.rag-hero-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.rag-kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.rag-kpi, .rag-panel { border: 1px solid #dbe3ef; border-radius: 8px; background: #fff; }
.rag-kpi { padding: 16px; }
.rag-kpi span, .rag-kpi small { display: block; color: #6b7b91; }
.rag-kpi strong { display: block; margin: 8px 0 4px; color: #14213a; font-size: 26px; }
.rag-kpi small { font-size: 12px; }
.tone-good { color: #15803d !important; }.tone-warning { color: #b45309 !important; }.tone-neutral { color: #64748b !important; }
.rag-grid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 16px; }
.action-list { display: grid; gap: 8px; }.action-row { display: grid; grid-template-columns: 28px 1fr 24px; align-items: center; gap: 10px; width: 100%; padding: 12px; border: 1px solid #e3e9f2; border-radius: 6px; background: #fbfdff; text-align: left; cursor: pointer; }.action-row:hover { border-color: #7aa7e8; background: #f5f9ff; }.action-icon { color: #2563eb; font-size: 18px; }.action-row strong, .action-row small { display: block; }.action-row small { margin-top: 3px; color: #718096; }.action-arrow { color: #2563eb; text-align: right; }
.provider-summary, .panel-title-row, .table-toolbar, .coverage-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }.provider-summary strong { display: block; margin-top: 4px; color: #14213a; }.provider-details { display: grid; gap: 10px; margin: 18px 0; }.provider-details div { display: flex; justify-content: space-between; gap: 12px; border-bottom: 1px solid #eef2f7; padding-bottom: 8px; }.provider-details dt { color: #718096; }.provider-details dd { margin: 0; color: #1f2937; text-align: right; }.muted-label { color: #718096; font-size: 12px; }
.table-toolbar { margin-bottom: 12px; }.table-toolbar .arco-input-wrapper { max-width: 320px; }
.trace-toolbar { display: grid; grid-template-columns: minmax(220px, 1fr) 180px auto; gap: 10px; margin-bottom: 12px; }.trace-list { display: grid; gap: 6px; }.trace-row { display: grid; grid-template-columns: 120px minmax(0, 1fr) 220px 24px; gap: 12px; align-items: center; width: 100%; padding: 11px 12px; border: 1px solid #e3e9f2; border-radius: 6px; background: #fbfdff; text-align: left; cursor: pointer; }.trace-row:hover { border-color: #7aa7e8; background: #f5f9ff; }.trace-stage, .trace-diagnostics, .trace-main small { color: #718096; font-size: 12px; }.trace-main strong, .trace-main small { display: block; }.trace-main small { margin-top: 3px; }.trace-arrow { color: #2563eb; text-align: right; }
.trace-details { display: grid; gap: 12px; margin: 0 0 18px; }.trace-details div { display: grid; grid-template-columns: 110px minmax(0, 1fr); gap: 10px; border-bottom: 1px solid #eef2f7; padding-bottom: 9px; }.trace-details dt { color: #718096; }.trace-details dd { min-width: 0; margin: 0; color: #1f2937; overflow-wrap: anywhere; }.trace-details code { white-space: pre-wrap; }
.retrieval-rows { display: grid; gap: 6px; margin-top: 12px; }.retrieval-row { display: grid; grid-template-columns: minmax(0, 1fr) auto auto auto; gap: 12px; align-items: center; padding: 9px 10px; border: 1px solid #edf1f6; border-radius: 6px; color: #344054; }.retrieval-row span, .retrieval-row small { color: #718096; font-size: 12px; }
.coverage-ring { display: grid; width: 128px; height: 128px; flex: 0 0 128px; place-content: center; border-radius: 50%; background: conic-gradient(#2563eb var(--coverage), #e8eef7 0); text-align: center; }.coverage-ring::before { content: ''; position: absolute; width: 96px; height: 96px; border-radius: 50%; background: #fff; }.coverage-ring strong, .coverage-ring span { position: relative; z-index: 1; }.coverage-ring strong { font-size: 26px; color: #14213a; }.coverage-ring span { width: 76px; color: #718096; font-size: 11px; }.coverage-copy { max-width: 620px; }.coverage-copy h3 { margin: 0; color: #14213a; }.coverage-copy p { margin: 8px 0 14px; color: #68778d; line-height: 1.6; }
@media (max-width: 900px) { .rag-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }.rag-grid { grid-template-columns: 1fr; }.trace-row { grid-template-columns: 100px minmax(0, 1fr) 24px; }.trace-diagnostics { display: none; } }
@media (max-width: 600px) { .rag-hero, .coverage-row { flex-direction: column; }.rag-hero h2 { font-size: 24px; }.rag-kpis { grid-template-columns: 1fr 1fr; }.rag-hero-actions { width: 100%; }.rag-hero-actions .arco-btn { flex: 1; }.coverage-ring { align-self: center; }.trace-toolbar { grid-template-columns: 1fr; }.trace-row { grid-template-columns: 76px minmax(0, 1fr) 24px; padding: 10px 8px; }.trace-main strong { overflow-wrap: anywhere; }.retrieval-row { grid-template-columns: minmax(0, 1fr) auto; }.retrieval-row span, .retrieval-row small { grid-column: 1 / -1; } }
</style>
