<template>
  <section class="case-review-page" aria-labelledby="case-review-title" data-test="case-generation-review-page">
    <div class="case-review-heading">
      <div>
        <p class="eyebrow">用例评审</p>
        <h2 id="case-review-title">用例生成评审</h2>
        <p>从已评审需求生成候选用例，逐条检查步骤、预期结果和 AI 理由，再决定是否进入正式用例库。</p>
      </div>
      <a-space>
        <a-tag color="blue">模拟 CaseGenerationAgent</a-tag>
        <a-tag color="green">评审后入库</a-tag>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" data-test="case-generation-error" type="error" :content="store.errorMessage" show-icon />

    <div class="case-review-layout">
      <a-card class="case-panel generation-entry-panel" :bordered="false">
        <template #title>生成入口</template>
        <form class="case-generation-form" @submit.prevent="submitGeneration">
          <label class="document-selector">
            <span>需求文档</span>
            <a-select
              v-model="form.requirementDocumentArtifactId"
              placeholder="选择正式需求文档"
              allow-clear
              @change="selectRequirementDocument"
            >
              <a-option
                v-for="document in store.requirementDocuments"
                :key="document.artifact_id"
                :value="document.artifact_id"
              >
                {{ document.document_number }} · {{ document.title }}
              </a-option>
            </a-select>
          </label>
          <div v-if="selectedRequirementDocument" class="document-source">
            <strong>{{ selectedRequirementDocument.document_number }}</strong>
            <span>{{ selectedRequirementDocument.title }} · {{ selectedRequirementDocument.status }}</span>
            <a :href="selectedRequirementDocument.download_url">下载 Markdown</a>
          </div>
          <label class="advanced-source-id">
            <span>需求 ID（高级）</span>
            <a-input data-test="requirement-id-input" v-model="form.requirementId" />
          </label>
          <label class="advanced-source-id">
            <span>评审 ID（高级）</span>
            <a-input data-test="requirement-review-id-input" v-model="form.requirementReviewId" />
          </label>
          <label class="target-types-field">
            <span>目标测试类型</span>
            <a-input v-model="targetTypesText" />
          </label>
          <label class="context-field">
            <span>ContextArtifact ID 列表</span>
            <a-input v-model="contextIdsText" placeholder="多个 ID 用逗号分隔" />
          </label>
          <p v-if="!hasGenerationSource" class="source-hint">请先完成需求评审，或选择一份正式需求文档。</p>
          <div class="decision-table-gate" data-test="decision-table-gate">
            <strong>生成前决策表确认</strong>
            <a-checkbox v-model="decisionTableGate.sourceConfirmed" data-test="decision-source-confirmed">
              需求文档或评审结论已确认
            </a-checkbox>
            <a-checkbox v-model="decisionTableGate.riskDimensionsConfirmed" data-test="decision-risk-confirmed">
              {{ reviewScopeConfirmationLabel }}
            </a-checkbox>
            <a-checkbox v-model="decisionTableGate.reviewReady" data-test="decision-review-ready">
              生成结果将按覆盖矩阵逐条评审后再入库
            </a-checkbox>
          </div>
          <p v-if="hasGenerationSource && !decisionTableReady" class="source-hint">
            请先确认生成前决策表，避免直接把未澄清需求送入最终用例生成。
          </p>
          <a-button
            data-test="start-case-generation"
            class="generation-submit"
            html-type="submit"
            type="primary"
            :disabled="!decisionTableReady"
            :loading="store.loadingGeneration"
          >
            开始生成候选用例
          </a-button>
        </form>

        <div class="case-generation-summary">
          <a-statistic title="候选总数" :value="store.totalCandidates" />
          <div class="generation-status">
            <span>当前任务</span>
            <strong>{{ generationStatusLabel }}</strong>
          </div>
        </div>

        <div v-if="store.generation || store.generationTask" class="generation-task-panel" data-test="recent-generation-run">
          <div>
            <span>CaseGenerationTask</span>
            <strong>{{ store.generationTask?.id ?? store.generation?.case_generation_task_id }}</strong>
          </div>
          <div>
            <span>AITask</span>
            <strong>{{ store.generationTask?.ai_task_id ?? store.generation?.ai_task_id }}</strong>
          </div>
          <div>
            <span>AI 状态</span>
            <strong>{{ store.generationTask?.ai_task_status ?? store.generation?.status }}</strong>
          </div>
          <a-alert
            v-if="store.generationTask?.error_message"
            type="error"
            :content="store.generationTask.error_message"
            show-icon
          />
          <p v-if="store.generationTask?.error_code" class="generation-error-line">
            {{ store.generationTask.error_code }} · {{ store.generationTask.error_message ?? '任务失败' }}
          </p>
          <a-alert
            v-if="isGenerationTaskStale"
            data-test="stale-generation-warning"
            type="warning"
            show-icon
            content="This generation run is older than 24 hours. Confirm the requirement context before continuing review."
          />
          <a-button
            v-if="store.candidates.length"
            data-test="resume-generation-review"
            size="small"
            @click="resumeGenerationReview"
          >
            Resume review
          </a-button>
        </div>

        <div v-if="store.metrics" class="case-metrics-strip" aria-label="批次指标">
          <span class="metrics-strip-title">批次指标</span>
          <div v-for="metric in metricItems" :key="metric.label" class="metric-item">
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
          </div>
        </div>

        <div v-if="store.candidates.length > 0" class="coverage-matrix" aria-label="测试覆盖矩阵">
          <div class="coverage-matrix-heading">
            <strong>测试维度覆盖</strong>
            <span>{{ coveredDimensionCount }}/{{ coverageDimensions.length }}</span>
          </div>
          <div class="coverage-grid">
            <div
              v-for="dimension in coverageDimensions"
              :key="dimension.key"
              class="coverage-cell"
              :class="{ covered: dimension.covered }"
            >
              <strong>{{ dimension.label }}</strong>
              <span>{{ dimension.covered ? '已覆盖' : dimension.hint }}</span>
            </div>
          </div>
        </div>
      </a-card>

      <a-card class="case-panel candidate-list-panel" :bordered="false">
        <template #title>候选用例</template>
        <a-spin :loading="store.loadingGeneration">
          <a-list v-if="store.candidates.length > 0" :data="store.candidates" :bordered="false">
            <template #item="{ item }">
              <a-list-item
                data-test="candidate-list-item"
                class="candidate-list-item"
                :class="{ active: item.id === store.selectedCandidateId }"
                @click="selectCandidate(item.id)"
              >
                <a-space direction="vertical" size="mini">
                  <strong>{{ item.title }}</strong>
                  <span>{{ item.ai_reason }}</span>
                  <a-space>
                    <a-tag color="red">{{ priorityLabel(item.priority) }}</a-tag>
                    <a-tag color="blue">{{ testTypeLabel(item.test_type) }}</a-tag>
                    <a-tag>{{ candidateStatusLabel(item.status) }}</a-tag>
                  </a-space>
                </a-space>
              </a-list-item>
            </template>
          </a-list>
          <a-empty v-else-if="!store.loadingGeneration" description="生成后展示候选用例" />
        </a-spin>
      </a-card>

      <a-card class="case-panel candidate-detail-panel" :bordered="false">
        <template #title>候选详情与评审动作</template>
        <template v-if="store.selectedCandidate">
          <a-descriptions :column="2" bordered size="small">
            <a-descriptions-item label="标题">{{ store.selectedCandidate.title }}</a-descriptions-item>
            <a-descriptions-item label="状态">{{ candidateStatusLabel(store.selectedCandidate.status) }}</a-descriptions-item>
            <a-descriptions-item label="优先级">{{ priorityLabel(store.selectedCandidate.priority) }}</a-descriptions-item>
            <a-descriptions-item label="类型">{{ testTypeLabel(store.selectedCandidate.test_type) }}</a-descriptions-item>
            <a-descriptions-item label="前置条件" :span="2">
              {{ store.selectedCandidate.precondition ?? '无' }}
            </a-descriptions-item>
            <a-descriptions-item label="需求引用" :span="2">
              {{ listText(store.selectedCandidate.requirement_refs) }}
            </a-descriptions-item>
          </a-descriptions>

          <div class="candidate-evidence-grid">
            <section>
              <h3>步骤</h3>
              <ol>
                <li v-for="step in store.selectedCandidate.steps" :key="step">{{ step }}</li>
              </ol>
            </section>
            <section>
              <h3>预期结果</h3>
              <ol>
                <li v-for="result in store.selectedCandidate.expected_results" :key="result">{{ result }}</li>
              </ol>
            </section>
            <section v-if="(store.selectedCandidate.source_knowledge_evidence ?? []).length">
              <h3>知识证据</h3>
              <ol>
                <li v-for="evidence in store.selectedCandidate.source_knowledge_evidence ?? []" :key="String(evidence.evidence_id)">
                  {{ evidenceTitle(evidence) }}
                </li>
              </ol>
            </section>
          </div>

          <section v-if="(store.selectedCandidate.coverage_dimensions ?? []).length" class="candidate-coverage-panel">
            <h3>覆盖维度</h3>
            <ol>
              <li v-for="dimension in store.selectedCandidate.coverage_dimensions ?? []" :key="dimension.key">
                {{ dimension.label }}：{{ dimension.evidence || dimension.source || '已覆盖' }}
              </li>
            </ol>
          </section>

          <form class="candidate-edit-form" data-test="candidate-edit-form" @submit.prevent>
            <h3>评审编辑</h3>
            <label>
              <span>标题</span>
              <a-input data-test="edit-case-title" v-model="editForm.title" />
            </label>
            <label>
              <span>优先级</span>
              <a-input v-model="editForm.priority" />
            </label>
            <label>
              <span>类型</span>
              <a-input v-model="editForm.testType" />
            </label>
            <label>
              <span>前置条件</span>
              <a-textarea v-model="editForm.precondition" :auto-size="{ minRows: 2, maxRows: 4 }" />
            </label>
            <label>
              <span>步骤（每行一条）</span>
              <a-textarea data-test="edit-case-steps" v-model="editForm.stepsText" :auto-size="{ minRows: 4, maxRows: 8 }" />
            </label>
            <label>
              <span>预期结果（每行一条）</span>
              <a-textarea
                data-test="edit-case-expected-results"
                v-model="editForm.expectedResultsText"
                :auto-size="{ minRows: 4, maxRows: 8 }"
              />
            </label>
            <label>
              <span>输入数据 JSON</span>
              <a-textarea v-model="editForm.inputDataJson" :auto-size="{ minRows: 3, maxRows: 6 }" />
            </label>
            <label>
              <span>标签（逗号分隔）</span>
              <a-input v-model="editForm.tagsText" />
            </label>
          </form>

          <a-space class="review-actions" wrap>
            <a-button type="primary" :loading="store.loadingReview" @click="review('approve')">通过</a-button>
            <a-button data-test="approve-after-edit" :loading="store.loadingReview" @click="review('approve_after_edit')">
              编辑后通过
            </a-button>
            <a-button status="warning" :loading="store.loadingReview" @click="review('needs_optimization')">需要优化</a-button>
            <a-button status="danger" :loading="store.loadingReview" @click="review('reject')">拒绝</a-button>
          </a-space>

          <div v-if="currentLastReview" data-test="review-result" class="review-result">
            <span>评审结果：{{ reviewStatusLabel(currentLastReview.status) }}</span>
            <strong>TestCase：{{ currentLastReview.test_case_id ?? '未创建' }}</strong>
          </div>
          <section
            v-if="currentReviewHistory.length"
            data-test="review-history"
            class="review-history-panel"
            aria-label="本地评审历史"
          >
            <h3>本地评审历史</h3>
            <div v-for="item in currentReviewHistory" :key="item.id" class="review-history-item">
              <strong>{{ actionLabel(item.action) }}</strong>
              <span>{{ item.reviewer }} · {{ statusTransition(item.from_status, item.to_status) }}</span>
              <small>{{ formatDateTime(item.created_at) }} · {{ item.comment || '无评审备注' }} · 证据 {{ item.evidence_artifact_ids.length }}</small>
            </div>
          </section>
          <a-alert
            v-if="currentLastReview"
            class="review-result-alert"
            type="success"
            content="候选用例评审动作已提交"
            show-icon
          />
        </template>

        <a-empty v-else description="请选择候选用例" />
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import type { CaseReviewAction, CaseReviewEditedCase, GeneratedCaseCandidateListItem } from '../../api/cases';
import { useCasesStore } from '../../stores/cases';

