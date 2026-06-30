<template>
  <section class="cicd-page" aria-labelledby="cicd-title">
    <div class="cicd-heading">
      <div>
        <p class="eyebrow">本地 CI/CD 质量</p>
        <h2 id="cicd-title">CI/CD 质量中心</h2>
        <p>从本地 diff 创建 CICDRun，查看变更文件和模拟风险分析证据。</p>
      </div>
      <a-space>
        <a-tag color="green">本地 diff</a-tag>
        <a-tag color="blue">手动 / 本地</a-tag>
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

        <a-card class="cicd-panel" :bordered="false">
          <template #title>风险分析证据</template>
          <template v-if="store.run?.analysis_artifacts.length">
            <a-table
              :columns="artifactColumns"
              :data="store.run.analysis_artifacts"
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
                <strong>{{ riskLevelLabel(store.unitTestPatch.scope_gate_result.risk_level) }}</strong>
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
    pending: '待处理',
    analyzed: '已分析',
    generated: '已生成',
    approved: '已批准',
    rejected: '已拒绝',
    passed: '通过',
    failed: '失败',
    needs_review: '需要复核',
  };
  return labels[status] ?? status;
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
.evidence-grid div {
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
.evidence-grid strong {
  display: block;
}

.status-strip span,
.patch-grid span,
.evidence-grid span {
  color: #64748b;
}

.status-strip strong,
.patch-grid strong,
.evidence-grid strong {
  margin-top: 8px;
  color: #0f172a;
  font-size: 16px;
  word-break: break-all;
}

.action-row {
  margin-bottom: 14px;
}

.patch-grid,
.evidence-grid {
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

@media (max-width: 980px) {
  .cicd-layout,
  .ref-grid,
  .patch-grid,
  .evidence-grid {
    grid-template-columns: 1fr;
  }

  .status-strip {
    grid-template-columns: repeat(2, minmax(120px, 1fr));
  }
}
</style>
