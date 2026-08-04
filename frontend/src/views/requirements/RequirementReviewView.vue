<template>
  <section class="requirement-review-page" aria-labelledby="requirement-review-title">
    <header class="requirement-review-heading">
      <div class="requirement-review-heading__copy">
        <p class="eyebrow">需求评审 / Evidence Gate</p>
        <h2 id="requirement-review-title">需求证据工作台</h2>
        <p>把需求先转成可审查证据：评分、问题、澄清问题和风险项都在生成用例前确认。</p>
      </div>
      <div class="requirement-review-heading__status" aria-label="当前评审状态">
        <a-tag color="blue">RequirementReviewAgent</a-tag>
        <a-tag :color="workflowStageColor">{{ workflowStageLabel }}</a-tag>
        <a-tag :color="workflowStateColor">{{ store.review ? workflowStateLabel : '待创建候选' }}</a-tag>
        <span v-if="store.review?.workflow" class="version-label">v{{ store.review.workflow.lock_version }}</span>
      </div>
    </header>

    <a-alert v-if="store.errorMessage" type="error" show-icon>{{ store.errorMessage }}</a-alert>
    <a-alert
      v-if="store.exactRestoreFailed"
      data-test="exact-review-restore-failed"
      type="warning"
      show-icon
    >指定需求评审无法恢复，请返回工作台或刷新</a-alert>

    <div class="workflow-rail" data-test="workflow-rail" aria-label="需求到用例流程">
      <span class="workflow-rail__step workflow-rail__step--active"><strong>1</strong>输入需求</span>
      <span class="workflow-rail__line"></span>
      <span class="workflow-rail__step" :class="{ 'workflow-rail__step--active': reviewProgress >= 2 }"><strong>2</strong>分析并检索知识</span>
      <span class="workflow-rail__line"></span>
      <span class="workflow-rail__step" :class="{ 'workflow-rail__step--active': reviewProgress >= 3 }"><strong>3</strong>完成评审</span>
      <span class="workflow-rail__line"></span>
      <span class="workflow-rail__step" :class="{ 'workflow-rail__step--active': reviewProgress >= 4 }"><strong>4</strong>生成用例</span>
    </div>

    <div class="requirement-review-layout">
      <a-card class="requirement-panel input-panel" data-test="review-input-panel" :bordered="false">
        <template #title>
          <div class="panel-heading">
            <span class="panel-heading__icon" aria-hidden="true"><IconEdit /></span>
            <div><small>输入与上下文</small><strong>需求输入</strong></div>
          </div>
        </template>
        <form class="requirement-form" @submit.prevent="submitReview">
          <label>
            <span>需求标题</span>
            <a-input v-model="form.title" :disabled="explicitRestoreRequested" />
          </label>
          <label>
            <span>需求内容</span>
            <a-textarea
              v-model="form.content"
              :disabled="explicitRestoreRequested"
              placeholder="描述用户动作、系统响应、约束条件和失败处理。可以直接粘贴需求文档。"
              :auto-size="{ minRows: 8, maxRows: 12 }"
            />
          </label>
          <div class="auto-knowledge-panel" data-test="auto-knowledge-panel">
            <span class="auto-knowledge-panel__icon" aria-hidden="true"><IconSearch /></span>
            <div>
              <strong>评审前先检索项目知识</strong>
              <small>先查看命中的测试知识，再开始需求评审。命中证据会自动带入评审，不需要选择数据源或填写 ID。</small>
            </div>
            <a-button
              data-test="retrieve-before-review"
              size="small"
              type="outline"
              :disabled="explicitRestoreRequested"
              :loading="store.loadingKnowledge"
              @click="previewKnowledge"
            >
              <template #icon><IconSearch /></template>
              分析并检索知识
            </a-button>
          </div>
          <div v-if="store.knowledgePreview" class="knowledge-preview" data-test="knowledge-preview">
            <div class="knowledge-preview__header">
              <strong>{{ store.knowledgePreview.total > 0 ? `已找到 ${store.knowledgePreview.total} 条相关知识` : '暂未找到相关知识' }}</strong>
              <a-tag :color="store.knowledgePreview.total > 0 ? 'green' : 'gray'">
                {{ store.knowledgePreview.total > 0 ? '可带入评审' : '继续按需求内容评审' }}
              </a-tag>
            </div>
            <article v-for="item in store.knowledgePreview.items" :key="item.evidence_id" class="knowledge-preview__item">
              <div>
                <strong>{{ item.title }}</strong>
                <span>匹配度 {{ item.score }}</span>
              </div>
              <p>{{ item.snippet }}</p>
            </article>
            <a-empty v-if="store.knowledgePreview.items.length === 0" description="没有命中已审核知识，仍可继续评审" />
          </div>
          <div class="input-actions">
            <a-button
              data-test="start-review"
              html-type="submit"
              type="primary"
              :disabled="explicitRestoreRequested"
              :loading="store.loading"
            >
              <template #icon><IconPlayArrow /></template>
              开始评审
            </a-button>
          </div>
        </form>
      </a-card>

      <a-card class="requirement-panel evidence-panel" data-test="review-evidence-panel" :bordered="false">
        <template #title>
          <div class="panel-heading">
            <span class="panel-heading__icon panel-heading__icon--evidence" aria-hidden="true"><IconFile /></span>
            <div><small>评分、问题与门禁</small><strong>评审证据</strong></div>
          </div>
        </template>
        <a-spin :loading="store.loading" class="review-spin">
          <div v-if="store.review" class="review-result" data-test="review-result">
            <div class="score-strip">
              <div class="score-strip__overall">
                <span>综合评分</span>
                <strong>{{ store.review.overall_score }}</strong>
              </div>
              <div v-for="score in scoreItems" :key="score.label">
                <span>{{ score.label }}</span>
                <strong>{{ score.value }}</strong>
              </div>
            </div>

            <a-descriptions :column="2" bordered size="small">
              <a-descriptions-item label="需求标题">{{ store.requirement?.title ?? '未创建' }}</a-descriptions-item>
              <a-descriptions-item label="状态">{{ reviewStatusLabel(store.review.status) }}</a-descriptions-item>
              <a-descriptions-item label="人工门禁">
                <a-tag :color="workflowStateColor">{{ workflowStateLabel }}</a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="知识检索" :span="2">
                {{ store.review.used_knowledge ? `已自动使用 ${store.review.used_context_artifact_ids.length} 条项目知识证据` : '未命中可用知识，评审仍可继续' }}
              </a-descriptions-item>
            </a-descriptions>

            <div class="review-next-step" data-test="review-next-step">
              <div>
                <a-tag :color="unresolvedClarificationCount > 0 ? 'orange' : 'green'">
                  {{ unresolvedClarificationCount > 0 ? `还有 ${unresolvedClarificationCount} 个问题待澄清` : '评审结果已连接' }}
                </a-tag>
                <strong>{{ workflowNextAction }}</strong>
                <span>只有服务端确认完成评审、批准并消费本次批准后，才能进入下一阶段。</span>
              </div>
              <div class="review-next-step__actions">
                <a-button v-if="store.review.workflow?.can_submit" data-test="submit-stage-review" type="primary" @click="submitCurrentStage">
                  <template #icon><IconPlayArrow /></template>{{ submitButtonLabel }}
                </a-button>
                <a-button v-if="store.review.workflow?.can_complete_review" data-test="complete-review" :disabled="isRequirementReview && (reviewInputChanged || unresolvedClarificationCount > 0)" @click="completeCurrentReview">
                  <template #icon><IconCheck /></template>完成评审
                </a-button>
                <a-button v-if="store.review.workflow?.can_approve" data-test="reject-review" status="danger" @click="rejectCurrentReview">
                  <template #icon><IconClose /></template>拒绝
                </a-button>
                <a-button v-if="store.review.workflow?.can_approve" type="primary" data-test="approve-review" :disabled="isRequirementReview && reviewInputChanged" @click="approveCurrentReview">
                  <template #icon><IconCheck /></template>批准
                </a-button>
                <a-button v-if="store.review.workflow?.can_continue" type="primary" status="success" data-test="continue-workflow" :disabled="isRequirementReview && (reviewInputChanged || unresolvedClarificationCount > 0)" @click="continueCurrentStage">
                  批准并进入下一阶段<template #icon><IconRight /></template>
                </a-button>
              </div>
            </div>
            <a-alert v-if="reviewInputChanged" type="warning" show-icon>需求输入已变化，当前候选和批准不可继续使用。请重新评审。</a-alert>
            <a-textarea v-if="store.review.workflow?.can_approve" v-model="reviewComment" data-test="review-comment" placeholder="填写批准或拒绝说明（可选）" :auto-size="{ minRows: 2, maxRows: 4 }" />

            <div v-if="store.review.workflow?.can_edit" class="review-section candidate-editor" data-test="candidate-editor">
              <a-space>
                <a-button data-test="toggle-candidate-editor" @click="toggleCandidateEditor">
                  <template #icon><IconEdit /></template>{{ editingCandidate ? '取消编辑' : '编辑候选' }}
                </a-button>
                <a-tag v-if="editingCandidate" color="orange">保存后将创建新快照并使旧批准失效</a-tag>
              </a-space>
              <div v-if="editingCandidate" class="candidate-editor__body">
                <label v-for="(issue, index) in (isRiskReview ? [] : editableIssues)" :key="`issue-${index}`">
                  <span>问题 {{ index + 1 }}</span>
                  <a-input v-model="issue.text" :data-test="`edit-issue-${index}`" />
                </label>
                <label v-for="(_question, index) in (isRiskReview ? [] : editableQuestions)" :key="`question-${index}`">
                  <span>澄清问题 {{ index + 1 }}</span>
                  <a-input v-model="editableQuestions[index]" :data-test="`edit-question-${index}`" />
                </label>
                <label v-for="(_note, index) in (isRiskReview ? [] : editableNotes)" :key="`note-${index}`">
                  <span>测试设计建议 {{ index + 1 }}</span>
                  <a-input v-model="editableNotes[index]" :data-test="`edit-note-${index}`" />
                </label>
                <div v-for="(risk, index) in editableRisks" :key="`risk-${index}`" class="candidate-editor__risk">
                  <a-input v-model="risk.title" :data-test="`edit-risk-title-${index}`" />
                  <a-textarea v-model="risk.suggestion" :data-test="`edit-risk-suggestion-${index}`" :auto-size="{ minRows: 2, maxRows: 4 }" />
                </div>
                <template v-if="isTestPlanReview">
                  <label>
                    <span>测试策略</span>
                    <a-textarea v-model="editableTestPlanStrategy" data-test="edit-test-plan-strategy" :auto-size="{ minRows: 3, maxRows: 6 }" />
                  </label>
                  <div v-for="(item, index) in editableTestPlanItems" :key="`plan-${index}`" class="candidate-editor__risk">
                    <a-input v-model="item.risk_title" :data-test="`edit-plan-risk-${index}`" />
                    <a-textarea v-model="item.strategy" :data-test="`edit-plan-strategy-${index}`" :auto-size="{ minRows: 2, maxRows: 4 }" />
                  </div>
                </template>
                <a-button type="primary" data-test="save-candidate-edit" :loading="store.loading" @click="saveCandidateEdit">
                  <template #icon><IconSave /></template>保存人工编辑
                </a-button>
              </div>
            </div>
            <a-alert
              v-if="unresolvedClarificationCount > 0"
              type="warning"
              show-icon
            >请先回答澄清问题并重新评审，再进入用例生成。</a-alert>

            <div class="review-section">
              <h3>问题</h3>
              <a-list :data="store.review.issues" :bordered="false">
                <template #item="{ item }">
                  <a-list-item>
                    <a-space direction="vertical" size="mini">
                      <a-tag color="orange">{{ severityLabel(item.severity) }}</a-tag>
                      <strong>{{ issueTypeLabel(item.type) }}</strong>
                      <span>{{ item.text }}</span>
                    </a-space>
                  </a-list-item>
                </template>
              </a-list>
            </div>

            <div class="review-section">
              <h3>澄清问题</h3>
              <a-list :data="store.review.clarification_questions" :bordered="false">
                <template #item="{ item }">
                  <a-list-item>{{ item }}</a-list-item>
                </template>
              </a-list>
            </div>

            <div v-if="store.review.clarification_questions.length > 0" class="review-section clarification-panel">
              <h3>补充说明</h3>
              <label>
                <span>整体补充</span>
                <a-textarea data-test="supplement-text" v-model="supplementText" :auto-size="{ minRows: 3, maxRows: 6 }" />
              </label>
              <label v-for="question in store.review.clarification_questions" :key="question">
                <span>{{ question }}</span>
                <a-input data-test="clarification-answer" v-model="clarificationAnswerMap[question]" />
              </label>
              <a-button data-test="submit-supplement" type="primary" :loading="store.loading" @click="submitSupplement">
                补充后重新评审
              </a-button>
            </div>

            <div class="review-section">
              <h3>风险项</h3>
              <a-table :columns="riskColumns" :data="store.review.risk_items" :pagination="false" size="small">
                <template #risk_level="{ record }">
                  <a-tag :color="riskColor(record.risk_level)">{{ riskLevelLabel(record.risk_level) }}</a-tag>
                </template>
              </a-table>
            </div>

            <div v-if="isTestPlanReview" class="review-section" data-test="test-plan-review-panel">
              <h3>测试计划</h3>
              <a-alert
                v-if="testPlanStrategyRequired"
                type="warning"
                show-icon
              >高风险或严重风险需要明确测试策略，才能批准计划。</a-alert>
              <p>{{ store.review.test_plan_strategy || '待人工确认本轮测试策略。' }}</p>
              <a-table :columns="testPlanColumns" :data="store.review.test_plan_items ?? []" :pagination="false" size="small">
                <template #risk_level="{ record }">
                  <a-tag :color="riskColor(record.risk_level ?? 'medium')">{{ riskLevelLabel(record.risk_level ?? 'medium') }}</a-tag>
                </template>
              </a-table>
            </div>

            <div class="review-section document-panel">
              <h3>正式需求文档</h3>
              <a-space wrap>
                <a-button data-test="generate-document" type="primary" :disabled="!canGenerateDocument" :loading="store.loadingDocument" @click="store.generateRequirementDocument()">
                  <template #icon><IconFile /></template>生成需求文档
                </a-button>
                <a-button :loading="store.loadingDocument" @click="store.loadRequirementDocuments()">
                  <template #icon><IconRefresh /></template>刷新文档
                </a-button>
              </a-space>
              <div v-if="store.createdDocument" class="document-result">
                <strong>{{ store.createdDocument.document_number }}</strong>
                <span>{{ store.createdDocument.title }} · {{ store.createdDocument.status }}</span>
                <a :href="store.createdDocument.download_url">下载 Markdown</a>
              </div>
              <a-list v-if="store.documents.length > 0" :data="store.documents" :bordered="false">
                <template #item="{ item }">
                  <a-list-item>
                    <a-space direction="vertical" size="mini">
                      <strong>{{ item.document_number }}</strong>
                      <span>{{ item.title }} · {{ item.version }} · {{ item.status }}</span>
                      <a :href="item.download_url">下载 Markdown</a>
                    </a-space>
                  </a-list-item>
                </template>
              </a-list>
            </div>
          </div>

          <div v-else-if="!store.loading" class="review-empty-state" data-test="review-empty-state">
            <span aria-hidden="true"><IconFile /></span>
            <strong>等待评审证据</strong>
            <p>提交需求后展示评分、问题、澄清项与风险证据。</p>
          </div>
        </a-spin>
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import {
  IconCheck,
  IconClose,
  IconEdit,
  IconFile,
  IconPlayArrow,
  IconRefresh,
  IconRight,
  IconSave,
  IconSearch,
} from '@arco-design/web-vue/es/icon';

