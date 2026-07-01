<template>
  <section class="cicd-page" aria-labelledby="cicd-title">
    <div class="cicd-heading">
      <div>
        <p class="eyebrow">本地 CI/CD 质量</p>
        <h2 id="cicd-title">CI/CD 质量中心</h2>
        <p>从本地 diff 或静态 CI 导入创建 CICDRun，查看变更文件、导入证据和本地质量门禁。</p>
      </div>
      <a-space>
        <a-tag color="green">本地 diff</a-tag>
        <a-tag color="blue">静态导入</a-tag>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <div class="cicd-layout">
      <a-card class="cicd-panel" :bordered="false">
        <template #title>本地变更输入</template>
        <form class="cicd-form" @submit.prevent="createRun">
          <label>
            <span>项目 ID</span>
            <a-input v-model="store.projectId" />
          </label>
          <label>
            <span>仓库 ID</span>
            <a-input v-model="store.repositoryId" />
          </label>
          <div class="ref-grid">
            <label>
              <span>基准引用</span>
              <a-input v-model="store.baseRef" />
            </label>
            <label>
              <span>当前引用</span>
              <a-input v-model="store.headRef" />
            </label>
          </div>
          <label>
            <span>统一 diff</span>
            <a-textarea v-model="store.diffText" :auto-size="{ minRows: 8, maxRows: 14 }" />
          </label>
          <a-space wrap>
            <a-button data-test="create-cicd-run" html-type="submit" type="primary" :loading="store.loading">
              创建 CICDRun
            </a-button>
            <a-button data-test="analyze-cicd-run" :disabled="!store.run" :loading="store.loading" @click="analyzeRun">
              生成风险分析
            </a-button>
          </a-space>
        </form>
      </a-card>

      <div class="cicd-detail">
        <a-card class="cicd-panel" :bordered="false">
          <template #title>变更证据</template>
          <template v-if="store.run">
            <div class="status-strip">
              <div>
                <span>状态</span>
                <strong>{{ statusLabel(store.run.status) }}</strong>
              </div>
              <div>
                <span>风险</span>
                <strong>{{ riskLevelLabel(store.run.overall_risk) }}</strong>
              </div>
              <div>
                <span>文件数</span>
                <strong>{{ store.run.changed_files.length }}</strong>
              </div>
            </div>
            <a-table
              :columns="changedFileColumns"
              :data="changedFileRows"
              :pagination="false"
              row-key="id"
              size="small"
            />
          </template>
          <a-empty v-else description="创建后展示变更文件证据" />
        </a-card>

        <a-card v-if="isImportedRun" class="cicd-panel" :bordered="false">
          <template #title>导入 CI 证据</template>
          <div class="import-grid">
            <div>
              <span>Provider</span>
              <strong>{{ providerLabel(store.run?.provider) }}</strong>
            </div>
            <div>
              <span>导入状态</span>
              <strong>{{ statusLabel(store.run?.status || '') }}</strong>
            </div>
            <div>
              <span>CI 结论</span>
              <strong>{{ conclusionLabel(importEvidence?.conclusion) }}</strong>
            </div>
            <div>
              <span>QualityGateDecision</span>
              <strong>{{ statusLabel(store.run?.quality_gate_status || '') }}</strong>
            </div>
            <div>
              <span>Job</span>
              <strong>{{ importEvidence?.job_name || '-' }}</strong>
            </div>
            <div>
              <span>外部运行</span>
              <strong>{{ importEvidence?.external_run_id || '-' }}</strong>
            </div>
          </div>
          <p class="evidence-line">导入 CI 结论仅作为证据，QualityGateDecision 仍需本地门禁计算。</p>
          <div v-if="artifactReferenceRows.length" class="reference-list">
            <div v-for="reference in artifactReferenceRows" :key="reference.key" class="reference-item">
              <strong>{{ reference.name }}</strong>
              <span>{{ reference.kind }}</span>
              <span>{{ reference.inert_reference ? '仅保存引用' : '引用' }}</span>
              <span>{{ reference.localOpenLabel }}</span>
              <span>{{ reference.remoteFetchLabel }}</span>
              <small>{{ reference.external_url || '-' }}</small>
            </div>
          </div>
          <a-empty v-else description="没有导入工件引用" />
        </a-card>

        <a-card class="cicd-panel" :bordered="false">
          <template #title>风险分析证据</template>
          <template v-if="riskAnalysisArtifacts.length">
            <a-table
              :columns="artifactColumns"
              :data="riskAnalysisArtifacts"
              :pagination="false"
              row-key="id"
              size="small"
            />
          </template>
          <a-empty v-else description="生成风险分析后展示风险分析工件" />
        </a-card>

        <a-card class="cicd-panel" :bordered="false">
          <template #title>UnitTestPatch 评审</template>
          <a-space wrap class="action-row">
            <a-button data-test="generate-unit-test-patch" :disabled="!store.run" :loading="store.loading" @click="generatePatch">
              生成 UnitTestPatch
            </a-button>
            <a-button
              data-test="approve-unit-test-patch"
              type="primary"
              :disabled="!store.unitTestPatch"
              :loading="store.loading"
              @click="approvePatch"
            >
              批准
            </a-button>
            <a-button
              data-test="reject-unit-test-patch"
              status="danger"
              :disabled="!store.unitTestPatch"
              :loading="store.loading"
              @click="rejectPatch"
            >
              拒绝
            </a-button>
          </a-space>
          <template v-if="store.unitTestPatch">
            <div class="patch-grid">
              <div>
                <span>补丁状态</span>
                <strong>{{ patchStatusLabel(store.patchReviewStatus || store.unitTestPatch.status) }}</strong>
              </div>
              <div>
                <span>PatchScopeGate</span>
                <strong>{{ store.unitTestPatch.scope_gate_result.allowed ? '通过' : '拒绝' }}</strong>
              </div>
              <div>
                <span>风险</span>
                <strong>{{ riskLevelLabel(store.unitTestPatch.scope_gate_result.risk_level ?? 'low') }}</strong>
              </div>
            </div>
            <p class="evidence-line">PatchScopeGate：{{ store.unitTestPatch.scope_gate_result.allowed ? '通过' : '拒绝' }}</p>
            <p class="evidence-line">{{ testIntentLabel(store.unitTestPatch.test_intent) }}</p>
            <div class="coverage-list">
              <a-tag v-for="target in store.unitTestPatch.coverage_target" :key="target.path" color="arcoblue">
                {{ target.path }} {{ target.reason }}
              </a-tag>
            </div>
            <div class="coverage-list">
              <a-tag v-for="path in store.unitTestPatch.scope_gate_result.checked_paths" :key="path" color="green">
                {{ path }}
              </a-tag>
            </div>
            <pre class="patch-diff">{{ store.unitTestPatch.patch_text }}</pre>
            <section v-if="store.patchReviewHistory.length" class="review-history-panel" aria-label="UnitTestPatch 本地评审历史">
              <h3>本地评审历史</h3>
              <div v-for="item in store.patchReviewHistory" :key="item.id" class="review-history-item">
                <strong>{{ actionLabel(item.action) }}</strong>
                <span>{{ item.reviewer }} · {{ statusTransition(item.from_status, item.to_status) }}</span>
                <small>{{ formatDateTime(item.created_at) }} · {{ item.comment || '无评审备注' }} · 证据 {{ item.evidence_artifact_ids.length }}</small>
              </div>
            </section>
          </template>
          <a-empty v-else description="生成后展示 UnitTestPatch diff 和范围门禁" />
        </a-card>

        <a-card class="cicd-panel" :bordered="false">
          <template #title>测试与质量门禁</template>
          <a-space wrap class="action-row">
            <a-button data-test="run-new-tests" :disabled="!store.unitTestPatch" :loading="store.loading" @click="runNewTestsForPatch">
              记录新增测试
            </a-button>
            <a-button data-test="select-regression" :disabled="!store.run" :loading="store.loading" @click="selectRegressionPlan">
              选择回归
            </a-button>
            <a-button data-test="run-regression" :disabled="!store.regressionPlan" :loading="store.loading" @click="runRegressionPlan">
              记录回归
            </a-button>
            <a-button data-test="compute-quality-gate" :disabled="!store.run" :loading="store.loading" @click="computeGate">
              计算门禁
            </a-button>
            <a-button data-test="generate-cicd-report" :disabled="!store.qualityGate" :loading="store.loading" @click="generateQualityReport">
              生成报告
            </a-button>
          </a-space>
          <div class="evidence-grid">
            <div>
              <span>新增 TestRun</span>
              <strong>{{ store.newTestRun?.test_run_id || '-' }}</strong>
            </div>
            <div>
              <span>回归计划</span>
              <strong>{{ store.regressionPlan?.regression_plan_artifact_id || '-' }}</strong>
            </div>
            <div>
              <span>回归运行</span>
              <strong>{{ store.regressionRun?.test_run_ids.join(', ') || '-' }}</strong>
            </div>
            <div>
              <span>QualityGateDecision</span>
              <strong>{{ store.qualityGate ? statusLabel(store.qualityGate.status) : '-' }}</strong>
            </div>
            <div>
              <span>报告</span>
              <strong>{{ store.qualityReport?.report_id || '-' }}</strong>
            </div>
          </div>
          <p v-if="store.qualityGate" class="evidence-line">{{ store.qualityGate.summary }}</p>
          <section v-if="store.qualityGate" class="quality-summary-panel" aria-label="门禁证据摘要">
            <h3>门禁证据摘要</h3>
            <div class="quality-summary-list">
              <div v-for="item in qualityEvidenceRows" :key="item.key" class="quality-summary-item">
                <div>
                  <strong>{{ item.label }}</strong>
                  <span>{{ item.statusLabel }}</span>
                </div>
                <small>{{ item.required ? '必需证据' : '辅助证据' }}</small>
                <a-link v-if="item.downloadUrl" :href="item.downloadUrl" target="_blank" rel="noreferrer">
                  打开
                </a-link>
                <span v-else class="muted-text">{{ item.availabilityLabel }}</span>
              </div>
            </div>
            <div v-if="blockingReasonRows.length" class="blocking-list">
              <strong>阻塞原因</strong>
              <a-tag v-for="reason in blockingReasonRows" :key="reason" color="orange">
                {{ reason }}
              </a-tag>
            </div>
          </section>
          <section v-if="store.gateReviewHistory.length" class="review-history-panel" aria-label="QualityGateDecision 本地评审历史">
            <h3>本地评审历史</h3>
            <div v-for="item in store.gateReviewHistory" :key="item.id" class="review-history-item">
              <strong>{{ actionLabel(item.action) }}</strong>
              <span>{{ item.reviewer }} · {{ statusTransition(item.from_status, item.to_status) }}</span>
              <small>{{ formatDateTime(item.created_at) }} · {{ item.comment || '无评审备注' }} · 证据 {{ item.evidence_artifact_ids.length }}</small>
            </div>
          </section>
        </a-card>

        <a-card class="cicd-panel" :bordered="false">
          <template #title>最近 CI/CD 运行</template>
          <a-table :columns="runColumns" :data="runRows" :pagination="false" row-key="id" size="small" />
        </a-card>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { useCICDStore } from '../../stores/cicd';
