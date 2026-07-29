import { defineStore } from 'pinia';

import { ApiError } from '../api/client';

import {
  createRequirement,
  createRequirementDocument,
  approveRequirementReview,
  approveRiskReview,
  approveTestPlanReview,
  completeRequirementReview,
  completeRiskReview,
  completeTestPlanReview,
  continueRequirementReview,
  continueRiskReview,
  continueTestPlanReview,
  editRequirementReview,
  editRiskReview,
  editTestPlanReview,
  getRequirementReview,
  getRiskReview,
  getTestPlanReview,
  listRequirementDocuments,
  rejectRequirementReview,
  rejectRiskReview,
  rejectTestPlanReview,
  startRequirementReview,
  submitRiskReview,
  submitTestPlanReview,
  type ClarificationAnswer,
  type RequirementDocumentRead,
  type RequirementRead,
  type RequirementReviewRead,
  type RequirementReviewStartRead,
  type RequirementReviewIssue,
  type RequirementRiskItem,
  type TestPlanItem,
} from '../api/requirements';
import {
  retrieveTestKnowledgeCards,
  type TestKnowledgeCardRetrievalRead,
} from '../api/extension';
import {
  DEFAULT_PROJECT_ID,
  getLatestRequirementReviewContext,
  saveLatestRequirementDocumentContext,
  saveLatestRequirementReviewContext,
} from './workflowContext';

