<template>
  <section class="reporting-page" aria-labelledby="reporting-title">
    <div class="reporting-heading">
      <div>
        <p class="eyebrow">报告 / 失败分析</p>
        <h2 id="reporting-title">报告与失败分析</h2>
        <p>围绕 TestRun 生成失败分析和自动化执行报告，优先呈现证据，再呈现 AI 结论。</p>
      </div>
      <a-space>
        <a-tag color="green">证据优先</a-tag>
        <a-tag color="blue">模拟提供方</a-tag>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <div class="reporting-layout">
      <a-card class="reporting-panel" :bordered="false">
        <template #title>生成入口</template>
        <form class="reporting-form" @submit.prevent>
          <label>
            <span>项目 ID</span>
            <a-input v-model="store.projectId" />
          </label>
          <label>
            <span>TestRun ID</span>
            <a-input v-model="store.testRunId" />
          </label>
          <a-space wrap>
            <a-button
              data-test="start-failure-analysis"
              type="primary"
              :loading="store.loadingAnalysis"
              @click="startFailureAnalysis"
            >
              生成失败分析
            </a-button>
            <a-button
              data-test="start-report"
              :loading="store.loadingReport"
              @click="startReport"
            >
              生成执行报告
            </a-button>
          </a-space>
        </form>
      </a-card>

      <div class="reporting-detail">
        <a-card class="reporting-panel" :bordered="false">
          <template #title>证据清单</template>
          <template v-if="store.report">
            <div class="manifest-strip">
              <div>
                <span>结论</span>
                <strong>{{ store.report.conclusion }}</strong>
              </div>
              <div>
                <span>证据</span>
                <strong>{{ evidenceCount }}</strong>
              </div>
              <div>
                <span>缺失</span>
                <strong>{{ missingEvidenceLabel }}</strong>
              </div>
            </div>
            <a-table
              :columns="evidenceColumns"
              :data="evidenceRows"
              :pagination="false"
              row-key="key"
              size="small"
            >
              <template #action="{ record }">
                <a v-if="record.downloadUrl" :href="record.downloadUrl" target="_blank" rel="noreferrer">打开</a>
                <span v-else>{{ record.availability }}</span>
              </template>
            </a-table>
          </template>
          <a-empty v-else description="生成执行报告后展示证据清单" />
        </a-card>

        <a-card class="reporting-panel" :bordered="false">
          <template #title>失败分析</template>
          <template v-if="store.failureAnalysis">
            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="分类">{{ store.failureAnalysis.classification }}</a-descriptions-item>
              <a-descriptions-item label="置信度">{{ confidenceLabel }}</a-descriptions-item>
              <a-descriptions-item label="状态">{{ store.failureAnalysis.status }}</a-descriptions-item>
              <a-descriptions-item label="证据数">{{ store.failureAnalysis.evidence_artifact_ids.length }}</a-descriptions-item>
              <a-descriptions-item label="根因" :span="2">
                {{ store.failureAnalysis.root_cause ?? '证据不足' }}
              </a-descriptions-item>
              <a-descriptions-item label="摘要" :span="2">{{ store.failureAnalysis.summary }}</a-descriptions-item>
            </a-descriptions>
            <div class="action-list">
              <span v-for="action in suggestedActions" :key="action">{{ action }}</span>
            </div>
          </template>
          <a-empty v-else description="生成失败分析后展示分类、置信度和建议动作" />
        </a-card>

        <a-card class="reporting-panel" :bordered="false">
          <template #title>执行报告</template>
          <template v-if="store.report">
            <div class="metric-grid compact">
              <div v-for="item in metricItems" :key="item.label" class="metric-tile">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
            <p class="report-summary">{{ store.report.summary }}</p>
            <a-table
              :columns="artifactColumns"
              :data="store.report.artifacts"
              :pagination="false"
              row-key="id"
              size="small"
            >
              <template #action="{ record }">
                <a :href="artifactDownloadUrl(record.id)" target="_blank" rel="noreferrer">打开</a>
              </template>
            </a-table>
          </template>
          <a-empty v-else description="生成执行报告后展示结论、指标和报告工件" />
        </a-card>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { artifactDownloadUrl } from '../../api/execution';
import { useReportingStore } from '../../stores/reporting';

const store = useReportingStore();