import type { CICDImportEvidenceContentRead } from '../../api/cicd';

const store = useCICDStore();

const changedFileColumns = [
  { title: '路径', dataIndex: 'path' },
  { title: '类型', dataIndex: 'changeTypeLabel' },
  { title: '角色', dataIndex: 'fileRoleLabel' },
  { title: '风险', dataIndex: 'riskLevelLabel' },
  { title: '原因', dataIndex: 'riskReasonsLabel' },
];

const artifactColumns = [
  { title: '类型', dataIndex: 'artifact_type' },
  { title: '路径', dataIndex: 'file_path' },
  { title: '大小', dataIndex: 'size_bytes' },
];

const runColumns = [
  { title: '运行', dataIndex: 'id' },
  { title: '状态', dataIndex: 'statusLabel' },
  { title: '风险', dataIndex: 'riskLabel' },
  { title: '基准', dataIndex: 'base_ref' },
  { title: '当前', dataIndex: 'head_ref' },
];

const changedFileRows = computed(() =>
  (store.run?.changed_files ?? []).map((file) => ({
    ...file,
    changeTypeLabel: changeTypeLabel(file.change_type),
    fileRoleLabel: fileRoleLabel(file.file_role),
    riskLevelLabel: riskLevelLabel(file.risk_level),
    riskReasonsLabel: file.risk_reasons.map((reason) => riskReasonLabel(reason)).join('，'),
  })),
);