import type { RequirementReviewIssue, RequirementRiskItem, TestPlanItem } from '../../api/requirements';
import { useRequirementsStore } from '../../stores/requirements';

const store = useRequirementsStore();
const route = useRoute();

const form = reactive({
  title: '优惠券结算规则',
  sourceRef: 'manual',
  content:
    '用户在提交订单时，可以选择一张可用优惠券。优惠券不可与积分同时使用。过期优惠券不可使用。优惠券金额不能超过订单应付金额。提交订单后，系统需要展示优惠后的最终支付金额。',
});
const supplementText = ref('');
const reviewComment = ref('');
const editingCandidate = ref(false);
const editableIssues = ref<RequirementReviewIssue[]>([]);
const editableQuestions = ref<string[]>([]);
const editableNotes = ref<string[]>([]);
const editableRisks = ref<RequirementRiskItem[]>([]);
const editableTestPlanStrategy = ref('');
const editableTestPlanItems = ref<TestPlanItem[]>([]);
const clarificationAnswerMap = reactive<Record<string, string>>({});

function queryValue(value: unknown): string | undefined {
  const candidate = Array.isArray(value) ? value[0] : value;
  return typeof candidate === 'string' && candidate.length ? candidate : undefined;
}

const requestedRequirementId = computed(() => queryValue(route.query.requirement_id));
const requestedReviewId = computed(() => queryValue(route.query.requirement_review_id));
const requestedWorkflowRunId = computed(() => queryValue(route.query.workflow_run_id));
const requestedWorkflowStage = computed(() => queryValue(route.query.workflow_stage));
const explicitRestoreRequested = computed(() => (
  route.query.requirement_id !== undefined
  || route.query.requirement_review_id !== undefined
  || route.query.workflow_run_id !== undefined
  || route.query.workflow_stage !== undefined
));

