<template>
  <section class="campaign-scope-page" aria-labelledby="campaign-scope-title">
    <header class="campaign-heading">
      <div>
        <p class="eyebrow">测试活动 / Scope</p>
        <h2 id="campaign-scope-title">本轮测试范围</h2>
        <p>先锁定环境、版本、退出条件和证据覆盖，再决定是否进入需求评审。</p>
      </div>
      <div class="campaign-heading__status">
        <a-tag :color="stageColor">{{ stageLabel }}</a-tag>
        <a-tag :color="stateColor">{{ stateLabel }}</a-tag>
        <span v-if="store.workflow" class="version-label">v{{ store.workflow.lock_version }}</span>
      </div>
    </header>

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />
    <a-alert v-if="store.successMessage" type="success" :content="store.successMessage" show-icon closable />
    <a-alert
      v-if="store.stale"
      type="warning"
      content="当前页面已过期。编辑和审批动作已锁定，请刷新服务器状态。"
      show-icon
    />

    <div class="workflow-track" aria-label="测试工作流">
      <span
        v-for="(step, index) in workflowSteps"
        :key="step.key"
        class="workflow-track__step"
        :class="workflowStepClass(step.key)"
      >
        <strong>{{ index + 1 }}</strong>{{ step.label }}
      </span>
    </div>

    <a-spin :loading="store.loading" class="campaign-spin">
      <div class="campaign-workspace">
        <section class="workspace-panel evidence-input-panel" aria-labelledby="scope-input-title">
          <div class="panel-heading">
            <div>
              <p class="panel-kicker">输入与证据</p>
              <h3 id="scope-input-title">目标上下文</h3>
            </div>
            <a-button type="text" :loading="store.loading" @click="store.refresh()">
              <template #icon><IconRefresh /></template>
              刷新
            </a-button>
          </div>

          <div class="field-stack">
            <label class="scope-field">
              <span>目标环境</span>
              <a-select
                v-model="form.targetEnvironmentId"
                data-test="campaign-environment"
                placeholder="选择项目环境"
                :disabled="!store.canSave"
              >
                <a-option
                  v-for="environment in activeEnvironments"
                  :key="environment.id"
                  :value="environment.id"
                >
                  {{ environment.name }}
                </a-option>
              </a-select>
            </label>
            <label class="scope-field">
              <span>版本 / 构建 / Commit</span>
              <a-input
                v-model="form.targetVersionRef"
                data-test="campaign-version"
                placeholder="release/2026.08 或 commit SHA"
                :disabled="!store.canSave"
              />
            </label>
            <EvidenceIdField v-model="form.requirementIdsText" label="Requirement IDs" test-id="campaign-requirements" />
            <EvidenceIdField v-model="form.riskIdsText" label="Risk IDs" test-id="campaign-risks" />
            <EvidenceIdField v-model="form.testPlanSnapshotIdsText" label="TestPlan Snapshot IDs" test-id="campaign-plans" />
            <EvidenceIdField v-model="form.approvedCaseIdsText" label="Approved TestCase IDs" test-id="campaign-cases" />
          </div>
        </section>

        <section class="workspace-panel candidate-panel" aria-labelledby="scope-candidate-title">
          <div class="panel-heading">
            <div>
              <p class="panel-kicker">可编辑候选</p>
              <h3 id="scope-candidate-title">Scope 草稿</h3>
            </div>
            <span class="snapshot-label">Snapshot {{ store.workflow?.snapshot_iteration ?? 0 }}</span>
          </div>

          <div class="field-stack candidate-fields">
            <label class="scope-field">
              <span>活动名称</span>
              <a-input
                v-model="form.name"
                data-test="campaign-name"
                placeholder="例如：Checkout 2026.08 发布验证"
                :disabled="!store.canSave"
              />
            </label>
            <label class="scope-field">
              <span>范围说明</span>
              <a-textarea
                v-model="form.scopeStatement"
                data-test="campaign-scope"
                :auto-size="{ minRows: 8, maxRows: 16 }"
                placeholder="明确本轮覆盖目标、边界和不包含内容"
                :disabled="!store.canSave"
              />
            </label>
            <label class="scope-field">
              <span>退出条件（每行一条）</span>
              <a-textarea
                v-model="form.exitConditionsText"
                data-test="campaign-exit-conditions"
                :auto-size="{ minRows: 6, maxRows: 12 }"
                placeholder="无未解决严重缺陷&#10;所有高风险均有批准用例"
                :disabled="!store.canSave"
              />
            </label>
            <label class="scope-field">
              <span>评审说明</span>
              <a-textarea
                v-model="reviewComment"
                data-test="campaign-review-comment"
                :auto-size="{ minRows: 3, maxRows: 6 }"
                placeholder="记录本次编辑、批准或拒绝原因"
                :disabled="store.stale"
              />
            </label>
          </div>
        </section>

        <section class="workspace-panel validation-panel" aria-labelledby="scope-validation-title">
          <div class="panel-heading">
            <div>
              <p class="panel-kicker">确定性门禁</p>
              <h3 id="scope-validation-title">覆盖与阻塞项</h3>
            </div>
            <span class="coverage-summary">{{ coveredCount }} / {{ coverageRows.length }}</span>
          </div>

          <div v-if="coverageRows.length" class="coverage-list" data-test="campaign-coverage-list">
            <article v-for="row in coverageRows" :key="`${row.kind}:${row.target_id}`" class="coverage-row">
              <div class="coverage-row__heading">
                <span class="coverage-kind">{{ coverageKindLabel(row.kind) }}</span>
                <a-tag :color="row.coverage_status === 'covered' ? 'green' : 'orange'">
                  {{ row.coverage_status === 'covered' ? '已覆盖' : '缺口' }}
                </a-tag>
              </div>
              <strong>{{ row.label }}</strong>
              <code>{{ row.target_id }}</code>
              <p v-if="row.gap_reason" class="coverage-gap">{{ row.gap_reason }}</p>
              <p v-else-if="row.evidence_case_ids.length" class="coverage-evidence">
                用例证据 {{ row.evidence_case_ids.length }} 条
              </p>
              <p v-else-if="row.evidence_snapshot_id" class="coverage-evidence">计划审批证据已确认</p>
            </article>
          </div>
          <a-empty v-else description="保存范围后显示服务器计算的覆盖矩阵" />

          <div class="gate-audit" v-if="store.workflow">
            <div><span>Snapshot Hash</span><code>{{ store.workflow.snapshot_hash }}</code></div>
            <div><span>Approval</span><code>{{ store.workflow.approval_decision_id ?? '未授予' }}</code></div>
          </div>
        </section>
      </div>
    </a-spin>

    <footer class="campaign-action-bar" aria-label="Scope 审批操作">
      <div class="action-bar__state">
        <span class="state-dot" :class="`state-dot--${stateTone}`"></span>
        <div>
          <strong>{{ stateLabel }}</strong>
          <small>{{ actionHint }}</small>
        </div>
      </div>
      <div class="action-bar__buttons">
        <a-button :disabled="store.stale" :loading="store.loading" @click="store.refresh()">
          <template #icon><IconRefresh /></template>
          刷新
        </a-button>
        <a-button data-test="campaign-save" :disabled="!store.canSave" :loading="store.saving" @click="saveScope">
          <template #icon><IconSave /></template>
          保存草稿
        </a-button>
        <a-button data-test="campaign-reject" status="danger" :disabled="!store.canDecide" :loading="store.saving" @click="rejectScope">
          <template #icon><IconClose /></template>
          拒绝
        </a-button>
        <a-button data-test="campaign-submit" :disabled="!store.canSubmit" :loading="store.saving" @click="store.submit()">
          提交评审
        </a-button>
        <a-button data-test="campaign-complete" :disabled="!store.canCompleteReview" :loading="store.saving" @click="completeReview">
          完成评审
        </a-button>
        <a-button data-test="campaign-approve" type="primary" :disabled="!canApprove" :loading="store.saving" @click="approveScope">
          <template #icon><IconCheck /></template>
          批准
        </a-button>
        <a-button data-test="campaign-continue" type="primary" status="success" :disabled="!store.canContinue" :loading="store.saving" @click="continueWorkflow">
          进入需求阶段
          <template #icon><IconRight /></template>
        </a-button>
      </div>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { IconCheck, IconClose, IconRefresh, IconRight, IconSave } from '@arco-design/web-vue/es/icon';