const runRows = computed(() =>
  store.runs.map((run) => ({
    ...run,
    statusLabel: statusLabel(run.status),
    riskLabel: riskLevelLabel(run.overall_risk),
  })),
);

const ciImportArtifact = computed(() => store.run?.analysis_artifacts.find((artifact) => artifact.artifact_type === 'ci_run_metadata'));

const importEvidence = computed(() => {
  const content = ciImportArtifact.value?.metadata_json.content_json;
  return isRecord(content) ? (content as CICDImportEvidenceContentRead) : null;
});

const artifactReferenceRows = computed(() =>
  (importEvidence.value?.artifact_references ?? []).map((reference, index) => ({
    ...reference,
    key: `${reference.name ?? 'reference'}-${reference.kind ?? 'artifact'}-${index}`,
    name: reference.name || '未命名引用',
    kind: reference.kind || 'artifact',
    localOpenLabel: '不可本地打开',
    remoteFetchLabel: ciImportArtifact.value?.metadata_json.remote_fetch_performed === true ? '已远程拉取' : '未远程拉取',
  })),
);

const riskAnalysisArtifacts = computed(() => store.run?.analysis_artifacts.filter((artifact) => artifact.artifact_type === 'risk_analysis') ?? []);

const isImportedRun = computed(() => store.run?.source_type === 'ci_import' || Boolean(ciImportArtifact.value));