const riskColumns = [
  { title: '风险', dataIndex: 'title' },
  { title: '等级', slotName: 'risk_level' },
  { title: '建议', dataIndex: 'suggestion' },
];

const testPlanColumns = [
  { title: '风险', dataIndex: 'risk_title' },
  { title: '等级', slotName: 'risk_level' },
  { title: '测试策略', dataIndex: 'strategy' },
];

const scoreItems = computed(() => {
  if (!store.review) {
    return [];
  }
  return [
    { label: '完整性', value: store.review.scores.completeness },
    { label: '清晰度', value: store.review.scores.clarity },
    { label: '一致性', value: store.review.scores.consistency },
    { label: '可测性', value: store.review.scores.testability },
    { label: '可行性', value: store.review.scores.feasibility },
    { label: '逻辑性', value: store.review.scores.logic },
  ];
});

const unresolvedClarificationCount = computed(() =>
  (store.review?.clarification_questions ?? []).filter(
    (question) => !clarificationAnswerMap[question]?.trim() && !supplementText.value.trim(),
  ).length,
);

const reviewInputChanged = computed(() => Boolean(
  store.requirement
  && (store.requirement.title !== form.title || store.requirement.content !== form.content),
));

const isRequirementReview = computed(() => store.review?.workflow?.stage === 'requirement_review');
const isRiskReview = computed(() => store.review?.workflow?.stage === 'risk_review');
const isTestPlanReview = computed(() => store.review?.workflow?.stage === 'test_plan_review');