import type { CampaignCoverageKind, TestCampaignRead, TestCampaignScopeInput } from '../../api/testCampaigns';
import { useTestCampaignStore } from '../../stores/testCampaigns';

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const workflowSteps = [
  { key: 'scope', label: '范围' },
  { key: 'requirement_review', label: '需求' },
  { key: 'risk_review', label: '风险' },
  { key: 'test_plan_review', label: '计划' },
  { key: 'case_review', label: '用例' },
] as const;

const store = useTestCampaignStore();
const router = useRouter();
const reviewComment = ref('');
const form = reactive({
  name: '',
  scopeStatement: '',
  targetEnvironmentId: '',
  targetVersionRef: '',
  exitConditionsText: '',
  requirementIdsText: '',
  riskIdsText: '',
  testPlanSnapshotIdsText: '',
  approvedCaseIdsText: '',
});

const EvidenceIdField = defineComponent({
  name: 'EvidenceIdField',
  props: {
    modelValue: { type: String, required: true },
    label: { type: String, required: true },
    testId: { type: String, required: true },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () => h('label', { class: 'scope-field' }, [
      h('span', props.label),
      h('textarea', {
        class: 'evidence-id-input',
        value: props.modelValue,
        rows: 3,
        'data-test': props.testId,
        placeholder: '每行一个 UUID',
        disabled: !store.canSave,
        onInput: (event: Event) => emit('update:modelValue', (event.target as HTMLTextAreaElement).value),
      }),
    ]);
  },
});

