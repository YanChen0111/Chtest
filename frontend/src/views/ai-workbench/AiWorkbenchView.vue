<template>
  <section class="ai-workbench-page" aria-labelledby="ai-workbench-title">
    <div class="workbench-heading">
      <div>
        <p class="eyebrow">Evidence Loop</p>
        <h2 id="ai-workbench-title">AI 工作台</h2>
        <p>查看最近 AI 任务、上下文使用、工件安全标记和大模型调用日志，先确认状态再进入评审动作。</p>
      </div>
      <a-space>
        <a-tag color="blue">单用户本地项目</a-tag>
        <a-button type="primary" :loading="store.loadingList" @click="refreshWorkbench">刷新</a-button>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <a-card class="health-card status-panel" :bordered="false">
      <div class="health-row">
        <div>
          <p class="health-label">后端健康</p>
          <strong>{{ healthLabel }}</strong>
        </div>
        <span class="health-detail">{{ healthDetail }}</span>
      </div>
    </a-card>

    <div class="ai-metric-grid">
      <a-card v-for="metric in metrics" :key="metric.label" class="ai-metric-card" :bordered="false">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
      </a-card>
    </div>

    <div class="ai-task-layout">
      <a-card class="task-panel" :bordered="false">
        <template #title>最近 AI 任务</template>
        <a-spin :loading="store.loadingList">
          <a-table
            :columns="taskColumns"
            :data="taskRows"
            :pagination="false"
            row-key="id"
            size="small"
            @row-click="selectTask"
          >
            <template #status="{ record }">
              <a-tag :color="statusColor(record.status)">{{ statusLabel(record.status) }}</a-tag>
            </template>
            <template #contextCount="{ record }">
              {{ record.context_artifact_ids.length }}
            </template>
          </a-table>
          <a-empty v-if="!store.loadingList && store.tasks.length === 0" description="暂无 AI 任务" />
        </a-spin>
      </a-card>

      <a-card class="task-panel detail-panel" :bordered="false">
        <template #title>任务详情</template>
        <a-spin :loading="store.loadingDetail">
          <template v-if="store.selectedTask">
            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="Agent">{{ store.selectedTask.agent_name }}</a-descriptions-item>
              <a-descriptions-item label="状态">
                <a-tag :color="statusColor(store.selectedTask.status)">
                  {{ statusLabel(store.selectedTask.status) }}
                </a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="Prompt">{{ store.selectedTask.prompt_version_id }}</a-descriptions-item>
              <a-descriptions-item label="Skill">{{ store.selectedTask.skill_version_id }}</a-descriptions-item>
              <a-descriptions-item label="模型">
                {{ store.selectedTask.model_provider }} / {{ store.selectedTask.model_name }}
              </a-descriptions-item>
              <a-descriptions-item label="Token">
                {{ compactJson(store.selectedTask.token_usage) }}
              </a-descriptions-item>
              <a-descriptions-item label="上下文工件" :span="2">
                {{ idListText(store.selectedTask.context_artifact_ids) }}
              </a-descriptions-item>
              <a-descriptions-item label="已使用上下文" :span="2">
                {{ idListText(store.selectedTask.used_context_artifact_ids) }}
              </a-descriptions-item>
            </a-descriptions>

            <div class="detail-section">
              <h3>工件摘要</h3>
              <a-table
                :columns="artifactColumns"
                :data="artifactRows"
                :pagination="false"
                row-key="id"
                size="small"
              >
                <template #safe="{ record }">
                  <a-tag :color="record.safe_to_show ? 'green' : 'orange'">
                    {{ record.safe_to_show ? '可展示' : '不可直接展示' }}
                  </a-tag>
                </template>
              </a-table>
            </div>

            <div class="detail-section">
              <h3>大模型调用日志</h3>
              <a-table
                :columns="llmCallColumns"
                :data="llmCallRows"
                :pagination="false"
                row-key="id"
                size="small"
              >
                <template #status="{ record }">
                  <a-tag :color="statusColor(record.status)">{{ statusLabel(record.status) }}</a-tag>
                </template>
              </a-table>
            </div>
          </template>

          <a-empty v-else-if="!store.loadingDetail" description="请选择一个 AI 任务查看详情" />
        </a-spin>
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import type { TableData } from '@arco-design/web-vue';

import { getBackendHealth } from '../../api/health';
import { useAITasksStore } from '../../stores/aiTasks';

const store = useAITasksStore();

const healthLabel = ref('检测中');
const healthDetail = ref('正在检查后端 /health');

const taskColumns = [
  { title: 'Agent', dataIndex: 'agent_name' },
  { title: '任务类型', dataIndex: 'task_type' },
  { title: '状态', slotName: 'status' },
  { title: '模型', dataIndex: 'model_name' },
  { title: '上下文数', slotName: 'contextCount' },
];

