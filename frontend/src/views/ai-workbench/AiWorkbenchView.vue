<template>
  <section class="ai-workbench-page" aria-labelledby="ai-workbench-title">
    <div class="workbench-heading">
      <div>
        <p class="eyebrow">证据闭环</p>
        <h2 id="ai-workbench-title">AI 工作台</h2>
        <p>查看最近 AI 任务、上下文使用、工件安全标记和大模型调用日志，先确认状态再进入评审动作。</p>
      </div>
      <a-space>
        <a-tag color="blue">单用户本地项目</a-tag>
        <a-button type="primary" :loading="store.loadingList || store.loadingWorkflowQueue" @click="refreshWorkbench">刷新</a-button>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <div class="status-grid">
      <a-card class="health-card status-panel" :bordered="false">
        <div class="health-row">
          <div>
            <p class="health-label">后端健康</p>
            <strong>{{ healthLabel }}</strong>
          </div>
          <span class="health-detail">{{ healthDetail }}</span>
        </div>
      </a-card>

      <a-card class="health-card status-panel" :bordered="false">
        <div class="health-row">
          <div>
            <p class="health-label">&#27169;&#22411;&#26381;&#21153;</p>
            <strong>{{ modelConnectionLabel }}</strong>
          </div>
          <span class="health-detail">{{ modelConnectionDetail }}</span>
        </div>
      </a-card>
    </div>

    <div class="ai-metric-grid">
      <a-card v-for="metric in metrics" :key="metric.label" class="ai-metric-card" :bordered="false">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
      </a-card>
    </div>

    <a-card class="task-panel workflow-queue-panel" :bordered="false" data-test="workflow-queue-panel">
      <template #title>流程待办</template>
      <div
        v-if="store.workflowQueueError"
        class="workflow-queue-error"
        role="alert"
        data-test="workflow-queue-error"
      >
        {{ store.workflowQueueError }}
      </div>
      <div v-if="store.loadingWorkflowQueue" class="muted-text" data-test="workflow-queue-loading">
        正在加载流程待办...
      </div>
      <div v-else class="workflow-queue-groups">
        <section
          v-for="group in workflowQueueGroups"
          :key="group.bucket"
          class="workflow-queue-group"
          :class="{ 'workflow-queue-group--empty': !group.items.length }"
          :data-test="`workflow-queue-${group.bucket}`"
        >
          <div class="workflow-queue-heading">
            <strong>{{ group.title }}</strong>
            <a-tag color="blue">{{ group.items.length }}</a-tag>
          </div>
          <a-table
            v-if="group.items.length"
            :columns="workflowQueueColumns"
            :data="group.items"
            :pagination="false"
            row-key="id"
            size="small"
          >
            <template #stage="{ record }">
              <a-tag :color="workflowStageColor(record.gate_state)">{{ workflowStageLabel(record.current_stage) }}</a-tag>
            </template>
            <template #snapshot="{ record }">
              <span class="workflow-snapshot">{{ record.current_snapshot_id }}</span>
            </template>
            <template #open="{ record }">
              <a v-if="record.route_path" :href="record.route_path" data-test="workflow-queue-open">打开</a>
              <span v-else class="muted-text">暂无入口</span>
            </template>
          </a-table>
          <a-empty v-else class="detail-empty" description="暂无待办" />
        </section>
      </div>
    </a-card>

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
              <a-descriptions-item label="智能体">{{ readableAgentName(store.selectedTask.agent_name) }}</a-descriptions-item>
              <a-descriptions-item label="状态">
                <a-tag :color="statusColor(store.selectedTask.status)">
                  {{ statusLabel(store.selectedTask.status) }}
                </a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="模型">
                {{ store.selectedTask.model_provider }} / {{ readableModelName(store.selectedTask.model_name) }}
              </a-descriptions-item>
              <a-descriptions-item label="令牌用量">
                {{ compactJson(store.selectedTask.token_usage) }}
              </a-descriptions-item>
              <a-descriptions-item label="上下文工件" :span="2">
                {{ contextUsageLabel(store.selectedTask.context_artifact_ids, '已关联') }}
              </a-descriptions-item>
              <a-descriptions-item label="已使用上下文" :span="2">
                {{ contextUsageLabel(store.selectedTask.used_context_artifact_ids, '本次使用') }}
              </a-descriptions-item>
            </a-descriptions>

            <a-collapse class="technical-trace-collapse" :default-active-key="[]">
              <a-collapse-item key="trace" title="查看执行追踪">
                <a-descriptions :column="2" bordered size="small">
                  <a-descriptions-item label="提示词版本">
                    {{ store.selectedTask.prompt_version_id ? '已记录，可在 Prompt / Skill 中心追溯' : '未记录' }}
                  </a-descriptions-item>
                  <a-descriptions-item label="技能版本">
                    {{ store.selectedTask.skill_version_id ? '已记录，可在 Prompt / Skill 中心追溯' : '未记录' }}
                  </a-descriptions-item>
                  <a-descriptions-item label="上下文清单证据" :span="2">
                    <div class="evidence-cell">
                      <a-tag :color="contextManifestEvidence.recorded ? 'green' : 'gray'">
                        {{ contextManifestEvidence.statusText }}
                      </a-tag>
                      <a-link
                        v-if="contextManifestEvidence.openable"
                        :href="contextManifestEvidence.downloadUrl"
                        :aria-label="contextManifestEvidence.openLabel"
                        :title="contextManifestEvidence.openLabel"
                        target="_blank"
                        rel="noreferrer"
                      >
                        打开
                      </a-link>
                      <span v-else class="muted-text">
                        {{ contextManifestEvidence.recorded ? '不可打开' : '未生成' }}
                      </span>
                    </div>
                  </a-descriptions-item>
                </a-descriptions>
              </a-collapse-item>
            </a-collapse>

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
                <template #open="{ record }">
                  <a-link
                    v-if="record.downloadable"
                    :href="record.downloadUrl"
                    :aria-label="record.openLabel"
                    :title="record.openLabel"
                    target="_blank"
                    rel="noreferrer"
                  >
                    打开
                  </a-link>
                  <span v-else class="muted-text">不可直接打开</span>
                </template>
              </a-table>
              <a-empty
                v-if="artifactRows.length === 0"
                class="detail-empty"
                description="暂无工件证据"
              />
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
                <template #requestEvidence="{ record }">
                  <div class="evidence-cell">
                    <a-tag :color="record.requestEvidence.recorded ? 'green' : 'gray'">
                      {{ record.requestEvidence.statusText }}
                    </a-tag>
                    <a-link
                      v-if="record.requestEvidence.openable"
                      :href="record.requestEvidence.downloadUrl"
                      :aria-label="record.requestEvidence.openLabel"
                      :title="record.requestEvidence.openLabel"
                      target="_blank"
                      rel="noreferrer"
                    >
                      打开
                    </a-link>
                    <span v-else class="muted-text">
                      {{ record.requestEvidence.recorded ? '不可打开' : '无本地工件' }}
                    </span>
                  </div>
                </template>
                <template #parsedOutputEvidence="{ record }">
                  <div class="evidence-cell">
                    <a-tag :color="record.parsedOutputEvidence.recorded ? 'green' : 'gray'">
                      {{ record.parsedOutputEvidence.statusText }}
                    </a-tag>
                    <a-link
                      v-if="record.parsedOutputEvidence.openable"
                      :href="record.parsedOutputEvidence.downloadUrl"
                      :aria-label="record.parsedOutputEvidence.openLabel"
                      :title="record.parsedOutputEvidence.openLabel"
                      target="_blank"
                      rel="noreferrer"
                    >
                      打开
                    </a-link>
                    <span v-else class="muted-text">
                      {{ record.parsedOutputEvidence.recorded ? '不可打开' : '无本地工件' }}
                    </span>
                  </div>
                </template>
                <template #schemaValidationEvidence="{ record }">
                  <div class="evidence-cell">
                    <a-tag :color="record.schemaValidationEvidence.recorded ? 'green' : 'gray'">
                      {{ record.schemaValidationEvidence.statusText }}
                    </a-tag>
                    <a-link
                      v-if="record.schemaValidationEvidence.openable"
                      :href="record.schemaValidationEvidence.downloadUrl"
                      :aria-label="record.schemaValidationEvidence.openLabel"
                      :title="record.schemaValidationEvidence.openLabel"
                      target="_blank"
                      rel="noreferrer"
                    >
                      打开
                    </a-link>
                    <span v-else class="muted-text">
                      {{ record.schemaValidationEvidence.recorded ? '不可打开' : '无本地工件' }}
                    </span>
                  </div>
                </template>
              </a-table>
              <a-empty
                v-if="llmCallRows.length === 0"
                class="detail-empty"
                description="暂无大模型调用日志"
              />
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
import { useModelConnectionStore } from '../../stores/modelConnection';