const reviewProgress = computed(() => {
  if (
    store.review?.workflow?.can_continue
    || (store.review?.workflow?.stage && store.review.workflow.stage !== 'requirement_review')
  ) return 4;
  if (store.review) return 3;
  if (store.knowledgePreview) return 2;
  return 1;
});

const workflowStageLabel = computed(() => {
  const labels: Record<string, string> = {
    requirement_review: '需求评审',
    risk_review: '风险评审',
    test_plan_review: '测试计划评审',
  };
  return labels[store.review?.workflow?.stage ?? ''] ?? '需求输入';
});

const workflowStageColor = computed(() => {
  const colors: Record<string, string> = {
    risk_review: 'orange',
    test_plan_review: 'purple',
  };
  return colors[store.review?.workflow?.stage ?? ''] ?? 'blue';
});

const testPlanStrategyRequired = computed(() => Boolean(
  isTestPlanReview.value
  && !store.review?.test_plan_strategy?.trim()
  && store.review?.risk_items.some((risk) => ['high', 'critical'].includes(String(risk.risk_level).toLowerCase())),
));

const submitButtonLabel = computed(() => {
  if (isRiskReview.value) return '提交风险候选';
  if (isTestPlanReview.value) return '提交测试计划候选';
  return '提交候选';
});

