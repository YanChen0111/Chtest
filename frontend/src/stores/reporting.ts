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
  approveAndContinueReportReviewWorkflow,
  approveReportReviewWorkflow,
  completeReportReviewWorkflow,
  createFailureAnalysis,
  createReport,
  continueReportReviewWorkflow,
  editReportReviewWorkflow,
  getFailureAnalysis,
  getReport,
  getReportReviewWorkflow,
  rejectReportReviewWorkflow,
  submitReportReviewWorkflow,
  type FailureAnalysisRead,
  type ReportRead,
  type ReportReviewWorkflowRead,
} from '../api/reporting';
import { getRequirement, getRequirementReview } from '../api/requirements';
import { DEFAULT_PROJECT_ID } from './workflowContext';

const DEFAULT_TEST_RUN_ID = '00000000-0000-0000-0000-000000001301';

export const useReportingStore = defineStore('reporting', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    testRunId: DEFAULT_TEST_RUN_ID,
    requirementReviewId: '',
    executionResultReviewWorkflow: null as ExecutionResultReviewWorkflowRead | null,
    reportReviewWorkflow: null as ReportReviewWorkflowRead | null,
    failureAnalysis: null as FailureAnalysisRead | null,
    report: null as ReportRead | null,
    requestedRequirementId: null as string | null,
    requestedReviewId: null as string | null,
    requestedWorkflowRunId: null as string | null,
    requestedWorkflowStage: null as string | null,
    exactRestoreFailed: false,
    loadingAnalysis: false,
    loadingReport: false,
    errorMessage: '',
  }),
  actions: {
    clearExplicitRestoreRequest() {
      this.requestedRequirementId = null;
      this.requestedReviewId = null;
      this.requestedWorkflowRunId = null;
      this.requestedWorkflowStage = null;
      this.exactRestoreFailed = false;
      this.errorMessage = '';
    },
    clearReportingSelection() {
      this.testRunId = '';
      this.requirementReviewId = '';
      this.executionResultReviewWorkflow = null;
      this.reportReviewWorkflow = null;
      this.failureAnalysis = null;
      this.report = null;
    },
    async loadExactExecutionResultReview(
      projectId: string,
      requirementId?: string,
      reviewId?: string,
      workflowRunId?: string,
      workflowStage?: string,
    ) {
      this.loadingReport = true;
      this.errorMessage = '';
      this.projectId = projectId;
      this.requestedRequirementId = requirementId ?? null;
      this.requestedReviewId = reviewId ?? null;
      this.requestedWorkflowRunId = workflowRunId ?? null;
      this.requestedWorkflowStage = workflowStage ?? 'execution_result_review';
      this.exactRestoreFailed = false;
      this.clearReportingSelection();
      try {
        if (!requirementId || !reviewId || !workflowRunId) {
          throw new Error('ExecutionResultReview 精确恢复参数不完整。');
        }
        const expectedStage = workflowStage ?? 'execution_result_review';
        if (expectedStage !== 'execution_result_review') {
          throw new Error('请求的工作流阶段不是 ExecutionResultReview。');
        }
        const [requirement, review, workflow] = await Promise.all([
          getRequirement(requirementId),
          getRequirementReview(requirementId),
          getExecutionResultReviewWorkflow(projectId, reviewId),
        ]);
        if (
          requirement.id !== requirementId
          || requirement.project_id !== projectId
          || requirement.status !== 'active'
          || review.id !== reviewId
          || review.requirement_id !== requirementId
          || workflow.project_id !== projectId
          || workflow.requirement_review_id !== reviewId
          || workflow.workflow.stage !== expectedStage
          || workflow.workflow.run_id !== workflowRunId
        ) {
          throw new Error('请求的 ExecutionResultReview 与服务端权威工作流不匹配。');
        }
        this.requirementReviewId = reviewId;
        this.executionResultReviewWorkflow = workflow;
        this.testRunId = workflow.generated_test_run_ids[0] ?? '';
        return true;
      } catch (error) {
        this.clearReportingSelection();
        this.exactRestoreFailed = true;
        this.errorMessage = error instanceof Error ? error.message : '无法恢复指定的 ExecutionResultReview。';
        return false;
      } finally {
        this.loadingReport = false;
      }
    },
    async startFailureAnalysis() {
      if (!this.testRunId) {
        this.errorMessage = 'Select an exact TestRun before starting failure analysis.';
        return;
      }
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
      if (!this.testRunId) {
        this.errorMessage = 'Select an exact TestRun before generating a report.';
        return;
      }
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
        await this.loadReportReviewWorkflow();
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
    async loadReportReviewWorkflow() {
      if (!this.projectId || !this.requirementReviewId) {
        this.reportReviewWorkflow = null;
        return null;
      }
      try {
        this.reportReviewWorkflow = await getReportReviewWorkflow(this.projectId, this.requirementReviewId);
        return this.reportReviewWorkflow;
      } catch {
        this.reportReviewWorkflow = null;
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
        if (this.executionResultReviewWorkflow.workflow.stage === 'report_review') {
          await this.loadReportReviewWorkflow();
        }
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
      if (!workflow || !this.requirementReviewId || !this.testRunId) return false;
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
    currentReportDecisionSnapshot() {
      if (!this.report) {
        return [];
      }
      return [
        {
          report_id: this.report.id,
          status: this.report.status,
          artifact_ids: this.report.artifact_ids,
          conclusion: this.report.conclusion,
        },
      ];
    },
    async runReportReviewAction(action: () => Promise<ReportReviewWorkflowRead>) {
      this.loadingReport = true;
      this.errorMessage = '';
      try {
        this.reportReviewWorkflow = await action();
        if (this.report?.id) {
          this.report = await getReport(this.report.id);
        }
        return true;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'ReportReview workflow action failed';
        await this.loadReportReviewWorkflow();
        return false;
      } finally {
        this.loadingReport = false;
      }
    },
    async submitReportReviewGate() {
      const workflow = this.reportReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runReportReviewAction(() => submitReportReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async completeReportReviewGate() {
      const workflow = this.reportReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runReportReviewAction(() => completeReportReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async editReportReviewGate() {
      const workflow = this.reportReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runReportReviewAction(() => editReportReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        report_decisions: this.currentReportDecisionSnapshot(),
      }));
    },
    async approveReportReviewGate(comment?: string) {
      const workflow = this.reportReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runReportReviewAction(() => approveReportReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async rejectReportReviewGate(comment?: string) {
      const workflow = this.reportReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runReportReviewAction(() => rejectReportReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async continueReportReviewGate() {
      const workflow = this.reportReviewWorkflow?.workflow;
      const approvalDecisionId = workflow?.approval_decision_id;
      if (!workflow || !this.requirementReviewId || !approvalDecisionId) return false;
      return this.runReportReviewAction(() => continueReportReviewWorkflow(
        this.projectId,
        this.requirementReviewId,
        {
          expected_version: workflow.lock_version,
          approval_decision_id: approvalDecisionId,
        },
      ));
    },
    async approveAndContinueReportReviewGate(comment?: string) {
      const workflow = this.reportReviewWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runReportReviewAction(() => approveAndContinueReportReviewWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
  },
});