const activeEnvironments = computed(() => (
  store.settings?.environments.filter((environment) => environment.status === 'active') ?? []
));
const coverageRows = computed(() => store.campaign?.coverage_rows ?? []);
const coveredCount = computed(() => coverageRows.value.filter((row) => row.coverage_status === 'covered').length);
const canApprove = computed(() => store.workflow?.state === 'waiting_approval' && !store.stale);
const stageLabel = computed(() => {
  if (!store.workflow || store.workflow.stage === 'scope') return 'Scope';
  return 'RequirementReview';
});
const stateLabel = computed(() => ({
  draft: '草稿',
  waiting_review: '待人工评审',
  waiting_approval: '待批准',
  approved: '已批准',
  rejected: '已拒绝',
}[store.workflow?.state ?? ''] ?? store.workflow?.state ?? '未创建'));
const stageColor = computed(() => store.workflow?.stage === 'scope' ? 'blue' : 'green');
const stateColor = computed(() => ({
  draft: 'gray', waiting_review: 'arcoblue', waiting_approval: 'orange', approved: 'green', rejected: 'red',
}[store.workflow?.state ?? 'draft']));
const stateTone = computed(() => ({
  approved: 'success', rejected: 'danger', waiting_approval: 'warning', waiting_review: 'info',
}[store.workflow?.state ?? 'draft'] ?? 'neutral'));
const actionHint = computed(() => {
  if (store.stale) return '刷新后才能继续操作';
  if (!store.campaign) return '填写范围并保存第一个草稿';
  if (store.canSubmit) return '草稿需要提交后才能进入人工评审';
  if (store.canCompleteReview) return '人工检查后完成评审';
  if (canApprove.value) return '批准或拒绝当前精确快照';
  if (store.canContinue) return '当前批准可被消费一次';
  return '等待服务器返回下一项可用操作';
});

watch(() => store.campaign, (campaign) => hydrateForm(campaign), { immediate: true });
watch(activeEnvironments, (environments) => {
  if (!form.targetEnvironmentId && environments[0]) form.targetEnvironmentId = environments[0].id;
}, { immediate: true });

function hydrateForm(campaign: TestCampaignRead | null) {
  if (!campaign) return;
  form.name = campaign.name;
  form.scopeStatement = campaign.scope_statement;
  form.targetEnvironmentId = campaign.target_environment_id;
  form.targetVersionRef = campaign.target_version_ref;
  form.exitConditionsText = campaign.exit_conditions.join('\n');
  form.requirementIdsText = campaign.requirement_ids.join('\n');
  form.riskIdsText = campaign.risk_ids.join('\n');
  form.testPlanSnapshotIdsText = campaign.test_plan_snapshot_ids.join('\n');
  form.approvedCaseIdsText = campaign.approved_case_ids.join('\n');
}

function parseLines(value: string): string[] {
  return [...new Set(value.split(/[\n,]/).map((item) => item.trim()).filter(Boolean))];
}

