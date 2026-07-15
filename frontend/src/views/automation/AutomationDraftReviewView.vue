<template>
  <section class="automation-draft-page" data-test="automation-draft-workbench" aria-labelledby="automation-draft-title">
    <div class="automation-draft-heading">
      <div>
        <p class="eyebrow">AutomationDraft 评审</p>
        <h2 id="automation-draft-title">自动化草稿</h2>
        <p>从已评审用例生成可审查的自动化草稿，审批后在同一页面按自动化类型启动执行并查看证据。</p>
      </div>
      <a-space>
        <a-tag color="blue">模拟 AutomationDraftAgent</a-tag>
        <a-tag color="green">草稿评审 + 执行证据</a-tag>
      </a-space>
    </div>

    <ol class="workflow-progress" aria-label="自动化评审流程">
      <li
        v-for="(step, index) in workflowSteps"
        :key="step.key"
        :class="{ active: step.state === 'active', completed: step.state === 'completed' }"
        :data-test="`automation-workflow-step-${step.key}`"
      >
        <span class="workflow-progress__index">{{ index + 1 }}</span>
        <div>
          <strong>{{ step.label }}</strong>
          <small>{{ step.detail }}</small>
        </div>
      </li>
    </ol>

    <a-alert v-if="store.errorMessage" data-test="automation-error-state" type="error" show-icon>{{ store.errorMessage }}</a-alert>
    <a-alert v-if="store.assetErrorMessage" data-test="automation-stale-assets-state" type="warning" show-icon>
      {{ store.assetErrorMessage }}。已保留当前选择，可重试加载评审资产。
    </a-alert>

    <ExecutionRecentRuns />

    <div class="automation-draft-layout">
      <a-card class="draft-panel" :bordered="false">
        <template #title>草稿入口</template>
        <form class="draft-form" @submit.prevent="submitPlan">
          <label>
            <span>已评审用例</span>
            <a-select
              v-model="form.testCaseId"
              data-test="automation-test-case-select"
              allow-search
              allow-clear
              :loading="store.loadingAssets"
              placeholder="按标题或优先级选择用例"
            >
              <a-option v-for="testCase in store.testCases" :key="testCase.id" :value="testCase.id" :label="testCase.title">
                <div class="asset-option">
                  <strong>{{ testCase.title }}</strong>
                  <span>{{ testCase.priority }} · {{ testCase.test_type }} · {{ shortId(testCase.id) }}</span>
                </div>
              </a-option>
            </a-select>
          </label>
          <div v-if="selectedTestCase" class="selected-asset-summary" data-test="selected-test-case-summary">
            <strong>{{ selectedTestCase.title }}</strong>
            <span>{{ selectedTestCase.priority }} · {{ selectedTestCase.test_type }} · {{ selectedTestCase.review_status }}</span>
          </div>
          <label>
            <span>目标框架</span>
            <a-select v-model="form.targetFramework">
              <a-option value="pytest">pytest</a-option>
              <a-option value="playwright">Playwright</a-option>
            </a-select>
          </label>
          <a-checkbox v-model="form.useKnowledge">结合 RAG 知识库</a-checkbox>
          <a-button
            data-test="generate-plan"
            html-type="submit"
            type="primary"
            :disabled="!form.testCaseId"
            :loading="store.loading"
          >
            生成自动化方案
          </a-button>
        </form>

        <section v-if="store.plan" class="automation-plan-panel">
          <h3>AutomationPlan</h3>
          <a-descriptions :column="1" bordered size="small">
            <a-descriptions-item label="标题">{{ store.plan.title }}</a-descriptions-item>
            <a-descriptions-item label="状态">{{ store.plan.status }}</a-descriptions-item>
            <a-descriptions-item label="知识证据">
              {{ store.plan.knowledge_retrieval_artifact_id ?? '无命中证据' }}
            </a-descriptions-item>
            <a-descriptions-item label="依赖说明">{{ store.plan.dependency_notes ?? '无' }}</a-descriptions-item>
            <a-descriptions-item label="风险说明">{{ store.plan.risk_notes ?? '无' }}</a-descriptions-item>
          </a-descriptions>
          <ol class="automation-plan-steps">
            <li v-for="step in store.plan.execution_steps" :key="step">{{ step }}</li>
          </ol>
          <a-space class="draft-actions" wrap>
            <a-button data-test="approve-plan" :disabled="!canApprovePlan" :loading="store.loading" @click="approvePlan">
              批准方案
            </a-button>
            <a-button
              data-test="generate-draft-from-plan"
              type="primary"
              :disabled="store.plan.status !== 'approved'"
              :loading="store.loading"
              @click="generateDraftFromPlan"
            >
              生成草稿
            </a-button>
          </a-space>
          <div v-if="store.lastPlanReview" class="draft-result">
            <span>方案评审结果：{{ store.lastPlanReview.status }}</span>
            <strong>AutomationPlan：{{ store.lastPlanReview.automation_plan_id }}</strong>
          </div>
          <section v-if="store.planReviewHistory.length" class="review-history-panel" aria-label="方案评审历史">
            <h3>方案评审历史</h3>
            <div v-for="item in store.planReviewHistory" :key="item.id" class="review-history-item">
              <strong>{{ actionLabel(item.action) }}</strong>
              <span>{{ item.reviewer }} 路 {{ statusTransition(item.from_status, item.to_status) }}</span>
              <small>{{ formatDateTime(item.created_at) }} 路 {{ item.comment || '无评审备注' }} 路 证据 {{ item.evidence_artifact_ids.length }}</small>
            </div>
          </section>
        </section>
      </a-card>

      <a-card class="draft-panel draft-detail-panel" :bordered="false">
        <template #title>草稿评审</template>
        <a-spin :loading="store.loading">
          <template v-if="store.draft">
            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="标题">{{ store.draft.title }}</a-descriptions-item>
              <a-descriptions-item label="状态">{{ store.draft.status }}</a-descriptions-item>
              <a-descriptions-item label="框架">{{ store.draft.target_framework }}</a-descriptions-item>
              <a-descriptions-item label="语言">{{ store.draft.draft_language }}</a-descriptions-item>
              <a-descriptions-item label="建议路径">{{ store.draft.suggested_file_path ?? '未建议' }}</a-descriptions-item>
              <a-descriptions-item label="审批要求">
                {{ store.draft.approval_required ? '需要审批' : '无需审批' }}
              </a-descriptions-item>
              <a-descriptions-item label="执行策略" :span="2">{{ store.draft.execution_strategy }}</a-descriptions-item>
              <a-descriptions-item label="执行说明" :span="2">
                {{ store.draft.execution_notes ?? '无' }}
              </a-descriptions-item>
              <a-descriptions-item label="风险说明" :span="2">{{ store.draft.risk_notes ?? '无' }}</a-descriptions-item>
            </a-descriptions>

            <section class="draft-code-panel">
              <h3>草稿代码</h3>
              <pre>{{ store.draft.draft_code }}</pre>
            </section>

            <div
              class="draft-quality-gate"
              :class="{ 'draft-quality-gate--blocked': approvalBlockingReasons.length > 0 }"
              data-test="draft-quality-gate"
              role="note"
            >
              <strong>Quality gate: {{ draftQualityGate.status }}</strong>
              <small>Evidence level: {{ draftQualityGate.execution_evidence_level }}</small>
              <ul v-if="approvalBlockingReasons.length" data-test="draft-quality-blockers">
                <li v-for="reason in approvalBlockingReasons" :key="reason">{{ reason }}</li>
              </ul>
              <ul v-if="evidenceWarnings.length" data-test="draft-quality-warnings">
                <li v-for="warning in evidenceWarnings" :key="warning">{{ warning }}</li>
              </ul>
              <span>
                fake, stub, placeholder, or assert True-only drafts cannot be approved. Replace them with real selectors,
                steps, and assertions before approval.
              </span>
            </div>

            <a-space class="draft-actions" wrap>
              <a-button data-test="edit-draft" :loading="store.loading" @click="editDraft">保存评审编辑</a-button>
              <a-button
                data-test="approve-draft"
                type="primary"
                :disabled="!canApproveDraft"
                :loading="store.loading"
                @click="approveDraft"
              >
                批准草稿
              </a-button>
            </a-space>

            <div v-if="store.lastReview" class="draft-result">
              <span>评审结果：{{ store.lastReview.status }}</span>
              <strong>AutomationDraft：{{ store.lastReview.automation_draft_id }}</strong>
            </div>

            <section v-if="store.reviewHistory.length" class="review-history-panel" aria-label="本地评审历史">
              <h3>本地评审历史</h3>
              <div v-for="item in store.reviewHistory" :key="item.id" class="review-history-item">
                <strong>{{ actionLabel(item.action) }}</strong>
                <span>{{ item.reviewer }} · {{ statusTransition(item.from_status, item.to_status) }}</span>
                <small>{{ formatDateTime(item.created_at) }} · {{ item.comment || '无评审备注' }} · 证据 {{ item.evidence_artifact_ids.length }}</small>
              </div>
            </section>

            <section class="automation-execution-panel" data-test="automation-execution-panel">
              <div class="section-heading">
                <h3>自动化执行</h3>
                <span>{{ selectedExecutionType.sourceLabel }}</span>
              </div>

              <div class="execution-type-control" role="group" aria-label="自动化执行类型">
                <button
                  v-for="option in executionTypeOptions"
                  :key="option.value"
                  type="button"
                  class="execution-type-option"
                  :class="{ active: option.value === executionForm.executionType }"
                  :data-test="`automation-execution-type-${option.value}`"
                  @click="selectExecutionType(option.value)"
                >
                  <strong>{{ option.label }}</strong>
                  <span>{{ option.runnerLabel }}</span>
                </button>
              </div>

              <a-alert
                v-if="executionStore.errorMessage"
                data-test="automation-execution-error-state"
                type="error"
                :content="executionStore.errorMessage"
                show-icon
              />

              <form class="automation-execution-form" @submit.prevent="startAutomationExecution">
                <label>
                  <span>项目 ID</span>
                  <a-input :model-value="store.projectId" readonly />
                </label>
                <label v-if="selectedExecutionType.sourceMode === 'automation_draft'">
                  <span>AutomationDraft ID</span>
                  <a-input :model-value="store.draft.id" readonly />
                </label>
                <label v-else>
                  <span>测试命令</span>
                  <a-select
                    v-model="executionForm.testCommandId"
                    data-test="automation-test-command-select"
                    allow-search
                    allow-clear
                    :disabled="availableTestCommands.length === 0"
                    :loading="store.loadingAssets"
                    :placeholder="availableTestCommands.length ? '选择已配置命令' : '项目中没有匹配命令'"
                  >
                    <a-option
                      v-for="command in availableTestCommands"
                      :key="command.id"
                      :value="command.id"
                      :label="command.name"
                      :data-test="`automation-test-command-option-${command.id}`"
                    >
                      <div class="asset-option">
                        <strong>{{ command.name }}</strong>
                        <span>{{ command.command_type }} · {{ command.command }}</span>
                      </div>
                    </a-option>
                  </a-select>
                </label>
                <a-space class="execution-actions" wrap>
                  <a-button
                    data-test="start-automation-execution"
                    html-type="submit"
                    type="primary"
                    :disabled="!canStartAutomationExecution"
                    :loading="executionStore.loading"
                  >
                    {{ selectedExecutionType.startLabel }}
                  </a-button>
                  <a-button
                    data-test="refresh-automation-execution"
                    :disabled="!executionStore.run"
                    :loading="executionStore.loading"
                    @click="refreshAutomationExecution"
                  >
                    刷新结果
                  </a-button>
                </a-space>
                <p v-if="executionStartHint" class="execution-start-hint">{{ executionStartHint }}</p>
              </form>

              <a-spin :loading="executionStore.loading">
                <template v-if="executionStore.run">
                  <a-descriptions class="execution-run-context" :column="2" bordered size="small">
                    <a-descriptions-item label="运行名称" :span="2">
                      {{ executionStore.run.name }}
                    </a-descriptions-item>
                    <a-descriptions-item label="状态">
                      {{ executionRunStatusLabel(executionStore.run.status) }}
                    </a-descriptions-item>
                    <a-descriptions-item label="退出码">
                      {{ executionStore.run.exit_code ?? '运行中' }}
                    </a-descriptions-item>
                    <a-descriptions-item label="耗时">{{ executionDurationLabel }}</a-descriptions-item>
                    <a-descriptions-item label="运行器">{{ executionStore.run.runner_mode }}</a-descriptions-item>
                    <a-descriptions-item label="来源">
                      {{ executionStore.run.automation_draft_id ? 'AutomationDraft' : 'TestCommand' }}
                    </a-descriptions-item>
                    <a-descriptions-item label="网络">
                      {{ executionStore.run.network_enabled ? '开启' : '关闭' }}
                    </a-descriptions-item>
                    <a-descriptions-item label="命令" :span="2">{{ executionStore.run.command }}</a-descriptions-item>
                    <a-descriptions-item label="工作目录" :span="2">
                      {{ executionStore.run.working_directory }}
                    </a-descriptions-item>
                  </a-descriptions>

                  <ExecutionRunManifestPanel
                    :run="executionStore.run"
                    :rows="executionManifestRows"
                    title-id="automation-run-manifest-title"
                  />

                  <ExecutionMetricsPanel :items="executionMetricItems" />

                  <ExecutionArtifactTable
                    title="执行工件"
                    title-id="automation-execution-artifacts-title"
                    :artifacts="executionArtifacts"
                  />

                  <ExecutionResultTable
                    title="执行结果"
                    title-id="automation-execution-results-title"
                    :columns="executionResultColumns"
                    :rows="executionResultRows"
                  />
                </template>

                <a-empty v-else data-test="automation-execution-empty-state" description="启动后展示自动化执行证据" />
              </a-spin>
            </section>
          </template>

          <a-empty v-else description="生成后展示自动化草稿" />
        </a-spin>
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue';

