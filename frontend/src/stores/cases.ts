import { defineStore } from 'pinia';

import {
  approveAndContinueCaseReviewWorkflow,
  approveCaseReviewWorkflow,
  completeCaseReviewWorkflow,
  continueCaseReviewWorkflow,
  editCaseReviewWorkflow,
  getCaseGenerationTask,
  getCaseMetrics,
  getCaseReviewWorkflow,
  importTestCases,
  listCaseCandidates,
  listTestCases,
  rejectCaseReviewWorkflow,
  reviewCaseCandidate,
  startCaseGeneration,
  submitCaseReviewWorkflow,
  updateTestCaseStatus,
  type CaseGenerationStartRead,
  type CaseGenerationTaskRead,
  type CaseMetricsRead,
  type CaseReviewAction,
  type CaseReviewEditedCase,
  type CaseReviewRead,
  type CaseReviewWorkflowRead,
  type GeneratedCaseCandidateListItem,
  type TestCaseListItem,
  type TestCaseImportItem,
} from '../api/cases';
import { listReviewHistory, type ReviewHistoryItem } from '../api/reviewHistory';
import {
  getRequirementReview,
  listRequirementDocuments,
  listRequirements,
  type RequirementDocumentRead,
} from '../api/requirements';
import {
  DEFAULT_PROJECT_ID,
  getLatestRequirementDocumentContext,
  getLatestRequirementReviewContext,
  saveLatestApprovedTestCaseContext,
} from './workflowContext';