const store = useAITasksStore();
const modelConnectionStore = useModelConnectionStore();

const healthLabel = ref('检测中');
const healthDetail = ref('正在检查后端 /health');
const configuredText = '\u5df2\u914d\u7f6e';
const checkingText = '\u68c0\u6d4b\u4e2d';
const notConfiguredText = '\u672a\u914d\u7f6e';
const modelSetupHintText = '\u8bf7\u5728\u8bbe\u7f6e\u9875\u914d\u7f6e\u5927\u6a21\u578b\u670d\u52a1';

const taskColumns = [
  { title: '智能体', dataIndex: 'agentLabel', width: 220 },
  { title: '任务类型', dataIndex: 'taskTypeLabel', width: 180 },
  { title: '状态', slotName: 'status', width: 110 },
  { title: '模型', dataIndex: 'modelLabel', ellipsis: true, tooltip: true },
  { title: '上下文数量', slotName: 'contextCount', width: 120 },
];

const artifactColumns = [
  { title: '工件类型', dataIndex: 'artifact_type' },
  { title: '文件格式', dataIndex: 'mime_type' },
  { title: '展示安全', slotName: 'safe' },
  { title: '本地打开', slotName: 'open', width: 120 },
];

const llmCallColumns = [
  { title: '序号', dataIndex: 'call_index' },
  { title: '模型', dataIndex: 'model_name' },
  { title: '状态', slotName: 'status' },
  { title: '证据', dataIndex: 'evidenceSummary', width: 150 },
  { title: '耗时', dataIndex: 'latencyText' },
  { title: '令牌用量', dataIndex: 'tokenUsageText' },
];