const canGenerateDocument = computed(() => {
  const workflow = store.review?.workflow;
  return Boolean(workflow && (workflow.state === 'approved' || workflow.stage !== 'requirement_review'));
});

const workflowStateLabel = computed(() => {
  const labels: Record<string, string> = {
    waiting_review: '待人工评审',
    waiting_approval: '待批准',
    approved: '已批准',
    rejected: '已拒绝',
    draft: '草稿',
  };
  return labels[store.review?.workflow?.state ?? ''] ?? '未接入门禁';
});

const workflowStateColor = computed(() => {
  const colors: Record<string, string> = {
    approved: 'green',
    rejected: 'red',
    waiting_approval: 'orange',
  };
  return colors[store.review?.workflow?.state ?? ''] ?? 'blue';
});

const workflowNextAction = computed(() => {
  const workflow = store.review?.workflow;
  if (workflow?.can_submit) return '下一步：提交风险候选供人工评审';
  if (workflow?.can_complete_review) return '下一步：完成人工评审';
  if (workflow?.can_approve) return '下一步：批准或拒绝候选';
  if (workflow?.can_continue) return '下一步：消费批准并继续';
  return '等待服务端确认可执行操作';
});

function riskColor(level: string): string {
  const colors: Record<string, string> = {
    low: 'green',
    medium: 'orange',
    high: 'red',
    critical: 'purple',
  };
  return colors[level] ?? 'gray';
}

function riskLevelLabel(level: string): string {
  const labels: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '严重',
  };
  return labels[level] ?? level;
}

function severityLabel(severity: string): string {
  return riskLevelLabel(severity);
}

function issueTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    ambiguity: '歧义',
    missing_constraint: '约束缺失',
    inconsistency: '不一致',
    testability: '可测性',
  };
  return labels[type] ?? type.replace(/_/g, ' ');
}

function reviewStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    draft: '草稿',
    reviewed: '已评审',
    confirmed: '已确认',
  };
  return labels[status] ?? status;
}

async function previewKnowledge() {
  await store.retrieveKnowledgePreview(form.content);
}

async function submitReview() {
  if (store.knowledgePreviewQuery !== form.content.trim()) {
    await store.retrieveKnowledgePreview(form.content);
  }
  void store.reviewRequirement({
    title: form.title,
    content: form.content,
    sourceRef: form.sourceRef,
    contextArtifactIds: store.previewContextArtifactIds,
  });
}

async function submitSupplement() {
  const answers = (store.review?.clarification_questions ?? [])
    .map((question) => ({
      question,
      answer: clarificationAnswerMap[question]?.trim() ?? '',
    }))
    .filter((item) => item.answer);
  if (store.knowledgePreviewQuery !== form.content.trim()) {
    await store.retrieveKnowledgePreview(form.content);
  }
  void store.reviewRequirement({
    title: form.title,
    content: form.content,
    sourceRef: form.sourceRef,
    contextArtifactIds: store.previewContextArtifactIds,
    supplementText: supplementText.value,
    clarificationAnswers: answers,
  });
}