import { useAutomationStore } from '../../stores/automation';
import { useExecutionStore } from '../../stores/execution';
import ExecutionArtifactTable from '../execution/ExecutionArtifactTable.vue';
import ExecutionMetricsPanel from '../execution/ExecutionMetricsPanel.vue';
import ExecutionResultTable from '../execution/ExecutionResultTable.vue';
import ExecutionRecentRuns from '../execution/ExecutionRecentRuns.vue';
import ExecutionRunManifestPanel from '../execution/ExecutionRunManifestPanel.vue';
import { executionRunDurationLabel, executionRunStatusLabel } from '../execution/executionDisplay';
import {
  jmeterOutputArtifacts,
  newmanOutputArtifacts,
  playwrightOutputArtifacts,
  pytestOutputArtifacts,
} from '../execution/executionOutputArtifacts';
import { buildExecutionRunManifestRows, type ExecutionRunManifestOutputArtifact } from '../execution/executionRunManifest';

const store = useAutomationStore();
const executionStore = useExecutionStore();

type AutomationExecutionType = 'pytest' | 'playwright' | 'api' | 'jmeter';
type ExecutionSourceMode = 'automation_draft' | 'test_command';

interface AutomationExecutionTypeOption {
  readonly value: AutomationExecutionType;
  readonly label: string;
  readonly runnerLabel: string;
  readonly sourceLabel: string;
  readonly sourceMode: ExecutionSourceMode;
  readonly runnerMode: string;
  readonly requiredDraftFramework?: string;
  readonly requiredCommandType?: string;
  readonly startLabel: string;
  readonly reason: string;
  readonly artifactTypes: readonly string[];
  readonly outputArtifacts: readonly ExecutionRunManifestOutputArtifact[];
}

