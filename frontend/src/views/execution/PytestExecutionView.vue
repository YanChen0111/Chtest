<template>
  <section class="execution-page" data-test="execution-page-pytest" aria-labelledby="execution-title">
    <div class="execution-heading">
      <div>
        <p class="eyebrow">pytest 执行证据</p>
        <h2 id="execution-title">执行中心</h2>
        <p>从已批准自动化草稿或已配置 TestCommand 启动本地 pytest，并查看本次运行证据。</p>
      </div>
      <a-space>
        <a-tag color="green">本地子进程</a-tag>
        <a-tag color="blue">仅 pytest</a-tag>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" data-test="execution-error-state" type="error" :content="store.errorMessage" show-icon />

    <div class="execution-layout">
      <a-card class="execution-panel" :bordered="false">
        <template #title>执行入口</template>
        <form class="execution-form" data-test="execution-form-pytest" @submit.prevent="startRun">
          <label>
            <span>当前项目</span>
            <a-input :model-value="store.projectId" data-test="execution-project-id" readonly />
          </label>
          <label>
            <span>执行来源</span>
            <a-radio-group v-model="store.sourceMode" type="button">
              <a-radio value="automation_draft">AutomationDraft</a-radio>
              <a-radio value="test_command">TestCommand</a-radio>
            </a-radio-group>
          </label>
          <label v-if="store.sourceMode === 'automation_draft'">
            <span>已批准自动化草稿</span>
            <a-input
              class="execution-source-compat-input"
              :model-value="store.automationDraftId"
              data-test="execution-source-id"
              readonly
              placeholder="请先在自动化草稿页批准草稿"
            />
          </label>
          <section
            v-if="store.sourceMode === 'automation_draft' && store.requirementReviewId"
            class="execution-approval-panel"
            data-test="execution-approval-panel"
          >
            <div class="execution-approval-heading">
              <strong>ExecutionApproval gate</strong>
              <a-tag :color="store.executionApprovalWorkflow?.workflow.state === 'approved' ? 'green' : 'orange'">
                {{ executionApprovalStateLabel }}
              </a-tag>
            </div>
            <div class="execution-approval-body">
              <span>snapshot</span>
              <strong>{{ store.executionApprovalWorkflow?.workflow.snapshot_id ?? 'not loaded' }}</strong>
              <span>approval</span>
              <strong>{{ store.executionApprovalWorkflow?.workflow.approval_decision_id ?? 'none' }}</strong>
            </div>
            <a-space wrap>
              <a-button data-test="execution-approval-submit" :disabled="!store.executionApprovalWorkflow?.workflow.can_submit" :loading="store.loading" @click="runExecutionApprovalAction('submit')">
                Submit
              </a-button>
              <a-button data-test="execution-approval-complete" :disabled="!store.executionApprovalWorkflow?.workflow.can_complete_review" :loading="store.loading" @click="runExecutionApprovalAction('complete')">
                Complete review
              </a-button>
              <a-button data-test="execution-approval-edit" :disabled="!store.executionApprovalWorkflow?.workflow.can_edit" :loading="store.loading" @click="runExecutionApprovalAction('edit')">
                Save snapshot
              </a-button>
              <a-button data-test="execution-approval-approve" type="primary" :disabled="!store.executionApprovalWorkflow?.workflow.can_approve" :loading="store.loading" @click="runExecutionApprovalAction('approve')">
                Approve
              </a-button>
              <a-button data-test="execution-approval-reject" status="danger" :disabled="!store.executionApprovalWorkflow?.workflow.can_approve" :loading="store.loading" @click="runExecutionApprovalAction('reject')">
                Reject
              </a-button>
              <a-button data-test="execution-approval-continue" :disabled="!store.executionApprovalWorkflow?.workflow.can_continue" :loading="store.loading" @click="runExecutionApprovalAction('continue')">
                Continue
              </a-button>
            </a-space>
          </section>
          <label v-if="store.sourceMode === 'test_command'">
              <span>测试命令</span>
            <div class="execution-source-control" data-test="execution-source-id">
              <input class="execution-source-compat" v-model="store.testCommandId" aria-hidden="true" tabindex="-1" />
              <a-select
                v-model="store.testCommandId"
                allow-clear
                :loading="store.loadingCommands"
                placeholder="选择项目中已配置的 TestCommand"
                @click="store.loadTestCommands"
              >
                <a-option v-for="command in store.testCommands" :key="command.id" :value="command.id">
                  {{ command.name }} · {{ command.command_type }}
                </a-option>
              </a-select>
            </div>
          </label>
          <a-space wrap>
            <a-button
              data-test="start-run"
              html-type="submit"
              type="primary"
              :disabled="!canStartRun"
              :loading="store.loading"
            >
              启动 pytest
            </a-button>
            <a-button data-test="refresh-run" :disabled="!store.run" :loading="store.loading" @click="refreshRun">
              刷新结果
            </a-button>
          </a-space>
          <p v-if="startHint" class="execution-start-hint" data-test="execution-start-hint">{{ startHint }}</p>
          <p v-else class="execution-start-hint">执行只会使用已批准草稿或项目中已配置的 TestCommand，并自动记录运行证据。</p>
        </form>
        <ExecutionRecentRuns />
      </a-card>

      <a-card class="execution-panel execution-result-panel" :bordered="false">
        <template #title>运行证据</template>
        <a-spin :loading="store.loading" :data-test="store.loading ? 'execution-loading-state' : 'execution-ready-state'">
          <template v-if="store.run">
            <div data-test="execution-run-detail">
            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="状态">{{ executionRunStatusLabel(store.run.status) }}</a-descriptions-item>
              <a-descriptions-item label="退出码">{{ store.run.exit_code ?? '运行中' }}</a-descriptions-item>
              <a-descriptions-item label="耗时">{{ durationLabel }}</a-descriptions-item>
            </a-descriptions>

            <ExecutionRunManifestPanel :run="store.run" :rows="manifestRows" title-id="run-manifest-title" />

            <ExecutionMetricsPanel :items="metricItems" />

            <ExecutionArtifactTable title="工件" title-id="pytest-artifacts-title" :artifacts="store.run.artifacts" />

            <ExecutionResultTable
              title="测试结果"
              title-id="pytest-results-title"
              :columns="resultColumns"
              :rows="store.run.test_results"
            />
            </div>
          </template>

          <a-empty v-else data-test="execution-empty-state" description="启动后展示 pytest 执行证据" />
        </a-spin>
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { useExecutionStore } from '../../stores/execution';
import ExecutionArtifactTable from './ExecutionArtifactTable.vue';
import ExecutionMetricsPanel from './ExecutionMetricsPanel.vue';
import ExecutionResultTable from './ExecutionResultTable.vue';
import ExecutionRunManifestPanel from './ExecutionRunManifestPanel.vue';
import ExecutionRecentRuns from './ExecutionRecentRuns.vue';
import { executionRunDurationLabel, executionRunStatusLabel } from './executionDisplay';
import { pytestOutputArtifacts } from './executionOutputArtifacts';
import { buildExecutionRunManifestRows } from './executionRunManifest';