function toggleCandidateEditor() {
  editingCandidate.value = !editingCandidate.value;
  if (!editingCandidate.value || !store.review) return;
  editableIssues.value = store.review.issues.map((item) => ({ ...item }));
  editableQuestions.value = [...store.review.clarification_questions];
  editableNotes.value = store.review.test_design_notes.map((item) => String(item));
  editableRisks.value = store.review.risk_items.map((item) => ({ ...item }));
  editableTestPlanStrategy.value = store.review.test_plan_strategy ?? '';
  editableTestPlanItems.value = (store.review.test_plan_items ?? []).map((item) => ({ ...item }));
}

async function saveCandidateEdit() {
  const saved = isTestPlanReview.value
    ? await store.editTestPlanReview(editableTestPlanStrategy.value, editableTestPlanItems.value, reviewComment.value)
    : isRiskReview.value
    ? await store.editRiskReview(editableRisks.value, reviewComment.value)
    : await store.editReview({
        issues: editableIssues.value,
        clarification_questions: editableQuestions.value,
        test_design_notes: editableNotes.value,
        risk_items: editableRisks.value,
      });
  if (saved) editingCandidate.value = false;
}

function submitCurrentStage() {
  if (isTestPlanReview.value) return store.submitTestPlanReview();
  if (isRiskReview.value) return store.submitRiskReview();
  return false;
}

function completeCurrentReview() {
  if (isTestPlanReview.value) return store.completeTestPlanReview();
  return isRiskReview.value ? store.completeRiskReview() : store.completeReview();
}

function approveCurrentReview() {
  if (isTestPlanReview.value) return store.approveTestPlanReview(reviewComment.value);
  return isRiskReview.value ? store.approveRiskReview(reviewComment.value) : store.approveReview(reviewComment.value);
}

function rejectCurrentReview() {
  if (isTestPlanReview.value) return store.rejectTestPlanReview(reviewComment.value);
  return isRiskReview.value ? store.rejectRiskReview(reviewComment.value) : store.rejectReview(reviewComment.value);
}

function continueCurrentStage() {
  if (isTestPlanReview.value) return store.continueTestPlanReview();
  return isRiskReview.value ? store.continueRiskReview() : store.continueReview();
}

function syncRequirementForm() {
  if (store.requirement) {
    form.title = store.requirement.title;
    form.sourceRef = store.requirement.source_ref ?? '';
    form.content = store.requirement.content;
  }
}

onMounted(async () => {
  if (explicitRestoreRequested.value) {
    const restored = await store.loadExactRequirementReview(
      store.projectId,
      requestedRequirementId.value,
      requestedReviewId.value,
      requestedWorkflowRunId.value,
      requestedWorkflowStage.value,
    );
    if (restored) {
      syncRequirementForm();
      void store.loadRequirementDocuments();
    }
    return;
  }
  store.clearExplicitRestoreRequest();
  if (store.restoreLatestRequirementReview() && store.requirement) {
    syncRequirementForm();
    await store.refreshCurrentReview();
  }
  void store.loadRequirementDocuments();
});

watch(
  () => form.content,
  (content) => {
    if (store.knowledgePreviewQuery && store.knowledgePreviewQuery !== content.trim()) {
      store.clearKnowledgePreview();
    }
  },
);
</script>

<style scoped>
.requirement-review-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  padding-bottom: 12px;
}

.requirement-review-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.requirement-review-heading__copy {
  min-width: 0;
}

.requirement-review-heading h2,
.requirement-review-heading p {
  margin: 0;
}

.requirement-review-heading h2 {
  margin-top: 2px;
  color: var(--color-text-1);
  font-size: 24px;
  line-height: 1.25;
}

.requirement-review-heading p:not(.eyebrow) {
  margin-top: 8px;
  max-width: 720px;
  color: var(--color-text-3);
  line-height: 1.65;
}

.requirement-review-heading__status {
  display: flex;
  max-width: 420px;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.version-label {
  display: inline-flex;
  min-width: 32px;
  height: 24px;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  border: 1px solid var(--color-border-2);
  border-radius: 6px;
  color: var(--color-text-3);
  background: var(--color-fill-1);
  font-size: 12px;
  font-weight: 700;
}

.workflow-rail {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border: 1px solid var(--color-border-2);
  border-radius: 6px;
  background: var(--color-bg-2);
  color: var(--color-text-4);
  font-size: 12px;
}

.workflow-rail__step {
  display: inline-flex;
  min-width: 0;
  align-items: center;
  gap: 7px;
  white-space: nowrap;
}

.workflow-rail__step strong {
  display: inline-flex;
  width: 22px;
  height: 22px;
  flex: 0 0 22px;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--color-fill-2);
  color: var(--color-text-3);
  font-size: 11px;
}

.workflow-rail__step--active {
  color: rgb(var(--primary-6));
  font-weight: 700;
}

.workflow-rail__step--active strong {
  color: #ffffff;
  background: rgb(var(--primary-6));
}