interface ExecutionMetricItem {
  readonly label: string;
  readonly value: string | number;
}

const executionTypeOptions: readonly AutomationExecutionTypeOption[] = [
  {
    value: 'pytest',
    label: 'pytest',
    runnerLabel: '本地子进程',
    sourceLabel: '从已批准 AutomationDraft 执行',
    sourceMode: 'automation_draft',
    runnerMode: 'local_subprocess',
    requiredDraftFramework: 'pytest',
    startLabel: '启动 pytest',
    reason: 'automation draft pytest execution',
    artifactTypes: ['stdout', 'stderr', 'parsed_output', 'junit', 'coverage'],
    outputArtifacts: pytestOutputArtifacts,
  },
  {
    value: 'playwright',
    label: 'Playwright',
    runnerLabel: '浏览器自动化',
    sourceLabel: '从已批准 Playwright 草稿执行',
    sourceMode: 'automation_draft',
    runnerMode: 'playwright_local',
    requiredDraftFramework: 'playwright',
    startLabel: '启动 Playwright',
    reason: 'automation draft playwright execution',
    artifactTypes: ['stdout', 'stderr', 'parsed_output', 'junit', 'playwright_trace', 'screenshot'],
    outputArtifacts: playwrightOutputArtifacts,
  },
  {
    value: 'api',
    label: 'API / Newman',
    runnerLabel: '接口集合',
    sourceLabel: '使用 TestCommand 执行 API 自动化',
    sourceMode: 'test_command',
    runnerMode: 'newman_local',
    requiredCommandType: 'newman',
    startLabel: '启动 API 执行',
    reason: 'automation draft api execution',
    artifactTypes: ['stdout', 'stderr', 'newman_json', 'parsed_output', 'junit'],
    outputArtifacts: newmanOutputArtifacts,
  },
  {
    value: 'jmeter',
    label: 'JMeter',
    runnerLabel: '接口/性能脚本',
    sourceLabel: '使用 TestCommand 执行 JMeter 自动化',
    sourceMode: 'test_command',
    runnerMode: 'jmeter_local',
    requiredCommandType: 'jmeter',
    startLabel: '启动 JMeter',
    reason: 'automation draft jmeter execution',
    artifactTypes: ['stdout', 'stderr', 'jmeter_jtl', 'parsed_output'],
    outputArtifacts: jmeterOutputArtifacts,
  },
];