function campaignInput(): TestCampaignScopeInput | null {
  const exitConditions = parseLines(form.exitConditionsText);
  const idGroups = [
    parseLines(form.requirementIdsText),
    parseLines(form.riskIdsText),
    parseLines(form.testPlanSnapshotIdsText),
    parseLines(form.approvedCaseIdsText),
  ];
  if (!form.name.trim() || !form.scopeStatement.trim() || !form.targetEnvironmentId || !form.targetVersionRef.trim()) {
    store.errorMessage = '请完整填写活动名称、范围、目标环境和版本';
    return null;
  }
  if (!exitConditions.length) {
    store.errorMessage = '至少填写一条退出条件';
    return null;
  }
  if (idGroups.flat().some((value) => !UUID_PATTERN.test(value))) {
    store.errorMessage = '证据 ID 必须是完整 UUID，每行一个';
    return null;
  }
  return {
    name: form.name.trim(),
    scope_statement: form.scopeStatement.trim(),
    target_environment_id: form.targetEnvironmentId,
    target_version_ref: form.targetVersionRef.trim(),
    exit_conditions: exitConditions,
    requirement_ids: idGroups[0],
    risk_ids: idGroups[1],
    test_plan_snapshot_ids: idGroups[2],
    approved_case_ids: idGroups[3],
  };
}

async function saveScope() {
  const input = campaignInput();
  if (input) await store.saveScope(input, reviewComment.value);
}

async function completeReview() { await store.completeReview(reviewComment.value); }
async function approveScope() { await store.approve(reviewComment.value); }
async function rejectScope() { await store.reject(reviewComment.value); }

async function continueWorkflow() {
  const campaign = await store.continueWorkflow();
  if (campaign?.workflow.stage === 'requirement_review') {
    await router.push({ name: 'requirement-review' });
  }
}

function coverageKindLabel(kind: CampaignCoverageKind): string {
  return { requirement: '需求', risk: '风险', test_plan: '测试计划', approved_case: '批准用例' }[kind];
}

function workflowStepClass(step: string) {
  const currentIndex = workflowSteps.findIndex((item) => item.key === (store.workflow?.stage ?? 'scope'));
  const stepIndex = workflowSteps.findIndex((item) => item.key === step);
  return {
    'workflow-track__step--active': stepIndex === currentIndex,
    'workflow-track__step--completed': stepIndex < currentIndex,
  };
}

onMounted(() => store.load());
</script>

