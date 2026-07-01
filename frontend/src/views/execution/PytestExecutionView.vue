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
              <a-descriptions-item label="状态">{{ runStatusLabel(store.run.status) }}</a-descriptions-item>
              <a-descriptions-item label="退出码">{{ store.run.exit_code ?? '运行中' }}</a-descriptions-item>
              <a-descriptions-item label="耗时">{{ durationLabel }}</a-descriptions-item>
              <a-descriptions-item label="运行器">{{ store.run.runner_mode }}</a-descriptions-item>
              <a-descriptions-item label="只读仓库">{{ store.run.repository_readonly ? '是' : '否' }}</a-descriptions-item>
              <a-descriptions-item label="网络">{{ store.run.network_enabled ? '开启' : '关闭' }}</a-descriptions-item>
              <a-descriptions-item label="命令" :span="2">{{ store.run.command }}</a-descriptions-item>
              <a-descriptions-item label="工作目录" :span="2">{{ store.run.working_directory }}</a-descriptions-item>
            </a-descriptions>

            <div class="result-metrics">
              <div v-for="item in metricItems" :key="item.label" class="metric-tile">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>

            <section class="evidence-section">
              <h3>工件</h3>
              <a-table
                :columns="artifactColumns"
                :data="store.run.artifacts"
                :pagination="false"
                row-key="id"
                size="small"
              >
                <template #action="{ record }">
                  <a :href="artifactDownloadUrl(record.id)" target="_blank" rel="noreferrer">打开</a>
                </template>
              </a-table>
            </section>

            <section class="evidence-section">
              <h3>测试结果</h3>
              <a-table
                :columns="resultColumns"
                :data="store.run.test_results"
                :pagination="false"
                row-key="id"
                size="small"
              />
            </section>
          </template>

          <a-empty v-else description="启动后展示 pytest 执行证据" />
        </a-spin>
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { artifactDownloadUrl } from '../../api/execution';
import { useExecutionStore } from '../../stores/execution';

const store = useExecutionStore();

const artifactColumns = [
  { title: '类型', dataIndex: 'artifact_type' },
  { title: '路径', dataIndex: 'file_path' },
  { title: '大小', dataIndex: 'size_bytes' },
  { title: 'Artifact', slotName: 'action' },
];

const resultColumns = [
  { title: '测试', dataIndex: 'test_name' },
  { title: '状态', dataIndex: 'status' },
  { title: '耗时', dataIndex: 'duration_ms' },
  { title: '失败信息', dataIndex: 'failure_message' },
];

const durationLabel = computed(() => {
  if (!store.run || store.run.duration_ms === null) {
    return '运行中';
  }
  return `${store.run.duration_ms} ms`;
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

function runStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    passed: '通过',
    failed: '失败',
    running: '运行中',
    pending: '排队中',
    error: '错误',
  };
  return labels[status] ?? status;
}

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

.result-metrics {
  display: grid;
  grid-template-columns: repeat(5, minmax(86px, 1fr));
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