.workflow-rail__line {
  height: 1px;
  min-width: 22px;
  flex: 1;
  background: var(--color-border-2);
}

.requirement-review-layout {
  display: grid;
  grid-template-columns: minmax(340px, 0.82fr) minmax(520px, 1.45fr);
  align-items: start;
  gap: 16px;
}

.requirement-panel {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--color-border-2);
  border-radius: 6px;
  background: var(--color-bg-2);
  box-shadow: 0 4px 14px rgba(29, 41, 57, 0.05);
}

.requirement-panel :deep(.arco-card-header) {
  height: auto;
  min-height: 58px;
  padding: 12px 16px;
  border-bottom-color: var(--color-border-2);
}

.requirement-panel :deep(.arco-card-body) {
  padding: 16px;
}

.panel-heading {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 10px;
}

.panel-heading__icon {
  display: inline-flex;
  width: 32px;
  height: 32px;
  flex: 0 0 32px;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: rgb(var(--primary-6));
  background: rgb(var(--primary-1));
  font-size: 17px;
}

.panel-heading__icon--evidence {
  color: rgb(var(--success-6));
  background: rgb(var(--success-1));
}

.panel-heading div {
  display: grid;
  min-width: 0;
  gap: 1px;
}

.panel-heading small {
  color: var(--color-text-3);
  font-size: 11px;
  font-weight: 500;
}

.panel-heading strong {
  color: var(--color-text-1);
  font-size: 15px;
}

.requirement-form,
.clarification-panel label {
  display: grid;
  gap: 14px;
}

.requirement-form label {
  display: grid;
  gap: 7px;
  color: var(--color-text-2);
  font-weight: 700;
}

.requirement-form label > span {
  font-size: 13px;
}

.auto-knowledge-panel {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border: 1px solid rgb(var(--success-3));
  border-radius: 6px;
  background: rgb(var(--success-1));
}

.auto-knowledge-panel__icon {
  display: inline-flex;
  width: 26px;
  height: 26px;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: rgb(var(--success-7));
  background: var(--color-bg-2);
  font-weight: 800;
}

.auto-knowledge-panel strong,
.auto-knowledge-panel small {
  display: block;
}

.auto-knowledge-panel strong {
  color: rgb(var(--success-7));
  font-size: 13px;
}

.auto-knowledge-panel small {
  margin-top: 3px;
  color: var(--color-text-2);
  line-height: 1.5;
}

.knowledge-preview {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px solid rgb(var(--success-3));
  border-radius: 6px;
  background: rgb(var(--success-1));
}

.knowledge-preview__header,
.knowledge-preview__item > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.knowledge-preview__header strong,
.knowledge-preview__item strong {
  color: rgb(var(--success-7));
}

.knowledge-preview__item {
  display: grid;
  gap: 4px;
  padding: 9px 10px;
  border: 1px solid rgb(var(--success-2));
  border-radius: 6px;
  background: var(--color-bg-2);
}

.knowledge-preview__item span {
  color: var(--color-text-3);
  font-size: 11px;
}

.knowledge-preview__item p {
  margin: 0;
  color: var(--color-text-2);
  font-size: 12px;
  line-height: 1.55;
}

.input-actions {
  display: grid;
  gap: 8px;
}

.input-actions :deep(.arco-btn) {
  width: 100%;
}

.review-spin,
.review-spin :deep(.arco-spin) {
  display: block;
  width: 100%;
}

.review-empty-state {
  display: grid;
  min-height: 240px;
  place-items: center;
  align-content: center;
  gap: 8px;
  padding: 28px 20px;
  color: var(--color-text-3);
  text-align: center;
}

.review-empty-state > span {
  display: inline-flex;
  width: 48px;
  height: 48px;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border-2);
  border-radius: 8px;
  color: rgb(var(--primary-6));
  background: var(--color-fill-1);
  font-size: 24px;
}

.review-empty-state strong {
  color: var(--color-text-2);
  font-size: 15px;
}

.review-empty-state p {
  max-width: 320px;
  margin: 0;
  line-height: 1.6;
}

.review-result {
  min-width: 0;
}

.score-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(82px, 1fr));
  gap: 8px;
  margin-bottom: 16px;
}

.score-strip div {
  min-height: 70px;
  padding: 10px;
  border: 1px solid var(--color-border-2);
  border-radius: 6px;
  background: var(--color-fill-1);
}

.score-strip .score-strip__overall {
  border-color: rgb(var(--primary-3));
  background: rgb(var(--primary-1));
}

.score-strip span,
.score-strip strong {
  display: block;
}

.score-strip span {
  color: var(--color-text-3);
  font-size: 12px;
}

.score-strip strong {
  margin-top: 6px;
  color: rgb(var(--primary-6));
  font-size: 22px;
  line-height: 1;
}