<style scoped>
.campaign-scope-page { display: grid; gap: 18px; padding-bottom: 12px; }
.campaign-heading, .panel-heading, .campaign-action-bar, .coverage-row__heading, .action-bar__state, .action-bar__buttons { display: flex; align-items: center; }
.campaign-heading { justify-content: space-between; gap: 24px; }
.campaign-heading h2, .panel-heading h3 { margin: 0; letter-spacing: 0; }
.campaign-heading h2 { font-size: 24px; }
.campaign-heading p:not(.eyebrow) { margin: 6px 0 0; color: var(--color-text-2); }
.campaign-heading__status { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.eyebrow, .panel-kicker { margin: 0 0 4px; color: rgb(var(--primary-6)); font-size: 12px; font-weight: 700; }
.version-label, .snapshot-label, .coverage-summary { font-size: 12px; color: var(--color-text-3); font-variant-numeric: tabular-nums; }
.workflow-track { display: grid; grid-template-columns: repeat(5, minmax(90px, 1fr)); border: 1px solid var(--color-border-2); border-radius: 6px; overflow: hidden; background: var(--color-bg-2); }
.workflow-track__step { min-height: 44px; display: flex; align-items: center; justify-content: center; gap: 8px; color: var(--color-text-3); border-right: 1px solid var(--color-border-2); }
.workflow-track__step:last-child { border-right: 0; }
.workflow-track__step strong { display: grid; place-items: center; width: 22px; height: 22px; border-radius: 50%; background: var(--color-fill-3); }
.workflow-track__step--active { color: rgb(var(--primary-6)); background: rgb(var(--primary-1)); font-weight: 700; }
.workflow-track__step--completed { color: rgb(var(--success-6)); }
.campaign-spin { width: 100%; }
.campaign-workspace { display: grid; grid-template-columns: minmax(240px, 0.8fr) minmax(340px, 1.15fr) minmax(280px, 1fr); border: 1px solid var(--color-border-2); border-radius: 6px; background: var(--color-bg-2); min-height: 590px; }
.workspace-panel { min-width: 0; padding: 20px; border-right: 1px solid var(--color-border-2); }
.workspace-panel:last-child { border-right: 0; }
.panel-heading { min-height: 44px; justify-content: space-between; gap: 12px; margin-bottom: 18px; }
.panel-heading h3 { font-size: 17px; }
.field-stack { display: grid; gap: 16px; }
.scope-field { display: grid; gap: 7px; min-width: 0; color: var(--color-text-2); font-size: 13px; font-weight: 600; }
.evidence-id-input { width: 100%; min-height: 72px; padding: 8px 10px; resize: vertical; border: 1px solid var(--color-border-2); border-radius: 4px; outline: none; color: var(--color-text-1); background: var(--color-fill-1); font: 12px/1.5 ui-monospace, SFMono-Regular, Consolas, monospace; }
.evidence-id-input:focus { border-color: rgb(var(--primary-6)); }
.evidence-id-input:disabled { cursor: not-allowed; color: var(--color-text-4); }
.coverage-list { display: grid; gap: 10px; }
.coverage-row { display: grid; gap: 7px; padding: 12px 0; border-bottom: 1px solid var(--color-border-2); }
.coverage-row:first-child { padding-top: 0; }
.coverage-row:last-child { border-bottom: 0; }
.coverage-row__heading { justify-content: space-between; gap: 8px; }
.coverage-kind { font-size: 12px; color: var(--color-text-3); }
.coverage-row strong { font-size: 14px; overflow-wrap: anywhere; }
.coverage-row code, .gate-audit code { color: var(--color-text-3); font-size: 11px; overflow-wrap: anywhere; white-space: normal; }
.coverage-row p { margin: 0; font-size: 12px; line-height: 1.5; }
.coverage-gap { color: rgb(var(--warning-6)); }
.coverage-evidence { color: rgb(var(--success-6)); }
.gate-audit { display: grid; gap: 10px; margin-top: 18px; padding-top: 16px; border-top: 1px solid var(--color-border-2); }
.gate-audit div { display: grid; gap: 4px; }
.gate-audit span { color: var(--color-text-3); font-size: 12px; }
.campaign-action-bar { position: sticky; z-index: 8; bottom: 12px; justify-content: space-between; gap: 18px; min-height: 68px; padding: 12px 16px; border: 1px solid var(--color-border-2); border-radius: 6px; background: color-mix(in srgb, var(--color-bg-2) 94%, transparent); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); backdrop-filter: blur(12px); }
.action-bar__state { gap: 10px; flex: 0 0 auto; }
.action-bar__state div { display: grid; gap: 2px; }
.action-bar__state small { color: var(--color-text-3); }
.action-bar__buttons { justify-content: flex-end; gap: 8px; flex-wrap: wrap; }
.state-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--color-neutral-4); }
.state-dot--success { background: rgb(var(--success-6)); }
.state-dot--danger { background: rgb(var(--danger-6)); }
.state-dot--warning { background: rgb(var(--warning-6)); }
.state-dot--info { background: rgb(var(--primary-6)); }
@media (max-width: 1180px) {
  .campaign-workspace { grid-template-columns: minmax(240px, 0.85fr) minmax(360px, 1.15fr); }
  .validation-panel { grid-column: 1 / -1; border-top: 1px solid var(--color-border-2); border-right: 0; }
  .coverage-list { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .campaign-heading { align-items: flex-start; flex-direction: column; gap: 12px; }
  .workflow-track { grid-template-columns: repeat(5, minmax(72px, 1fr)); overflow-x: auto; }
  .workflow-track__step { min-width: 72px; font-size: 12px; }
  .workflow-track__step strong { display: none; }
  .campaign-workspace { grid-template-columns: minmax(0, 1fr); min-height: 0; }
  .workspace-panel { padding: 16px; border-right: 0; border-bottom: 1px solid var(--color-border-2); }
  .workspace-panel:last-child { border-bottom: 0; }
  .validation-panel { grid-column: auto; border-top: 0; }
  .coverage-list { grid-template-columns: minmax(0, 1fr); }
  .campaign-action-bar { position: static; align-items: stretch; flex-direction: column; }
  .action-bar__buttons { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .action-bar__buttons :deep(.arco-btn) { width: 100%; min-width: 0; white-space: normal; }
}
</style>