export const useRequirementsStore = defineStore('requirements', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    requirement: null as RequirementRead | null,
    reviewStart: null as RequirementReviewStartRead | null,
    review: null as RequirementReviewRead | null,
    documents: [] as RequirementDocumentRead[],
    createdDocument: null as RequirementDocumentRead | null,
    knowledgePreview: null as TestKnowledgeCardRetrievalRead | null,
    knowledgePreviewQuery: '',
    loading: false,
    loadingKnowledge: false,
    loadingDocument: false,
    errorMessage: '',
  }),
  getters: {
    previewContextArtifactIds(state): string[] {
      return [...new Set((state.knowledgePreview?.items ?? []).map((item) => item.source_artifact_id))];
    },
  },
  actions: {
    async retrieveKnowledgePreview(queryText: string) {
      const normalizedQuery = queryText.trim();
      if (!normalizedQuery) {
        this.errorMessage = '请先输入需求内容';
        return false;
      }
      this.loadingKnowledge = true;
      this.errorMessage = '';
      try {
        this.knowledgePreview = await retrieveTestKnowledgeCards({
          project_id: this.projectId,
          query_text: normalizedQuery,
          limit: 5,
          approved_only: true,
        });
        this.knowledgePreviewQuery = normalizedQuery;
        return true;
      } catch (error) {
        this.knowledgePreview = null;
        this.knowledgePreviewQuery = '';
        this.errorMessage = error instanceof Error ? error.message : '项目知识检索失败';
        return false;
      } finally {
        this.loadingKnowledge = false;
      }
    },
    clearKnowledgePreview() {
      this.knowledgePreview = null;
      this.knowledgePreviewQuery = '';
    },
    async reviewRequirement(data: {
      title: string;
      content: string;
      sourceRef?: string;
      contextArtifactIds?: string[];
      supplementText?: string;
      clarificationAnswers?: ClarificationAnswer[];
    }) {
      this.loading = true;
      this.errorMessage = '';
      this.reviewStart = null;
      this.review = null;
      this.createdDocument = null;
      try {
        const requirement =
          this.requirement?.title === data.title && this.requirement?.content === data.content
            ? this.requirement
            : await createRequirement({
                project_id: this.projectId,
                module_id: null,
                title: data.title,
                content: data.content,
                source_type: 'manual',
                source_ref: data.sourceRef || 'manual',
              });
        this.requirement = requirement;
        this.reviewStart = await startRequirementReview(requirement.id, {
          prompt_version: 'requirement_review:v1',
          skill_version: 'requirement-review-skill:v1',
          use_knowledge: true,
          context_artifact_ids: data.contextArtifactIds ?? [],
          supplement_text: data.supplementText || null,
          clarification_answers: data.clarificationAnswers ?? [],
        });
        this.review = await getRequirementReview(requirement.id);
        saveLatestRequirementReviewContext({
          projectId: this.projectId,
          requirementId: requirement.id,
          requirementReviewId: this.review.id,
          requirement,
          review: this.review,
        });
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '需求评审失败';
      } finally {
        this.loading = false;
      }
    },
    restoreLatestRequirementReview() {
      const context = getLatestRequirementReviewContext();
      if (!context?.requirement || !context.review) {
        return false;
      }
      if (
        context.requirement.id !== context.requirementId ||
        context.review.id !== context.requirementReviewId ||
        context.review.requirement_id !== context.requirementId
      ) {
        return false;
      }
      this.projectId = context.projectId;
      this.requirement = context.requirement;
      this.review = context.review;
      return true;
    },
    async refreshCurrentReview() {
      if (!this.requirement) return false;
      try {
        this.review = this.review?.workflow?.stage === 'test_plan_review'
          ? await getTestPlanReview(this.projectId, this.review.id)
          : this.review?.workflow?.stage === 'risk_review'
            ? await getRiskReview(this.projectId, this.review.id)
            : await getRequirementReview(this.requirement.id);
        saveLatestRequirementReviewContext({
          projectId: this.projectId,
          requirementId: this.requirement.id,
          requirementReviewId: this.review.id,
          requirement: this.requirement,
          review: this.review,
        });
        return true;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '无法刷新服务端评审状态';
        return false;
      }
    },
    async loadRequirementDocuments() {
      this.errorMessage = '';
      try {
        const documents = await listRequirementDocuments(this.projectId);
        this.documents = documents.items;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '需求文档加载失败';
      }
    },
    async completeReview() {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => completeRequirementReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
      }));
    },
    async editReview(payload: { issues: RequirementReviewIssue[]; clarification_questions: string[]; test_design_notes: unknown[]; risk_items: RequirementRiskItem[] }) {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => editRequirementReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
        ...payload,
      }));
    },
    async approveReview(comment?: string) {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => approveRequirementReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
        comment: comment || null,
      }));
    },
    async rejectReview(comment?: string) {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => rejectRequirementReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
        comment: comment || null,
      }));
    },
    async continueReview() {
      const workflow = this.review?.workflow;
      if (!this.review || !workflow?.approval_decision_id) return false;
      return this.runWorkflowAction(() => continueRequirementReview(this.projectId, this.review!.id, workflow.lock_version, workflow.approval_decision_id!));
    },
    async submitRiskReview() {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => submitRiskReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
      }));
    },
    async completeRiskReview() {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => completeRiskReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
      }));
    },
    async editRiskReview(riskItems: RequirementRiskItem[], comment?: string) {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => editRiskReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
        comment: comment || null,
        risk_items: riskItems,
      }));
    },
    async approveRiskReview(comment?: string) {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => approveRiskReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
        comment: comment || null,
      }));
    },
    async rejectRiskReview(comment?: string) {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => rejectRiskReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
        comment: comment || null,
      }));
    },
    async continueRiskReview() {
      const workflow = this.review?.workflow;
      if (!this.review || !workflow?.approval_decision_id) return false;
      return this.runWorkflowAction(() => continueRiskReview(
        this.projectId, this.review!.id, workflow.lock_version, workflow.approval_decision_id!,
      ));
    },
    async submitTestPlanReview() {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => submitTestPlanReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
      }));
    },
    async completeTestPlanReview() {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => completeTestPlanReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
      }));
    },
    async editTestPlanReview(testStrategy: string, planItems: TestPlanItem[], comment?: string) {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => editTestPlanReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
        comment: comment || null,
        test_strategy: testStrategy,
        plan_items: planItems,
      }));
    },
    async approveTestPlanReview(comment?: string) {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => approveTestPlanReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
        comment: comment || null,
      }));
    },
    async rejectTestPlanReview(comment?: string) {
      if (!this.review?.workflow) return false;
      return this.runWorkflowAction(() => rejectTestPlanReview(this.projectId, this.review!.id, {
        expected_version: this.review!.workflow!.lock_version,
        comment: comment || null,
      }));
    },
    async continueTestPlanReview() {
      const workflow = this.review?.workflow;
      if (!this.review || !workflow?.approval_decision_id) return false;
      return this.runWorkflowAction(() => continueTestPlanReview(
        this.projectId, this.review!.id, workflow.lock_version, workflow.approval_decision_id!,
      ));
    },
    async runWorkflowAction(action: () => Promise<RequirementReviewRead>) {
      this.loading = true;
      this.errorMessage = '';
      try {
        this.review = await action();
        if (this.requirement && this.review) {
          saveLatestRequirementReviewContext({ projectId: this.projectId, requirementId: this.requirement.id, requirementReviewId: this.review.id, requirement: this.requirement, review: this.review });
        }
        return true;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'Workflow action failed';
        if (error instanceof ApiError && error.status === 409 && this.requirement) {
          await this.refreshCurrentReview();
          this.errorMessage = '评审输入或审批状态已变化，已加载服务端最新版本。请重新检查后操作。';
        }
        return false;
      } finally {
        this.loading = false;
      }
    },
    async generateRequirementDocument() {
      if (!this.requirement || !this.review) {
        this.errorMessage = '请先完成需求评审';
        return;
      }
      const workflow = this.review.workflow;
      if (!workflow || (workflow.stage === 'requirement_review' && workflow.state !== 'approved')) {
        this.errorMessage = '必须先批准当前需求评审，才能生成正式需求文档。';
        return;
      }
      this.loadingDocument = true;
      this.errorMessage = '';
      try {
        this.createdDocument = await createRequirementDocument(this.requirement.id, {
          requirement_review_id: this.review.id,
          version: 'v1',
          status: this.review.clarification_questions.length > 0 ? 'draft' : 'confirmed',
        });
        saveLatestRequirementDocumentContext({
          projectId: this.projectId,
          requirementId: this.createdDocument.requirement_id,
          requirementReviewId: this.createdDocument.requirement_review_id,
          requirementDocumentArtifactId: this.createdDocument.artifact_id,
          documentNumber: this.createdDocument.document_number,
          downloadUrl: this.createdDocument.download_url,
        });
        await this.loadRequirementDocuments();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '需求文档生成失败';
      } finally {
        this.loadingDocument = false;
      }
    },
  },
});
