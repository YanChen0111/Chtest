import { defineStore } from 'pinia';

import {
  approveAutomationPlan,
  approveAutomationDraft,
  createAutomationPlan,
  createAutomationDraft,
  editAutomationDraft,
  generateAutomationDraftFromPlan,
  getAutomationDraft,
  type AutomationDraftCreateRead,
  type AutomationDraftRead,
  type AutomationDraftReviewRead,
  type AutomationPlanRead,
  type AutomationPlanReviewRead,
} from '../api/automation';
import { listReviewHistory, type ReviewHistoryItem } from '../api/reviewHistory';
import { getLatestApprovedTestCaseContext } from './workflowContext';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';
const DEFAULT_TEST_CASE_ID = '00000000-0000-0000-0000-000000000901';

export const useAutomationStore = defineStore('automation', {
  state: () => {
    const latestCase = getLatestApprovedTestCaseContext();
    return {
      projectId: latestCase?.projectId ?? DEFAULT_PROJECT_ID,
      testCaseId: latestCase?.testCaseId ?? DEFAULT_TEST_CASE_ID,
      plan: null as AutomationPlanRead | null,
      lastPlanReview: null as AutomationPlanReviewRead | null,
      planReviewHistory: [] as ReviewHistoryItem[],
      createdDraft: null as AutomationDraftCreateRead | null,
      draft: null as AutomationDraftRead | null,
      lastReview: null as AutomationDraftReviewRead | null,
      reviewHistory: [] as ReviewHistoryItem[],
      loading: false,
      errorMessage: '',
    };
  },
  actions: {
    loadLatestApprovedTestCaseContext() {
      const latestCase = getLatestApprovedTestCaseContext();
      if (!latestCase) {
        return false;
      }
      this.projectId = latestCase.projectId;
      this.testCaseId = latestCase.testCaseId;
      return true;
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
        await this.loadCurrentDraftReviewHistory();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '自动化草稿审批失败';
      } finally {
        this.loading = false;
      }
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
  },
});
