import { defineStore } from 'pinia';

import {
  approveAndContinueExecutionResultReviewWorkflow,
  approveExecutionResultReviewWorkflow,
  completeExecutionResultReviewWorkflow,
  continueExecutionResultReviewWorkflow,
  editExecutionResultReviewWorkflow,
  getExecutionResultReviewWorkflow,
  rejectExecutionResultReviewWorkflow,
  submitExecutionResultReviewWorkflow,
  type ExecutionResultReviewWorkflowRead,
} from '../api/execution';

import {
  createFailureAnalysis,
  createReport,
  getFailureAnalysis,
  getReport,
  type FailureAnalysisRead,
  type ReportRead,
} from '../api/reporting';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';
const DEFAULT_TEST_RUN_ID = '00000000-0000-0000-0000-000000001301';

export const useReportingStore = defineStore('reporting', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    testRunId: DEFAULT_TEST_RUN_ID,
    requirementReviewId: '',
    executionResultReviewWorkflow: null as ExecutionResultReviewWorkflowRead | null,
    failureAnalysis: null as FailureAnalysisRead | null,
    report: null as ReportRead | null,
    loadingAnalysis: false,
    loadingReport: false,
    errorMessage: '',
  }),
  actions: {
    async startFailureAnalysis() {
      if (this.requirementReviewId && !this.executionResultReviewWorkflow?.workflow.approval_decision_id) {
        this.errorMessage = 'ExecutionResultReview gate must be approved before failure analysis.';
        return;
      }
      this.loadingAnalysis = true;
      this.errorMessage = '';
      try {
        await createFailureAnalysis(this.testRunId, {
          model_provider: 'mock',
          model_name: 'mock-failure-analysis',
          execution_result_review_decision_id:
            this.executionResultReviewWorkflow?.workflow.approval_decision_id ?? undefined,
        });
        this.failureAnalysis = await getFailureAnalysis(this.testRunId);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '失败分析生成失败';
      } finally {
        this.loadingAnalysis = false;
      }
    },
    async startReport() {
      if (this.requirementReviewId && !this.executionResultReviewWorkflow?.workflow.approval_decision_id) {
        this.errorMessage = 'ExecutionResultReview gate must be approved before report generation.';
        return;
      }
      this.loadingReport = true;
      this.errorMessage = '';
      try {
        const created = await createReport({
          project_id: this.projectId,
          report_type: 'automation_execution',
          related_entity_type: 'TestRun',
          related_entity_id: this.testRunId,
          execution_result_review_decision_id:
            this.executionResultReviewWorkflow?.workflow.approval_decision_id ?? undefined,
        });
        this.report = await getReport(created.report_id);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '报告生成失败';
      } finally {
        this.loadingReport = false;
      }
    },
    async loadExecutionResultReviewWorkflow() {
      if (!this.projectId || !this.requirementReviewId) {
        this.executionResultReviewWorkflow = null;
        return null;
      }
      try {
        this.executionResultReviewWorkflow = await getExecutionResultReviewWorkflow(this.projectId, this.requirementReviewId);
        if (this.executionResultReviewWorkflow.generated_test_run_ids.length > 0) {
          this.testRunId = this.executionResultReviewWorkflow.generated_test_run_ids[0];
        }
        return this.executionResultReviewWorkflow;
      } catch {
        this.executionResultReviewWorkflow = null;
        return null;
      }
    },
    currentExecutionResultDecisionSnapshot() {
      if (!this.testRunId) {
        return [];
      }
      return [
        {
          test_run_id: this.testRunId,
          artifact_ids: this.executionResultReviewWorkflow?.execution_artifact_ids ?? [],
          conclusion: 'Frontend execution result evidence reviewed.',
        },
      ];
    },
    async runExecutionResultReviewAction(action: () => Promise<ExecutionResultReviewWorkflowRead>) {
      this.loadingReport = true;
      this.errorMessage = '';
      try {
        this.executionResultReviewWorkflow = await action();
        return true;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'ExecutionResultReview workflow action failed';
        await this.loadExecutionResultReviewWorkflow();
        return false;
      } finally {
        this.loadingReport = false;
      }
    },
    async submitExecutionResultReviewGate() {
      const workflow = this.executionResultReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionResultReviewAction(() => submitExecutionResultReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async completeExecutionResultReviewGate() {
      const workflow = this.executionResultReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionResultReviewAction(() => completeExecutionResultReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async editExecutionResultReviewGate() {
      const workflow = this.executionResultReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionResultReviewAction(() => editExecutionResultReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        result_decisions: this.currentExecutionResultDecisionSnapshot(),
      }));
    },
    async approveExecutionResultReviewGate(comment?: string) {
      const workflow = this.executionResultReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionResultReviewAction(() => approveExecutionResultReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async rejectExecutionResultReviewGate(comment?: string) {
      const workflow = this.executionResultReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionResultReviewAction(() => rejectExecutionResultReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async continueExecutionResultReviewGate() {
      const workflow = this.executionResultReviewWorkflow?.workflow;
      const approvalDecisionId = workflow?.approval_decision_id;
      if (!workflow || !this.requirementReviewId || !approvalDecisionId) return false;
      return this.runExecutionResultReviewAction(() => continueExecutionResultReviewWorkflow(
        this.projectId,
        this.requirementReviewId,
        {
          expected_version: workflow.lock_version,
          approval_decision_id: approvalDecisionId,
        },
      ));
    },
    async approveAndContinueExecutionResultReviewGate(comment?: string) {
      const workflow = this.executionResultReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionResultReviewAction(() => approveAndContinueExecutionResultReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
  },
});