const qualityEvidenceRows = computed(() => {
  if (!store.qualityGate) return [];
  const detail = store.qualityGate.status_detail;
  const unitPatch = readStatusDetail(detail.unit_test_patch);
  const newTests = readStatusDetail(detail.new_tests);
  const regression = readStatusDetail(detail.regression);
  const artifactIds = store.qualityGate.evidence_artifact_ids;
  return [
    qualityEvidenceRow('unit_test_patch', 'UnitTestPatch / PatchScopeGate', unitPatch.status, artifactIds[0]),
    qualityEvidenceRow('new_tests', '新增测试证据', newTests.status),
    qualityEvidenceRow('regression', '回归证据', regression.status),
  ];
});

const blockingReasonRows = computed(() => (store.qualityGate?.blocking_reasons ?? []).map((reason) => blockingReasonLabel(reason)));

function createRun() {
  void store.createRun();
}

function analyzeRun() {
  void store.analyzeRun();
}

function generatePatch() {
  void store.generatePatch();
}

function approvePatch() {
  void store.approvePatch();
}

function rejectPatch() {
  void store.rejectPatch();
}

function runNewTestsForPatch() {
  void store.runNewTestsForPatch();
}

function selectRegressionPlan() {
  void store.selectRegressionPlan();
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    imported: '已导入',
    pending: '待处理',
    created: '已创建',
    analyzed: '已分析',
    generated: '已生成',
    approved: '已批准',
    rejected: '已拒绝',
    passed: '通过',
    failed: '失败',
    needs_review: '需要复核',
    scope_validated: '范围已验证',
    unknown: '未知',
  };
  return labels[status] ?? status;
}