export const useCasesStore = defineStore('cases', {
  state: () => {
    const latestDocument = getLatestRequirementDocumentContext();
    const latestContext = getLatestRequirementReviewContext();
    const matchingDocument = latestDocument && (!latestContext || latestDocument.requirementId === latestContext.requirementId)
      ? latestDocument
      : null;
    return {
      projectId: latestContext?.projectId ?? matchingDocument?.projectId ?? DEFAULT_PROJECT_ID,
      requirementId: latestContext?.requirementId ?? matchingDocument?.requirementId ?? '',
      requirementReviewId: latestContext?.requirementReviewId ?? matchingDocument?.requirementReviewId ?? '',
      requirementDocumentArtifactId: matchingDocument?.requirementDocumentArtifactId ?? '',
      selectedRequirementDocumentNumber: matchingDocument?.documentNumber ?? '',
      requirementTitle: latestContext?.requirement?.title ?? '',
      requirementReviewConfirmed: Boolean(latestContext?.review),
      requirementRiskTitles: latestContext?.review?.risk_items.map((item) => item.title) ?? [],
      requirementClarificationQuestions: latestContext?.review?.clarification_questions ?? [],
      requirementDocuments: [] as RequirementDocumentRead[],
      generation: null as CaseGenerationStartRead | null,
      generationTask: null as CaseGenerationTaskRead | null,
      candidates: [] as GeneratedCaseCandidateListItem[],
      metrics: null as CaseMetricsRead | null,
      testCases: [] as TestCaseListItem[],
      totalTestCases: 0,
      selectedTestCaseId: '',
      totalCandidates: 0,
      selectedCandidateId: '',
      lastReview: null as CaseReviewRead | null,
      lastReviewCandidateId: '',
      caseReviewWorkflow: null as CaseReviewWorkflowRead | null,
      reviewHistory: [] as ReviewHistoryItem[],
      loadingGeneration: false,
      loadingReview: false,
      errorMessage: '',
      successMessage: '',
    };
  },
  getters: {
    selectedCandidate(state) {
      return state.candidates.find((candidate) => candidate.id === state.selectedCandidateId) ?? state.candidates[0] ?? null;
    },
    selectedTestCase(state) {
      return state.testCases.find((testCase) => testCase.id === state.selectedTestCaseId) ?? state.testCases[0] ?? null;
    },
  },
  actions: {
    loadLatestRequirementReviewContext() {
      const latestDocument = getLatestRequirementDocumentContext();
      const latestContext = getLatestRequirementReviewContext();
      const matchingDocument = latestDocument && (!latestContext || latestDocument.requirementId === latestContext.requirementId)
        ? latestDocument
        : null;
      if (matchingDocument) {
        this.projectId = matchingDocument.projectId;
        this.requirementId = matchingDocument.requirementId;
        this.requirementReviewId = matchingDocument.requirementReviewId;
        this.requirementDocumentArtifactId = matchingDocument.requirementDocumentArtifactId;
        this.selectedRequirementDocumentNumber = matchingDocument.documentNumber;
        this.requirementTitle = latestContext?.requirement?.title ?? '';
        this.requirementReviewConfirmed = true;
        return true;
      }
      if (!latestContext) {
        return false;
      }
      this.projectId = latestContext.projectId;
      this.requirementId = latestContext.requirementId;
      this.requirementReviewId = latestContext.requirementReviewId;
      this.requirementDocumentArtifactId = '';
      this.selectedRequirementDocumentNumber = '';
      this.requirementTitle = latestContext.requirement?.title ?? '';
      this.requirementReviewConfirmed = Boolean(latestContext.review);
      this.requirementRiskTitles = latestContext.review?.risk_items.map((item) => item.title) ?? [];
      this.requirementClarificationQuestions = latestContext.review?.clarification_questions ?? [];
      return true;
    },
    async loadGenerationSource() {
      if (this.loadLatestRequirementReviewContext() && this.requirementId && this.requirementReviewId) {
        try {
          const review = await getRequirementReview(this.requirementId);
          if (review.id === this.requirementReviewId) {
            return true;
          }
        } catch {
          // The browser can outlive runtime data; recover from current project records below.
        }
      }
      this.projectId = this.projectId || DEFAULT_PROJECT_ID;
      try {
        const requirements = await listRequirements(this.projectId);
        for (const requirement of [...requirements.items].reverse()) {
          try {
            const review = await getRequirementReview(requirement.id);
            this.projectId = requirement.project_id;
            this.requirementId = requirement.id;
            this.requirementReviewId = review.id;
            this.requirementDocumentArtifactId = '';
            this.selectedRequirementDocumentNumber = '';
            this.requirementTitle = requirement.title;
            this.requirementReviewConfirmed = true;
            this.requirementRiskTitles = review.risk_items.map((item) => item.title);
            this.requirementClarificationQuestions = review.clarification_questions;
            return true;
          } catch {
            // Continue to the next most recent requirement with a completed review.
          }
        }
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '无法加载已评审需求';
      }
      return false;
    },
    async loadCaseReviewWorkflow() {
      if (!this.projectId || !this.requirementReviewId) {
        return null;
      }
      try {
        this.caseReviewWorkflow = await getCaseReviewWorkflow(this.projectId, this.requirementReviewId);
        return this.caseReviewWorkflow;
      } catch {
        this.caseReviewWorkflow = null;
        return null;
      }
    },
    async loadRequirementDocuments() {
      this.loadingGeneration = true;
      this.errorMessage = '';
      try {
        const documents = await listRequirementDocuments(this.projectId);
        this.requirementDocuments = documents.items;
        this.reconcileRequirementDocumentSelection();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '需求文档加载失败';
      } finally {
        this.loadingGeneration = false;
      }
    },
    reconcileRequirementDocumentSelection() {
      if (!this.requirementDocumentArtifactId) {
        return;
      }
      const document = this.requirementDocuments.find(
        (item) => item.artifact_id === this.requirementDocumentArtifactId
          && item.requirement_id === this.requirementId
          && (!this.requirementReviewId || item.requirement_review_id === this.requirementReviewId),
      );
      if (document) {
        this.selectRequirementDocument(document.artifact_id);
        return;
      }
      this.clearRequirementDocumentSelection();
    },
    selectRequirementDocument(artifactId: string) {
      const document = this.requirementDocuments.find((item) => item.artifact_id === artifactId);
      if (!document) {
        return false;
      }
      this.projectId = document.project_id;
      this.requirementId = document.requirement_id;
      this.requirementReviewId = document.requirement_review_id;
      this.requirementDocumentArtifactId = document.artifact_id;
      this.selectedRequirementDocumentNumber = document.document_number;
      const latestContext = getLatestRequirementReviewContext();
      if (latestContext?.requirementReviewId === document.requirement_review_id) {
        this.requirementTitle = latestContext.requirement?.title ?? document.title;
        this.requirementReviewConfirmed = Boolean(latestContext.review);
        this.requirementRiskTitles = latestContext.review?.risk_items.map((item) => item.title) ?? [];
        this.requirementClarificationQuestions = latestContext.review?.clarification_questions ?? [];
      } else {
        this.requirementTitle = document.title;
        this.requirementReviewConfirmed = false;
        this.requirementRiskTitles = [];
        this.requirementClarificationQuestions = [];
      }
      return true;
    },
    clearRequirementDocumentSelection() {
      this.requirementDocumentArtifactId = '';
      this.selectedRequirementDocumentNumber = '';
      const latestContext = getLatestRequirementReviewContext();
      if (!latestContext) {
        this.requirementId = '';
        this.requirementReviewId = '';
        this.requirementTitle = '';
        this.requirementReviewConfirmed = false;
        this.requirementRiskTitles = [];
        this.requirementClarificationQuestions = [];
        return false;
      }
      this.projectId = latestContext.projectId;
      this.requirementId = latestContext.requirementId;
      this.requirementReviewId = latestContext.requirementReviewId;
      this.requirementTitle = latestContext.requirement?.title ?? '';
      this.requirementReviewConfirmed = Boolean(latestContext.review);
      return true;
    },
    async loadTestCases() {
      this.loadingGeneration = true;
      this.errorMessage = '';
      try {
        const library = await listTestCases(this.projectId);
        this.testCases = library.items;
        this.totalTestCases = library.total;
        this.selectedTestCaseId = this.testCases[0]?.id ?? '';
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '用例库加载失败';
      } finally {
        this.loadingGeneration = false;
      }
    },
    async importCases(items: TestCaseImportItem[]) {
      this.loadingGeneration = true;
      this.errorMessage = '';
      this.successMessage = '';
      try {
        const result = await importTestCases(this.projectId, items);
        this.successMessage = `已导入 ${result.imported_count} 条用例${result.skipped_count ? `，跳过 ${result.skipped_count} 条重复标题` : ''}`;
        await this.loadTestCases();
        return result;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '用例导入失败';
        return null;
      } finally {
        this.loadingGeneration = false;
      }
    },
    async setTestCaseStatus(caseId: string, status: 'active' | 'archived') {
      this.loadingGeneration = true;
      this.errorMessage = '';
      this.successMessage = '';
      try {
        await updateTestCaseStatus(this.projectId, caseId, status);
        this.successMessage = status === 'archived' ? '用例已归档' : '用例已恢复';
        await this.loadTestCases();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '用例状态更新失败';
      } finally {
        this.loadingGeneration = false;
      }
    },
    async generateCandidates(data: {
      requirementId: string;
      requirementReviewId: string;
      targetTestTypes: string[];
      contextArtifactIds?: string[];
      requirementDocumentArtifactId?: string;
      decisionTableAcknowledged?: boolean;
    }) {
      this.loadingGeneration = true;
      this.errorMessage = '';
      this.candidates = [];
      this.metrics = null;
      this.totalCandidates = 0;
      this.generationTask = null;
      this.lastReview = null;
      this.lastReviewCandidateId = '';
      this.reviewHistory = [];
      this.requirementId = data.requirementId;
      this.requirementReviewId = data.requirementReviewId;
      this.requirementDocumentArtifactId = data.requirementDocumentArtifactId ?? this.requirementDocumentArtifactId;
      if (!data.requirementId || !data.requirementReviewId) {
        this.errorMessage = '请先选择已评审需求或正式需求文档';
        this.loadingGeneration = false;
        return;
      }
      try {
        this.generation = await startCaseGeneration({
          project_id: this.projectId,
          requirement_id: data.requirementId,
          requirement_review_id: data.requirementReviewId,
          requirement_document_artifact_id: data.requirementDocumentArtifactId || null,
          target_test_types: data.targetTestTypes,
          prompt_version: 'case_generation:v2',
          skill_version: 'test-case-generation-skill:v2',
          use_knowledge: true,
          context_artifact_ids: data.contextArtifactIds ?? [],
          decision_table_acknowledged: Boolean(data.decisionTableAcknowledged),
        });
        this.generationTask = await this.waitForGenerationTask(this.generation.case_generation_task_id);
        if (this.generationTask.status !== 'succeeded') {
          const fallbackMessage = `用例生成任务未成功完成：${this.generationTask.status}`;
          const errorMessage = this.generationTask.error_message ?? fallbackMessage;
          this.errorMessage = this.generationTask.error_code
            ? `${this.generationTask.error_code}: ${errorMessage}`
            : errorMessage;
          return;
        }
        const candidates = await listCaseCandidates(this.generation.case_generation_task_id);
        this.candidates = candidates.items;
        this.totalCandidates = candidates.total;
        this.selectedCandidateId = this.candidates[0]?.id ?? '';
        this.lastReview = null;
        this.lastReviewCandidateId = '';
        this.reviewHistory = [];
        if (this.selectedCandidateId) {
          await this.loadSelectedCandidateReviewHistory(this.selectedCandidateId);
        }
        this.metrics = await getCaseMetrics(this.generation.case_generation_task_id);
        await this.loadCaseReviewWorkflow();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '候选用例生成失败';
      } finally {
        this.loadingGeneration = false;
      }
    },
    async waitForGenerationTask(generationTaskId: string) {
      const finalStatuses = new Set(['succeeded', 'failed', 'cancelled']);
      let latest = await getCaseGenerationTask(generationTaskId);
      this.generationTask = latest;
      for (let attempt = 0; attempt < 60 && !finalStatuses.has(latest.status); attempt += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 1000));
        latest = await getCaseGenerationTask(generationTaskId);
        this.generationTask = latest;
      }
      return latest;
    },
    async selectCandidate(candidateId: string) {
      if (this.selectedCandidateId === candidateId) {
        return;
      }
      this.selectedCandidateId = candidateId;
      this.lastReview = null;
      this.lastReviewCandidateId = '';
      this.reviewHistory = [];
      await this.loadSelectedCandidateReviewHistory(candidateId);
    },
    async reviewSelectedCandidate(
      action: CaseReviewAction,
      reviewComment: string,
      editedCase?: CaseReviewEditedCase,
    ) {
      const candidate = this.selectedCandidate;
      if (!candidate) {
        this.errorMessage = '请先选择候选用例';
        return;
      }
      this.loadingReview = true;
      this.errorMessage = '';
      try {
        this.lastReview = await reviewCaseCandidate(candidate.id, {
          action,
          review_comment: reviewComment,
          edited_case:
            action === 'approve_after_edit' ? editedCase ?? caseReviewEditedCaseFromCandidate(candidate) : undefined,
        });
        this.lastReviewCandidateId = candidate.id;
        this.candidates = this.candidates.map((item) =>
          item.id === candidate.id ? { ...item, status: this.lastReview?.status ?? item.status } : item,
        );
        this.rememberLatestApprovedTestCase(candidate.id, this.lastReview);
        await this.loadSelectedCandidateReviewHistory(candidate.id);
        if (this.generation) {
          this.metrics = await getCaseMetrics(this.generation.case_generation_task_id);
        }
        await this.loadCaseReviewWorkflow();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '候选用例评审失败';
      } finally {
        this.loadingReview = false;
      }
    },
    rememberLatestApprovedTestCase(candidateId: string, review: CaseReviewRead | null) {
      if (!review?.test_case_id || !['approved', 'approved_after_edit'].includes(review.status)) {
        return;
      }
      saveLatestApprovedTestCaseContext({
        projectId: this.projectId,
        testCaseId: review.test_case_id,
        sourceCandidateId: candidateId,
        reviewStatus: review.status,
      });
      this.selectedTestCaseId = review.test_case_id;
    },
    async loadSelectedCandidateReviewHistory(candidateId?: string) {
      const targetCandidateId = candidateId ?? this.selectedCandidate?.id ?? '';
      if (!targetCandidateId) {
        this.reviewHistory = [];
        return;
      }
      const history = await listReviewHistory({
        projectId: this.projectId,
        entityType: 'GeneratedCaseCandidate',
        entityId: targetCandidateId,
        limit: 20,
      });
      if (this.selectedCandidateId === targetCandidateId) {
        this.reviewHistory = history.items;
      }
    },
    currentCandidateDecisionSnapshot() {
      return this.candidates.map((candidate) => {
        const matchingReview = this.lastReviewCandidateId === candidate.id ? this.lastReview : null;
        const matchingTestCase = this.testCases.find((testCase) => testCase.source_candidate_id === candidate.id);
        return {
          candidate_id: candidate.id,
          status: candidate.status,
          review_comment: matchingReview?.candidate_id === candidate.id ? null : undefined,
          test_case_id: matchingReview?.candidate_id === candidate.id
            ? matchingReview.test_case_id
            : matchingTestCase?.id ?? null,
        };
      });
    },
    async runCaseWorkflowAction(action: () => Promise<CaseReviewWorkflowRead>) {
      this.loadingReview = true;
      this.errorMessage = '';
      try {
        this.caseReviewWorkflow = await action();
        return true;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'CaseReview workflow action failed';
        await this.loadCaseReviewWorkflow();
        return false;
      } finally {
        this.loadingReview = false;
      }
    },
    async submitCaseReviewGate() {
      const workflow = this.caseReviewWorkflow?.workflow;
      if (!workflow) return false;
      return this.runCaseWorkflowAction(() => submitCaseReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async completeCaseReviewGate() {
      const workflow = this.caseReviewWorkflow?.workflow;
      if (!workflow) return false;
      return this.runCaseWorkflowAction(() => completeCaseReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async editCaseReviewGate() {
      const workflow = this.caseReviewWorkflow?.workflow;
      if (!workflow) return false;
      return this.runCaseWorkflowAction(() => editCaseReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        candidate_decisions: this.currentCandidateDecisionSnapshot(),
      }));
    },
    async approveCaseReviewGate(comment?: string) {
      const workflow = this.caseReviewWorkflow?.workflow;
      if (!workflow) return false;
      return this.runCaseWorkflowAction(() => approveCaseReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async rejectCaseReviewGate(comment?: string) {
      const workflow = this.caseReviewWorkflow?.workflow;
      if (!workflow) return false;
      return this.runCaseWorkflowAction(() => rejectCaseReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async continueCaseReviewGate() {
      const workflow = this.caseReviewWorkflow?.workflow;
      const approvalDecisionId = workflow?.approval_decision_id;
      if (!workflow || !approvalDecisionId) return false;
      return this.runCaseWorkflowAction(() => continueCaseReviewWorkflow(
        this.projectId,
        this.requirementReviewId,
        {
          expected_version: workflow.lock_version,
          approval_decision_id: approvalDecisionId,
        },
      ));
    },
    async approveAndContinueCaseReviewGate(comment?: string) {
      const workflow = this.caseReviewWorkflow?.workflow;
      if (!workflow) return false;
      return this.runCaseWorkflowAction(() => approveAndContinueCaseReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
  },
});

function caseReviewEditedCaseFromCandidate(candidate: GeneratedCaseCandidateListItem): CaseReviewEditedCase {
  return {
    title: candidate.title,
    priority: candidate.priority,
    test_type: candidate.test_type,
    precondition: candidate.precondition,
    steps: candidate.steps,
    expected_results: candidate.expected_results,
    input_data: candidate.input_data,
    tags: ['ai-generated', 'reviewed'],
  };
}