const store = useCasesStore();

const form = reactive({
  requirementId: store.requirementId,
  requirementReviewId: store.requirementReviewId,
  requirementDocumentArtifactId: store.requirementDocumentArtifactId,
});
const targetTypesText = ref('functional, ui');
const contextIdsText = ref('');
const editForm = reactive({
  title: '',
  priority: '',
  testType: '',
  precondition: '',
  stepsText: '',
  expectedResultsText: '',
  inputDataJson: '{}',
  tagsText: 'ai-generated, reviewed',
});
const decisionTableGate = reactive({
  sourceConfirmed: false,
  riskDimensionsConfirmed: false,
  reviewReady: false,
});

const selectedRequirementDocument = computed(() =>
  store.requirementDocuments.find((document) => document.artifact_id === form.requirementDocumentArtifactId) ?? null,
);

const hasGenerationSource = computed(() => Boolean(form.requirementId && form.requirementReviewId));
const currentLastReview = computed(() =>
  store.lastReviewCandidateId === store.selectedCandidate?.id ? store.lastReview : null,
);
const currentReviewHistory = computed(() => store.reviewHistory);
const generationStatusLabel = computed(
  () => store.generationTask?.status ?? store.generation?.status ?? '未生成',
);
const isGenerationTaskStale = computed(() => {
  const updatedAt = store.generationTask?.updated_at;
  return Boolean(updatedAt && Date.now() - new Date(updatedAt).getTime() > 24 * 60 * 60 * 1000);
});
const decisionTableReady = computed(
  () => decisionTableGate.sourceConfirmed && decisionTableGate.riskDimensionsConfirmed && decisionTableGate.reviewReady,
);
const reviewScopeConfirmationLabel = computed(() => {
  const riskTitles = store.requirementRiskTitles.filter(Boolean).slice(0, 4);
  const riskSummary = riskTitles.length > 0 ? `风险：${riskTitles.join('、')}` : '当前评审识别的风险';
  const clarificationSummary = store.requirementClarificationQuestions.length
    ? `，以及 ${store.requirementClarificationQuestions.length} 个待澄清项`
    : '';
  return `${riskSummary}${clarificationSummary}已纳入本次生成范围`;
});
const generationSourceKey = computed(
  () => `${form.requirementId}|${form.requirementReviewId}|${form.requirementDocumentArtifactId}`,
);
const coverageDimensions = computed(() => buildCoverageDimensions(store.candidates));
const coveredDimensionCount = computed(() => coverageDimensions.value.filter((dimension) => dimension.covered).length);