const form = reactive({
  testCaseId: store.testCaseId,
  targetFramework: 'pytest',
  useKnowledge: true,
});
const executionForm = reactive({
  executionType: 'pytest' as AutomationExecutionType,
  testCommandId: '',
});

const canApprovePlan = computed(() => ['plan_generated', 'edited'].includes(store.plan?.status ?? ''));
const selectedTestCase = computed(() => store.testCases.find((item) => item.id === form.testCaseId) ?? null);
const draftQualityGate = computed(
  () =>
    store.draft?.quality_gate ?? {
      status: 'unknown',
      execution_evidence_level: 'review_required',
      approval_blocking_reasons: [],
      evidence_warnings: [],
    },
);
const approvalBlockingReasons = computed(() => draftQualityGate.value.approval_blocking_reasons ?? []);
const evidenceWarnings = computed(() => draftQualityGate.value.evidence_warnings ?? []);
const canApproveDraft = computed(
  () => ['draft_generated', 'edited'].includes(store.draft?.status ?? '') && approvalBlockingReasons.value.length === 0,
);
const selectedExecutionType = computed<AutomationExecutionTypeOption>(
  () => executionTypeOptions.find((option) => option.value === executionForm.executionType) ?? executionTypeOptions[0]!,
);
const availableTestCommands = computed(() => {
  const commandType = selectedExecutionType.value.requiredCommandType;
  if (!commandType) {
    return [];
  }
  return store.testCommands.filter((command) => command.command_type === commandType);
});
const workflowSteps = computed(() => {
  const hasTestCase = Boolean(form.testCaseId);
  const hasPlan = Boolean(store.plan);
  const planCompleted = ['approved', 'draft_generated'].includes(store.plan?.status ?? '');
  const hasDraft = Boolean(store.draft);
  const draftCompleted = ['approved', 'execution_pending', 'executed', 'promoted'].includes(store.draft?.status ?? '');
  const hasRun = Boolean(executionStore.run);
  return [
    {
      key: 'case',
      label: '选择用例',
      detail: selectedTestCase.value?.title ?? (hasTestCase ? shortId(form.testCaseId) : '等待选择'),
      state: hasTestCase ? 'completed' : 'active',
    },
    {
      key: 'plan',
      label: '审批方案',
      detail: hasPlan ? statusLabel(store.plan?.status ?? null) : '尚未生成',
      state: planCompleted ? 'completed' : hasTestCase ? 'active' : 'pending',
    },
    {
      key: 'draft',
      label: '评审草稿',
      detail: hasDraft ? statusLabel(store.draft?.status ?? null) : '等待方案批准',
      state: draftCompleted ? 'completed' : planCompleted ? 'active' : 'pending',
    },
    {
      key: 'evidence',
      label: '执行取证',
      detail: hasRun ? executionRunStatusLabel(executionStore.run?.status ?? '') : '等待草稿批准',
      state: hasRun ? 'completed' : draftCompleted ? 'active' : 'pending',
    },
  ] as const;
});
const executionStartHint = computed(() => {
  if (!store.draft) {
    return '请先生成自动化草稿。';
  }
  const option = selectedExecutionType.value;
  if (option.sourceMode === 'automation_draft') {
    if (store.draft.status !== 'approved') {
      return 'AutomationDraft 需要先批准，才能执行草稿代码。';
    }
    if (option.requiredDraftFramework && store.draft.target_framework !== option.requiredDraftFramework) {
      return `当前草稿框架是 ${store.draft.target_framework}，请选择匹配的执行类型。`;
    }
    return '';
  }
  if (!executionForm.testCommandId.trim()) {
    return availableTestCommands.value.length
      ? '请选择一个与当前执行类型匹配的测试命令。'
      : '项目中没有可用于当前执行类型的测试命令，请先在设置中配置。';
  }
  return '';
});
const canStartAutomationExecution = computed(() => !executionStartHint.value);
const executionDurationLabel = computed(() => executionRunDurationLabel(executionStore.run?.duration_ms ?? null));
const executionManifestRows = computed(() =>
  buildExecutionRunManifestRows(executionStore.run, selectedExecutionType.value.outputArtifacts),
);
const executionArtifacts = computed(() => {
  const allowedTypes = new Set(selectedExecutionType.value.artifactTypes);
  return (executionStore.run?.artifacts ?? []).filter((artifact) => allowedTypes.has(artifact.artifact_type));
});
const executionMetricItems = computed(() => metricItemsForExecutionType(executionForm.executionType));
const executionResultColumns = computed(() => {
  if (executionForm.executionType === 'jmeter') {
    return [
      { title: 'Sampler', dataIndex: 'test_name' },
      { title: '状态', dataIndex: 'status_label' },
      { title: '耗时', dataIndex: 'duration_label' },
      { title: '失败信息', dataIndex: 'failure_message' },
    ];
  }
  if (executionForm.executionType === 'api') {
    return [
      { title: '断言', dataIndex: 'test_name' },
      { title: '状态', dataIndex: 'status' },
      { title: '失败信息', dataIndex: 'failure_message' },
    ];
  }
  return [
    { title: '测试', dataIndex: 'test_name' },
    { title: '状态', dataIndex: 'status' },
    { title: '耗时', dataIndex: 'duration_ms' },
    { title: '失败信息', dataIndex: 'failure_message' },
  ];
});
const executionResultRows = computed(() => {
  if (executionForm.executionType !== 'jmeter') {
    return executionStore.run?.test_results ?? [];
  }
  return (executionStore.run?.test_results ?? []).map((result) => ({
    ...result,
    status_label: executionRunStatusLabel(result.status),
    duration_label: result.duration_ms === null ? '未记录' : `${result.duration_ms} ms`,
    failure_message: result.failure_message ?? '无',
  }));
});

