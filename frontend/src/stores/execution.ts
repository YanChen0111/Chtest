import { defineStore } from 'pinia';

import { createTestRun, getTestRun, type TestRunRead } from '../api/execution';
import { DEFAULT_PROJECT_ID, getLatestAutomationDraftContext } from './workflowContext';

const RECENT_RUNS_STORAGE_KEY = 'chtest.execution.recent-runs';
const MAX_RECENT_RUNS = 8;

export const useExecutionStore = defineStore('execution', {
  state: () => {
    const latestDraft = getLatestAutomationDraftContext();
    return {
      projectId: latestDraft?.projectId ?? DEFAULT_PROJECT_ID,
      automationDraftId: latestDraft?.status === 'approved' ? latestDraft.automationDraftId : '',
      automationDraftFramework: latestDraft?.status === 'approved' ? latestDraft.targetFramework : '',
      testCommandId: '',
      sourceMode: 'automation_draft' as 'automation_draft' | 'test_command',
      run: null as TestRunRead | null,
      recentRuns: [] as TestRunRead[],
      recentRunsHydrated: false,
      loading: false,
      errorMessage: '',
    };
  },
  actions: {
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
  },
});
