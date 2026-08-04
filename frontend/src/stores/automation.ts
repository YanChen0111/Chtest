import { defineStore } from 'pinia';

import {
  approveAndContinueAutomationPlanReviewWorkflow,
  approveAndContinueAutomationDraftReviewWorkflow,
  approveAutomationPlan,
  approveAutomationPlanReviewWorkflow,
  approveAutomationDraft,
  approveAutomationDraftReviewWorkflow,
  completeAutomationPlanReviewWorkflow,
  completeAutomationDraftReviewWorkflow,
  continueAutomationPlanReviewWorkflow,
  continueAutomationDraftReviewWorkflow,
  createAutomationPlan,
  createAutomationDraft,
  editAutomationPlanReviewWorkflow,
  editAutomationDraft,
  editAutomationDraftReviewWorkflow,
  generateAutomationDraftFromPlan,
  getAutomationDraft,
  getAutomationDraftReviewWorkflow,
  getAutomationPlanReviewWorkflow,
  rejectAutomationPlanReviewWorkflow,
  rejectAutomationDraftReviewWorkflow,
  submitAutomationPlanReviewWorkflow,
  submitAutomationDraftReviewWorkflow,
  type AutomationDraftCreateRead,
  type AutomationDraftRead,
  type AutomationDraftReviewRead,
  type AutomationDraftReviewWorkflowRead,
  type AutomationPlanRead,
  type AutomationPlanReviewRead,
  type AutomationPlanReviewWorkflowRead,
} from '../api/automation';
import { listTestCases, type TestCaseListItem } from '../api/cases';
import { getProjectSettings, type ProjectTestCommand } from '../api/projects';
import { getRequirement, getRequirementReview } from '../api/requirements';
import { listReviewHistory, type ReviewHistoryItem } from '../api/reviewHistory';
import {
  DEFAULT_PROJECT_ID,
  getLatestApprovedTestCaseContext,
  getLatestAutomationDraftContext,
  saveLatestAutomationDraftContext,
} from './workflowContext';

