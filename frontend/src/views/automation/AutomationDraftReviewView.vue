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

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <div class="automation-draft-layout">
      <a-card class="draft-panel" :bordered="false">
        <template #title>草稿入口</template>
        <form class="draft-form" @submit.prevent="submitDraft">
          <label>
            <span>TestCase ID</span>
            <a-input v-model="form.testCaseId" />
          </label>
          <label>
            <span>目标框架</span>
            <a-input v-model="form.targetFramework" />
          </label>
          <a-button html-type="submit" type="primary" :loading="store.loading">生成自动化草稿</a-button>
        </form>
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
import { reactive } from 'vue';

import { useAutomationStore } from '../../stores/automation';

const store = useAutomationStore();

const form = reactive({
  testCaseId: '00000000-0000-0000-0000-000000000901',
  targetFramework: 'pytest',
});

function submitDraft() {
  void store.createDraft({
    testCaseId: form.testCaseId,
    targetFramework: form.targetFramework,
  });
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
