<template>
  <section class="knowledge-base-page" aria-labelledby="knowledge-base-title" data-test="knowledge-base-page">
    <div class="settings-heading">
      <div>
        <p class="eyebrow">项目知识</p>
        <h2 id="knowledge-base-title">RAG 知识库</h2>
        <p>导入并审核项目知识，让批准后的证据参与需求评审、用例生成和检索。</p>
      </div>
      <a-space>
        <a-tag color="blue">ContextArtifact</a-tag>
        <a-tag color="gray">本地检索</a-tag>
        <a-button type="primary" data-test="open-knowledge-import" @click="openKnowledgeImport">导入文档</a-button>
        <a-button type="primary" :loading="store.loading" @click="store.loadExtensionSurface()">刷新</a-button>
      </a-space>
    </div>

    <div class="knowledge-workflow-rail" data-test="knowledge-workflow-rail" aria-label="知识处理流程">
      <div class="knowledge-workflow-step knowledge-workflow-step--active"><strong>1</strong><span>导入上下文</span><small>文档、截图、接口说明</small></div>
      <span class="knowledge-workflow-arrow">›</span>
      <div class="knowledge-workflow-step"><strong>2</strong><span>抽取知识卡</span><small>把文档变成可审核条目</small></div>
      <span class="knowledge-workflow-arrow">›</span>
      <div class="knowledge-workflow-step"><strong>3</strong><span>审核并允许使用</span><small>只有批准内容进入 AI</small></div>
      <span class="knowledge-workflow-arrow">›</span>
      <div class="knowledge-workflow-step"><strong>4</strong><span>建索引并验证</span><small>检查检索是否命中</small></div>
    </div>

    <a-alert v-if="store.errorMessage" data-test="knowledge-base-error" type="error" :content="store.errorMessage" show-icon />
    <p v-if="store.errorMessage" class="operation-message operation-message--error">{{ store.errorMessage }}</p>
    <a-button v-if="store.errorMessage" data-test="retry-knowledge-base" size="small" @click="store.loadExtensionSurface()">Retry loading</a-button>
    <a-alert v-if="store.successMessage" data-test="knowledge-base-success" type="success" :content="store.successMessage" show-icon />
    <p v-if="store.successMessage" class="operation-message operation-message--success">{{ store.successMessage }}</p>

    <div class="knowledge-metrics">
      <a-card class="settings-panel" :bordered="false">
        <span>上下文工件</span>
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
        <span>测试知识卡</span>
        <strong>{{ store.testKnowledgeCardCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>检索证据</span>
        <strong>{{ store.latestRetrievals.length }}</strong>
      </a-card>
    </div>

    <div class="knowledge-view-switch" data-test="knowledge-view-switch">
      <span>工作区</span>
      <a-space size="mini" wrap>
        <a-button data-test="view-all" size="small" :type="activeKnowledgeView === 'all' ? 'primary' : 'secondary'" @click="activeKnowledgeView = 'all'">总览</a-button>
        <a-button data-test="view-ingestion" size="small" :type="activeKnowledgeView === 'ingestion' ? 'primary' : 'secondary'" @click="activeKnowledgeView = 'ingestion'">导入处理</a-button>
        <a-button data-test="view-cards" size="small" :type="activeKnowledgeView === 'cards' ? 'primary' : 'secondary'" @click="activeKnowledgeView = 'cards'">知识卡</a-button>
        <a-button data-test="view-retrieval" size="small" :type="activeKnowledgeView === 'retrieval' ? 'primary' : 'secondary'" @click="activeKnowledgeView = 'retrieval'">检索记录</a-button>
      </a-space>
    </div>

    <a-spin :loading="store.loading" class="settings-spin">
      <div class="knowledge-grid">
        <a-card class="settings-panel knowledge-adapter-panel" :bordered="false">
          <template #title><span class="step-title"><b>基础设置 <span class="compat-label">KnowledgeAdapter</span></b><small>先启用本地检索，后续评审才会使用知识</small></span></template>
          <div class="adapter-state">
            <div>
              <span>状态</span>
              <strong>{{ adapterStatusLabel(adapterState.status) }}</strong>
            </div>
            <a-tag :color="adapterState.used_knowledge ? 'orange' : 'green'">
              使用知识={{ adapterState.used_knowledge ? '是' : '否' }}
            </a-tag>
          </div>
          <div class="adapter-meta">
            <span>当前模式</span>
            <strong>{{ retrievalModeLabel(adapterState.retrieval_mode) }}</strong>
            <small>{{ adapterState.used_knowledge ? '评审正在使用知识证据' : '导入后可直接参与需求评审' }}</small>
          </div>
          <a-button
            class="adapter-action"
            data-test="enable-local-retrieval"
            :loading="store.loadingMutation"
            @click="store.enableDeterministicRetrieval()"
          >
            启用本地检索
          </a-button>
        </a-card>

        <a-card v-if="activeKnowledgeView === 'all' || activeKnowledgeView === 'ingestion'" id="knowledge-import" class="settings-panel" :bordered="false">
          <template #title><span class="step-title"><b>1. 导入上下文</b><small>上传需求、接口、规则、截图或测试资料</small></span></template>
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
                ref="knowledgeFileInput"
                type="file"
                accept=".md,.markdown,.txt,.csv,.json,.yaml,.yml,.pdf,.xlsx,.jpg,.jpeg,.png,.webp,.tif,.tiff,text/markdown,text/plain,text/csv,application/json,application/yaml,text/yaml,application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,image/*"
                @change="handleKnowledgeFileChange"
              />
            </label>
            <label v-if="!pendingBinaryUpload">
              <span>手动内容格式</span>
              <a-radio-group v-model="knowledgeForm.artifactType">
                <a-radio value="context_markdown">Markdown</a-radio>
                <a-radio value="context_text">TXT</a-radio>
              </a-radio-group>
            </label>
            <div v-else class="detected-file-format" data-test="detected-file-format">
              <span>已识别文件</span>
              <strong>{{ knowledgeForm.title }}</strong>
              <a-tag color="blue">{{ artifactTypeLabel(knowledgeForm.artifactType) }}</a-tag>
            </div>
            <div class="supported-format-list">
              <span>支持格式</span>
              <a-tag>Markdown</a-tag>
              <a-tag>TXT</a-tag>
              <a-tag color="red">PDF</a-tag>
              <a-tag color="green">XLSX</a-tag>
              <a-tag color="orange">图片 OCR</a-tag>
            </div>
            <label v-if="!pendingBinaryUpload">
              <span>内容</span>
              <a-textarea data-test="knowledge-content" v-model="knowledgeForm.content" :auto-size="{ minRows: 5, maxRows: 9 }" />
            </label>
            <a-alert
              v-else
              type="info"
              show-icon
              content="文件会在导入后自动提取文字，再进入知识抽取、审核和索引流程。"
            />
            <a-button data-test="upload-knowledge" html-type="submit" type="primary" :loading="store.loadingMutation">
              导入并自动处理
            </a-button>
            <small class="automation-note">导入后系统会自动抽取、审核高置信知识并建立索引；只有低置信或受限内容需要人工复核。</small>
          </form>
        </a-card>

        <a-card v-if="activeKnowledgeView === 'all' || activeKnowledgeView === 'retrieval'" class="settings-panel retrieval-test-panel" :bordered="false">
          <template #title><span class="step-title"><b>5. 检索验证</b><small>输入真实测试问题，确认 AI 能找到正确知识</small></span></template>
          <form class="knowledge-form" @submit.prevent="submitRetrievalTest">
            <label>
              <span>查询</span>
              <a-textarea data-test="retrieval-query" v-model="retrievalQuery" :auto-size="{ minRows: 3, maxRows: 5 }" />
            </label>
            <a-button data-test="run-retrieval" html-type="submit" type="primary" :loading="store.loadingMutation">
              运行检索验证
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

        <a-card v-if="activeKnowledgeView === 'all' || activeKnowledgeView === 'cards'" class="settings-panel test-knowledge-card-panel" :bordered="false">
          <template #title><span class="step-title"><b>2-4. 知识卡处理</b><small>抽取 → 审核 → 建索引，按顺序完成</small></span></template>
          <a-space>
            <a-button
              data-test="extract-knowledge-cards"
              type="primary"
              :disabled="promptEligibleContextArtifactIds.length === 0"
              :loading="store.loadingMutation"
              @click="extractKnowledgeCards()"
            >
              重新处理未完成文档
            </a-button>
            <a-popconfirm
              content="将删除全部待审核卡并使用新规则重新抽取；已批准和已归档卡会保留。"
              ok-text="重新抽取"
              cancel-text="取消"
              @ok="extractKnowledgeCards(true)"
            >
              <a-button data-test="reextract-knowledge-cards" :disabled="promptEligibleContextArtifactIds.length === 0" :loading="store.loadingMutation">
                清理并重新抽取
              </a-button>
            </a-popconfirm>
            <a-tag color="blue">{{ store.testKnowledgeCardCount }} 张</a-tag>
            <a-button
              data-test="rebuild-knowledge-index"
              :disabled="store.promptReadyKnowledgeCardCount === 0"
              :loading="store.loadingMutation"
              @click="store.rebuildKnowledgeIndex()"
            >
              重建检索索引 <span class="compat-label">Vector Index</span>
            </a-button>
          </a-space>
          <div class="knowledge-card-status-filter" data-test="knowledge-card-status-filter">
            <span>查看列表</span>
            <a-space size="mini" wrap>
              <a-button data-test="filter-extracted-cards" size="small" :aria-pressed="knowledgeCardStatusFilter === 'extracted'" :type="knowledgeCardStatusFilter === 'extracted' ? 'primary' : 'secondary'" @click="knowledgeCardStatusFilter = 'extracted'">
                待审核 {{ extractedCardCount }}
              </a-button>
              <a-button data-test="filter-approved-cards" size="small" :aria-pressed="knowledgeCardStatusFilter === 'approved'" :type="knowledgeCardStatusFilter === 'approved' ? 'primary' : 'secondary'" @click="knowledgeCardStatusFilter = 'approved'">
                已批准 {{ approvedCardCount }}
              </a-button>
              <a-button data-test="filter-archived-cards" size="small" :aria-pressed="knowledgeCardStatusFilter === 'archived'" :type="knowledgeCardStatusFilter === 'archived' ? 'primary' : 'secondary'" @click="knowledgeCardStatusFilter = 'archived'">
                已归档 {{ archivedCardCount }}
              </a-button>
              <a-button data-test="filter-all-cards" size="small" :aria-pressed="knowledgeCardStatusFilter === 'all'" :type="knowledgeCardStatusFilter === 'all' ? 'primary' : 'secondary'" @click="knowledgeCardStatusFilter = 'all'">
                全部 {{ store.testKnowledgeCardCount }}
              </a-button>
            </a-space>
          </div>
          <div class="knowledge-card-bulk-actions" data-test="knowledge-card-bulk-actions">
            <a-checkbox :model-value="allVisibleCardsSelected" @change="toggleVisibleCardSelection">
              选择当前页
            </a-checkbox>
            <span>已选 {{ selectedKnowledgeCardIds.length }} 张</span>
            <a-button size="small" type="primary" :disabled="selectedKnowledgeCardIds.length === 0" :loading="store.loadingMutation" @click="bulkReviewKnowledgeCards('approved')">
              批量批准
            </a-button>
            <a-button size="small" status="danger" :disabled="selectedKnowledgeCardIds.length === 0" :loading="store.loadingMutation" @click="bulkReviewKnowledgeCards('archived')">
              批量归档
            </a-button>
          </div>
          <div class="knowledge-readiness-strip" data-test="knowledge-readiness-strip">
            <span>Approved <strong>{{ store.approvedKnowledgeCardCount }}</strong></span>
            <span>Needs Review <strong>{{ store.pendingKnowledgeCardCount }}</strong></span>
            <span>Prompt Ready <strong>{{ store.promptReadyKnowledgeCardCount }}</strong></span>
            <span>Vector Coverage <strong>{{ Math.round(store.vectorIndexCoverageRatio * 100) }}%</strong></span>
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
          <div v-if="filteredKnowledgeCards.length" class="test-knowledge-card-list">
            <article v-for="card in visibleKnowledgeCards" :key="card.id" class="test-knowledge-card">
              <div class="retrieval-result__meta">
                <div class="knowledge-card-title">
                  <a-checkbox :disabled="card.status !== 'extracted'" :model-value="selectedKnowledgeCardIds.includes(card.id)" @change="toggleKnowledgeCardSelection(card.id)" />
                  <strong>{{ card.title }}</strong>
                </div>
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
            <div v-if="knowledgeCardPageCount > 1" class="knowledge-card-pagination">
              <a-button size="small" :disabled="knowledgeCardPage <= 1" @click="knowledgeCardPage -= 1">上一页</a-button>
              <span>第 {{ knowledgeCardPage }} / {{ knowledgeCardPageCount }} 页，共 {{ filteredKnowledgeCards.length }} 张</span>
              <a-button size="small" :disabled="knowledgeCardPage >= knowledgeCardPageCount" @click="knowledgeCardPage += 1">下一页</a-button>
            </div>
          </div>
          <a-empty v-else description="还没有知识卡。先导入上下文，再点击“从待处理文档抽取”。" />
        </a-card>
      </div>

      <div class="knowledge-grid knowledge-main-grid">
        <a-card v-if="activeKnowledgeView === 'all' || activeKnowledgeView === 'ingestion'" class="settings-panel" :bordered="false">
          <template #title><span class="step-title"><b>上下文清单</b><small>这里查看导入资料是否允许进入 AI</small></span></template>
          <a-table
            :columns="contextColumns"
            :data="contextRows"
            :pagination="false"
            :scroll="{ x: 760 }"
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
            <template #actions="{ record }">
              <a-popconfirm
                :content="`删除“${record.title}”及其自动生成的知识卡？`"
                ok-text="删除"
                cancel-text="取消"
                @ok="store.deleteContextArtifact(record.id, record.title)"
              >
                <a-button data-test="delete-context-artifact" size="mini" status="danger" :loading="store.loadingMutation">
                  删除
                </a-button>
              </a-popconfirm>
            </template>
          </a-table>
          <a-empty v-if="!store.loading && contextRows.length === 0" description="暂无 ContextArtifact" />
        </a-card>

        <a-card v-if="activeKnowledgeView === 'all' || activeKnowledgeView === 'retrieval'" class="settings-panel retrieval-panel" :bordered="false" data-test="recent-knowledge-retrievals">
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
                  <span class="muted-label">检索时间</span>
                  <strong>{{ retrieval.createdAt }}</strong>
                </div>
                <a-tag color="blue">{{ retrieval.snippet_count }} 条证据</a-tag>
              </div>
              <div class="retrieval-terms">
                <span>命中词</span>
                <a-tag v-for="term in retrieval.query_terms" :key="term" color="green">{{ term }}</a-tag>
              </div>
              <a-button data-test="resume-knowledge-retrieval" size="small" @click="resumeRetrieval(retrieval.query_terms)">重新使用查询</a-button>
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
          <a-empty v-else-if="!store.loading" description="暂无检索记录" />
        </a-card>

      </div>
    </a-spin>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue';

import { useExtensionStore } from '../../stores/extension';

const store = useExtensionStore();
const activeKnowledgeView = ref<'all' | 'ingestion' | 'cards' | 'retrieval'>('ingestion');

const knowledgeForm = reactive({
  title: 'coupon-api-notes.md',
  sourceRef: 'manual:coupon-api-notes.md',
  artifactType: 'context_markdown' as 'context_markdown' | 'context_text' | 'context_pdf' | 'context_xlsx' | 'context_image',
  content: '# Coupon API Notes\nCoupons are validated before order submit.',
});
const retrievalQuery = ref('coupon expired checkout');
const knowledgeCardQuery = ref('coupon expired checkout');
const knowledgeCardPage = ref(1);
const knowledgeCardsPageSize = 10;
const knowledgeCardStatusFilter = ref<'all' | 'extracted' | 'approved' | 'archived'>('extracted');
const selectedKnowledgeCardIds = ref<string[]>([]);
const pendingBinaryUpload = ref<{
  contentBase64: string;
  mimeType: string;
  ocrLanguage?: string;
} | null>(null);
const knowledgeFileInput = ref<HTMLInputElement | null>(null);

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
  { title: '文件格式', dataIndex: 'displayMimeType', width: 150 },
  { title: '展示安全', slotName: 'safe', width: 120 },
  { title: '提示词', slotName: 'prompt', width: 110 },
  { title: '检索次数', dataIndex: 'retrieved_count', width: 110 },
  { title: '操作', slotName: 'actions', width: 96, fixed: 'right' as const },
];

const contextRows = computed(() =>
  (store.knowledgeBase?.context_artifacts ?? []).map((artifact) => ({
    ...artifact,
    displayMimeType: artifact.source_mime_type ?? artifact.mime_type,
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

const knowledgeCardPageCount = computed(() =>
  Math.max(1, Math.ceil(filteredKnowledgeCards.value.length / knowledgeCardsPageSize)),
);

const extractedCardCount = computed(() => store.testKnowledgeCards.filter((card) => card.status === 'extracted').length);
const approvedCardCount = computed(() => store.testKnowledgeCards.filter((card) => card.status === 'approved').length);
const archivedCardCount = computed(() => store.testKnowledgeCards.filter((card) => card.status === 'archived').length);

const filteredKnowledgeCards = computed(() =>
  knowledgeCardStatusFilter.value === 'all'
    ? store.testKnowledgeCards
    : store.testKnowledgeCards.filter((card) => card.status === knowledgeCardStatusFilter.value),
);

const visibleKnowledgeCards = computed(() => {
  const page = Math.min(knowledgeCardPage.value, knowledgeCardPageCount.value);
  const start = (page - 1) * knowledgeCardsPageSize;
  return filteredKnowledgeCards.value.slice(start, start + knowledgeCardsPageSize);
});

const selectableVisibleKnowledgeCardIds = computed(() =>
  visibleKnowledgeCards.value.filter((card) => card.status === 'extracted').map((card) => card.id),
);

const allVisibleCardsSelected = computed(() =>
  selectableVisibleKnowledgeCardIds.value.length > 0
  && selectableVisibleKnowledgeCardIds.value.every((cardId) => selectedKnowledgeCardIds.value.includes(cardId)),
);

watch(knowledgeCardStatusFilter, () => {
  knowledgeCardPage.value = 1;
  selectedKnowledgeCardIds.value = [];
});

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

function artifactTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    context_markdown: 'Markdown',
    context_text: 'TXT',
    context_pdf: 'PDF',
    context_xlsx: 'XLSX',
    context_image: '图片 OCR',
  };
  return labels[type] ?? type;
}

async function submitKnowledge() {
  await store.uploadContextArtifact({
    title: knowledgeForm.title,
    sourceRef: knowledgeForm.sourceRef,
    artifactType: knowledgeForm.artifactType,
    ...(pendingBinaryUpload.value
      ? pendingBinaryUpload.value
      : { content: knowledgeForm.content }),
  });
  if (!store.errorMessage) {
    pendingBinaryUpload.value = null;
    selectBestKnowledgeCardStatus();
  }
}

async function openKnowledgeImport() {
  activeKnowledgeView.value = 'ingestion';
  await nextTick();
  document.getElementById('knowledge-import')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  knowledgeFileInput.value?.click();
}

function toggleKnowledgeCardSelection(cardId: string) {
  selectedKnowledgeCardIds.value = selectedKnowledgeCardIds.value.includes(cardId)
    ? selectedKnowledgeCardIds.value.filter((id) => id !== cardId)
    : [...selectedKnowledgeCardIds.value, cardId];
}

function toggleVisibleCardSelection() {
  selectedKnowledgeCardIds.value = allVisibleCardsSelected.value
    ? selectedKnowledgeCardIds.value.filter((id) => !selectableVisibleKnowledgeCardIds.value.includes(id))
    : [...new Set([...selectedKnowledgeCardIds.value, ...selectableVisibleKnowledgeCardIds.value])];
}

async function bulkReviewKnowledgeCards(status: 'approved' | 'archived') {
  const completed = await store.bulkReviewKnowledgeCards(selectedKnowledgeCardIds.value, status);
  if (completed) {
    selectedKnowledgeCardIds.value = [];
    knowledgeCardStatusFilter.value = status;
  }
}

async function handleKnowledgeFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) {
    return;
  }
  pendingBinaryUpload.value = null;
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
    knowledgeForm.artifactType = binaryType;
    knowledgeForm.content = '';
    pendingBinaryUpload.value = {
      contentBase64,
      mimeType: file.type || (binaryType === 'context_pdf'
        ? 'application/pdf'
        : binaryType === 'context_xlsx'
          ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          : 'image/png'),
      ...(binaryType === 'context_image' ? { ocrLanguage: 'eng+chi_sim' } : {}),
    };
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

async function extractKnowledgeCards(replaceUnreviewed = false) {
  if (promptEligibleContextArtifactIds.value.length === 0) {
    return;
  }
  await store.extractAllKnowledgeCards(promptEligibleContextArtifactIds.value, replaceUnreviewed);
  if (!store.errorMessage) selectBestKnowledgeCardStatus();
}

function selectBestKnowledgeCardStatus() {
  knowledgeCardStatusFilter.value = extractedCardCount.value > 0
    ? 'extracted'
    : approvedCardCount.value > 0
      ? 'approved'
      : archivedCardCount.value > 0
        ? 'archived'
        : 'all';
}

function submitKnowledgeCardRetrieval() {
  void store.runKnowledgeCardRetrieval(knowledgeCardQuery.value);
}

function reviewKnowledgeCard(cardId: string, status: string) {
  void store.reviewKnowledgeCard(cardId, status);
}

onMounted(async () => {
  const resumedQuery = window.sessionStorage.getItem('chtest:knowledge-retrieval-query');
  if (resumedQuery) {
    retrievalQuery.value = resumedQuery;
    window.sessionStorage.removeItem('chtest:knowledge-retrieval-query');
  }
  await store.loadExtensionSurface();
  selectBestKnowledgeCardStatus();
});
</script>

<style scoped>
.adapter-action,
.retrieval-test-results {
  margin-top: 14px;
}

.knowledge-workflow-rail {
  display: flex;
  align-items: stretch;
  gap: 10px;
  padding: 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #ffffff;
}

.knowledge-workflow-step {
  display: grid;
  grid-template-columns: 26px 1fr;
  column-gap: 8px;
  align-items: center;
  flex: 1;
  min-width: 0;
  color: #667085;
}

.knowledge-workflow-step strong {
  display: grid;
  grid-row: span 2;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  color: #475467;
  background: #eef2f6;
}

.knowledge-workflow-step span {
  font-weight: 700;
  color: #344054;
}

.knowledge-workflow-step small {
  overflow: hidden;
  color: #98a2b3;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.knowledge-workflow-step--active strong {
  color: #ffffff;
  background: #2563eb;
}

.knowledge-workflow-arrow {
  align-self: center;
  color: #98a2b3;
  font-size: 22px;
}

.step-title {
  display: grid;
  gap: 3px;
}

.step-title small {
  color: #98a2b3;
  font-size: 11px;
  font-weight: 400;
}

.compat-label {
  color: #98a2b3;
  font-size: 11px;
  font-weight: 400;
}

.knowledge-form {
  display: grid;
  gap: 12px;
}

.adapter-meta {
  display: grid;
  gap: 4px;
  padding: 12px 0;
}

.adapter-meta span,
.adapter-meta small {
  color: #667085;
}

.adapter-meta strong {
  color: #101828;
  font-size: 16px;
}

.knowledge-form label {
  display: grid;
  gap: 6px;
  color: #344054;
  font-weight: 700;
}

.automation-note {
  color: #667085;
  font-size: 12px;
  line-height: 1.6;
}

.supported-format-list,
.detected-file-format {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.supported-format-list > span,
.detected-file-format > span {
  margin-right: 4px;
  color: #667085;
  font-size: 12px;
}

.detected-file-format strong {
  overflow-wrap: anywhere;
  color: #344054;
  font-size: 13px;
}

@media (max-width: 860px) {
  .knowledge-workflow-rail {
    align-items: flex-start;
    flex-direction: column;
  }

  .knowledge-workflow-step {
    width: 100%;
  }

  .knowledge-workflow-arrow {
    display: none;
  }
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

.knowledge-card-pagination {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 8px;
}

.knowledge-card-pagination span {
  color: #667085;
  font-size: 12px;
}

.knowledge-card-status-filter {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.knowledge-view-switch {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.knowledge-view-switch > span {
  color: #667085;
  font-size: 12px;
  font-weight: 700;
}

.knowledge-card-status-filter > span {
  color: #667085;
  font-size: 12px;
  font-weight: 600;
}

.knowledge-card-bulk-actions {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 0;
}

.knowledge-card-bulk-actions > span {
  color: #667085;
  font-size: 12px;
}

.knowledge-card-title {
  align-items: flex-start;
  display: flex;
  gap: 8px;
  min-width: 0;
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
