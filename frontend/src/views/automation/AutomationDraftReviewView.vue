<template>
  <section class="automation-draft-page" aria-labelledby="automation-draft-title">
    <div class="automation-draft-heading">
      <div>
        <p class="eyebrow">AutomationDraft 评审</p>
        <h2 id="automation-draft-title">自动化草稿</h2>
        <p>从已评审用例生成可审查的自动化草稿，只做编辑和审批，不在此页面执行代码。</p>
      </div>
      <a-space>
        <a-tag color="blue">模拟 AutomationDraftAgent</a-tag>
        <a-tag color="green">审批后进入待执行状态</a-tag>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" type="error" show-icon>{{ store.errorMessage }}</a-alert>

    <div class="automation-draft-layout">
      <a-card class="draft-panel" :bordered="false">
        <template #title>草稿入口</template>
        <form class="draft-form" @submit.prevent="submitPlan">
          <label>
            <span>TestCase ID</span>
            <a-input data-test="automation-test-case-id" v-model="form.testCaseId" />
          </label>
          <label>
            <span>目标框架</span>
            <a-input v-model="form.targetFramework" />
          </label>
          <a-checkbox v-model="form.useKnowledge">结合 RAG 知识库</a-checkbox>
          <a-button data-test="generate-plan" html-type="submit" type="primary" :loading="store.loading">生成自动化方案</a-button>
        </form>

        <section v-if="store.plan" class="automation-plan-panel">
          <h3>AutomationPlan</h3>
          <a-descriptions :column="1" bordered size="small">
            <a-descriptions-item label="标题">{{ store.plan.title }}</a-descriptions-item>
            <a-descriptions-item label="状态">{{ store.plan.status }}</a-descriptions-item>
            <a-descriptions-item label="知识证据">
              {{ store.plan.knowledge_retrieval_artifact_id ?? '无命中证据' }}
            </a-descriptions-item>
            <a-descriptions-item label="依赖说明">{{ store.plan.dependency_notes ?? '无' }}</a-descriptions-item>
            <a-descriptions-item label="风险说明">{{ store.plan.risk_notes ?? '无' }}</a-descriptions-item>
          </a-descriptions>
          <ol class="automation-plan-steps">
            <li v-for="step in store.plan.execution_steps" :key="step">{{ step }}</li>
          </ol>
          <a-space class="draft-actions" wrap>
            <a-button data-test="approve-plan" :disabled="!canApprovePlan" :loading="store.loading" @click="approvePlan">
              批准方案
            </a-button>
            <a-button
              data-test="generate-draft-from-plan"
              type="primary"
              :disabled="store.plan.status !== 'approved'"
              :loading="store.loading"
              @click="generateDraftFromPlan"
            >
              生成草稿
            </a-button>
          </a-space>
          <div v-if="store.lastPlanReview" class="draft-result">
            <span>方案评审结果：{{ store.lastPlanReview.status }}</span>
            <strong>AutomationPlan：{{ store.lastPlanReview.automation_plan_id }}</strong>
          </div>
          <section v-if="store.planReviewHistory.length" class="review-history-panel" aria-label="方案评审历史">
            <h3>方案评审历史</h3>
            <div v-for="item in store.planReviewHistory" :key="item.id" class="review-history-item">
              <strong>{{ actionLabel(item.action) }}</strong>
              <span>{{ item.reviewer }} 路 {{ statusTransition(item.from_status, item.to_status) }}</span>
              <small>{{ formatDateTime(item.created_at) }} 路 {{ item.comment || '无评审备注' }} 路 证据 {{ item.evidence_artifact_ids.length }}</small>
            </div>
          </section>
        </section>
      </a-card>

      <a-card class="draft-panel draft-detail-panel" :bordered="false">
        <template #title>草稿评审</template>
        <a-spin :loading="store.loading">
          <template v-if="store.draft">
            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="标题">{{ store.draft.title }}</a-descriptions-item>
              <a-descriptions-item label="状态">{{ store.draft.status }}</a-descriptions-item>
              <a-descriptions-item label="框架">{{ store.draft.target_framework }}</a-descriptions-item>
              <a-descriptions-item label="语言">{{ store.draft.draft_language }}</a-descriptions-item>
              <a-descriptions-item label="建议路径">{{ store.draft.suggested_file_path ?? '未建议' }}</a-descriptions-item>
              <a-descriptions-item label="审批要求">
                {{ store.draft.approval_required ? '需要审批' : '无需审批' }}
              </a-descriptions-item>
              <a-descriptions-item label="执行策略" :span="2">{{ store.draft.execution_strategy }}</a-descriptions-item>
              <a-descriptions-item label="执行说明" :span="2">
                {{ store.draft.execution_notes ?? '无' }}
              </a-descriptions-item>
              <a-descriptions-item label="风险说明" :span="2">{{ store.draft.risk_notes ?? '无' }}</a-descriptions-item>
            </a-descriptions>

            <section class="draft-code-panel">
              <h3>草稿代码</h3>
              <pre>{{ store.draft.draft_code }}</pre>
            </section>

            <div class="draft-quality-gate" data-test="draft-quality-gate" role="note">
              <strong>Quality gate</strong>
              <span>
                fake, stub, placeholder, or assert True-only drafts cannot be approved. Replace them with real selectors,
                steps, and assertions before approval.
              </span>
            </div>

            <a-space class="draft-actions" wrap>
              <a-button data-test="edit-draft" :loading="store.loading" @click="editDraft">保存评审编辑</a-button>
              <a-button data-test="approve-draft" type="primary" :loading="store.loading" @click="approveDraft">批准草稿</a-button>
            </a-space>

            <div v-if="store.lastReview" class="draft-result">
              <span>评审结果：{{ store.lastReview.status }}</span>
              <strong>AutomationDraft：{{ store.lastReview.automation_draft_id }}</strong>
            </div>

            <section v-if="store.reviewHistory.length" class="review-history-panel" aria-label="本地评审历史">
              <h3>本地评审历史</h3>
              <div v-for="item in store.reviewHistory" :key="item.id" class="review-history-item">
                <strong>{{ actionLabel(item.action) }}</strong>
                <span>{{ item.reviewer }} · {{ statusTransition(item.from_status, item.to_status) }}</span>
                <small>{{ formatDateTime(item.created_at) }} · {{ item.comment || '无评审备注' }} · 证据 {{ item.evidence_artifact_ids.length }}</small>
              </div>
            </section>
          </template>

          <a-empty v-else description="生成后展示自动化草稿" />
        </a-spin>
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue';