function providerLabel(provider?: string | null): string {
  const labels: Record<string, string> = {
    github_actions: 'GitHub Actions',
    gitlab_ci: 'GitLab CI',
    jenkins: 'Jenkins',
    circleci: 'CircleCI',
    buildkite: 'Buildkite',
    imported: '导入',
    other: '其他',
    local: '本地',
  };
  return provider ? (labels[provider] ?? provider) : '-';
}

function conclusionLabel(conclusion?: string | null): string {
  const labels: Record<string, string> = {
    success: '成功',
    failure: '失败',
    cancelled: '已取消',
    skipped: '已跳过',
    timed_out: '超时',
    unknown: '未知',
  };
  return conclusion ? (labels[conclusion] ?? conclusion) : '-';
}

function patchStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    scope_validated: '范围已验证',
    generated: '已生成',
    approved: '已批准',
    rejected: '已拒绝',
  };
  return labels[status] ?? statusLabel(status);
}

function actionLabel(action: string): string {
  const labels: Record<string, string> = {
    approve: '批准',
    reject: '拒绝',
    compute_quality_gate: '计算门禁',
  };
  return labels[action] ?? action;
}

function statusTransition(fromStatus: string | null, toStatus: string | null): string {
  return `${statusLabel(fromStatus ?? 'unknown')} -> ${statusLabel(toStatus ?? 'unknown')}`;
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

function riskLevelLabel(level: string): string {
  const labels: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '严重',
  };
  return labels[level] ?? level;
}

function changeTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    added: '新增',
    modified: '修改',
    deleted: '删除',
    renamed: '重命名',
  };
  return labels[type] ?? type;
}

function fileRoleLabel(role: string): string {
  const labels: Record<string, string> = {
    source: '源码',
    test: '测试',
    config: '配置',
    docs: '文档',
    unknown: '未知',
  };
  return labels[role] ?? role;
}

function riskReasonLabel(reason: string): string {
  const labels: Record<string, string> = {
    'source file changed': '源码文件变更',
    'test file changed': '测试文件变更',
    'config file changed': '配置文件变更',
  };
  return labels[reason] ?? reason;
}

function blockingReasonLabel(reason: string): string {
  const labels: Record<string, string> = {
    'missing applied UnitTestPatch evidence': '缺少已应用 UnitTestPatch 证据',
    'patch scope gate rejected': 'PatchScopeGate 被拒绝',
    'missing new-test evidence': '缺少新增测试证据',
    'new-test evidence failed': '新增测试证据失败',
    'missing regression evidence': '缺少回归证据',
    'regression evidence failed': '回归证据失败',
  };
  return labels[reason] ?? reason;
}

function readStatusDetail(value: unknown): { status: string } {
  if (isRecord(value) && typeof value.status === 'string') {
    return { status: value.status };
  }
  return { status: 'missing' };
}

function qualityEvidenceRow(key: string, label: string, status: string, artifactId?: string) {
  const hasArtifact = typeof artifactId === 'string' && artifactId.length > 0;
  return {
    key,
    label,
    statusLabel: qualityEvidenceStatusLabel(status),
    required: true,
    downloadUrl: hasArtifact ? `/api/artifacts/${artifactId}/download` : '',
    availabilityLabel: status === 'missing' ? '缺失不可打开' : '结构化证据',
  };
}

function qualityEvidenceStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    applied: '已应用',
    passed: '通过',
    succeeded: '成功',
    failed: '失败',
    pending: '待处理',
    missing: '缺失',
  };
  return labels[status] ?? statusLabel(status);
}

