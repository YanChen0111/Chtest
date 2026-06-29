<template>
  <section class="requirement-review-page" aria-labelledby="requirement-review-title">
    <div class="requirement-review-heading">
      <div>
        <p class="eyebrow">Requirement Review</p>
        <h2 id="requirement-review-title">需求评审</h2>
        <p>把需求先转成可审查证据：评分、问题、澄清问题和风险项都在生成用例前确认。</p>
      </div>
      <a-space>
        <a-tag color="blue">Mock RequirementReviewAgent</a-tag>
        <a-tag color="green">人工评审前置</a-tag>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <div class="requirement-review-layout">
      <a-card class="requirement-panel" :bordered="false">
        <template #title>需求输入</template>
        <form class="requirement-form" @submit.prevent="submitReview">
          <label>
            <span>需求标题</span>
            <a-input v-model="form.title" />
          </label>
          <label>
            <span>来源编号</span>
            <a-input v-model="form.sourceRef" />
          </label>
          <label>
            <span>需求内容</span>
            <a-textarea v-model="form.content" :auto-size="{ minRows: 8, maxRows: 12 }" />
          </label>
          <label>
            <span>ContextArtifact IDs</span>
            <a-input v-model="contextIdsText" placeholder="多个 ID 用逗号分隔" />
          </label>
          <a-button html-type="submit" type="primary" :loading="store.loading">开始评审</a-button>
        </form>
      </a-card>

      <a-card class="requirement-panel evidence-panel" :bordered="false">
        <template #title>评审证据</template>
        <a-spin :loading="store.loading">
          <template v-if="store.review">
            <div class="score-strip">
              <div>
                <span>综合评分</span>
                <strong>{{ store.review.overall_score }}</strong>
              </div>
              <div v-for="score in scoreItems" :key="score.label">
                <span>{{ score.label }}</span>
                <strong>{{ score.value }}</strong>
              </div>
            </div>

            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="需求标题">{{ store.requirement?.title ?? '未创建' }}</a-descriptions-item>
              <a-descriptions-item label="需求 ID">{{ store.review.requirement_id }}</a-descriptions-item>
              <a-descriptions-item label="状态">{{ reviewStatusLabel(store.review.status) }}</a-descriptions-item>
              <a-descriptions-item label="外部知识库">
                {{ store.review.used_knowledge ? '已使用外部知识库' : '外部知识库未使用' }}
              </a-descriptions-item>
              <a-descriptions-item label="context_manifest">
                {{ store.review.context_manifest_artifact_id ?? '未生成' }}
              </a-descriptions-item>
              <a-descriptions-item label="已使用上下文" :span="2">
                {{ idListText(store.review.used_context_artifact_ids) }}
              </a-descriptions-item>
            </a-descriptions>

            <div class="review-section">
              <h3>问题</h3>
              <a-list :data="store.review.issues" :bordered="false">
                <template #item="{ item }">
                  <a-list-item>
                    <a-space direction="vertical" size="mini">
                      <a-tag color="orange">{{ item.severity }}</a-tag>
                      <strong>{{ item.type }}</strong>
                      <span>{{ item.text }}</span>
                    </a-space>
                  </a-list-item>
                </template>
              </a-list>
            </div>

            <div class="review-section">
              <h3>澄清问题</h3>
              <a-list :data="store.review.clarification_questions" :bordered="false">
                <template #item="{ item }">
                  <a-list-item>{{ item }}</a-list-item>
                </template>
              </a-list>
            </div>

            <div class="review-section">
              <h3>风险项</h3>
              <a-table :columns="riskColumns" :data="store.review.risk_items" :pagination="false" size="small">
                <template #risk_level="{ record }">
                  <a-tag :color="riskColor(record.risk_level)">{{ record.risk_level }}</a-tag>
                </template>
              </a-table>
            </div>
          </template>

          <a-empty v-else-if="!store.loading" description="提交需求后展示评审结果" />
        </a-spin>
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';

import { useRequirementsStore } from '../../stores/requirements';

const store = useRequirementsStore();

const form = reactive({
  title: '优惠券结算规则',
  sourceRef: 'REQ-COUPON-001',
  content:
    '用户在提交订单时，可以选择一张可用优惠券。优惠券不可与积分同时使用。过期优惠券不可使用。优惠券金额不能超过订单应付金额。提交订单后，系统需要展示优惠后的最终支付金额。',
});
const contextIdsText = ref('');

const riskColumns = [
  { title: '风险', dataIndex: 'title' },
  { title: '等级', slotName: 'risk_level' },
  { title: '建议', dataIndex: 'suggestion' },
];

const scoreItems = computed(() => {
  if (!store.review) {
    return [];
  }
  return [
    { label: '完整性', value: store.review.scores.completeness },
    { label: '清晰度', value: store.review.scores.clarity },
    { label: '一致性', value: store.review.scores.consistency },
    { label: '可测性', value: store.review.scores.testability },
    { label: '可行性', value: store.review.scores.feasibility },
    { label: '逻辑性', value: store.review.scores.logic },
  ];
});

function contextArtifactIds(): string[] {
  return contextIdsText.value
    .split(',')
    .map((id) => id.trim())
    .filter(Boolean);
}

function idListText(ids: string[]): string {
  return ids.length > 0 ? ids.join(', ') : '无';
}

function riskColor(level: string): string {
  const colors: Record<string, string> = {
    low: 'green',
    medium: 'orange',
    high: 'red',
    critical: 'purple',
  };
  return colors[level] ?? 'gray';
}

function reviewStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    draft: '草稿',
    reviewed: '已评审',
    confirmed: '已确认',
  };
  return labels[status] ?? status;
}

function submitReview() {
  void store.reviewRequirement({
    title: form.title,
    content: form.content,
    sourceRef: form.sourceRef,
    contextArtifactIds: contextArtifactIds(),
  });
}
</script>

<style scoped>
.requirement-review-page {
  display: grid;
  gap: 18px;
}

.requirement-review-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.requirement-review-heading h2,
.requirement-review-heading p {
  margin: 0;
}

.requirement-review-heading h2 {
  font-size: 26px;
}

.requirement-review-heading p:not(.eyebrow) {
  margin-top: 10px;
  max-width: 780px;
  color: #5b6472;
  line-height: 1.7;
}

.requirement-review-layout {
  display: grid;
  grid-template-columns: minmax(360px, 0.85fr) minmax(0, 1.45fr);
  gap: 16px;
}

.requirement-panel {
  border-radius: 8px;
}

.requirement-form,
.review-section {
  display: grid;
  gap: 14px;
}

.requirement-form label {
  display: grid;
  gap: 7px;
  color: #344054;
  font-weight: 700;
}

.score-strip {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.score-strip div {
  min-height: 72px;
  padding: 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.score-strip span,
.score-strip strong {
  display: block;
}

.score-strip span {
  color: #64748b;
}

.score-strip strong {
  margin-top: 8px;
  color: #1d4ed8;
  font-size: 24px;
}

.review-section {
  margin-top: 18px;
}

.review-section h3 {
  margin: 0;
  font-size: 16px;
}

@media (max-width: 1100px) {
  .requirement-review-layout,
  .score-strip {
    grid-template-columns: 1fr;
  }
}
</style>
