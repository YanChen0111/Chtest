import { defineStore } from 'pinia';

import {
  getCaseMetrics,
  listCaseCandidates,
  listTestCases,
  reviewCaseCandidate,
  startCaseGeneration,
  type CaseGenerationStartRead,
  type CaseMetricsRead,
  type CaseReviewAction,
  type CaseReviewRead,
  type GeneratedCaseCandidateListItem,
  type TestCaseListItem,
} from '../api/cases';
import { listReviewHistory, type ReviewHistoryItem } from '../api/reviewHistory';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';
const DEFAULT_REQUIREMENT_ID = '00000000-0000-0000-0000-000000000401';
const DEFAULT_REVIEW_ID = '00000000-0000-0000-0000-000000000601';

export const useCasesStore = defineStore('cases', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    requirementId: DEFAULT_REQUIREMENT_ID,
    requirementReviewId: DEFAULT_REVIEW_ID,
    generation: null as CaseGenerationStartRead | null,
    candidates: [] as GeneratedCaseCandidateListItem[],
    metrics: null as CaseMetricsRead | null,
    testCases: [] as TestCaseListItem[],
    totalTestCases: 0,
    selectedTestCaseId: '',
    totalCandidates: 0,
    selectedCandidateId: '',
    lastReview: null as CaseReviewRead | null,
    reviewHistory: [] as ReviewHistoryItem[],
    loadingGeneration: false,
    loadingReview: false,
    errorMessage: '',
  }),
  getters: {
    selectedCandidate(state) {
      return state.candidates.find((candidate) => candidate.id === state.selectedCandidateId) ?? state.candidates[0] ?? null;
    },
    selectedTestCase(state) {
      return state.testCases.find((testCase) => testCase.id === state.selectedTestCaseId) ?? state.testCases[0] ?? null;
    },
  },
  actions: {
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
    }) {
      this.loadingGeneration = true;
      this.errorMessage = '';
      this.candidates = [];
      this.metrics = null;
      this.totalCandidates = 0;
      this.lastReview = null;
      this.reviewHistory = [];
      this.requirementId = data.requirementId;
      this.requirementReviewId = data.requirementReviewId;
      try {
        this.generation = await startCaseGeneration({
          project_id: this.projectId,
          requirement_id: data.requirementId,
          requirement_review_id: data.requirementReviewId,
          target_test_types: data.targetTestTypes,
          prompt_version: 'case_generation:v1',
          skill_version: 'test-case-generation-skill:v1',
          model_provider: 'mock',
          model_name: 'mock-case-generator',
          use_knowledge: false,
          context_artifact_ids: data.contextArtifactIds,
        });
        const candidates = await listCaseCandidates(this.generation.case_generation_task_id);
        this.candidates = candidates.items;
        this.totalCandidates = candidates.total;
        this.selectedCandidateId = this.candidates[0]?.id ?? '';
        this.metrics = await getCaseMetrics(this.generation.case_generation_task_id);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '候选用例生成失败';
      } finally {
        this.loadingGeneration = false;
      }
    },
    async reviewSelectedCandidate(action: CaseReviewAction, reviewComment: string) {
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
            action === 'approve_after_edit'
              ? {
                  title: candidate.title,
                  priority: candidate.priority,
                  test_type: candidate.test_type,
                  precondition: candidate.precondition,
                  steps: ['补充测试数据准备', ...candidate.steps],
                  expected_results: candidate.expected_results,
                  input_data: { review_edit: 'test_data_preparation' },
                  tags: ['ai-generated', 'reviewed'],
                }
              : undefined,
        });
        this.candidates = this.candidates.map((item) =>
          item.id === candidate.id ? { ...item, status: this.lastReview?.status ?? item.status } : item,
        );
        await this.loadSelectedCandidateReviewHistory();
        if (this.generation) {
          this.metrics = await getCaseMetrics(this.generation.case_generation_task_id);
        }
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '候选用例评审失败';
      } finally {
        this.loadingReview = false;
      }
    },
    async loadSelectedCandidateReviewHistory() {
      const candidate = this.selectedCandidate;
      if (!candidate) {
        this.reviewHistory = [];
        return;
      }
      const history = await listReviewHistory({
        projectId: this.projectId,
        entityType: 'GeneratedCaseCandidate',
        entityId: candidate.id,
        limit: 20,
      });
      this.reviewHistory = history.items;
    },
  },
});
