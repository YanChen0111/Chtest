import { defineStore } from 'pinia';

import {
  approveAndContinueExecutionApprovalWorkflow,
  approveExecutionApprovalWorkflow,
  completeExecutionApprovalWorkflow,
  continueExecutionApprovalWorkflow,
  createTestRun,
  editExecutionApprovalWorkflow,
  getExecutionApprovalWorkflow,
  getTestRun,
  rejectExecutionApprovalWorkflow,
  submitExecutionApprovalWorkflow,
  type ExecutionApprovalWorkflowRead,
  type TestRunRead,
} from '../api/execution';
import { getProjectSettings, type ProjectTestCommand } from '../api/projects';
import { DEFAULT_PROJECT_ID, getLatestAutomationDraftContext } from './workflowContext';

const RECENT_RUNS_STORAGE_KEY = 'chtest.execution.recent-runs';
const MAX_RECENT_RUNS = 8;

export const useExecutionStore = defineStore('execution', {
  state: () => {
    const latestDraft = getLatestAutomationDraftContext();
    return {
      projectId: latestDraft?.projectId ?? DEFAULT_PROJECT_ID,
      requirementReviewId: latestDraft?.requirementReviewId ?? '',
      automationDraftId: latestDraft?.status === 'approved' ? latestDraft.automationDraftId : '',
      automationDraftFramework: latestDraft?.status === 'approved' ? latestDraft.targetFramework : '',
      testCommandId: '',
      testCommands: [] as ProjectTestCommand[],
      loadingCommands: false,
      sourceMode: 'automation_draft' as 'automation_draft' | 'test_command',
      executionApprovalWorkflow: null as ExecutionApprovalWorkflowRead | null,
      run: null as TestRunRead | null,
      recentRuns: [] as TestRunRead[],
      recentRunsHydrated: false,
      loading: false,
      errorMessage: '',
    };
  },
  actions: {
    async loadTestCommands() {
      if (this.loadingCommands || this.testCommands.length > 0) return;
      this.loadingCommands = true;
      try {
        const settings = await getProjectSettings(this.projectId);
        this.testCommands = settings.test_commands.filter((item) => item.status === 'active');
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '加载项目测试命令失败';
      } finally {
        this.loadingCommands = false;
      }
    },
    hydrateRecentRuns() {
      if (this.recentRunsHydrated || typeof window === 'undefined') return;
      this.recentRunsHydrated = true;
      try {
        const value = JSON.parse(window.localStorage.getItem(RECENT_RUNS_STORAGE_KEY) ?? '[]');
        if (Array.isArray(value)) this.recentRuns = value.slice(0, MAX_RECENT_RUNS) as TestRunRead[];
      } catch {
        this.recentRuns = [];
      }
    },
    persistRecentRuns() {
      if (typeof window === 'undefined') return;
      window.localStorage.setItem(RECENT_RUNS_STORAGE_KEY, JSON.stringify(this.recentRuns.slice(0, MAX_RECENT_RUNS)));
    },
    rememberRun(run: TestRunRead) {
      this.recentRuns = [run, ...this.recentRuns.filter((item) => item.id !== run.id)].slice(0, MAX_RECENT_RUNS);
      this.persistRecentRuns();
    },
    async startRun(options: { runnerMode?: string; reason?: string } = {}) {
      const runnerMode = options.runnerMode ?? 'local_subprocess';
      this.loading = true;
      this.errorMessage = '';
      if (this.sourceMode === 'automation_draft' && !this.automationDraftId) {
        this.errorMessage = '请先在自动化草稿页批准草稿，再启动执行。';
        this.loading = false;
        return;
      }
      if (
        this.sourceMode === 'automation_draft'
        && this.requirementReviewId
        && !this.executionApprovalWorkflow?.workflow.approval_decision_id
      ) {
        this.errorMessage = 'ExecutionApproval gate must be approved before running this AutomationDraft.';
        this.loading = false;
        return;
      }
      if (this.sourceMode === 'test_command' && !this.testCommandId) {
        this.errorMessage = '请先选择已配置的 TestCommand。';
        this.loading = false;
        return;
      }
      try {
        this.run = await createTestRun({
          project_id: this.projectId,
          automation_draft_id: this.sourceMode === 'automation_draft' ? this.automationDraftId : null,
          test_command_id: this.sourceMode === 'test_command' ? this.testCommandId : null,
          execution_approval_decision_id:
            this.sourceMode === 'automation_draft'
              ? this.executionApprovalWorkflow?.workflow.approval_decision_id ?? null
              : null,
          reason: options.reason ?? 'frontend pytest execution',
          runner_mode: runnerMode,
        });
        this.rememberRun(this.run);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '执行失败';
      } finally {
        this.loading = false;
      }
    },
    async refreshRun() {
      if (!this.run) {
        this.errorMessage = '请先启动一次执行';
        return;
      }
      this.loading = true;
      this.errorMessage = '';
      try {
        this.run = await getTestRun(this.run.id);
        this.rememberRun(this.run);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '执行结果刷新失败';
      } finally {
        this.loading = false;
      }
    },
    async resumeRun(runId: string) {
      this.hydrateRecentRuns();
      const cachedRun = this.recentRuns.find((item) => item.id === runId);
      if (!cachedRun) {
        this.errorMessage = 'Recent run is no longer available.';
        return;
      }
      this.run = cachedRun;
      await this.refreshRun();
    },
    async loadExecutionApprovalWorkflow() {
      if (!this.projectId || !this.requirementReviewId || !this.automationDraftId) {
        this.executionApprovalWorkflow = null;
        return null;
      }
      try {
        this.executionApprovalWorkflow = await getExecutionApprovalWorkflow(this.projectId, this.requirementReviewId);
        return this.executionApprovalWorkflow;
      } catch {
        this.executionApprovalWorkflow = null;
        return null;
      }
    },
    currentExecutionDecisionSnapshot() {
      if (!this.automationDraftId) {
        return [];
      }
      return [
        {
          automation_draft_id: this.automationDraftId,
          status: this.executionApprovalWorkflow?.approved_automation_draft_ids.includes(this.automationDraftId)
            ? 'approved'
            : 'unknown',
          runner_mode: this.automationDraftFramework === 'playwright' ? 'playwright_local' : 'local_subprocess',
          reason: 'Frontend execution scope reviewed.',
        },
      ];
    },
    async runExecutionApprovalAction(action: () => Promise<ExecutionApprovalWorkflowRead>) {
      this.loading = true;
      this.errorMessage = '';
      try {
        this.executionApprovalWorkflow = await action();
        return true;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'ExecutionApproval workflow action failed';
        await this.loadExecutionApprovalWorkflow();
        return false;
      } finally {
        this.loading = false;
      }
    },
    async submitExecutionApprovalGate() {
      const workflow = this.executionApprovalWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionApprovalAction(() => submitExecutionApprovalWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async completeExecutionApprovalGate() {
      const workflow = this.executionApprovalWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionApprovalAction(() => completeExecutionApprovalWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
      }));
    },
    async editExecutionApprovalGate() {
      const workflow = this.executionApprovalWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionApprovalAction(() => editExecutionApprovalWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        execution_decisions: this.currentExecutionDecisionSnapshot(),
      }));
    },
    async approveExecutionApprovalGate(comment?: string) {
      const workflow = this.executionApprovalWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionApprovalAction(() => approveExecutionApprovalWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async rejectExecutionApprovalGate(comment?: string) {
      const workflow = this.executionApprovalWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionApprovalAction(() => rejectExecutionApprovalWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
    async continueExecutionApprovalGate() {
      const workflow = this.executionApprovalWorkflow?.workflow;
      const approvalDecisionId = workflow?.approval_decision_id;
      if (!workflow || !this.requirementReviewId || !approvalDecisionId) return false;
      return this.runExecutionApprovalAction(() => continueExecutionApprovalWorkflow(
        this.projectId,
        this.requirementReviewId,
        {
          expected_version: workflow.lock_version,
          approval_decision_id: approvalDecisionId,
        },
      ));
    },
    async approveAndContinueExecutionApprovalGate(comment?: string) {
      const workflow = this.executionApprovalWorkflow?.workflow;
      if (!workflow || !this.requirementReviewId) return false;
      return this.runExecutionApprovalAction(() => approveAndContinueExecutionApprovalWorkflow(this.projectId, this.requirementReviewId, {
        expected_version: workflow.lock_version,
        comment,
      }));
    },
  },
});