function submitPlan() {
  void store.createPlan({
    testCaseId: form.testCaseId,
    targetFramework: form.targetFramework,
    useKnowledge: form.useKnowledge,
  });
}

function approvePlan() {
  void store.approveCurrentPlan('前端批准自动化方案');
}

function generateDraftFromPlan() {
  void store.generateDraftFromPlan();
}

function editDraft() {
  void store.editCurrentDraft('前端评审编辑');
}

function approveDraft() {
  if (!canApproveDraft.value) {
    return;
  }
  void store.approveCurrentDraft('前端批准草稿');
}

function selectExecutionType(type: AutomationExecutionType) {
  executionForm.executionType = type;
  executionForm.testCommandId = '';
  executionStore.run = null;
  executionStore.errorMessage = '';
}

function startAutomationExecution() {
  if (!store.draft || !canStartAutomationExecution.value) {
    return;
  }
  const option = selectedExecutionType.value;
  executionStore.projectId = store.projectId;
  executionStore.sourceMode = option.sourceMode;
  executionStore.automationDraftId = store.draft.id;
  executionStore.testCommandId = executionForm.testCommandId.trim();
  void executionStore.startRun({
    runnerMode: option.runnerMode,
    reason: option.reason,
  });
}

function refreshAutomationExecution() {
  void executionStore.refreshRun();
}