const store = useExecutionStore();
if (store.automationDraftFramework && store.automationDraftFramework !== 'pytest') {
  store.automationDraftId = '';
}
void store.loadExecutionApprovalWorkflow();

const resultColumns = [
  { title: '测试', dataIndex: 'test_name' },
  { title: '状态', dataIndex: 'status' },
  { title: '耗时', dataIndex: 'duration_ms' },
  { title: '失败信息', dataIndex: 'failure_message' },
];

const durationLabel = computed(() => {
  return executionRunDurationLabel(store.run?.duration_ms ?? null);
});

const metricItems = computed(() => {
  const parsed = store.run?.parsed_result ?? {};
  return [
    { label: '总数', value: parsed.total ?? 0 },
    { label: '通过', value: parsed.passed ?? 0 },
    { label: '失败', value: parsed.failed ?? 0 },
    { label: '跳过', value: parsed.skipped ?? 0 },
    { label: '错误', value: parsed.error ?? 0 },
  ];
});

const manifestRows = computed(() => buildExecutionRunManifestRows(store.run, pytestOutputArtifacts));
const startHint = computed(() => {
  if (store.sourceMode === 'automation_draft' && !store.automationDraftId) {
    return '请先在自动化草稿页选择用例、生成并批准草稿。';
  }
  if (
    store.sourceMode === 'automation_draft'
    && store.requirementReviewId
    && !store.executionApprovalWorkflow?.workflow.approval_decision_id
  ) {
    return 'ExecutionApproval gate must be approved before starting this AutomationDraft run.';
  }
  if (store.sourceMode === 'test_command' && !store.testCommandId) {
    return '请输入或选择项目中已配置的 TestCommand。';
  }
  return '';
});
const canStartRun = computed(() => !startHint.value);
const executionApprovalStateLabel = computed(() => store.executionApprovalWorkflow?.workflow.state ?? 'not_loaded');

function startRun() {
  void store.startRun();
}

function refreshRun() {
  void store.refreshRun();
}

function runExecutionApprovalAction(
  action: 'submit' | 'complete' | 'edit' | 'approve' | 'reject' | 'continue',
) {
  const operations = {
    submit: () => store.submitExecutionApprovalGate(),
    complete: () => store.completeExecutionApprovalGate(),
    edit: () => store.editExecutionApprovalGate(),
    approve: () => store.approveExecutionApprovalGate('Approved for controlled local pytest execution.'),
    reject: () => store.rejectExecutionApprovalGate('Execution approval rejected.'),
    continue: () => store.continueExecutionApprovalGate(),
  };
  void operations[action]();
}

</script>

<style scoped>
.execution-page {
  display: grid;
  gap: 18px;
}

.execution-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.execution-heading h2,
.execution-heading p {
  margin: 0;
}

.execution-heading h2 {
  font-size: 26px;
}

.execution-heading p:not(.eyebrow) {
  margin-top: 10px;
  max-width: 760px;
  color: #5b6472;
  line-height: 1.7;
}

.execution-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.72fr) minmax(0, 1.5fr);
  gap: 16px;
}

.execution-panel {
  border-radius: 8px;
}

.execution-form {
  display: grid;
  gap: 14px;
}

.execution-form label {
  display: grid;
  gap: 7px;
  color: #344054;
  font-weight: 700;
}

.execution-start-hint {
  margin: 0;
  color: #d46b08;
  line-height: 1.5;
}

.execution-approval-panel {
  display: grid;
  gap: 10px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f8fafc;
}

.execution-approval-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.execution-approval-body {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 6px 10px;
  color: #5b6472;
}

.execution-approval-body strong {
  min-width: 0;
  overflow-wrap: anywhere;
  color: #111827;
}

@media (max-width: 980px) {
  .execution-layout {
    grid-template-columns: 1fr;
  }

}
</style>