import { useAutomationStore } from '../../stores/automation';

const store = useAutomationStore();

const form = reactive({
  testCaseId: store.testCaseId,
  targetFramework: 'pytest',
  useKnowledge: true,
});

const canApprovePlan = computed(() => ['plan_generated', 'edited'].includes(store.plan?.status ?? ''));

function submitPlan() {
  void store.createPlan({
    testCaseId: form.testCaseId,
    targetFramework: form.targetFramework,
    useKnowledge: form.useKnowledge,
  });
}

function approvePlan() {
  void store.approveCurrentPlan('前端批准自动化方案');
}

function generateDraftFromPlan() {
  void store.generateDraftFromPlan();
}

function editDraft() {
  void store.editCurrentDraft('前端评审编辑');
}

function approveDraft() {
  void store.approveCurrentDraft('前端批准草稿');
}

function actionLabel(action: string): string {
  const labels: Record<string, string> = {
    edit: '编辑',
    approve: '批准',
    reject: '拒绝',
    generate_draft: '生成草稿',
  };
  return labels[action] ?? action;
}

function statusTransition(fromStatus: string | null, toStatus: string | null): string {
  return `${statusLabel(fromStatus)} -> ${statusLabel(toStatus)}`;
}

function statusLabel(status: string | null): string {
  const labels: Record<string, string> = {
    draft_generated: '已生成',
    edited: '已编辑',
    approved: '已批准',
    plan_generated: '方案已生成',
    rejected: '已拒绝',
  };
  return status ? (labels[status] ?? status) : '未知';
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

onMounted(() => {
  if (store.loadLatestApprovedTestCaseContext()) {
    form.testCaseId = store.testCaseId;
  }
});
</script>

<style scoped>
.automation-draft-page {
  display: grid;
  gap: 18px;
}

.automation-draft-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.automation-draft-heading h2,
.automation-draft-heading p {
  margin: 0;
}

.automation-draft-heading h2 {
  font-size: 26px;
}

.automation-draft-heading p:not(.eyebrow) {
  margin-top: 10px;
  max-width: 780px;
  color: #5b6472;
  line-height: 1.7;
}

.automation-draft-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.75fr) minmax(0, 1.4fr);
  gap: 16px;
}

.draft-panel {
  border-radius: 8px;
}

.draft-form {
  display: grid;
  gap: 14px;
}

.draft-form label {
  display: grid;
  gap: 7px;
  color: #344054;
  font-weight: 700;
}

.automation-plan-panel {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.automation-plan-panel h3,
.automation-plan-steps {
  margin: 0;
}

.automation-plan-steps {
  padding-left: 20px;
  color: #475569;
  line-height: 1.7;
}

.draft-code-panel {
  margin-top: 18px;
}

.draft-code-panel h3 {
  margin: 0 0 10px;
  font-size: 16px;
}

.draft-code-panel pre {
  overflow: auto;
  margin: 0;
  padding: 14px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
  color: #0f172a;
  line-height: 1.6;
}

.draft-actions,
.draft-result {
  margin-top: 16px;
}

.draft-quality-gate {
  margin-top: 14px;
}

.draft-result {
  padding: 12px;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  background: #f0fdf4;
}

.draft-result span,
.draft-result strong {
  display: block;
}

.draft-result span {
  color: #64748b;
}

.draft-result strong {
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

@media (max-width: 980px) {
  .automation-draft-layout {
    grid-template-columns: 1fr;
  }
}
</style>