function testIntentLabel(intent: string): string {
  const labels: Record<string, string> = {
    'Cover coupon boundary change': '覆盖优惠券边界变更',
  };
  return labels[intent] ?? intent;
}

function runRegressionPlan() {
  void store.runRegressionPlan();
}

function computeGate() {
  void store.computeGate();
}

function generateQualityReport() {
  void store.generateQualityReport();
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
</script>

<style scoped>
.cicd-page {
  display: grid;
  gap: 18px;
}

.cicd-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.cicd-heading h2,
.cicd-heading p {
  margin: 0;
}

.cicd-heading h2 {
  font-size: 26px;
}

.cicd-heading p:not(.eyebrow) {
  margin-top: 10px;
  max-width: 760px;
  color: #5b6472;
  line-height: 1.7;
}

.cicd-layout {
  display: grid;
  grid-template-columns: minmax(340px, 0.72fr) minmax(0, 1.5fr);
  gap: 16px;
}

.cicd-detail {
  display: grid;
  gap: 16px;
}

.cicd-panel {
  border-radius: 8px;
}

.cicd-form {
  display: grid;
  gap: 14px;
}

.cicd-form label {
  display: grid;
  gap: 7px;
  color: #344054;
  font-weight: 700;
}

.ref-grid,
.status-strip {
  display: grid;
  gap: 10px;
}

.ref-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.status-strip {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-bottom: 14px;
}

.status-strip div,
.patch-grid div,
.evidence-grid div,
.import-grid div {
  min-height: 70px;
  padding: 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.status-strip span,
.status-strip strong,
.patch-grid span,
.patch-grid strong,
.evidence-grid span,
.evidence-grid strong,
.import-grid span,
.import-grid strong {
  display: block;
}

.status-strip span,
.patch-grid span,
.evidence-grid span,
.import-grid span {
  color: #64748b;
}

.status-strip strong,
.patch-grid strong,
.evidence-grid strong,
.import-grid strong {
  margin-top: 8px;
  color: #0f172a;
  font-size: 16px;
  word-break: break-all;
}

.action-row {
  margin-bottom: 14px;
}

.patch-grid,
.evidence-grid,
.import-grid {
  display: grid;
  gap: 10px;
}

.patch-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-bottom: 12px;
}

.evidence-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.import-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-bottom: 12px;
}

.evidence-line {
  margin: 8px 0;
  color: #344054;
}

.coverage-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 0;
}

.reference-list {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}

.reference-item {
  display: grid;
  grid-template-columns: minmax(140px, 1.2fr) minmax(100px, 0.7fr) minmax(90px, 0.6fr) minmax(0, 1.7fr);
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #ffffff;
}

.reference-item span,
.reference-item small {
  color: #5b6472;
  word-break: break-all;
}

.patch-diff {
  max-height: 220px;
  overflow: auto;
  padding: 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #0f172a;
  color: #dbeafe;
  font-size: 12px;
  line-height: 1.6;
}

.review-history-panel {
  display: grid;
  gap: 8px;
  margin-top: 16px;
}

.quality-summary-panel {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.quality-summary-panel h3 {
  margin: 0;
  font-size: 16px;
}

.quality-summary-list {
  display: grid;
  gap: 8px;
}

.quality-summary-item {
  display: grid;
  grid-template-columns: minmax(180px, 1.4fr) minmax(90px, 0.7fr) minmax(90px, 0.6fr);
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #ffffff;
}

.quality-summary-item div {
  display: grid;
  gap: 4px;
}

.quality-summary-item span,
.quality-summary-item small,
.muted-text {
  color: #64748b;
}

.blocking-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
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
  .cicd-layout,
  .ref-grid,
  .patch-grid,
  .evidence-grid,
  .import-grid,
  .reference-item,
  .quality-summary-item {
    grid-template-columns: 1fr;
  }

  .status-strip {
    grid-template-columns: repeat(2, minmax(120px, 1fr));
  }
}
</style>
