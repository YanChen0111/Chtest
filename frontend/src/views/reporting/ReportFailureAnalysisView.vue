<template>
  <section class="reporting-page" data-test="reporting-workbench" aria-labelledby="reporting-title">
    <div class="reporting-heading">
      <div>
        <p class="eyebrow">报告 / 失败分析</p>
        <h2 id="reporting-title">报告与失败分析</h2>
        <p>围绕 TestRun 生成失败分析和自动化执行报告，优先呈现证据，再呈现 AI 结论。</p>
      </div>
      <a-space>
        <a-tag color="green">证据优先</a-tag>
        <a-tag color="blue">证据分析</a-tag>
      </a-space>
    </div>

    <a-alert
      v-if="store.exactRestoreFailed"
      data-test="exact-execution-result-review-restore-failed"
      type="error"
      :content="store.errorMessage || '无法恢复指定的 ExecutionResultReview，请返回 AI 工作台刷新队列。'"
      show-icon
    />
    <a-alert
      v-else-if="store.errorMessage"
      data-test="reporting-error-state"
      type="error"
      :content="store.errorMessage"
      show-icon
    />

    <div class="reporting-layout">
      <a-card class="reporting-panel" :bordered="false">
        <template #title>生成入口</template>
        <form class="reporting-form" @submit.prevent>
          <div class="reporting-source-summary" data-test="reporting-source-summary">
            <span>当前分析对象</span>
            <strong>{{ selectedRun?.name ?? '尚未选择运行' }}</strong>
            <small>{{ selectedRun ? `${selectedRun.status} · ${selectedRun.command}` : '请从下方最近运行中选择' }}</small>
          </div>
          <div class="reporting-test-run-compatibility" aria-hidden="true">
            <a-input v-model="store.testRunId" data-test="reporting-test-run-id" />
          </div>
          <p class="reporting-form-helper">先在执行中心完成一次测试，再从“最近运行”选择要分析的运行。</p>
          <section
            v-if="store.requirementReviewId"
            class="execution-result-review-panel"
            data-test="execution-result-review-panel"
          >
            <div class="gate-heading">
              <strong>ExecutionResultReview gate</strong>
              <a-tag :color="store.executionResultReviewWorkflow?.workflow.state === 'approved' ? 'green' : 'orange'">
                {{ executionResultReviewStateLabel }}
              </a-tag>
            </div>
            <div class="gate-body">
              <span>snapshot</span>
              <strong>{{ store.executionResultReviewWorkflow?.workflow.snapshot_id ?? 'not loaded' }}</strong>
              <span>approval</span>
              <strong>{{ store.executionResultReviewWorkflow?.workflow.approval_decision_id ?? 'none' }}</strong>
              <span>test runs</span>
              <strong>{{ store.executionResultReviewWorkflow?.generated_test_run_ids.length ?? 0 }}</strong>
              <span>artifacts</span>
              <strong>{{ store.executionResultReviewWorkflow?.execution_artifact_ids.length ?? 0 }}</strong>
            </div>
            <a-space wrap>
              <a-button data-test="execution-result-review-submit" :disabled="!store.executionResultReviewWorkflow?.workflow.can_submit" :loading="store.loadingReport" @click="runExecutionResultReviewAction('submit')">
                Submit
              </a-button>
              <a-button data-test="execution-result-review-complete" :disabled="!store.executionResultReviewWorkflow?.workflow.can_complete_review" :loading="store.loadingReport" @click="runExecutionResultReviewAction('complete')">
                Complete review
              </a-button>
              <a-button data-test="execution-result-review-edit" :disabled="!store.executionResultReviewWorkflow?.workflow.can_edit" :loading="store.loadingReport" @click="runExecutionResultReviewAction('edit')">
                Save snapshot
              </a-button>
              <a-button data-test="execution-result-review-approve" type="primary" :disabled="!store.executionResultReviewWorkflow?.workflow.can_approve" :loading="store.loadingReport" @click="runExecutionResultReviewAction('approve')">
                Approve
              </a-button>
              <a-button data-test="execution-result-review-reject" status="danger" :disabled="!store.executionResultReviewWorkflow?.workflow.can_approve" :loading="store.loadingReport" @click="runExecutionResultReviewAction('reject')">
                Reject
              </a-button>
              <a-button data-test="execution-result-review-continue" :disabled="!store.executionResultReviewWorkflow?.workflow.can_continue" :loading="store.loadingReport" @click="runExecutionResultReviewAction('continue')">
                Continue
              </a-button>
            </a-space>
          </section>
          <section
            v-if="store.requirementReviewId && store.reportReviewWorkflow"
            class="execution-result-review-panel"
            data-test="report-review-panel"
          >
            <div class="gate-heading">
              <strong>ReportReview gate</strong>
              <a-tag :color="store.reportReviewWorkflow.workflow.published ? 'green' : store.reportReviewWorkflow.workflow.state === 'approved' ? 'blue' : 'orange'">
                {{ reportReviewStateLabel }}
              </a-tag>
            </div>
            <div class="gate-body">
              <span>snapshot</span>
              <strong>{{ store.reportReviewWorkflow.workflow.snapshot_id }}</strong>
              <span>approval</span>
              <strong>{{ store.reportReviewWorkflow.workflow.approval_decision_id ?? 'none' }}</strong>
              <span>reports</span>
              <strong>{{ store.reportReviewWorkflow.generated_report_ids.length }}</strong>
              <span>artifacts</span>
              <strong>{{ store.reportReviewWorkflow.report_artifact_ids.length }}</strong>
            </div>
            <a-space wrap>
              <a-button data-test="report-review-submit" :disabled="!store.reportReviewWorkflow.workflow.can_submit" :loading="store.loadingReport" @click="runReportReviewAction('submit')">
                Submit
              </a-button>
              <a-button data-test="report-review-complete" :disabled="!store.reportReviewWorkflow.workflow.can_complete_review" :loading="store.loadingReport" @click="runReportReviewAction('complete')">
                Complete review
              </a-button>
              <a-button data-test="report-review-edit" :disabled="!store.reportReviewWorkflow.workflow.can_edit || !store.report" :loading="store.loadingReport" @click="runReportReviewAction('edit')">
                Save report snapshot
              </a-button>
              <a-button data-test="report-review-approve" type="primary" :disabled="!store.reportReviewWorkflow.workflow.can_approve" :loading="store.loadingReport" @click="runReportReviewAction('approve')">
                Approve
              </a-button>
              <a-button data-test="report-review-reject" status="danger" :disabled="!store.reportReviewWorkflow.workflow.can_approve" :loading="store.loadingReport" @click="runReportReviewAction('reject')">
                Reject
              </a-button>
              <a-button data-test="report-review-continue" :disabled="!store.reportReviewWorkflow.workflow.can_continue" :loading="store.loadingReport" @click="runReportReviewAction('continue')">
                Publish
              </a-button>
            </a-space>
          </section>
          <a-space wrap>
            <a-button
              data-test="start-failure-analysis"
              type="primary"
              :disabled="explicitRestoreRequested && !exactGenerationReady"
              :loading="store.loadingAnalysis"
              @click="startFailureAnalysis"
            >
              生成失败分析
            </a-button>
            <a-button
              data-test="start-report"
              :disabled="explicitRestoreRequested && !exactGenerationReady"
              :loading="store.loadingReport"
              @click="startReport"
            >
              生成执行报告
            </a-button>
          </a-space>
        </form>

        <section v-if="!explicitRestoreRequested" class="recent-reporting-runs" data-test="reporting-recent-runs" aria-labelledby="reporting-recent-title">
          <div class="recent-heading">
            <div>
              <p class="eyebrow">会话连续性</p>
              <h3 id="reporting-recent-title">最近 TestRun</h3>
            </div>
            <a-tag v-if="staleRecentRunCount" color="orange" data-test="reporting-recent-runs-stale-state">
              {{ staleRecentRunCount }} 条待刷新
            </a-tag>
          </div>
          <div v-if="executionStore.recentRuns.length" class="recent-run-list" data-test="reporting-recent-runs-list">
            <article v-for="run in executionStore.recentRuns" :key="run.id" class="recent-run-row">
              <div>
                <strong>{{ run.name }}</strong>
                <span>{{ run.status }} · {{ run.command }}</span>
              </div>
              <a-button
                size="small"
                :type="store.testRunId === run.id ? 'primary' : 'secondary'"
                :data-test="`resume-reporting-run-${run.id}`"
                @click="resumeReportingRun(run.id)"
              >
                {{ store.testRunId === run.id ? '当前运行' : '继续分析' }}
              </a-button>
            </article>
          </div>
          <a-empty
            v-else
            data-test="reporting-recent-runs-empty-state"
            description="暂无最近运行，请先在执行页启动测试"
          />
        </section>
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
          <a-empty v-else data-test="reporting-evidence-empty-state" description="生成执行报告后展示证据清单" />
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
          <a-empty v-else data-test="reporting-analysis-empty-state" description="生成失败分析后展示分类、置信度和建议动作" />
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
          <a-empty v-else data-test="reporting-report-empty-state" description="生成执行报告后展示结论、指标和报告工件" />
        </a-card>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';

