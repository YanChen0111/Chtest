<template>
  <section class="case-review-page" aria-labelledby="case-review-title">
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

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <div class="case-review-layout">
      <a-card class="case-panel" :bordered="false">
        <template #title>生成入口</template>
        <form class="case-generation-form" @submit.prevent="submitGeneration">
          <label>
            <span>Requirement ID</span>
            <a-input v-model="form.requirementId" />
          </label>
          <label>
            <span>RequirementReview ID</span>
            <a-input v-model="form.requirementReviewId" />
          </label>
          <label>
            <span>目标测试类型</span>
            <a-input v-model="targetTypesText" />
          </label>
          <label>
            <span>ContextArtifact ID 列表</span>
            <a-input v-model="contextIdsText" placeholder="多个 ID 用逗号分隔" />
          </label>
          <a-button html-type="submit" type="primary" :loading="store.loadingGeneration">开始生成候选用例</a-button>
        </form>

        <div class="case-generation-summary">
          <a-statistic title="候选总数" :value="store.totalCandidates" />
          <div class="generation-status">
            <span>当前任务</span>
            <strong>{{ store.generation?.status ?? '未生成' }}</strong>
          </div>
        </div>

        <div v-if="store.metrics" class="case-metrics-strip" aria-label="批次指标">
          <span class="metrics-strip-title">批次指标</span>
          <div v-for="metric in metricItems" :key="metric.label" class="metric-item">
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
          </div>
        </div>
      </a-card>

      <a-card class="case-panel candidate-list-panel" :bordered="false">
        <template #title>候选用例</template>
        <a-spin :loading="store.loadingGeneration">
          <a-list v-if="store.candidates.length > 0" :data="store.candidates" :bordered="false">
            <template #item="{ item }">
              <a-list-item
                class="candidate-list-item"
                :class="{ active: item.id === store.selectedCandidateId }"
                @click="store.selectedCandidateId = item.id"
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
          </div>

          <a-space class="review-actions" wrap>
            <a-button type="primary" :loading="store.loadingReview" @click="review('approve')">通过</a-button>
            <a-button data-test="approve-after-edit" :loading="store.loadingReview" @click="review('approve_after_edit')">
              编辑后通过
            </a-button>
            <a-button status="warning" :loading="store.loadingReview" @click="review('needs_optimization')">需要优化</a-button>
            <a-button status="danger" :loading="store.loadingReview" @click="review('reject')">拒绝</a-button>
          </a-space>

          <div v-if="store.lastReview" class="review-result">
            <span>评审结果：{{ reviewStatusLabel(store.lastReview.status) }}</span>
            <strong>TestCase：{{ store.lastReview.test_case_id ?? '未创建' }}</strong>
          </div>
          <section v-if="store.reviewHistory.length" class="review-history-panel" aria-label="本地评审历史">
            <h3>本地评审历史</h3>
            <div v-for="item in store.reviewHistory" :key="item.id" class="review-history-item">
              <strong>{{ actionLabel(item.action) }}</strong>
              <span>{{ item.reviewer }} · {{ statusTransition(item.from_status, item.to_status) }}</span>
              <small>{{ formatDateTime(item.created_at) }} · {{ item.comment || '无评审备注' }} · 证据 {{ item.evidence_artifact_ids.length }}</small>
            </div>
          </section>
          <a-alert
            v-if="store.lastReview"
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
import { computed, reactive, ref } from 'vue';
import type { CaseReviewAction } from '../../api/cases';
import { useCasesStore } from '../../stores/cases';

const store = useCasesStore();

const form = reactive({
  requirementId: '00000000-0000-0000-0000-000000000401',
  requirementReviewId: '00000000-0000-0000-0000-000000000601',
});
const targetTypesText = ref('functional, ui');
const contextIdsText = ref('');

function commaList(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function listText(items: string[]): string {
  return items.length > 0 ? items.join(', ') : '无';
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
  void store.generateCandidates({
    requirementId: form.requirementId,
    requirementReviewId: form.requirementReviewId,
    targetTestTypes: commaList(targetTypesText.value),
    contextArtifactIds: commaList(contextIdsText.value),
  });
}

function review(action: CaseReviewAction) {
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
  grid-template-columns: minmax(320px, 0.75fr) minmax(340px, 1fr) minmax(0, 1.3fr);
  gap: 16px;
}

.case-panel {
  border-radius: 8px;
}

.case-generation-form {
  display: grid;
  gap: 14px;
}

.case-generation-form label {
  display: grid;
  gap: 7px;
  color: #344054;
  font-weight: 700;
}

.case-generation-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
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

.case-metrics-strip {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
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
  .candidate-evidence-grid {
    grid-template-columns: 1fr;
  }
}
</style>