const workflowQueueColumns = [
  { title: '阶段', slotName: 'stage', width: 160 },
  { title: '对象', dataIndex: 'subject_ref', ellipsis: true, tooltip: true },
  { title: '版本', dataIndex: 'lock_version', width: 88 },
  { title: '输入快照', slotName: 'snapshot', width: 220 },
  { title: '操作', slotName: 'open', width: 90 },
];

const metrics = computed(() => [
  { label: '最近 AI 任务', value: String(store.totalTasks) },
  { label: '运行中', value: String(store.runningTasks) },
  { label: '失败任务', value: String(store.failedTasks) },
  { label: '上下文工件', value: String(store.contextArtifactCount) },
  { label: '流程待处理', value: String(store.workflowQueueTotal) },
]);

const workflowQueueGroups = computed(() => [
  {
    bucket: 'waiting_review',
    title: '待人工评审',
    items: store.workflowQueueItems('waiting_review'),
  },
  {
    bucket: 'waiting_approval',
    title: '待批准',
    items: store.workflowQueueItems('waiting_approval'),
  },
  {
    bucket: 'can_continue',
    title: '已批准，可继续',
    items: store.workflowQueueItems('can_continue'),
  },
]);

const modelConnectionLabel = computed(() => {
  if (modelConnectionStore.loading) {
    return checkingText;
  }
  return modelConnectionStore.config?.configured ? configuredText : notConfiguredText;
});

const modelConnectionDetail = computed(() => {
  const config = modelConnectionStore.config;
  if (!config?.configured) {
    return modelSetupHintText;
  }
  return `${config.provider ?? notConfiguredText} · ${config.model_name ?? notConfiguredText}`;
});

