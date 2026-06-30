<template>
  <section class="execution-page" aria-labelledby="newman-execution-title">
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
            <span>TestCommand ID</span>
            <a-input v-model="store.testCommandId" />
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
      </a-card>

      <a-card class="execution-panel execution-result-panel" :bordered="false">
        <template #title>API 证据</template>
        <a-spin :loading="store.loading">
          <template v-if="store.run">
            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="状态">{{ runStatusLabel(store.run.status) }}</a-descriptions-item>
              <a-descriptions-item label="退出码">{{ store.run.exit_code ?? '运行中' }}</a-descriptions-item>
              <a-descriptions-item label="耗时">{{ durationLabel }}</a-descriptions-item>
              <a-descriptions-item label="运行器">{{ store.run.runner_mode }}</a-descriptions-item>
              <a-descriptions-item label="网络">{{ store.run.network_enabled ? '开启' : '关闭' }}</a-descriptions-item>
              <a-descriptions-item label="集合">{{ collectionName }}</a-descriptions-item>
              <a-descriptions-item label="命令" :span="2">{{ store.run.command }}</a-descriptions-item>
            </a-descriptions>

            <div class="result-metrics">
              <div v-for="item in metricItems" :key="item.label" class="metric-tile">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>

            <section class="evidence-section">
              <h3>Newman 工件</h3>
              <a-table
                :columns="artifactColumns"
                :data="newmanArtifacts"
                :pagination="false"
                row-key="id"
                size="small"
              />
            </section>

            <section class="evidence-section">
              <h3>断言结果</h3>
              <a-table
                :columns="resultColumns"
                :data="store.run.test_results"
                :pagination="false"
                row-key="id"
                size="small"
              />
            </section>
          </template>

          <a-empty v-else description="启动后展示 Newman API 执行证据" />
        </a-spin>
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';

import { useExecutionStore } from '../../stores/execution';

const store = useExecutionStore();

const artifactColumns = [
  { title: '类型', dataIndex: 'artifact_type' },
  { title: '路径', dataIndex: 'file_path' },
  { title: 'MIME', dataIndex: 'mime_type' },
];

const resultColumns = [
  { title: '断言', dataIndex: 'test_name' },
  { title: '状态', dataIndex: 'status' },
  { title: '失败信息', dataIndex: 'failure_message' },
];

const durationLabel = computed(() => {
  if (!store.run || store.run.duration_ms === null) {
    return '运行中';
  }
  return `${store.run.duration_ms} ms`;
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

function runStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    passed: '通过',
    failed: '失败',
    running: '运行中',
    pending: '排队中',
    error: '错误',
    timeout: '超时',
  };
  return labels[status] ?? status;
}

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

.result-metrics {
  display: grid;
  grid-template-columns: repeat(6, minmax(86px, 1fr));
  gap: 10px;
  margin-top: 16px;
}

.metric-tile {
  min-height: 72px;
  padding: 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.metric-tile span,
.metric-tile strong {
  display: block;
}

.metric-tile span {
  color: #64748b;
}

.metric-tile strong {
  margin-top: 8px;
  color: #0f172a;
  font-size: 22px;
}

.evidence-section {
  margin-top: 18px;
}

.evidence-section h3 {
  margin: 0 0 10px;
  font-size: 16px;
}

@media (max-width: 980px) {
  .execution-layout {
    grid-template-columns: 1fr;
  }

  .result-metrics {
    grid-template-columns: repeat(2, minmax(120px, 1fr));
  }
}
</style>