import { artifactDownloadUrl } from '../../api/execution';
import { useReportingStore } from '../../stores/reporting';
import { useExecutionStore } from '../../stores/execution';
import { DEFAULT_PROJECT_ID } from '../../stores/workflowContext';

const store = useReportingStore();
const executionStore = useExecutionStore();
const route = useRoute();

function queryValue(value: unknown): string | undefined {
  const candidate = Array.isArray(value) ? value[0] : value;
  return typeof candidate === 'string' && candidate.length ? candidate : undefined;
}

const requestedRequirementId = computed(() => queryValue(route.query.requirement_id));
const requestedReviewId = computed(() => queryValue(route.query.requirement_review_id));
const requestedWorkflowRunId = computed(() => queryValue(route.query.workflow_run_id));
const requestedWorkflowStage = computed(() => queryValue(route.query.workflow_stage));
const explicitRestoreRequested = computed(() => (
  route.query.requirement_id !== undefined
  || route.query.requirement_review_id !== undefined
  || route.query.workflow_run_id !== undefined
  || route.query.workflow_stage !== undefined
));

const staleRecentRunCount = computed(() =>
  executionStore.recentRuns.filter((run) => ['pending', 'running', 'execution_pending'].includes(run.status)).length,
);

const selectedRun = computed(() => executionStore.recentRuns.find((run) => run.id === store.testRunId) ?? null);
const executionResultReviewStateLabel = computed(() => store.executionResultReviewWorkflow?.workflow.state ?? 'not_loaded');
const exactGenerationReady = computed(() => Boolean(
  store.testRunId && store.executionResultReviewWorkflow?.workflow.approval_decision_id,
));
const reportReviewStateLabel = computed(() => {
  if (store.reportReviewWorkflow?.workflow.published) {
    return 'published';
  }
  return store.reportReviewWorkflow?.workflow.state ?? 'not_loaded';
});

