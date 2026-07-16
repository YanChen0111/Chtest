<template>
  <section class="knowledge-base-page" aria-labelledby="knowledge-base-title" data-test="knowledge-base-page">
    <div class="settings-heading">
      <div>
        <p class="eyebrow">扩展表面</p>
        <h2 id="knowledge-base-title">RAG 知识库</h2>
        <p>查看项目上下文、提示词可用性、AI 使用记录和 MCP-ready 工具结构；V1 仅保留扩展表面。</p>
      </div>
      <a-space>
        <a-tag color="blue">ContextArtifact</a-tag>
        <a-tag color="gray">无 RAG 运行时</a-tag>
        <a-button type="primary" :loading="store.loading" @click="store.loadExtensionSurface()">刷新</a-button>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" data-test="knowledge-base-error" type="error" :content="store.errorMessage" show-icon />
    <p v-if="store.errorMessage" class="operation-message operation-message--error">{{ store.errorMessage }}</p>
    <a-button v-if="store.errorMessage" data-test="retry-knowledge-base" size="small" @click="store.loadExtensionSurface()">Retry loading</a-button>
    <a-alert v-if="store.successMessage" data-test="knowledge-base-success" type="success" :content="store.successMessage" show-icon />
    <p v-if="store.successMessage" class="operation-message operation-message--success">{{ store.successMessage }}</p>

    <div class="knowledge-metrics">
      <a-card class="settings-panel" :bordered="false">
        <span>ContextArtifact</span>
        <strong>{{ store.contextArtifactCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>可安全展示</span>
        <strong>{{ store.safeContextArtifactCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>允许进入提示词</span>
        <strong>{{ store.promptEligibleCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>MCP-ready 工具</span>
        <strong>{{ store.mcpReadyToolCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>检索证据</span>
        <strong>{{ store.latestRetrievals.length }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>测试知识卡</span>
        <strong>{{ store.testKnowledgeCardCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>知识覆盖率</span>
        <strong>{{ Math.round(store.knowledgeCoverageRatio * 100) }}%</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>Vector Index</span>
        <strong>{{ store.indexedKnowledgeCardCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>Vector Coverage</span>
        <strong>{{ Math.round(store.vectorIndexCoverageRatio * 100) }}%</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>Prompt Ready</span>
        <strong>{{ store.promptReadyKnowledgeCardCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>Index Gap</span>
        <strong>{{ store.knowledgeIndexGapCount }}</strong>
      </a-card>
    </div>

    <a-spin :loading="store.loading" class="settings-spin">
      <div class="knowledge-grid">
        <a-card class="settings-panel knowledge-adapter-panel" :bordered="false">
          <template #title>KnowledgeAdapter</template>
          <div class="adapter-state">
            <div>
              <span>状态</span>
              <strong>{{ adapterStatusLabel(adapterState.status) }}</strong>
            </div>
            <a-tag :color="adapterState.used_knowledge ? 'orange' : 'green'">
              使用知识={{ adapterState.used_knowledge ? '是' : '否' }}
            </a-tag>
          </div>
          <a-descriptions :column="1" size="small" bordered>
            <a-descriptions-item label="适配器">{{ adapterState.adapter_name }}</a-descriptions-item>
            <a-descriptions-item label="提供方">{{ adapterState.provider_type }}</a-descriptions-item>
            <a-descriptions-item label="检索模式">{{ retrievalModeLabel(adapterState.retrieval_mode) }}</a-descriptions-item>
            <a-descriptions-item label="最近检查">{{ adapterState.last_checked_at ?? '未检查' }}</a-descriptions-item>
            <a-descriptions-item label="备注">{{ adapterState.notes ?? 'V1 空适配器外壳' }}</a-descriptions-item>
          </a-descriptions>
          <a-button
            class="adapter-action"
            data-test="enable-local-retrieval"
            :loading="store.loadingMutation"
            @click="store.enableDeterministicRetrieval()"
          >
            启用本地检索
          </a-button>
        </a-card>

        <a-card class="settings-panel" :bordered="false">
          <template #title>V1 非目标</template>
          <div class="non-goal-list">
            <a-tag v-for="goal in store.knowledgeBase?.non_goals ?? []" :key="goal" color="gray">{{ goal }}</a-tag>
          </div>
          <a-empty v-if="(store.knowledgeBase?.non_goals.length ?? 0) === 0" description="暂无边界声明" />
        </a-card>

        <a-card class="settings-panel" :bordered="false">
          <template #title>导入知识</template>
          <form class="knowledge-form" @submit.prevent="submitKnowledge">
            <label>
              <span>标题</span>
              <a-input data-test="knowledge-title" v-model="knowledgeForm.title" />
            </label>
            <label>
              <span>来源</span>
              <a-input data-test="knowledge-source" v-model="knowledgeForm.sourceRef" />
            </label>
            <label>
              <span>文件</span>
              <input
                class="knowledge-file-input"
                data-test="knowledge-file"
                type="file"
                accept=".md,.markdown,.txt,.csv,.json,.yaml,.yml,.pdf,.xlsx,.jpg,.jpeg,.png,.webp,.tif,.tiff,text/markdown,text/plain,text/csv,application/json,application/yaml,text/yaml,application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,image/*"
                @change="handleKnowledgeFileChange"
              />
            </label>
            <label>
              <span>格式</span>
              <a-radio-group v-model="knowledgeForm.artifactType">
                <a-radio value="context_markdown">Markdown</a-radio>
                <a-radio value="context_text">TXT</a-radio>
              </a-radio-group>
            </label>
            <label>
              <span>内容</span>
              <a-textarea data-test="knowledge-content" v-model="knowledgeForm.content" :auto-size="{ minRows: 5, maxRows: 9 }" />
            </label>
            <a-button data-test="upload-knowledge" html-type="submit" type="primary" :loading="store.loadingMutation">
              导入 ContextArtifact
            </a-button>
          </form>
        </a-card>

        <a-card class="settings-panel retrieval-test-panel" :bordered="false">
          <template #title>检索测试</template>
          <form class="knowledge-form" @submit.prevent="submitRetrievalTest">
            <label>
              <span>查询</span>
              <a-textarea data-test="retrieval-query" v-model="retrievalQuery" :auto-size="{ minRows: 3, maxRows: 5 }" />
            </label>
            <a-button data-test="run-retrieval" html-type="submit" type="primary" :loading="store.loadingMutation">
              运行本地检索
            </a-button>
          </form>
          <div v-if="store.retrievalTest" class="retrieval-test-results">
            <div class="retrieval-terms">
              <span>检索词</span>
              <a-tag v-for="term in store.retrievalTest.query_terms" :key="term" color="green">{{ term }}</a-tag>
            </div>
            <a-alert
              :type="store.retrievalTest.used_knowledge ? 'success' : 'warning'"
              :content="store.retrievalTest.used_knowledge ? '已命中本地知识' : '未命中可用知识'"
              show-icon
            />
            <div v-for="result in store.retrievalTest.results" :key="result.context_artifact_id" class="retrieval-result">
              <div class="retrieval-result__meta">
                <strong>{{ result.title }}</strong>
                <a-tag color="orange">得分 {{ result.score }}</a-tag>
              </div>
              <p>{{ result.snippet }}</p>
            </div>
          </div>
        </a-card>

        <a-card class="settings-panel test-knowledge-card-panel" :bordered="false">
          <template #title>测试知识卡</template>
          <a-space>
            <a-button
              data-test="extract-knowledge-cards"
              type="primary"
              :disabled="promptEligibleContextArtifactIds.length === 0"
              :loading="store.loadingMutation"
              @click="extractKnowledgeCards"
            >
              抽取知识卡
            </a-button>
            <a-tag color="blue">{{ store.testKnowledgeCardCount }} 张</a-tag>
            <a-button
              data-test="rebuild-knowledge-index"
              :disabled="store.promptReadyKnowledgeCardCount === 0"
              :loading="store.loadingMutation"
              @click="store.rebuildKnowledgeIndex()"
            >
              Rebuild Vector Index
            </a-button>
          </a-space>
          <div class="knowledge-readiness-strip" data-test="knowledge-readiness-strip">
            <span>Approved <strong>{{ store.approvedKnowledgeCardCount }}</strong></span>
            <span>Needs Review <strong>{{ store.pendingKnowledgeCardCount }}</strong></span>
            <span>Prompt Ready <strong>{{ store.promptReadyKnowledgeCardCount }}</strong></span>
            <span>Index Gap <strong>{{ store.knowledgeIndexGapCount }}</strong></span>
          </div>
          <div
            v-if="store.knowledgeIndexGapCount > 0"
            class="knowledge-index-gap-alert"
            role="status"
          >
            Prompt-ready knowledge cards missing index: {{ store.knowledgeIndexGapCount }}
          </div>
          <div v-if="store.latestKnowledgeExtraction" class="knowledge-extraction-result">
            新增 {{ store.latestKnowledgeExtraction.created_count }}，跳过 {{ store.latestKnowledgeExtraction.skipped_count }}
          </div>
          <form
            class="knowledge-card-search"
            data-test="knowledge-card-retrieval-form"
            @submit.prevent="submitKnowledgeCardRetrieval"
          >
            <a-input
              v-model="knowledgeCardQuery"
              data-test="knowledge-card-query"
              placeholder="输入需求、接口或风险关键词"
              allow-clear
            />
            <a-button data-test="retrieve-knowledge-cards" html-type="submit" :loading="store.loadingMutation">
              检索知识卡
            </a-button>
          </form>
          <div v-if="store.knowledgeCardRetrieval" class="knowledge-card-retrieval">
            <article
              v-for="item in store.knowledgeCardRetrieval.items"
              :key="item.evidence_id"
              class="test-knowledge-card"
            >
              <div class="retrieval-result__meta">
                <strong>{{ item.title }}</strong>
                <a-space>
                  <a-tag :color="cardStatusColor(item.status)">{{ item.status }}</a-tag>
                  <a-tag color="orange">score {{ item.score }}</a-tag>
                  <a-tag v-if="item.semantic_score !== undefined" color="purple">
                    vector {{ formatSemanticScore(item.semantic_score) }}
                  </a-tag>
                </a-space>
              </div>
              <p>{{ item.snippet }}</p>
              <small>{{ item.knowledge_type }} · {{ item.matched_terms.join(', ') }}</small>
            </article>
            <a-empty
              v-if="store.knowledgeCardRetrieval.items.length === 0"
              description="没有命中可用于 prompt 的知识卡"
            />
          </div>
          <div v-if="store.testKnowledgeCards.length" class="test-knowledge-card-list">
            <article v-for="card in store.testKnowledgeCards.slice(0, 5)" :key="card.id" class="test-knowledge-card">
              <div class="retrieval-result__meta">
                <strong>{{ card.title }}</strong>
                <a-space>
                  <a-tag color="green">{{ card.knowledge_type }}</a-tag>
                  <a-tag :color="cardStatusColor(card.status)">{{ card.status }}</a-tag>
                </a-space>
              </div>
              <p>{{ card.content }}</p>
              <small>置信度 {{ card.confidence }} · {{ card.case_type_hint ?? 'functional' }}</small>
              <div class="knowledge-card-actions">
                <a-button
                  data-test="approve-knowledge-card"
                  size="mini"
                  type="primary"
                  :disabled="card.status === 'approved'"
                  :loading="store.loadingMutation"
                  @click="reviewKnowledgeCard(card.id, 'approved')"
                >
                  批准
                </a-button>
                <a-button
                  data-test="archive-knowledge-card"
                  size="mini"
                  status="danger"
                  :disabled="card.status === 'archived'"
                  :loading="store.loadingMutation"
                  @click="reviewKnowledgeCard(card.id, 'archived')"
                >
                  归档
                </a-button>
              </div>
            </article>
          </div>
          <a-empty v-else description="暂无测试知识卡" />
        </a-card>
      </div>

      <div class="knowledge-grid knowledge-main-grid">
        <a-card class="settings-panel" :bordered="false">
          <template #title>ContextArtifact 清单</template>
          <a-table
            :columns="contextColumns"
            :data="contextRows"
            :pagination="false"
            :scroll="{ x: 980 }"
            row-key="id"
            size="small"
          >
            <template #safe="{ record }">
              <a-tag :color="record.safe_to_show ? 'green' : 'orange'">{{ record.safe_to_show ? '安全' : '需复核' }}</a-tag>
            </template>
            <template #prompt="{ record }">
              <a-tag :color="record.allowed_for_prompt ? 'blue' : 'gray'">
                {{ record.allowed_for_prompt ? '允许' : '阻止' }}
              </a-tag>
            </template>
          </a-table>
          <a-empty v-if="!store.loading && contextRows.length === 0" description="暂无 ContextArtifact" />
        </a-card>

        <a-card class="settings-panel retrieval-panel" :bordered="false" data-test="recent-knowledge-retrievals">
          <template #title>最近检索证据</template>
          <a-alert
            v-if="hasStaleRetrievals"
            data-test="stale-retrieval-warning"
            type="warning"
            show-icon
            content="Recent retrieval evidence is older than 24 hours. Refresh before using it for a new review."
          />
          <div v-if="latestRetrievalRows.length > 0" class="retrieval-list">
            <article v-for="retrieval in latestRetrievalRows" :key="retrieval.retrieval_evidence_artifact_id" class="retrieval-item" data-test="recent-knowledge-retrieval-row">
              <div class="retrieval-item__header">
                <div>
                  <span class="muted-label">AI 任务</span>
                  <strong>{{ retrieval.ai_task_id }}</strong>
                </div>
                <a-tag color="blue">{{ retrieval.createdAt }}</a-tag>
              </div>
              <div class="retrieval-terms">
                <span>命中词</span>
                <a-tag v-for="term in retrieval.query_terms" :key="term" color="green">{{ term }}</a-tag>
              </div>
              <a-button data-test="resume-knowledge-retrieval" size="small" @click="resumeRetrieval(retrieval.query_terms)">Reuse query</a-button>
              <div class="retrieval-results">
                <div v-for="result in retrieval.results" :key="result.context_artifact_id" class="retrieval-result">
                  <div class="retrieval-result__meta">
                    <strong>{{ result.title }}</strong>
                    <a-tag color="orange">得分 {{ result.score }}</a-tag>
                  </div>
                  <p>{{ result.snippet }}</p>
                  <div class="retrieval-terms">
                    <span>匹配</span>
                    <a-tag v-for="term in result.matched_terms" :key="term" color="blue">{{ term }}</a-tag>
                  </div>
                </div>
              </div>
            </article>
          </div>
          <a-empty v-else-if="!store.loading" description="暂无 deterministic retrieval evidence" />
        </a-card>

        <a-card class="settings-panel" :bordered="false">
          <template #title>MCP-ready ToolDefinition</template>
          <a-table
            :columns="toolColumns"
            :data="toolRows"
            :pagination="false"
            :scroll="{ x: 920 }"
            row-key="id"
            size="small"
          >
            <template #ready="{ record }">
              <a-tag :color="record.is_mcp_ready ? 'green' : 'gray'">
                {{ record.is_mcp_ready ? '就绪' : '仅结构' }}
              </a-tag>
            </template>
            <template #approval="{ record }">
              <a-tag :color="record.approval_required ? 'orange' : 'blue'">
                {{ record.approval_required ? '需审批' : '已列入白名单' }}
              </a-tag>
            </template>
          </a-table>
          <a-empty v-if="!store.loading && toolRows.length === 0" description="暂无 ToolDefinition" />
        </a-card>
      </div>
    </a-spin>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';

import { useExtensionStore } from '../../stores/extension';

const store = useExtensionStore();

const knowledgeForm = reactive({
  title: 'coupon-api-notes.md',
  sourceRef: 'manual:coupon-api-notes.md',
  artifactType: 'context_markdown' as 'context_markdown' | 'context_text' | 'context_pdf' | 'context_xlsx' | 'context_image',
  content: '# Coupon API Notes\nCoupons are validated before order submit.',
});
const retrievalQuery = ref('coupon expired checkout');
const knowledgeCardQuery = ref('coupon expired checkout');

const emptyAdapter = {
  adapter_name: 'default',
  status: 'not_configured',
  provider_type: 'none',
  retrieval_mode: undefined,
  last_checked_at: null,
  notes: null,
  used_knowledge: false,
};

const adapterState = computed(() => store.knowledgeBase?.knowledge_adapter ?? emptyAdapter);

const contextColumns = [
  { title: '标题', dataIndex: 'title', width: 220 },
  { title: '来源', dataIndex: 'source_ref', width: 260 },
  { title: '文件格式', dataIndex: 'mime_type', width: 150 },
  { title: '展示安全', slotName: 'safe', width: 120 },
  { title: '提示词', slotName: 'prompt', width: 110 },
  { title: '使用次数', dataIndex: 'usage_count', width: 110 },
  { title: '最近使用', dataIndex: 'latestUsedAt', width: 180 },
  { title: '检索次数', dataIndex: 'retrieved_count', width: 110 },
  { title: '最近检索', dataIndex: 'latestRetrievedAt', width: 180 },
];

const toolColumns = [
  { title: '名称', dataIndex: 'name', width: 220 },
  { title: '类型', dataIndex: 'tool_type', width: 150 },
  { title: '风险', dataIndex: 'risk_level', width: 100 },
  { title: '审批', slotName: 'approval', width: 150 },
  { title: 'MCP', slotName: 'ready', width: 110 },
  { title: '能力', dataIndex: 'capability', width: 190 },
];

const contextRows = computed(() =>
  (store.knowledgeBase?.context_artifacts ?? []).map((artifact) => ({
    ...artifact,
    latestUsedAt: artifact.latest_used_at ?? '未使用',
    retrieved_count: artifact.retrieved_count ?? 0,
    latestRetrievedAt: artifact.latest_retrieved_at ?? '未检索',
  })),
);

const latestRetrievalRows = computed(() =>
  store.latestRetrievals.map((retrieval) => ({
    ...retrieval,
    createdAt: retrieval.created_at ?? '未知时间',
    results: retrieval.results ?? [],
  })),
);

const hasStaleRetrievals = computed(() => latestRetrievalRows.value.some((retrieval) => {
  if (!retrieval.created_at) return false;
  return Date.now() - new Date(retrieval.created_at).getTime() > 24 * 60 * 60 * 1000;
}));

const promptEligibleContextArtifactIds = computed(() =>
  contextRows.value.filter((artifact) => artifact.allowed_for_prompt).map((artifact) => artifact.id),
);

const toolRows = computed(() =>
  store.toolDefinitions.map((tool) => ({
    ...tool,
    capability: typeof tool.mcp_metadata.capability_name === 'string' ? tool.mcp_metadata.capability_name : '未声明',
  })),
);

function adapterStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    not_configured: '未配置',
    disabled: '已禁用',
    configured_stub: '已配置占位',
  };
  return labels[status] ?? status;
}

function retrievalModeLabel(mode: string | undefined): string {
  const labels: Record<string, string> = {
    deterministic_local: '确定性本地检索',
  };
  return mode ? (labels[mode] ?? mode) : '未启用检索证据';
}

function cardStatusColor(status: string): string {
  const colors: Record<string, string> = {
    approved: 'green',
    extracted: 'blue',
    stale: 'orange',
    unsafe: 'red',
    duplicate: 'purple',
    archived: 'gray',
  };
  return colors[status] ?? 'gray';
}

function formatSemanticScore(score: number): string {
  return score.toFixed(2);
}

function submitKnowledge() {
  void store.uploadContextArtifact({
    title: knowledgeForm.title,
    sourceRef: knowledgeForm.sourceRef,
    artifactType: knowledgeForm.artifactType,
    content: knowledgeForm.content,
  });
}

async function handleKnowledgeFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) {
    return;
  }
  const extension = file.name.toLowerCase().split('.').pop() ?? '';
  const textExtensions = new Set(['md', 'markdown', 'txt', 'csv', 'json', 'yaml', 'yml']);
  const binaryType = extension === 'pdf' || file.type === 'application/pdf'
    ? 'context_pdf'
    : extension === 'xlsx' || file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ? 'context_xlsx'
      : file.type.startsWith('image/') || ['jpg', 'jpeg', 'png', 'webp', 'tif', 'tiff'].includes(extension)
        ? 'context_image'
        : null;
  if (!textExtensions.has(extension) && !file.type.startsWith('text/') && !binaryType) {
    store.errorMessage = 'Supported formats are Markdown, TXT, CSV, JSON, YAML, PDF, XLSX and common images.';
    input.value = '';
    return;
  }
  knowledgeForm.title = file.name;
  knowledgeForm.sourceRef = `file:${file.name}`;
  if (binaryType) {
    const contentBase64 = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = typeof reader.result === 'string' ? reader.result : '';
        resolve(result.includes(',') ? result.split(',', 2)[1] : result);
      };
      reader.onerror = () => reject(reader.error ?? new Error('Failed to read file.'));
      reader.readAsDataURL(file);
    });
    void store.uploadContextArtifact({
      title: file.name,
      sourceRef: `file:${file.name}`,
      artifactType: binaryType,
      contentBase64,
      mimeType: file.type || (binaryType === 'context_pdf'
        ? 'application/pdf'
        : binaryType === 'context_xlsx'
          ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          : 'image/png'),
      ocrLanguage: 'eng+chi_sim',
    });
    input.value = '';
    return;
  }
  knowledgeForm.artifactType = extension === 'md' || extension === 'markdown' ? 'context_markdown' : 'context_text';
  knowledgeForm.content = await file.text();
}

function submitRetrievalTest() {
  void store.runRetrievalTest(retrievalQuery.value);
}

function resumeRetrieval(queryTerms: string[]) {
  retrievalQuery.value = queryTerms.join(' ');
}

function extractKnowledgeCards() {
  if (promptEligibleContextArtifactIds.value.length === 0) {
    return;
  }
  void store.extractAllKnowledgeCards(promptEligibleContextArtifactIds.value);
}

function submitKnowledgeCardRetrieval() {
  void store.runKnowledgeCardRetrieval(knowledgeCardQuery.value);
}

function reviewKnowledgeCard(cardId: string, status: string) {
  void store.reviewKnowledgeCard(cardId, status);
}

onMounted(() => {
  const resumedQuery = window.sessionStorage.getItem('chtest:knowledge-retrieval-query');
  if (resumedQuery) {
    retrievalQuery.value = resumedQuery;
    window.sessionStorage.removeItem('chtest:knowledge-retrieval-query');
  }
  void store.loadExtensionSurface();
});
</script>

<style scoped>
.adapter-action,
.retrieval-test-results {
  margin-top: 14px;
}

.knowledge-form {
  display: grid;
  gap: 12px;
}

.knowledge-form label {
  display: grid;
  gap: 6px;
  color: #344054;
  font-weight: 700;
}

.knowledge-file-input {
  width: 100%;
  min-height: 34px;
  padding: 6px 8px;
  border: 1px solid #d0d5dd;
  border-radius: 6px;
  background: #fff;
  color: #344054;
}

.retrieval-test-results {
  display: grid;
  gap: 12px;
}

.knowledge-extraction-result,
.knowledge-index-gap-alert,
.knowledge-card-search,
.knowledge-card-retrieval,
.test-knowledge-card-list {
  margin-top: 12px;
}

.knowledge-readiness-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 8px;
  margin-top: 12px;
}

.knowledge-readiness-strip span {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-height: 36px;
  padding: 8px 10px;
  border: 1px solid #dbe6f3;
  border-radius: 6px;
  background: #f8fbff;
  color: #344054;
}

.knowledge-readiness-strip strong {
  color: #1677ff;
}

.knowledge-index-gap-alert {
  padding: 8px 10px;
  border: 1px solid #f2c037;
  border-radius: 6px;
  background: #fff8e6;
  color: #8a5a00;
}

.knowledge-card-search {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
}

.knowledge-card-retrieval {
  display: grid;
  gap: 10px;
}

.test-knowledge-card-list {
  display: grid;
  gap: 10px;
}

.test-knowledge-card {
  padding: 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #ffffff;
}

.test-knowledge-card p {
  margin: 8px 0;
  color: #475569;
  line-height: 1.6;
}

.test-knowledge-card small {
  color: #64748b;
}

.knowledge-card-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.retrieval-result {
  padding: 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.retrieval-result p {
  margin: 8px 0 0;
  color: #475569;
  line-height: 1.6;
}

.retrieval-result__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
</style>
