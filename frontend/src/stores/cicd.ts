import { defineStore } from 'pinia';

import { analyzeCICDRun, createCICDRun, getCICDRun, listCICDRuns, type CICDRunRead } from '../api/cicd';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';
const DEFAULT_REPOSITORY_ID = '00000000-0000-0000-0000-000000000301';
const DEFAULT_DIFF_TEXT = `diff --git a/app/coupon.py b/app/coupon.py
--- a/app/coupon.py
+++ b/app/coupon.py
@@ -1 +1,2 @@
-old
+new
`;

export const useCICDStore = defineStore('cicd', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    repositoryId: DEFAULT_REPOSITORY_ID,
    baseRef: 'main',
    headRef: 'HEAD',
    diffText: DEFAULT_DIFF_TEXT,
    run: null as CICDRunRead | null,
    runs: [] as CICDRunRead[],
    loading: false,
    errorMessage: '',
  }),
  actions: {
    async createRun() {
      this.loading = true;
      this.errorMessage = '';
      try {
        const created = await createCICDRun({
          project_id: this.projectId,
          repository_id: this.repositoryId || null,
          source_type: 'local_diff',
          trigger_type: 'manual',
          provider: 'local',
          base_ref: this.baseRef,
          head_ref: this.headRef,
          diff_text: this.diffText,
        });
        this.run = await getCICDRun(created.cicd_run_id);
        await this.refreshRuns();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'CI/CD Run 创建失败';
      } finally {
        this.loading = false;
      }
    },
    async analyzeRun() {
      if (!this.run) {
        this.errorMessage = '请先创建 CI/CD Run';
        return;
      }
      this.loading = true;
      this.errorMessage = '';
      try {
        await analyzeCICDRun(this.run.id, {
          model_provider: 'mock',
          model_name: 'mock-cicd-analysis',
        });
        this.run = await getCICDRun(this.run.id);
        await this.refreshRuns();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '风险分析失败';
      } finally {
        this.loading = false;
      }
    },
    async refreshRuns() {
      const listed = await listCICDRuns();
      this.runs = listed.items;
    },
  },
});