function metricItemsForExecutionType(type: AutomationExecutionType): ExecutionMetricItem[] {
  const parsed = executionStore.run?.parsed_result ?? {};
  if (type === 'api') {
    return [
      { label: '总断言', value: parsed.total ?? 0 },
      { label: '通过', value: parsed.passed ?? 0 },
      { label: '失败', value: parsed.failed ?? 0 },
      { label: '跳过', value: parsed.skipped ?? 0 },
      { label: '请求数', value: parsed.request_count ?? 0 },
      { label: '断言数', value: parsed.assertion_count ?? 0 },
    ];
  }
  if (type === 'jmeter') {
    return [
      { label: '总样本', value: parsed.total ?? 0 },
      { label: '通过', value: parsed.passed ?? 0 },
      { label: '失败', value: parsed.failed ?? 0 },
      { label: '错误', value: parsed.error ?? 0 },
      { label: 'Sampler 数', value: parsed.sampler_count ?? 0 },
      { label: '断言数', value: parsed.assertion_count ?? 0 },
      { label: '平均延迟', value: formatMs(parsed.average_latency_ms) },
    ];
  }
  return [
    { label: '总数', value: parsed.total ?? 0 },
    { label: '通过', value: parsed.passed ?? 0 },
    { label: '失败', value: parsed.failed ?? 0 },
    { label: '跳过', value: parsed.skipped ?? 0 },
    { label: '错误', value: parsed.error ?? 0 },
  ];
}

