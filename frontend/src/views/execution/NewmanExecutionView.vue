<template>
  <section class="execution-page" data-test="execution-page-newman" aria-labelledby="newman-execution-title">
    <div class="execution-heading">
      <div>
        <p class="eyebrow">Newman API 执行证据</p>
        <h2 id="newman-execution-title">API 执行</h2>
        <p>从已配置 TestCommand 启动本地 Newman API 集合，并查看请求、断言和工件证据。</p>
      </div>
      <a-space>
        <a-tag color="green">本地 Newman</a-tag>
        <a-tag color="blue">请求 / 断言</a-tag>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" data-test="execution-error-state" type="error" :content="store.errorMessage" show-icon />

    <div class="execution-layout">
      <a-card class="execution-panel" :bordered="false">
        <template #title>执行入口</template>
        <form class="execution-form" data-test="execution-form-newman" @submit.prevent="startRun">
          <label>
            <span>当前项目</span>
            <a-input v-model="store.projectId" data-test="execution-project-id" />
          </label>
          <label>
            <span>测试命令</span>
            <div class="execution-source-control" data-test="execution-source-id">
              <input class="execution-source-compat" v-model="store.testCommandId" aria-hidden="true" tabindex="-1" />
              <a-select v-model="store.testCommandId" allow-clear :loading="store.loadingCommands" placeholder="选择项目中已配置的 Newman 命令" @click="store.loadTestCommands">
                <a-option v-for="command in store.testCommands" :key="command.id" :value="command.id">
                  {{ command.name }} · {{ command.command_type }}
                </a-option>
              </a-select>
            </div>
          </label>
          <a-space wrap>
            <a-button data-test="start-newman-run" html-type="submit" type="primary" :loading="store.loading">
              启动 Newman
            </a-button>
            <a-button data-test="refresh-newman-run" :disabled="!store.run" :loading="store.loading" @click="refreshRun">
              刷新结果
            </a-button>
          </a-space>
        </form>
        <ExecutionRecentRuns />
      </a-card>

      <a-card class="execution-panel execution-result-panel" :bordered="false">
        <template #title>API 证据</template>
        <a-spin :loading="store.loading" :data-test="store.loading ? 'execution-loading-state' : 'execution-ready-state'">
          <template v-if="store.run">
            <div data-test="execution-run-detail">
            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="状态">{{ executionRunStatusLabel(store.run.status) }}</a-descriptions-item>
              <a-descriptions-item label="退出码">{{ store.run.exit_code ?? '运行中' }}</a-descriptions-item>
              <a-descriptions-item label="耗时">{{ durationLabel }}</a-descriptions-item>
              <a-descriptions-item label="集合">{{ collectionName }}</a-descriptions-item>
            </a-descriptions>

            <ExecutionRunManifestPanel :run="store.run" :rows="manifestRows" title-id="newman-run-manifest-title" />

            <ExecutionMetricsPanel :items="metricItems" />

            <ExecutionArtifactTable
              title="Newman 工件"
              title-id="newman-artifacts-title"
              :artifacts="newmanArtifacts"
            />

            <ExecutionResultTable
              title="断言结果"
              title-id="newman-results-title"
              :columns="resultColumns"
              :rows="store.run.test_results"
            />
            </div>
          </template>

          <a-empty v-else data-test="execution-empty-state" description="启动后展示 Newman API 执行证据" />
        </a-spin>
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';

import { useExecutionStore } from '../../stores/execution';
import ExecutionArtifactTable from './ExecutionArtifactTable.vue';
import ExecutionMetricsPanel from './ExecutionMetricsPanel.vue';
import ExecutionResultTable from './ExecutionResultTable.vue';
import ExecutionRunManifestPanel from './ExecutionRunManifestPanel.vue';
import ExecutionRecentRuns from './ExecutionRecentRuns.vue';
import { executionRunDurationLabel, executionRunStatusLabel } from './executionDisplay';
import { newmanOutputArtifacts } from './executionOutputArtifacts';
import { buildExecutionRunManifestRows } from './executionRunManifest';

const store = useExecutionStore();

const resultColumns = [
  { title: '断言', dataIndex: 'test_name' },
  { title: '状态', dataIndex: 'status' },
  { title: '失败信息', dataIndex: 'failure_message' },
];

const durationLabel = computed(() => {
  return executionRunDurationLabel(store.run?.duration_ms ?? null);
});

const collectionName = computed(() => {
  const value = store.run?.parsed_result.collection_name;
  return typeof value === 'string' ? value : '未记录';
});

const metricItems = computed(() => {
  const parsed = store.run?.parsed_result ?? {};
  return [
    { label: '总断言', value: parsed.total ?? 0 },
    { label: '通过', value: parsed.passed ?? 0 },
    { label: '失败', value: parsed.failed ?? 0 },
    { label: '跳过', value: parsed.skipped ?? 0 },
    { label: '请求数', value: parsed.request_count ?? 0 },
    { label: '断言数', value: parsed.assertion_count ?? 0 },
  ];
});

const newmanArtifacts = computed(() => {
  return (store.run?.artifacts ?? []).filter((artifact) =>
    ['stdout', 'stderr', 'newman_json', 'parsed_output', 'junit'].includes(artifact.artifact_type),
  );
});

const manifestRows = computed(() => buildExecutionRunManifestRows(store.run, newmanOutputArtifacts));

function startRun() {
  store.sourceMode = 'test_command';
  void store.startRun({
    runnerMode: 'newman_local',
    reason: 'frontend newman api execution',
  });
}

function refreshRun() {
  void store.refreshRun();
}

onMounted(() => {
  store.sourceMode = 'test_command';
});
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
