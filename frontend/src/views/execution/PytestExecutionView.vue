<template>
  <section class="execution-page" aria-labelledby="execution-title">
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

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <div class="execution-layout">
      <a-card class="execution-panel" :bordered="false">
        <template #title>执行入口</template>
        <form class="execution-form" @submit.prevent="startRun">
          <label>
            <span>项目 ID</span>
            <a-input v-model="store.projectId" />
          </label>
          <label>
            <span>执行来源</span>
            <a-radio-group v-model="store.sourceMode" type="button">
              <a-radio value="automation_draft">AutomationDraft</a-radio>
              <a-radio value="test_command">TestCommand</a-radio>
            </a-radio-group>
          </label>
          <label v-if="store.sourceMode === 'automation_draft'">
            <span>AutomationDraft ID</span>
            <a-input v-model="store.automationDraftId" />
          </label>
          <label v-else>
            <span>TestCommand ID</span>
            <a-input v-model="store.testCommandId" />
          </label>
          <a-space wrap>
            <a-button data-test="start-run" html-type="submit" type="primary" :loading="store.loading">
              启动 pytest
            </a-button>
            <a-button data-test="refresh-run" :disabled="!store.run" :loading="store.loading" @click="refreshRun">
              刷新结果
            </a-button>
          </a-space>
        </form>
      </a-card>

      <a-card class="execution-panel execution-result-panel" :bordered="false">
        <template #title>运行证据</template>
        <a-spin :loading="store.loading">
          <template v-if="store.run">
            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="状态">{{ executionRunStatusLabel(store.run.status) }}</a-descriptions-item>
              <a-descriptions-item label="退出码">{{ store.run.exit_code ?? '运行中' }}</a-descriptions-item>
              <a-descriptions-item label="耗时">{{ durationLabel }}</a-descriptions-item>
              <a-descriptions-item label="运行器">{{ store.run.runner_mode }}</a-descriptions-item>
              <a-descriptions-item label="只读仓库">{{ store.run.repository_readonly ? '是' : '否' }}</a-descriptions-item>
              <a-descriptions-item label="网络">{{ store.run.network_enabled ? '开启' : '关闭' }}</a-descriptions-item>
              <a-descriptions-item label="命令" :span="2">{{ store.run.command }}</a-descriptions-item>
              <a-descriptions-item label="工作目录" :span="2">{{ store.run.working_directory }}</a-descriptions-item>
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
          </template>

          <a-empty v-else description="启动后展示 pytest 执行证据" />
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
import { executionRunDurationLabel, executionRunStatusLabel } from './executionDisplay';
import { pytestOutputArtifacts } from './executionOutputArtifacts';
import { buildExecutionRunManifestRows } from './executionRunManifest';

const store = useExecutionStore();

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

function startRun() {
  void store.startRun();
}

function refreshRun() {
  void store.refreshRun();
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

@media (max-width: 980px) {
  .execution-layout {
    grid-template-columns: 1fr;
  }

}
</style>