function formatMs(value: number | string | undefined): string | number {
  return typeof value === 'number' ? `${value} ms` : (value ?? 0);
}

function actionLabel(action: string): string {
  const labels: Record<string, string> = {
    edit: '编辑',
    approve: '批准',
    reject: '拒绝',
    generate_draft: '生成草稿',
  };
  return labels[action] ?? action;
}

function statusTransition(fromStatus: string | null, toStatus: string | null): string {
  return `${statusLabel(fromStatus)} -> ${statusLabel(toStatus)}`;
}

function statusLabel(status: string | null): string {
  const labels: Record<string, string> = {
    draft_generated: '已生成',
    edited: '已编辑',
    approved: '已批准',
    plan_generated: '方案已生成',
    rejected: '已拒绝',
  };
  return status ? (labels[status] ?? status) : '未知';
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

function shortId(value: string): string {
  return value.length > 8 ? `${value.slice(0, 8)}…` : value;
}

onMounted(async () => {
  if (store.loadLatestApprovedTestCaseContext()) {
    form.testCaseId = store.testCaseId;
  }
  await store.loadReviewerAssets();
});
</script>

<style scoped>
.automation-draft-page {
  display: grid;
  gap: 18px;
}

.automation-draft-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.automation-draft-heading h2,
.automation-draft-heading p {
  margin: 0;
}

.automation-draft-heading h2 {
  font-size: 26px;
}

.automation-draft-heading p:not(.eyebrow) {
  margin-top: 10px;
  max-width: 780px;
  color: #5b6472;
  line-height: 1.7;
}

.automation-draft-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.75fr) minmax(0, 1.4fr);
  gap: 16px;
}

.workflow-progress {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin: 0;
  padding: 0;
  border: 1px solid #dbe3ee;
  border-radius: 8px;
  background: #ffffff;
  list-style: none;
}

.workflow-progress li {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-right: 1px solid #e5eaf2;
  color: #64748b;
}

.workflow-progress li:last-child {
  border-right: 0;
}

.workflow-progress li.active {
  background: #eff6ff;
  color: #1d4ed8;
}

.workflow-progress li.completed {
  color: #166534;
}

.workflow-progress__index {
  display: inline-flex;
  width: 28px;
  height: 28px;
  flex: 0 0 28px;
  align-items: center;
  justify-content: center;
  border: 1px solid currentColor;
  border-radius: 50%;
  font-weight: 800;
}

.workflow-progress strong,
.workflow-progress small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.workflow-progress small {
  margin-top: 3px;
  color: inherit;
  opacity: 0.78;
}