export const useAutomationStore = defineStore('automation', {
  state: () => {
    const latestCase = getLatestApprovedTestCaseContext();
    return {
      projectId: latestCase?.projectId ?? DEFAULT_PROJECT_ID,
      testCaseId: latestCase?.testCaseId ?? '',
      requirementReviewId: '',
      testCases: [] as TestCaseListItem[],
      testCommands: [] as ProjectTestCommand[],
      plan: null as AutomationPlanRead | null,
      lastPlanReview: null as AutomationPlanReviewRead | null,
      planReviewWorkflow: null as AutomationPlanReviewWorkflowRead | null,
      planReviewHistory: [] as ReviewHistoryItem[],
      createdDraft: null as AutomationDraftCreateRead | null,
      draft: null as AutomationDraftRead | null,
      lastReview: null as AutomationDraftReviewRead | null,
      draftReviewWorkflow: null as AutomationDraftReviewWorkflowRead | null,
      reviewHistory: [] as ReviewHistoryItem[],
      requestedRequirementId: null as string | null,
      requestedReviewId: null as string | null,
      requestedWorkflowRunId: null as string | null,
      requestedWorkflowStage: null as string | null,
      exactRestoreFailed: false,
      loading: false,
      loadingAssets: false,
      errorMessage: '',
      assetErrorMessage: '',
    };
  },
  actions: {
    clearExplicitRestoreRequest() {
      this.requestedRequirementId = null;
      this.requestedReviewId = null;
      this.requestedWorkflowRunId = null;
      this.requestedWorkflowStage = null;
      this.exactRestoreFailed = false;
      this.errorMessage = '';
      this.requirementReviewId = this.plan?.requirement_review_id ?? '';
    },
    clearAutomationReviewSelection() {
      this.testCaseId = '';
      this.requirementReviewId = '';
      this.testCases = [];
      this.testCommands = [];
      this.plan = null;
      this.lastPlanReview = null;
      this.planReviewWorkflow = null;
      this.planReviewHistory = [];
      this.createdDraft = null;
      this.draft = null;
      this.lastReview = null;
      this.draftReviewWorkflow = null;
      this.reviewHistory = [];
      this.assetErrorMessage = '';
    },
    async loadExactAutomationPlanReview(
      projectId: string,
      requirementId?: string,
      reviewId?: string,
      workflowRunId?: string,
      workflowStage?: string,
    ) {
      this.loading = true;
      this.errorMessage = '';
      this.projectId = projectId;
      this.requestedRequirementId = requirementId ?? null;
      this.requestedReviewId = reviewId ?? null;
      this.requestedWorkflowRunId = workflowRunId ?? null;
      this.requestedWorkflowStage = workflowStage ?? 'automation_plan_review';
      this.exactRestoreFailed = false;
      this.clearAutomationReviewSelection();
      try {
        if (!requirementId || !reviewId || !workflowRunId) {
          throw new Error('AutomationPlanReview 精确恢复参数不完整。');
        }
        const expectedStage = workflowStage ?? 'automation_plan_review';
        if (expectedStage !== 'automation_plan_review') {
          throw new Error('请求的工作流阶段不是 AutomationPlanReview。');
        }
        const [requirement, review, planReview] = await Promise.all([
          getRequirement(requirementId),
          getRequirementReview(requirementId),
          getAutomationPlanReviewWorkflow(projectId, reviewId),
        ]);
        if (
          requirement.id !== requirementId
          || requirement.project_id !== projectId
          || requirement.status !== 'active'
          || review.id !== reviewId
          || review.requirement_id !== requirementId
          || planReview.project_id !== projectId
          || planReview.requirement_review_id !== reviewId
          || planReview.workflow.stage !== expectedStage
          || planReview.workflow.run_id !== workflowRunId
        ) {
          throw new Error('请求的 AutomationPlanReview 与服务端权威工作流不匹配。');
        }
        this.requirementReviewId = reviewId;
        this.planReviewWorkflow = planReview;
        return true;
      } catch (error) {
        this.clearAutomationReviewSelection();
        this.exactRestoreFailed = true;
        this.errorMessage = error instanceof Error ? error.message : '无法恢复指定的 AutomationPlanReview。';
        return false;
      } finally {
        this.loading = false;
      }
    },
    loadLatestApprovedTestCaseContext() {
      const latestCase = getLatestApprovedTestCaseContext();
      if (!latestCase) {
        return false;
      }
      this.projectId = latestCase.projectId;
      this.testCaseId = latestCase.testCaseId;
      return true;
    },
    async loadReviewerAssets() {
      this.loadingAssets = true;
      this.assetErrorMessage = '';
      try {
        const [testCaseLibrary, projectSettings] = await Promise.all([
          listTestCases(this.projectId),
          getProjectSettings(this.projectId),
        ]);
        this.testCases = testCaseLibrary.items.filter((item) => item.status === 'active');
        this.testCommands = projectSettings.test_commands.filter((item) => item.status === 'active');
      } catch (error) {
        this.assetErrorMessage = error instanceof Error ? error.message : '评审资产加载失败';
      } finally {
        this.loadingAssets = false;
      }
    },
    async createPlan(data: { testCaseId: string; targetFramework: string; useKnowledge: boolean }) {
      this.loading = true;
      this.errorMessage = '';
      this.testCaseId = data.testCaseId;
      this.plan = null;
      this.lastPlanReview = null;
      this.planReviewHistory = [];
      this.createdDraft = null;
      this.draft = null;
      this.lastReview = null;
      this.reviewHistory = [];
      try {
        this.plan = await createAutomationPlan({
          project_id: this.projectId,
          test_case_id: data.testCaseId,
          target_framework: data.targetFramework,
          use_knowledge: data.useKnowledge,
          context_artifact_ids: [],
          prompt_version: 'automation_plan_generation:v1',
          skill_version: 'automation-plan-skill:v1',
        });
        this.requirementReviewId = this.plan.requirement_review_id ?? '';
        await this.loadAutomationPlanReviewWorkflow();
        await this.loadCurrentPlanReviewHistory();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '自动化方案生成失败';
      } finally {
        this.loading = false;
      }
    },
    async approveCurrentPlan(reviewComment: string) {
      if (!this.plan) {
        this.errorMessage = '请先生成自动化方案';
        return;
      }
      this.loading = true;
      this.errorMessage = '';
      try {
        this.lastPlanReview = await approveAutomationPlan(this.plan.id, reviewComment);
        this.plan = { ...this.plan, status: this.lastPlanReview.status, review_comment: reviewComment };
        await this.loadAutomationPlanReviewWorkflow();
        await this.loadCurrentPlanReviewHistory();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '自动化方案审批失败';
      } finally {
        this.loading = false;
      }
    },
    async generateDraftFromPlan() {
      if (!this.plan) {
        this.errorMessage = '请先生成自动化方案';
        return;
      }
      this.loading = true;
      this.errorMessage = '';
      try {
        this.createdDraft = await generateAutomationDraftFromPlan(this.plan.id);
        this.plan = { ...this.plan, status: 'draft_generated' };
        this.draft = await getAutomationDraft(this.createdDraft.automation_draft_id);
        this.rememberCurrentDraft();
        await this.loadAutomationDraftReviewWorkflow();
        await Promise.all([this.loadCurrentPlanReviewHistory(), this.loadCurrentDraftReviewHistory()]);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '自动化草稿生成失败';
      } finally {
        this.loading = false;
      }
    },
    async createDraft(data: { testCaseId: string; targetFramework: string }) {
      this.loading = true;
      this.errorMessage = '';
      this.testCaseId = data.testCaseId;
      try {
        this.createdDraft = await createAutomationDraft({
          project_id: this.projectId,
          test_case_id: data.testCaseId,
          requirement_id: null,
          automation_plan_id: null,
          target_framework: data.targetFramework,
          prompt_version: 'automation_draft_generation:v1',
          skill_version: 'automation-draft-skill:v1',
        });
        this.draft = await getAutomationDraft(this.createdDraft.automation_draft_id);
        this.rememberCurrentDraft();
        await this.loadAutomationDraftReviewWorkflow();
        await this.loadCurrentDraftReviewHistory();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '自动化草稿生成失败';
      } finally {
        this.loading = false;
      }
    },
    async editCurrentDraft(reviewComment: string) {
      if (!this.draft) {
        this.errorMessage = '请先生成自动化草稿';
        return;
      }
      this.loading = true;
      this.errorMessage = '';
      try {
        this.lastReview = await editAutomationDraft(this.draft.id, {
          draft_code: this.draft.draft_code.replace('assert True', 'assert True  # reviewed'),
          suggested_file_path: this.draft.suggested_file_path,
          execution_notes: this.draft.execution_notes,
          risk_notes: this.draft.risk_notes,
          review_comment: reviewComment,
        });
        this.draft = { ...this.draft, status: this.lastReview.status, review_comment: reviewComment };
        this.rememberCurrentDraft();
        await this.loadAutomationDraftReviewWorkflow();
        await this.loadCurrentDraftReviewHistory();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '自动化草稿编辑失败';
      } finally {
        this.loading = false;
      }
    },
    async approveCurrentDraft(reviewComment: string) {
      if (!this.draft) {
        this.errorMessage = '请先生成自动化草稿';
        return;
      }
      this.loading = true;
      this.errorMessage = '';
      try {
        this.lastReview = await approveAutomationDraft(this.draft.id, reviewComment);
        this.draft = { ...this.draft, status: this.lastReview.status, review_comment: reviewComment };
        this.rememberCurrentDraft();
        await this.loadAutomationDraftReviewWorkflow();
        await this.loadCurrentDraftReviewHistory();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '自动化草稿审批失败';
      } finally {
        this.loading = false;
      }
    },
    async restoreLatestAutomationDraft() {
      const context = getLatestAutomationDraftContext();
      if (!context || context.projectId !== this.projectId) {
        return false;
      }
      this.testCaseId = context.testCaseId ?? this.testCaseId;
      if (context.draft) {
        this.draft = context.draft;
        return true;
      }
      try {
        this.draft = await getAutomationDraft(context.automationDraftId);
        this.rememberCurrentDraft();
        return true;
      } catch {
        return false;
      }
    },
    rememberCurrentDraft() {
      if (!this.draft) {
        return;
      }
      saveLatestAutomationDraftContext({
        projectId: this.projectId,
        requirementReviewId: this.requirementReviewId || this.plan?.requirement_review_id || null,
        testCaseId: this.draft.test_case_id,
        automationDraftId: this.draft.id,
        status: this.draft.status,
        targetFramework: this.draft.target_framework,
        draft: this.draft,
      });
    },
    async loadCurrentDraftReviewHistory() {
      if (!this.draft) {
        this.reviewHistory = [];
        return;
      }
      const history = await listReviewHistory({
        projectId: this.projectId,
        entityType: 'AutomationDraft',
        entityId: this.draft.id,
        limit: 20,
      });
      this.reviewHistory = history.items;
    },
    async loadCurrentPlanReviewHistory() {
      if (!this.plan) {
        this.planReviewHistory = [];
        return;
      }
      const history = await listReviewHistory({
        projectId: this.projectId,
        entityType: 'AutomationPlan',
        entityId: this.plan.id,
        limit: 20,
      });
      this.planReviewHistory = history.items;
    },
    async loadAutomationPlanReviewWorkflow() {
      const requirementReviewId = this.requirementReviewId || this.plan?.requirement_review_id;
      if (!this.projectId || !requirementReviewId) {
        this.planReviewWorkflow = null;
        return null;
      }
      try {
        this.planReviewWorkflow = await getAutomationPlanReviewWorkflow(this.projectId, requirementReviewId);
        return this.planReviewWorkflow;
      } catch {
        this.planReviewWorkflow = null;
        return null;
      }
    },
    currentAutomationPlanDecisionSnapshot() {
      if (!this.plan) {
        return [];
      }
      return [
        {
          automation_plan_id: this.plan.id,
          test_case_id: this.plan.test_case_id,
          status: this.plan.status,
          target_framework: this.plan.target_framework,
          review_comment: this.plan.review_comment,
        },
      ];
    },
    async runAutomationPlanWorkflowAction(action: () => Promise<AutomationPlanReviewWorkflowRead>) {
      this.loading = true;
      this.errorMessage = '';
      try {
        this.planReviewWorkflow = await action();
        return true;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'AutomationPlanReview workflow action failed';
        await this.loadAutomationPlanReviewWorkflow();
        return false;
      } finally {
        this.loading = false;
      }
    },
    async submitAutomationPlanReviewGate() {
      const workflow = this.planReviewWorkflow?.workflow;
      const requirementReviewId = this.requirementReviewId || this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId) return false;
      return this.runAutomationPlanWorkflowAction(() => submitAutomationPlanReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async completeAutomationPlanReviewGate() {
      const workflow = this.planReviewWorkflow?.workflow;
      const requirementReviewId = this.requirementReviewId || this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId) return false;
      return this.runAutomationPlanWorkflowAction(() => completeAutomationPlanReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async editAutomationPlanReviewGate() {
      const workflow = this.planReviewWorkflow?.workflow;
      const requirementReviewId = this.requirementReviewId || this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId || !this.plan) return false;
      return this.runAutomationPlanWorkflowAction(() => editAutomationPlanReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
        plan_decisions: this.currentAutomationPlanDecisionSnapshot(),
      }));
    },
    async approveAutomationPlanReviewGate(comment?: string) {
      const workflow = this.planReviewWorkflow?.workflow;
      const requirementReviewId = this.requirementReviewId || this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId) return false;
      return this.runAutomationPlanWorkflowAction(() => approveAutomationPlanReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async rejectAutomationPlanReviewGate(comment?: string) {
      const workflow = this.planReviewWorkflow?.workflow;
      const requirementReviewId = this.requirementReviewId || this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId) return false;
      return this.runAutomationPlanWorkflowAction(() => rejectAutomationPlanReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async continueAutomationPlanReviewGate() {
      const workflow = this.planReviewWorkflow?.workflow;
      const requirementReviewId = this.requirementReviewId || this.plan?.requirement_review_id;
      const approvalDecisionId = workflow?.approval_decision_id;
      if (!workflow || !requirementReviewId || !approvalDecisionId) return false;
      return this.runAutomationPlanWorkflowAction(() => continueAutomationPlanReviewWorkflow(
        this.projectId,
        requirementReviewId,
        {
          expected_version: workflow.lock_version,
          approval_decision_id: approvalDecisionId,
        },
      ));
    },
    async approveAndContinueAutomationPlanReviewGate(comment?: string) {
      const workflow = this.planReviewWorkflow?.workflow;
      const requirementReviewId = this.requirementReviewId || this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId) return false;
      return this.runAutomationPlanWorkflowAction(() => approveAndContinueAutomationPlanReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async loadAutomationDraftReviewWorkflow() {
      const requirementReviewId = this.plan?.requirement_review_id;
      if (!this.projectId || !requirementReviewId || !this.draft) {
        this.draftReviewWorkflow = null;
        return null;
      }
      try {
        this.draftReviewWorkflow = await getAutomationDraftReviewWorkflow(this.projectId, requirementReviewId);
        return this.draftReviewWorkflow;
      } catch {
        this.draftReviewWorkflow = null;
        return null;
      }
    },
    currentAutomationDraftDecisionSnapshot() {
      if (!this.draft) {
        return [];
      }
      return [
        {
          automation_draft_id: this.draft.id,
          automation_plan_id: this.draft.automation_plan_id,
          test_case_id: this.draft.test_case_id,
          status: this.draft.status,
          target_framework: this.draft.target_framework,
          review_comment: this.draft.review_comment,
        },
      ];
    },
    async runAutomationDraftWorkflowAction(action: () => Promise<AutomationDraftReviewWorkflowRead>) {
      this.loading = true;
      this.errorMessage = '';
      try {
        this.draftReviewWorkflow = await action();
        return true;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'AutomationDraftReview workflow action failed';
        await this.loadAutomationDraftReviewWorkflow();
        return false;
      } finally {
        this.loading = false;
      }
    },
    async submitAutomationDraftReviewGate() {
      const workflow = this.draftReviewWorkflow?.workflow;
      const requirementReviewId = this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId) return false;
      return this.runAutomationDraftWorkflowAction(() => submitAutomationDraftReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async completeAutomationDraftReviewGate() {
      const workflow = this.draftReviewWorkflow?.workflow;
      const requirementReviewId = this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId) return false;
      return this.runAutomationDraftWorkflowAction(() => completeAutomationDraftReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async editAutomationDraftReviewGate() {
      const workflow = this.draftReviewWorkflow?.workflow;
      const requirementReviewId = this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId) return false;
      return this.runAutomationDraftWorkflowAction(() => editAutomationDraftReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
        draft_decisions: this.currentAutomationDraftDecisionSnapshot(),
      }));
    },
    async approveAutomationDraftReviewGate(comment?: string) {
      const workflow = this.draftReviewWorkflow?.workflow;
      const requirementReviewId = this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId) return false;
      return this.runAutomationDraftWorkflowAction(() => approveAutomationDraftReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async rejectAutomationDraftReviewGate(comment?: string) {
      const workflow = this.draftReviewWorkflow?.workflow;
      const requirementReviewId = this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId) return false;
      return this.runAutomationDraftWorkflowAction(() => rejectAutomationDraftReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async continueAutomationDraftReviewGate() {
      const workflow = this.draftReviewWorkflow?.workflow;
      const requirementReviewId = this.plan?.requirement_review_id;
      const approvalDecisionId = workflow?.approval_decision_id;
      if (!workflow || !requirementReviewId || !approvalDecisionId) return false;
      return this.runAutomationDraftWorkflowAction(() => continueAutomationDraftReviewWorkflow(
        this.projectId,
        requirementReviewId,
        {
          expected_version: workflow.lock_version,
          approval_decision_id: approvalDecisionId,
        },
      ));
    },
    async approveAndContinueAutomationDraftReviewGate(comment?: string) {
      const workflow = this.draftReviewWorkflow?.workflow;
      const requirementReviewId = this.plan?.requirement_review_id;
      if (!workflow || !requirementReviewId) return false;
      return this.runAutomationDraftWorkflowAction(() => approveAndContinueAutomationDraftReviewWorkflow(this.projectId, requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
  },
});