const taskRows = computed(() =>
  store.tasks.map((task) => ({
    ...task,
    agentLabel: readableAgentName(task.agent_name),
    taskTypeLabel: taskTypeLabel(task.task_type),
    modelLabel: readableModelName(task.model_name),
  })),
);
const artifactRows = computed(
  () =>
    store.selectedTask?.artifacts.map((artifact) => ({
      ...artifact,
      sizeText: `${artifact.size_bytes} B`,
      redactionText: artifact.redaction_applied ? '已脱敏' : '未脱敏',
      downloadable: artifact.safe_to_show,
      downloadUrl: `/api/artifacts/${artifact.id}/download`,
      openLabel: artifactOpenLabel(artifact.artifact_type, artifact.id),
    })) ?? [],
);
const contextManifestEvidence = computed(() =>
  artifactEvidence(
    store.selectedTask?.context_manifest_artifact_id ?? null,
    '上下文清单证据',
    '未生成',
  ),
);
const llmCallRows = computed(
  () =>
    store.selectedTask?.llm_call_logs.map((callLog) => ({
      ...callLog,
      evidenceSummary: [callLog.request_artifact_id, callLog.parsed_artifact_id, callLog.schema_validation_artifact_id]
        .filter(Boolean).length + ' 项',
      requestEvidence: artifactEvidence(
        callLog.request_artifact_id,
        '请求证据',
        '未记录',
      ),
      parsedOutputEvidence: artifactEvidence(
        callLog.parsed_artifact_id,
        '解析输出证据',
        '未记录',
      ),
      schemaValidationEvidence: artifactEvidence(
        callLog.schema_validation_artifact_id,
        '结构验证证据',
        '未记录',
      ),
      latencyText: callLog.latency_ms === null ? '未记录' : `${callLog.latency_ms} ms`,
      tokenUsageText: compactJson(callLog.token_usage_json),
    })) ?? [],
);

function artifactEvidence(artifactId: string | null, label: string, missingText: string) {
  if (!artifactId) {
    return {
      recorded: false,
      statusText: missingText,
      openable: false,
      downloadUrl: '',
      openLabel: '',
    };
  }

  const artifact = store.selectedTask?.artifacts.find((item) => item.id === artifactId);
  const openable = artifact?.safe_to_show === true;
  const openLabel = `打开${label}工件 ${artifactId}`;

  return {
    recorded: true,
    statusText: '已记录',
    openable,
    downloadUrl: openable ? `/api/artifacts/${artifactId}/download` : '',
    openLabel,
  };
}

function artifactOpenLabel(artifactType: string, artifactId: string): string {
  return `打开 ${artifactType} 工件 ${artifactId}`;
}

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

function taskTypeLabel(taskType: string): string {
  const labels: Record<string, string> = {
    requirement_review: '需求评审',
    case_generation: '用例生成',
    automation_draft: '自动化草稿',
    failure_analysis: '失败分析',
    cicd_change_analysis: '代码变更分析',
    unit_test_patch: '单测补丁',
  };
  return labels[taskType] ?? taskType.replace(/_/g, ' ');
}

function readableAgentName(agentName: string): string {
  const labels: Record<string, string> = {
    RequirementReviewAgent: '需求评审智能体',
    RiskAgent: '风险分析智能体',
    CaseGenerationAgent: '用例生成智能体',
    AutomationDraftAgent: '自动化草稿智能体',
    ToolExecutionAgent: '工具执行智能体',
    ReportAgent: '报告智能体',
    CICDChangeAnalysisAgent: 'CI/CD 变更分析智能体',
    UnitTestAgent: '单测补丁智能体',
  };
  return labels[agentName] ?? agentName;
}