.draft-panel {
  border-radius: 8px;
}

.draft-form {
  display: grid;
  gap: 14px;
}

.draft-form label {
  display: grid;
  gap: 7px;
  color: #344054;
  font-weight: 700;
}

.asset-option {
  display: grid;
  gap: 3px;
  min-width: 0;
  padding: 2px 0;
}

.asset-option strong,
.asset-option span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.asset-option span {
  color: #64748b;
  font-size: 12px;
}

.selected-asset-summary {
  display: grid;
  gap: 4px;
  padding: 10px 12px;
  border-left: 3px solid #2563eb;
  background: #f8fafc;
}

.selected-asset-summary span {
  color: #64748b;
  font-size: 12px;
}

.automation-plan-panel {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.automation-plan-panel h3,
.automation-plan-steps {
  margin: 0;
}

.automation-plan-steps {
  padding-left: 20px;
  color: #475569;
  line-height: 1.7;
}

.draft-code-panel {
  margin-top: 18px;
}

.draft-code-panel h3 {
  margin: 0 0 10px;
  font-size: 16px;
}

.draft-code-panel pre {
  overflow: auto;
  margin: 0;
  padding: 14px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
  color: #0f172a;
  line-height: 1.6;
}

.draft-actions,
.draft-result {
  margin-top: 16px;
}

.draft-quality-gate {
  display: grid;
  gap: 6px;
  margin-top: 14px;
  padding: 12px;
  border: 1px solid #facc15;
  border-radius: 8px;
  background: #fffbeb;
  color: #713f12;
}

.draft-quality-gate--blocked {
  border-color: #fca5a5;
  background: #fff1f2;
  color: #7f1d1d;
}

.draft-quality-gate ul {
  margin: 0;
  padding-left: 18px;
}

.draft-quality-gate small {
  color: inherit;
  opacity: 0.78;
}

.draft-result {
  padding: 12px;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  background: #f0fdf4;
}

.draft-result span,
.draft-result strong {
  display: block;
}

.draft-result span {
  color: #64748b;
}

.draft-result strong {
  margin-top: 6px;
  color: #166534;
}

.review-history-panel {
  display: grid;
  gap: 8px;
  margin-top: 16px;
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

.automation-execution-panel {
  display: grid;
  gap: 14px;
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px solid #e5eaf2;
}

.section-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.section-heading h3 {
  margin: 0;
  font-size: 16px;
}

.section-heading span {
  color: #64748b;
  font-size: 13px;
}

.execution-type-control {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.execution-type-option {
  display: grid;
  gap: 4px;
  min-height: 62px;
  padding: 10px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #ffffff;
  color: #334155;
  text-align: left;
  cursor: pointer;
}

.execution-type-option.active {
  border-color: #2563eb;
  background: #eff6ff;
  color: #1d4ed8;
}

.execution-type-option span {
  color: #64748b;
  font-size: 12px;
}

.automation-execution-form {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) minmax(220px, 1fr) max-content;
  align-items: end;
  gap: 12px;
}

.automation-execution-form label {
  display: grid;
  gap: 7px;
  min-width: 0;
  color: #344054;
  font-weight: 700;
}

.execution-actions {
  align-self: end;
}

.execution-start-hint {
  grid-column: 1 / -1;
  margin: 0;
  color: #b45309;
  font-weight: 700;
}

.execution-run-context {
  margin-top: 4px;
}

@media (max-width: 980px) {
  .automation-draft-layout {
    grid-template-columns: 1fr;
  }

  .execution-type-control,
  .automation-execution-form {
    grid-template-columns: 1fr;
  }

  .workflow-progress {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .workflow-progress li:nth-child(2) {
    border-right: 0;
  }

  .workflow-progress li:nth-child(-n + 2) {
    border-bottom: 1px solid #e5eaf2;
  }
}

@media (max-width: 560px) {
  .workflow-progress {
    grid-template-columns: 1fr;
  }

  .workflow-progress li,
  .workflow-progress li:nth-child(2) {
    border-right: 0;
    border-bottom: 1px solid #e5eaf2;
  }

  .workflow-progress li:last-child {
    border-bottom: 0;
  }
}
</style>
