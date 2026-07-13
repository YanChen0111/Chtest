import { defineStore } from 'pinia';

import {
  getCaseGenerationTask,
  getCaseMetrics,
  listCaseCandidates,
  listTestCases,
  reviewCaseCandidate,
  startCaseGeneration,
  type CaseGenerationStartRead,
  type CaseGenerationTaskRead,
  type CaseMetricsRead,
  type CaseReviewAction,
  type CaseReviewEditedCase,
  type CaseReviewRead,
  type GeneratedCaseCandidateListItem,
  type TestCaseListItem,
} from '../api/cases';
import { listReviewHistory, type ReviewHistoryItem } from '../api/reviewHistory';
import { listRequirementDocuments, type RequirementDocumentRead } from '../api/requirements';
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
    return {
      projectId: latestDocument?.projectId ?? latestContext?.projectId ?? DEFAULT_PROJECT_ID,
      requirementId: latestDocument?.requirementId ?? latestContext?.requirementId ?? '',
      requirementReviewId: latestDocument?.requirementReviewId ?? latestContext?.requirementReviewId ?? '',
      requirementDocumentArtifactId: latestDocument?.requirementDocumentArtifactId ?? '',
      selectedRequirementDocumentNumber: latestDocument?.documentNumber ?? '',
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
      reviewHistory: [] as ReviewHistoryItem[],
      loadingGeneration: false,
      loadingReview: false,
      errorMessage: '',
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
      if (latestDocument) {
        this.projectId = latestDocument.projectId;
        this.requirementId = latestDocument.requirementId;
        this.requirementReviewId = latestDocument.requirementReviewId;
        this.requirementDocumentArtifactId = latestDocument.requirementDocumentArtifactId;
        this.selectedRequirementDocumentNumber = latestDocument.documentNumber;
        return true;
      }
      const latestContext = getLatestRequirementReviewContext();
      if (!latestContext) {
        return false;
      }
      this.projectId = latestContext.projectId;
      this.requirementId = latestContext.requirementId;
      this.requirementReviewId = latestContext.requirementReviewId;
      this.requirementDocumentArtifactId = '';
      this.selectedRequirementDocumentNumber = '';
      return true;
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
        (item) => item.artifact_id === this.requirementDocumentArtifactId,
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
      return true;
    },
    clearRequirementDocumentSelection() {
      this.requirementDocumentArtifactId = '';
      this.selectedRequirementDocumentNumber = '';
      const latestContext = getLatestRequirementReviewContext();
      if (!latestContext) {
        this.requirementId = '';
        this.requirementReviewId = '';
        return false;
      }
      this.projectId = latestContext.projectId;
      this.requirementId = latestContext.requirementId;
      this.requirementReviewId = latestContext.requirementReviewId;
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
    async generateCandidates(data: {
      requirementId: string;
      requirementReviewId: string;
      targetTestTypes: string[];
      contextArtifactIds: string[];
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
          prompt_version: 'case_generation:v1',
          skill_version: 'test-case-generation-skill:v1',
          use_knowledge: false,
          context_artifact_ids: data.contextArtifactIds,
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
