import { defineStore } from 'pinia';

import {
  approveAutomationDraft,
  createAutomationDraft,
  editAutomationDraft,
  getAutomationDraft,
  type AutomationDraftCreateRead,
  type AutomationDraftRead,
  type AutomationDraftReviewRead,
} from '../api/automation';
import { listReviewHistory, type ReviewHistoryItem } from '../api/reviewHistory';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';
const DEFAULT_TEST_CASE_ID = '00000000-0000-0000-0000-000000000901';

export const useAutomationStore = defineStore('automation', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    testCaseId: DEFAULT_TEST_CASE_ID,
    createdDraft: null as AutomationDraftCreateRead | null,
    draft: null as AutomationDraftRead | null,
    lastReview: null as AutomationDraftReviewRead | null,
    reviewHistory: [] as ReviewHistoryItem[],
    loading: false,
    errorMessage: '',
  }),
  actions: {
    async createDraft(data: { testCaseId: string; targetFramework: string }) {
      this.loading = true;
      this.errorMessage = '';
      this.testCaseId = data.testCaseId;
      try {
        this.createdDraft = await createAutomationDraft({
          project_id: this.projectId,
          test_case_id: data.testCaseId,
          requirement_id: null,
          target_framework: data.targetFramework,
          prompt_version: 'automation_draft_generation:v1',
          skill_version: 'automation-draft-skill:v1',
          model_provider: 'mock',
          model_name: 'mock-automation-draft',
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
  },
});