.review-section {
  display: grid;
  min-width: 0;
  gap: 12px;
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px solid var(--color-border-2);
}

.candidate-editor {
  padding: 14px;
  border: 1px solid var(--color-border-2);
  border-radius: 6px;
  background: var(--color-fill-1);
}

.candidate-editor__body,
.candidate-editor__body label,
.candidate-editor__risk {
  display: grid;
  gap: 8px;
}

.candidate-editor__body {
  margin-top: 12px;
}

.candidate-editor__body label span {
  color: var(--color-text-2);
  font-size: 12px;
  font-weight: 700;
}

.review-next-step {
  position: sticky;
  z-index: 6;
  top: 82px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 18px;
  padding: 14px;
  border: 1px solid rgb(var(--success-3));
  border-radius: 6px;
  background: color-mix(in srgb, rgb(var(--success-1)) 94%, transparent);
  box-shadow: 0 8px 20px rgba(29, 41, 57, 0.09);
  backdrop-filter: blur(12px);
}

.review-next-step > div {
  display: grid;
  gap: 5px;
}

.review-next-step strong {
  color: rgb(var(--success-7));
}

.review-next-step span {
  color: var(--color-text-2);
  font-size: 12px;
  line-height: 1.5;
}

.review-next-step__actions {
  display: flex !important;
  max-width: 420px;
  justify-content: flex-end;
  gap: 8px !important;
  flex-wrap: wrap;
}

.review-section h3 {
  margin: 0;
  color: var(--color-text-1);
  font-size: 15px;
}

.clarification-panel,
.document-panel {
  padding: 14px;
  border: 1px solid var(--color-border-2);
  border-radius: 6px;
  background: var(--color-fill-1);
}

.clarification-panel label span {
  color: var(--color-text-2);
  font-weight: 700;
}

.document-result {
  display: grid;
  gap: 4px;
  margin-top: 12px;
  padding: 12px;
  border: 1px solid rgb(var(--success-3));
  border-radius: 6px;
  background: rgb(var(--success-1));
}

.review-section :deep(.arco-table-container) {
  overflow-x: auto;
}

@media (max-width: 1100px) {
  .requirement-review-layout {
    grid-template-columns: 1fr;
  }

  .review-next-step {
    position: static;
    align-items: stretch;
    flex-direction: column;
  }

  .review-next-step__actions {
    max-width: none;
    justify-content: flex-start;
  }

  .auto-knowledge-panel {
    grid-template-columns: 28px minmax(0, 1fr);
  }

  .auto-knowledge-panel .arco-btn {
    grid-column: 2;
    justify-self: start;
  }
}

@media (max-width: 700px) {
  .requirement-review-page {
    gap: 14px;
  }

  .requirement-review-heading {
    gap: 12px;
    flex-direction: column;
  }

  .requirement-review-heading h2 {
    font-size: 22px;
  }

  .requirement-review-heading p:not(.eyebrow) {
    margin-top: 6px;
    line-height: 1.55;
  }

  .requirement-review-heading__status {
    max-width: none;
    justify-content: flex-start;
  }

  .workflow-rail {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    padding: 8px;
  }

  .workflow-rail__step {
    min-height: 40px;
    padding: 7px 8px;
    border-radius: 5px;
    background: var(--color-fill-1);
    line-height: 1.35;
    white-space: normal;
  }

  .workflow-rail__step--active {
    background: rgb(var(--primary-1));
  }

  .workflow-rail__line {
    display: none;
  }

  .requirement-panel :deep(.arco-card-header) {
    min-height: 54px;
    padding: 10px 14px;
  }

  .requirement-panel :deep(.arco-card-body) {
    padding: 14px;
  }

  .auto-knowledge-panel {
    grid-template-columns: 28px minmax(0, 1fr);
  }

  .auto-knowledge-panel .arco-btn {
    grid-column: 1 / -1;
    width: 100%;
    justify-self: stretch;
  }

  .knowledge-preview__header,
  .knowledge-preview__item > div {
    align-items: flex-start;
    flex-direction: column;
  }

  .review-empty-state {
    min-height: 190px;
    padding: 22px 12px;
  }

  .score-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .score-strip .score-strip__overall {
    grid-column: 1 / -1;
  }

  .review-next-step__actions {
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .review-next-step__actions :deep(.arco-btn) {
    width: 100%;
    min-width: 0;
    height: auto;
    min-height: 34px;
    padding-top: 6px;
    padding-bottom: 6px;
    white-space: normal;
  }

  .review-next-step__actions [data-test='continue-workflow'] {
    grid-column: 1 / -1;
  }

  .candidate-editor > :deep(.arco-space),
  .document-panel > :deep(.arco-space) {
    width: 100%;
  }
}
</style>