const artifactColumns = [
  { title: '工件类型', dataIndex: 'artifact_type' },
  { title: 'MIME', dataIndex: 'mime_type' },
  { title: '路径', dataIndex: 'file_path' },
  { title: '大小', dataIndex: 'sizeText' },
  { title: 'SHA256', dataIndex: 'sha256' },
  { title: '展示安全', slotName: 'safe' },
  { title: '脱敏状态', dataIndex: 'redactionText' },
];

const llmCallColumns = [
  { title: '序号', dataIndex: 'call_index' },
  { title: 'Provider', dataIndex: 'provider' },
  { title: '模型', dataIndex: 'model_name' },
  { title: '状态', slotName: 'status' },
  { title: '响应工件', dataIndex: 'responseArtifactText' },
  { title: '耗时', dataIndex: 'latencyText' },
  { title: 'Token', dataIndex: 'tokenUsageText' },
];

const metrics = computed(() => [
  { label: '最近 AI 任务', value: String(store.totalTasks) },
  { label: '运行中', value: String(store.runningTasks) },
  { label: '失败任务', value: String(store.failedTasks) },
  { label: '上下文工件', value: String(store.contextArtifactCount) },
]);

const taskRows = computed(() => store.tasks);
const artifactRows = computed(
  () =>
    store.selectedTask?.artifacts.map((artifact) => ({
      ...artifact,
      sizeText: `${artifact.size_bytes} B`,
      redactionText: artifact.redaction_applied ? '已脱敏' : '未脱敏',
    })) ?? [],
);
const llmCallRows = computed(
  () =>
    store.selectedTask?.llm_call_logs.map((callLog) => ({
      ...callLog,
      responseArtifactText: callLog.response_artifact_id ?? '无',
      latencyText: callLog.latency_ms === null ? '未记录' : `${callLog.latency_ms} ms`,
      tokenUsageText: compactJson(callLog.token_usage_json),
    })) ?? [],
);

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    created: '已创建',
    pending: '排队中',
    running: '运行中',
    succeeded: '成功',
    failed: '失败',
    cancelled: '已取消',
    timeout: '超时',
    schema_invalid: '结构异常',
  };
  return labels[status] ?? status;
}

function statusColor(status: string): string {
  const colors: Record<string, string> = {
    created: 'gray',
    pending: 'orange',
    running: 'blue',
    succeeded: 'green',
    failed: 'red',
    cancelled: 'gray',
    timeout: 'orange',
    schema_invalid: 'orange',
  };
  return colors[status] ?? 'gray';
}

function compactJson(value: Record<string, unknown>): string {
  return Object.entries(value)
    .map(([key, rawValue]) => `${key}: ${String(rawValue)}`)
    .join(', ');
}

function idListText(ids: string[]): string {
  return ids.length > 0 ? ids.join(', ') : '无';
}

function selectTask(task: TableData) {
  if (typeof task.id === 'string') {
    void store.loadTaskDetail(task.id);
  }
}

async function refreshHealth() {
  const result = await getBackendHealth();
  healthLabel.value = result.state;
  healthDetail.value = result.rawText;
}

function refreshWorkbench() {
  void refreshHealth();
  void store.loadRecentTasks();
}

onMounted(() => {
  refreshWorkbench();
});
</script>

<style scoped>
.ai-workbench-page {
  display: grid;
  gap: 18px;
}

.workbench-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.workbench-heading h2,
.workbench-heading p {
  margin: 0;
}

.workbench-heading h2 {
  font-size: 26px;
}

.workbench-heading p:not(.eyebrow) {
  margin-top: 10px;
  max-width: 820px;
  color: #4e5969;
  line-height: 1.7;
}

.status-panel,
.ai-metric-card,
.task-panel {
  border-radius: 8px;
}

.health-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.health-label {
  margin: 0 0 6px;
  color: #86909c;
}

.health-detail {
  color: #4e5969;
}

.ai-metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.ai-metric-card span,
.ai-metric-card strong {
  display: block;
}

.ai-metric-card span {
  color: #4e5969;
}

.ai-metric-card strong {
  margin-top: 8px;
  font-size: 26px;
}

.ai-task-layout {
  display: grid;
  grid-template-columns: minmax(420px, 0.95fr) minmax(520px, 1.3fr);
  gap: 16px;
  align-items: start;
}

.detail-panel {
  min-width: 0;
}

.detail-section {
  margin-top: 16px;
}

.detail-section h3 {
  margin: 0 0 10px;
  color: #1d2129;
  font-size: 15px;
}

@media (max-width: 1120px) {
  .ai-task-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .workbench-heading,
  .health-row {
    display: grid;
  }

  .ai-metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .ai-metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