interface CoverageDimension {
  readonly key: string;
  readonly label: string;
  readonly hint: string;
  readonly covered: boolean;
}

const coverageDimensionRules = [
  { key: 'positive', label: '主流程', hint: '缺少成功路径', keywords: ['成功', '有效', '正常', '可用', '启动', '创建'] },
  { key: 'negative', label: '异常/负向', hint: '缺少失败与拦截', keywords: ['失败', '不可', '拒绝', '错误', '阻止', '无效'] },
  { key: 'boundary', label: '边界值', hint: '缺少数值、时间或容量边界', keywords: ['边界', '最大', '最小', '超过', '等于', '为空', '限制', 'limit'] },
  { key: 'state', label: '状态转换', hint: '缺少生命周期和状态变化', keywords: ['状态', '开始', '结束', '执行', '等待', '创建', '删除', '修改', '暂停'] },
  { key: 'permission', label: '权限', hint: '缺少角色与授权覆盖', keywords: ['权限', '角色', '授权', '越权', '只读'] },
  { key: 'channel', label: '接口/链路', hint: '缺少接口、网络或集成链路覆盖', keywords: ['接口', '网络', '通道', '同步', '下发', '离线', '超时'] },
  { key: 'condition', label: '外部条件', hint: '缺少依赖和外部条件覆盖', keywords: ['依赖', '前置', '条件', '配置', '环境', '版本', '服务'] },
  { key: 'risk', label: '风险引用', hint: '缺少风险引用', keywords: [] },
] as const;