const evidenceColumns = [
  { title: '证据', dataIndex: 'label' },
  { title: '支撑结论', dataIndex: 'supports_claim' },
  { title: '必需', dataIndex: 'required' },
  { title: '访问', slotName: 'action' },
];

const artifactColumns = [
  { title: '类型', dataIndex: 'artifact_type' },
  { title: '路径', dataIndex: 'file_path' },
  { title: '大小', dataIndex: 'size_bytes' },
  { title: '访问', slotName: 'action' },
];

const confidenceLabel = computed(() => {
  if (!store.failureAnalysis) {
    return '-';
  }
  return `${Math.round(store.failureAnalysis.confidence * 100)}%`;
});

const suggestedActions = computed(() => {
  return (store.failureAnalysis?.suggested_actions ?? []).map((item) => String(item));
});

const evidenceRows = computed(() => {
  const evidence = (store.report?.evidence_manifest.evidence ?? []).map((item, index) => ({
    key: `${item.artifact_id ?? item.test_result_id ?? item.metric ?? index}`,
    label: item.artifact_type ?? item.metric ?? item.artifact_id ?? item.test_result_id ?? '结构化证据',
    supports_claim: item.supports_claim,
    required: item.required ? '是' : '否',
    downloadUrl: item.artifact_id ? artifactDownloadUrl(item.artifact_id) : '',
    availability: item.artifact_id ? '本地 Artifact' : '结构化证据',
  }));
  const missing = store.report?.evidence_manifest.missing_evidence ?? [];
  return evidence.concat(
    missing.map((item) => ({
      key: `missing:${item}`,
      label: item,
      supports_claim: '缺失证据',
      required: '是',
      downloadUrl: '',
      availability: '缺失不可打开',
    })),
  );
});

const evidenceCount = computed(() => evidenceRows.value.length);

const missingEvidenceLabel = computed(() => {
  const missing = store.report?.evidence_manifest.missing_evidence ?? [];
  return missing.length === 0 ? '0' : missing.join(', ');
});

const metricItems = computed(() => {
  const metrics = store.report?.metrics ?? {};
  return [
    { label: '总数', value: metrics.total ?? 0 },
    { label: '通过', value: metrics.passed ?? 0 },
    { label: '失败', value: metrics.failed ?? 0 },
    { label: '跳过', value: metrics.skipped ?? 0 },
  ];
});

function startFailureAnalysis() {
  void store.startFailureAnalysis();
}

function startReport() {
  void store.startReport();
}
</script>

<style scoped>
.reporting-page {
  display: grid;
  gap: 18px;
}

.reporting-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.reporting-heading h2,
.reporting-heading p {
  margin: 0;
}

.reporting-heading h2 {
  font-size: 26px;
}

.reporting-heading p:not(.eyebrow) {
  margin-top: 10px;
  max-width: 760px;
  color: #5b6472;
  line-height: 1.7;
}

.reporting-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.65fr) minmax(0, 1.55fr);
  gap: 16px;
}

.reporting-detail {
  display: grid;
  gap: 16px;
}

.reporting-panel {
  border-radius: 8px;
}

.reporting-form {
  display: grid;
  gap: 14px;
}

.reporting-form label {
  display: grid;
  gap: 7px;
  color: #344054;
  font-weight: 700;
}

.manifest-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}

.manifest-strip div,
.metric-tile {
  min-height: 70px;
  padding: 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.manifest-strip span,
.manifest-strip strong,
.metric-tile span,
.metric-tile strong {
  display: block;
}

.manifest-strip span,
.metric-tile span {
  color: #64748b;
}

.manifest-strip strong,
.metric-tile strong {
  margin-top: 8px;
  color: #0f172a;
  font-size: 20px;
}

.metric-grid.compact {
  grid-template-columns: repeat(4, minmax(86px, 1fr));
  margin-bottom: 14px;
}

.report-summary {
  margin: 0 0 14px;
  color: #475569;
}

.action-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.action-list span {
  padding: 6px 10px;
  border: 1px solid #bfdbfe;
  border-radius: 999px;
  color: #1d4ed8;
  background: #eff6ff;
}

@media (max-width: 980px) {
  .reporting-layout {
    grid-template-columns: 1fr;
  }

  .manifest-strip,
  .metric-grid.compact {
    grid-template-columns: repeat(2, minmax(120px, 1fr));
  }
}
</style>
