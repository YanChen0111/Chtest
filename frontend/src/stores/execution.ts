import { defineStore } from 'pinia';

import { createTestRun, getTestRun, type TestRunRead } from '../api/execution';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';
const DEFAULT_AUTOMATION_DRAFT_ID = '00000000-0000-0000-0000-000000001001';

export const useExecutionStore = defineStore('execution', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    automationDraftId: DEFAULT_AUTOMATION_DRAFT_ID,
    testCommandId: '',
    sourceMode: 'automation_draft' as 'automation_draft' | 'test_command',
    run: null as TestRunRead | null,
    loading: false,
    errorMessage: '',
  }),
  actions: {
    async startRun(options: { runnerMode?: string; reason?: string } = {}) {
      const runnerMode = options.runnerMode ?? 'local_subprocess';
      this.loading = true;
      this.errorMessage = '';
      try {
        this.run = await createTestRun({
          project_id: this.projectId,
          automation_draft_id: this.sourceMode === 'automation_draft' ? this.automationDraftId : null,
          test_command_id: this.sourceMode === 'test_command' ? this.testCommandId : null,
          reason: options.reason ?? 'frontend pytest execution',
          runner_mode: runnerMode,
        });
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
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '执行结果刷新失败';
      } finally {
        this.loading = false;
      }
    },
  },
});