const evidenceColumns = [
  { title: '证据', dataIndex: 'label' },
  { title: '支撑结论', dataIndex: 'supports_claim' },
  { title: '必需', dataIndex: 'required' },
  { title: '访问', slotName: 'action' },
];

const artifactColumns = [
  { title: '类型', dataIndex: 'artifact_type' },
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

function resumeReportingRun(runId: string) {
  store.testRunId = runId;
  store.failureAnalysis = null;
  store.report = null;
  store.errorMessage = '';
}

function runExecutionResultReviewAction(
  action: 'submit' | 'complete' | 'edit' | 'approve' | 'reject' | 'continue',
) {
  const operations = {
    submit: () => store.submitExecutionResultReviewGate(),
    complete: () => store.completeExecutionResultReviewGate(),
    edit: () => store.editExecutionResultReviewGate(),
    approve: () => store.approveExecutionResultReviewGate('Execution result evidence reviewed.'),
    reject: () => store.rejectExecutionResultReviewGate('Execution result review rejected.'),
    continue: () => store.continueExecutionResultReviewGate(),
  };
  void operations[action]();
}

function runReportReviewAction(
  action: 'submit' | 'complete' | 'edit' | 'approve' | 'reject' | 'continue',
) {
  const operations = {
    submit: () => store.submitReportReviewGate(),
    complete: () => store.completeReportReviewGate(),
    edit: () => store.editReportReviewGate(),
    approve: () => store.approveReportReviewGate('Report evidence reviewed.'),
    reject: () => store.rejectReportReviewGate('Report review rejected.'),
    continue: () => store.continueReportReviewGate(),
  };
  void operations[action]();
}

onMounted(async () => {
  if (explicitRestoreRequested.value) {
    executionStore.recentRuns = [];
    executionStore.recentRunsHydrated = false;
    await store.loadExactExecutionResultReview(
      DEFAULT_PROJECT_ID,
      requestedRequirementId.value,
      requestedReviewId.value,
      requestedWorkflowRunId.value,
      requestedWorkflowStage.value,
    );
    return;
  }
  store.clearExplicitRestoreRequest();
  executionStore.hydrateRecentRuns();
  await store.loadExecutionResultReviewWorkflow();
  await store.loadReportReviewWorkflow();
});
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

.reporting-source-summary {
  display: grid;
  gap: 4px;
  padding: 12px 14px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.reporting-source-summary span,
.reporting-source-summary small {
  color: #667085;
  font-size: 12px;
}

.reporting-source-summary strong {
  color: #1d4ed8;
}

.reporting-source-summary small {
  overflow-wrap: anywhere;
}

.reporting-test-run-compatibility {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

.recent-reporting-runs {
  display: grid;
  gap: 12px;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid #e5e6eb;
}

.recent-heading,
.recent-run-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.recent-heading h3,
.recent-heading p {
  margin: 0;
}

.recent-run-list {
  display: grid;
  gap: 8px;
}

.recent-run-row {
  padding: 10px 12px;
  border: 1px solid #e5e6eb;
  border-radius: 6px;
}

.recent-run-row > div {
  min-width: 0;
  display: grid;
  gap: 2px;
}

.recent-run-row strong,
.recent-run-row span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-run-row span {
  color: #86909c;
  font-size: 12px;
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

.execution-result-review-panel {
  display: grid;
  gap: 10px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f8fafc;
}

.gate-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.gate-body {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 6px 10px;
  color: #5b6472;
}

.gate-body strong {
  min-width: 0;
  overflow-wrap: anywhere;
  color: #111827;
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

@media (max-width: 600px) {
  .reporting-heading,
  .recent-heading {
    align-items: flex-start;
  }

  .reporting-heading {
    flex-direction: column;
  }
}
</style>