function readableModelName(modelName: string): string {
  return modelName
    .replace(/^mock-/, '本地模型 · ')
    .replace(/-/g, ' ');
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

function workflowStageLabel(stage: string): string {
  const labels: Record<string, string> = {
    scope: '测试范围',
    requirement_review: '需求评审',
    risk_review: '风险评审',
    test_plan_review: '测试计划评审',
    case_review: '用例评审',
    automation_plan_review: '自动化计划评审',
    automation_draft_review: '自动化草稿评审',
    execution_approval: '执行审批',
    execution_result_review: '执行结果评审',
    report_review: '报告评审',
    change_scope: '变更范围',
    unit_test_patch_review: '单元测试补丁评审',
    patch_apply_approval: '补丁应用审批',
    regression_plan_review: '回归计划评审',
    quality_gate_review: '质量门禁评审',
  };
  return labels[stage] ?? stage;
}

function workflowStageColor(gateState: string): string {
  if (gateState === 'waiting_review') {
    return 'orange';
  }
  if (gateState === 'waiting_approval') {
    return 'purple';
  }
  if (gateState === 'approved') {
    return 'green';
  }
  return 'gray';
}

function compactJson(value: Record<string, unknown>): string {
  const entries = Object.entries(value);
  if (entries.length === 0) {
    return '未记录';
  }
  return entries
    .map(([key, rawValue]) => `${tokenLabel(key)}: ${String(rawValue)}`)
    .join(', ');
}

function tokenLabel(key: string): string {
  const labels: Record<string, string> = {
    prompt_tokens: '提示词令牌',
    completion_tokens: '输出令牌',
    total_tokens: '总令牌',
  };
  return labels[key] ?? key;
}

function contextUsageLabel(ids: string[], prefix: string): string {
  return ids.length > 0 ? `${prefix} ${ids.length} 个上下文工件` : `${prefix} 0 个上下文工件`;
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
  void modelConnectionStore.loadConfig();
  void store.loadRecentTasks();
  void store.loadWorkflowQueue();
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

.status-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.health-label {
  margin: 0 0 6px;
  color: #86909c;
}

.health-detail {
  color: #4e5969;
  overflow-wrap: anywhere;
}

.ai-metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
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
  grid-template-columns: 1fr;
  gap: 16px;
}

.workflow-queue-panel {
  min-width: 0;
}

.workflow-queue-groups {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.workflow-queue-error {
  padding: 10px 12px;
  border: 1px solid #ffccc7;
  border-radius: 6px;
  margin-bottom: 12px;
  background: #fff1f0;
  color: #b42318;
}

.workflow-queue-group {
  display: grid;
  min-width: 0;
  gap: 10px;
  padding: 12px;
  border: 1px solid #e5e8ec;
  border-radius: 8px;
  background: #fafbfc;
}

.workflow-queue-group:not(.workflow-queue-group--empty) {
  grid-column: 1 / -1;
  background: #ffffff;
}

.workflow-queue-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.workflow-queue-group--empty :deep(.arco-empty) {
  min-height: 94px;
  padding: 14px 0 8px;
}

.workflow-snapshot {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: bottom;
  white-space: nowrap;
}

.detail-panel {
  min-width: 0;
}

.technical-trace-collapse {
  margin-top: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fafafa;
}

:deep(.arco-table-th),
:deep(.arco-table-td) {
  word-break: normal;
  overflow-wrap: anywhere;
}

:deep(.arco-descriptions-item-label) {
  min-width: 112px;
  color: #667085;
  white-space: nowrap;
}

:deep(.arco-descriptions-item-value) {
  word-break: normal;
  overflow-wrap: anywhere;
}

.detail-section {
  margin-top: 16px;
}

.detail-section h3 {
  margin: 0 0 10px;
  color: #1d2129;
  font-size: 15px;
}

.detail-empty {
  margin-top: 10px;
}

.muted-text {
  color: #86909c;
}

.evidence-cell {
  display: inline-grid;
  gap: 4px;
  align-items: start;
}

@media (max-width: 960px) {
  .workbench-heading,
  .health-row {
    display: grid;
  }

  .status-grid,
  .ai-metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .workflow-queue-groups {
    grid-template-columns: 1fr;
  }

  .workflow-queue-group:not(.workflow-queue-group--empty) {
    grid-column: auto;
  }
}

@media (max-width: 640px) {
  .status-grid,
  .ai-metric-grid {
    grid-template-columns: 1fr;
  }

  .workbench-heading :deep(.arco-space) {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
