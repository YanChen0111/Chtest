<template>
  <section class="execution-page" data-test="execution-page-jmeter" aria-labelledby="jmeter-execution-title">
    <div class="execution-heading">
      <div>
        <p class="eyebrow">JMeter 执行证据</p>
        <h2 id="jmeter-execution-title">JMeter 执行</h2>
        <p>从已配置 TestCommand 启动本地 JMeter non-GUI 运行，并查看 Sampler、断言、JTL 和工件证据。</p>
      </div>
      <a-space>
        <a-tag color="green">本地 JMeter</a-tag>
        <a-tag color="blue">JTL / Sampler</a-tag>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" data-test="execution-error-state" type="error" :content="store.errorMessage" show-icon />

    <div class="execution-layout">
      <a-card class="execution-panel" :bordered="false">
        <template #title>执行入口</template>
        <form class="execution-form" data-test="execution-form-jmeter" @submit.prevent="startRun">
          <label>
            <span>当前项目</span>
            <a-input v-model="store.projectId" data-test="execution-project-id" />
          </label>
          <label>
            <span>测试命令</span>
            <div class="execution-source-control" data-test="execution-source-id">
              <input class="execution-source-compat" v-model="store.testCommandId" aria-hidden="true" tabindex="-1" />
              <a-select v-model="store.testCommandId" allow-clear :loading="store.loadingCommands" placeholder="选择项目中已配置的 JMeter 命令" @click="store.loadTestCommands">
                <a-option v-for="command in store.testCommands" :key="command.id" :value="command.id">
                  {{ command.name }} · {{ command.command_type }}
                </a-option>
              </a-select>
            </div>
          </label>
          <a-space wrap>
            <a-button data-test="start-jmeter-run" html-type="submit" type="primary" :loading="store.loading">
              启动 JMeter
            </a-button>
            <a-button data-test="refresh-jmeter-run" :disabled="!store.run" :loading="store.loading" @click="refreshRun">
              刷新结果
            </a-button>
          </a-space>
        </form>
        <ExecutionRecentRuns />
      </a-card>

      <a-card class="execution-panel execution-result-panel" :bordered="false">
        <template #title>JMeter 证据</template>
        <a-spin :loading="store.loading" :data-test="store.loading ? 'execution-loading-state' : 'execution-ready-state'">
          <template v-if="store.run">
            <div data-test="execution-run-detail">
            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="状态">{{ executionRunStatusLabel(store.run.status) }}</a-descriptions-item>
              <a-descriptions-item label="退出码">{{ store.run.exit_code ?? '运行中' }}</a-descriptions-item>
              <a-descriptions-item label="耗时">{{ durationLabel }}</a-descriptions-item>
              <a-descriptions-item label="JTL 统计耗时">{{ parsedDurationLabel }}</a-descriptions-item>
            </a-descriptions>

            <ExecutionRunManifestPanel :run="store.run" :rows="manifestRows" title-id="jmeter-run-manifest-title" />

            <ExecutionMetricsPanel :items="metricItems" />

            <ExecutionArtifactTable
              title="JMeter 工件"
              title-id="jmeter-artifacts-title"
              :artifacts="jmeterArtifacts"
            />

            <ExecutionResultTable
              title="Sampler 结果"
              title-id="jmeter-results-title"
              :columns="resultColumns"
              :rows="resultRows"
            />
            </div>
          </template>

          <a-empty v-else data-test="execution-empty-state" description="启动后展示 JMeter 执行证据" />
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
import { jmeterOutputArtifacts } from './executionOutputArtifacts';
import { buildExecutionRunManifestRows } from './executionRunManifest';

const store = useExecutionStore();

const resultColumns = [
  { title: 'Sampler', dataIndex: 'test_name' },
  { title: '状态', dataIndex: 'status_label' },
  { title: '耗时', dataIndex: 'duration_label' },
  { title: '失败信息', dataIndex: 'failure_message' },
];

const durationLabel = computed(() => {
  return executionRunDurationLabel(store.run?.duration_ms ?? null);
});

const parsedDurationLabel = computed(() => {
  const value = store.run?.parsed_result.duration_ms;
  return typeof value === 'number' ? `${value} ms` : '未记录';
});

const metricItems = computed(() => {
  const parsed = store.run?.parsed_result ?? {};
  return [
    { label: '总样本', value: parsed.total ?? 0 },
    { label: '通过', value: parsed.passed ?? 0 },
    { label: '失败', value: parsed.failed ?? 0 },
    { label: '错误', value: parsed.error ?? 0 },
    { label: 'Sampler 数', value: parsed.sampler_count ?? 0 },
    { label: '断言数', value: parsed.assertion_count ?? 0 },
    { label: '平均延迟', value: formatMs(parsed.average_latency_ms) },
  ];
});

const jmeterArtifacts = computed(() => {
  return (store.run?.artifacts ?? []).filter((artifact) =>
    ['stdout', 'stderr', 'jmeter_jtl', 'parsed_output'].includes(artifact.artifact_type),
  );
});

const manifestRows = computed(() => buildExecutionRunManifestRows(store.run, jmeterOutputArtifacts));

const resultRows = computed(() => {
  return (store.run?.test_results ?? []).map((result) => ({
    ...result,
    status_label: executionRunStatusLabel(result.status),
    duration_label: result.duration_ms === null ? '未记录' : `${result.duration_ms} ms`,
    failure_message: result.failure_message ?? '无',
  }));
});

function formatMs(value: number | string | undefined): string | number {
  return typeof value === 'number' ? `${value} ms` : (value ?? 0);
}

function startRun() {
  store.sourceMode = 'test_command';
  void store.startRun({
    runnerMode: 'jmeter_local',
    reason: 'frontend jmeter execution',
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

  .execution-heading {
    display: grid;
  }
}

</style>