function commaList(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function lineList(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function buildCoverageDimensions(candidates: GeneratedCaseCandidateListItem[]): CoverageDimension[] {
  const coveredKeys = new Map<string, string>();
  for (const candidate of candidates) {
    for (const dimension of candidate.coverage_dimensions ?? []) {
      if (!coveredKeys.has(dimension.key)) {
        coveredKeys.set(dimension.key, dimension.evidence ?? dimension.source ?? '');
      }
    }
  }
  return coverageDimensionRules.map((rule) => {
    const covered = coveredKeys.has(rule.key);
    return {
      key: rule.key,
      label: rule.label,
      hint: coveredKeys.get(rule.key) || rule.hint,
      covered,
    };
  });
}

function resetDecisionTableGate() {
  decisionTableGate.sourceConfirmed = false;
  decisionTableGate.riskDimensionsConfirmed = false;
  decisionTableGate.reviewReady = false;
}

function listText(items: string[]): string {
  return items.length > 0 ? items.join(', ') : '无';
}

function populateEditForm(candidate: GeneratedCaseCandidateListItem | null) {
  editForm.title = candidate?.title ?? '';
  editForm.priority = candidate?.priority ?? '';
  editForm.testType = candidate?.test_type ?? '';
  editForm.precondition = candidate?.precondition ?? '';
  editForm.stepsText = candidate?.steps.join('\n') ?? '';
  editForm.expectedResultsText = candidate?.expected_results.join('\n') ?? '';
  editForm.inputDataJson = JSON.stringify(candidate?.input_data ?? {}, null, 2);
  editForm.tagsText = 'ai-generated, reviewed';
}

function editedCaseFromForm(): CaseReviewEditedCase | null {
  const title = editForm.title.trim();
  const steps = lineList(editForm.stepsText);
  const expectedResults = lineList(editForm.expectedResultsText);
  if (!title || steps.length === 0 || expectedResults.length === 0) {
    store.errorMessage = '编辑后的用例必须包含标题、步骤和预期结果';
    return null;
  }
  let inputData: Record<string, unknown>;
  try {
    const parsed = JSON.parse(editForm.inputDataJson || '{}') as unknown;
    inputData = parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? (parsed as Record<string, unknown>) : {};
  } catch {
    store.errorMessage = '输入数据 JSON 格式不正确';
    return null;
  }
  return {
    title,
    priority: editForm.priority.trim() || 'P2',
    test_type: editForm.testType.trim() || 'functional',
    precondition: editForm.precondition.trim() || null,
    steps,
    expected_results: expectedResults,
    input_data: inputData,
    tags: commaList(editForm.tagsText),
  };
}

function evidenceTitle(evidence: Record<string, unknown>): string {
  const title = typeof evidence.title === 'string' ? evidence.title : 'KnowledgeEvidence';
  const score = typeof evidence.score === 'number' ? evidence.score : 0;
  return `${title} · score ${score}`;
}

function formatRate(value: number | undefined): string {
  return `${Math.round((value ?? 0) * 100)}%`;
}

const metricItems = computed(() => {
  const metrics = store.metrics;
  if (!metrics) {
    return [];
  }
  return [
    { label: '生成总数', value: String(metrics.generated_count) },
    { label: '直接通过', value: String(metrics.approved_count) },
    { label: '拒绝', value: String(metrics.rejected_count) },
    { label: '采纳率', value: formatRate(metrics.acceptance_rate) },
    { label: '编辑率', value: formatRate(metrics.edit_rate) },
    { label: '评审进度', value: formatRate(metrics.review_progress) },
    { label: '字段完整率', value: formatRate(metrics.field_complete_rate) },
  ];
});

function submitGeneration() {
  if (!hasGenerationSource.value) {
    store.errorMessage = '请先选择已评审需求或正式需求文档';
    return;
  }
  if (!decisionTableReady.value) {
    store.errorMessage = '请先确认生成前决策表。';
    return;
  }
  void store.generateCandidates({
    requirementId: form.requirementId,
    requirementReviewId: form.requirementReviewId,
    requirementDocumentArtifactId: form.requirementDocumentArtifactId,
    targetTestTypes: commaList(targetTypesText.value),
    contextArtifactIds: commaList(contextIdsText.value),
    decisionTableAcknowledged: decisionTableReady.value,
  });
}

function syncLatestRequirementReviewContext() {
  if (!store.loadLatestRequirementReviewContext()) {
    return;
  }
  form.requirementId = store.requirementId;
  form.requirementReviewId = store.requirementReviewId;
  form.requirementDocumentArtifactId = store.requirementDocumentArtifactId;
}

function selectRequirementDocument(value: unknown) {
  if (typeof value !== 'string' || !value) {
    store.clearRequirementDocumentSelection();
    form.requirementId = store.requirementId;
    form.requirementReviewId = store.requirementReviewId;
    form.requirementDocumentArtifactId = '';
    return;
  }
  if (!store.selectRequirementDocument(value)) {
    return;
  }
  form.requirementId = store.requirementId;
  form.requirementReviewId = store.requirementReviewId;
  form.requirementDocumentArtifactId = store.requirementDocumentArtifactId;
}

function selectCandidate(candidateId: string) {
  void store.selectCandidate(candidateId);
}

function resumeGenerationReview() {
  const candidateId = store.selectedCandidateId || store.candidates[0]?.id;
  if (candidateId) void store.selectCandidate(candidateId);
}

function review(action: CaseReviewAction) {
  if (action === 'approve_after_edit') {
    const editedCase = editedCaseFromForm();
    if (!editedCase) {
      return;
    }
    void store.reviewSelectedCandidate(action, '前端评审编辑后通过', editedCase);
    return;
  }
  void store.reviewSelectedCandidate(action, '前端评审动作');
}

function priorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    p0: 'P0',
    p1: 'P1',
    p2: 'P2',
    high: '高',
    medium: '中',
    low: '低',
  };
  return labels[priority] ?? priority;
}

function testTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    functional: '功能',
    ui: '界面',
    api: '接口',
    regression: '回归',
  };
  return labels[type] ?? type;
}

function candidateStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    generated: '已生成',
    approved: '已通过',
    approved_after_edit: '编辑后通过',
    rejected: '已拒绝',
    needs_optimization: '需要优化',
    unknown: '未知',
  };
  return labels[status] ?? status;
}

function reviewStatusLabel(status: string): string {
  return candidateStatusLabel(status);
}

function actionLabel(action: string): string {
  const labels: Record<string, string> = {
    approve: '通过',
    approve_after_edit: '编辑后通过',
    reject: '拒绝',
    edit: '编辑',
    compute_quality_gate: '计算门禁',
  };
  return labels[action] ?? action;
}

function statusTransition(fromStatus: string | null, toStatus: string | null): string {
  return `${reviewStatusLabel(fromStatus ?? 'unknown')} -> ${reviewStatusLabel(toStatus ?? 'unknown')}`;
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

onMounted(async () => {
  await store.loadGenerationSource();
  await store.loadRequirementDocuments();
  form.requirementId = store.requirementId;
  form.requirementReviewId = store.requirementReviewId;
  form.requirementDocumentArtifactId = store.requirementDocumentArtifactId;
});

watch(
  () => store.selectedCandidate,
  (candidate) => {
    populateEditForm(candidate);
  },
  { immediate: true },
);

watch(generationSourceKey, resetDecisionTableGate);
</script>

<style scoped>
.case-review-page {
  display: grid;
  gap: 18px;
}

.case-review-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.case-review-heading h2,
.case-review-heading p {
  margin: 0;
}

.case-review-heading h2 {
  font-size: 26px;
}

.case-review-heading p:not(.eyebrow) {
  margin-top: 10px;
  max-width: 780px;
  color: #5b6472;
  line-height: 1.7;
}

.case-review-layout {
  display: grid;
  grid-template-columns: minmax(300px, 0.82fr) minmax(0, 1.58fr);
  gap: 16px;
  align-items: start;
}

.case-panel {
  border-radius: 8px;
}

.generation-entry-panel {
  grid-column: 1 / -1;
}

.case-generation-form {
  display: grid;
  grid-template-columns: minmax(320px, 1.9fr) minmax(150px, 0.85fr) minmax(190px, 1fr) max-content;
  align-items: end;
  gap: 14px;
}

.case-generation-form label {
  display: grid;
  gap: 7px;
  min-width: 0;
  color: #344054;
  font-weight: 700;
}

.document-selector {
  order: 1;
}

.target-types-field {
  order: 2;
}

.context-field {
  order: 3;
}

.generation-submit {
  order: 4;
}

.document-source {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 12px;
  order: 5;
  padding: 10px 12px;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  background: #f0fdf4;
}

.document-source,
.decision-table-gate,
.case-generation-form .source-hint {
  grid-column: 1 / -1;
}

.generation-submit {
  min-height: 32px;
  align-self: end;
}

.advanced-source-id {
  grid-column: span 2;
  order: 6;
}

.case-generation-form .source-hint {
  order: 7;
}

.document-source strong {
  overflow-wrap: anywhere;
}

.document-source span {
  color: #64748b;
}

.decision-table-gate {
  display: grid;
  grid-template-columns: minmax(140px, 0.55fr) repeat(3, minmax(180px, 1fr));
  gap: 10px;
  order: 5;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.decision-table-gate strong {
  color: #0f172a;
}

.source-hint {
  margin: 0;
  color: #b45309;
  font-weight: 700;
}

.case-generation-summary {
  display: grid;
  grid-template-columns: minmax(180px, 0.28fr) minmax(180px, 0.28fr);
  gap: 12px;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid #e5eaf2;
}

.generation-status {
  display: grid;
  align-content: center;
  min-height: 72px;
}

.generation-status span,
.generation-status strong,
.review-result span,
.review-result strong {
  display: block;
}

.generation-status span,
.review-result span {
  color: #64748b;
}

.generation-status strong {
  margin-top: 6px;
  font-size: 20px;
}

.generation-task-panel {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.generation-task-panel > div {
  display: grid;
  gap: 4px;
  min-width: 0;
  padding: 10px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.generation-task-panel span {
  color: #64748b;
  font-size: 12px;
}

.generation-task-panel strong {
  overflow-wrap: anywhere;
  color: #0f172a;
  font-size: 13px;
}

.generation-task-panel .arco-alert {
  grid-column: 1 / -1;
}

.generation-error-line {
  grid-column: 1 / -1;
  margin: 0;
  color: #b91c1c;
  font-weight: 700;
  overflow-wrap: anywhere;
}

.case-metrics-strip {
  display: grid;
  grid-template-columns: repeat(7, minmax(90px, 1fr));
  gap: 10px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5eaf2;
}

.metrics-strip-title {
  grid-column: 1 / -1;
  color: #475569;
  font-weight: 700;
}

.candidate-list-panel,
.candidate-detail-panel {
  min-width: 0;
}

.metric-item {
  display: grid;
  gap: 4px;
  min-height: 58px;
  padding: 10px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.metric-item span {
  color: #64748b;
  font-size: 12px;
}

.metric-item strong {
  color: #0f172a;
  font-size: 18px;
}

.coverage-matrix {
  display: grid;
  gap: 10px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5eaf2;
}

.coverage-matrix-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #475569;
}

.coverage-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.coverage-cell {
  display: grid;
  gap: 4px;
  min-height: 62px;
  padding: 10px;
  border: 1px solid #fed7aa;
  border-radius: 8px;
  background: #fff7ed;
}

.coverage-cell.covered {
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.coverage-cell span {
  color: #64748b;
  font-size: 12px;
}

.candidate-list-item {
  cursor: pointer;
  border-radius: 8px;
}

.candidate-list-item.active {
  background: #eff6ff;
}

.candidate-list-item span {
  color: #5b6472;
}

.candidate-evidence-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.candidate-evidence-grid section {
  padding: 14px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.candidate-evidence-grid h3 {
  margin: 0 0 10px;
  font-size: 16px;
}

.candidate-evidence-grid ol {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 18px;
}

.candidate-coverage-panel {
  display: grid;
  gap: 8px;
  margin-top: 18px;
  padding: 14px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.candidate-coverage-panel h3,
.candidate-coverage-panel ol {
  margin: 0;
}

.candidate-coverage-panel ol {
  display: grid;
  gap: 8px;
  padding-left: 18px;
}

.candidate-coverage-panel li {
  color: #344054;
}

.candidate-edit-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
  padding: 14px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #ffffff;
}

.candidate-edit-form h3 {
  grid-column: 1 / -1;
  margin: 0;
  font-size: 16px;
}

.candidate-edit-form label {
  display: grid;
  gap: 7px;
  min-width: 0;
  color: #344054;
  font-weight: 700;
}

.candidate-edit-form label:nth-of-type(n + 4) {
  grid-column: 1 / -1;
}

.review-actions,
.review-result,
.review-result-alert {
  margin-top: 16px;
}

.review-result {
  padding: 12px;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  background: #f0fdf4;
}

.review-result strong {
  margin-top: 6px;
  color: #166534;
}

.review-history-panel {
  display: grid;
  gap: 8px;
  margin-top: 16px;
}

.review-history-panel h3 {
  margin: 0;
  font-size: 16px;
}

.review-history-item {
  display: grid;
  gap: 4px;
  padding: 10px 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #ffffff;
}

.review-history-item span,
.review-history-item small {
  color: #64748b;
}

@media (max-width: 1180px) {
  .case-review-layout,
  .case-generation-form,
  .decision-table-gate,
  .generation-task-panel,
  .coverage-grid,
  .candidate-evidence-grid,
  .candidate-edit-form {
    grid-template-columns: 1fr;
  }

  .generation-entry-panel,
  .document-source,
  .advanced-source-id,
  .case-generation-form .source-hint,
  .candidate-edit-form h3,
  .candidate-edit-form label:nth-of-type(n + 4) {
    grid-column: auto;
  }
}
</style>
