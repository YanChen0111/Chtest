import { defineStore } from 'pinia';

import {
  analyzeCICDRun,
  approveUnitTestPatch,
  computeQualityGate,
  createCICDRun,
  generateCICDQualityReport,
  generateUnitTestPatch,
  getCICDRun,
  listCICDRuns,
  rejectUnitTestPatch,
  runNewTests,
  runRegression,
  selectRegression,
  type CICDQualityReportRead,
  type CICDRegressionRunRead,
  type CICDRegressionSelectRead,
  type CICDRunNewTestsRead,
  type CICDRunRead,
  type QualityGateDecisionRead,
  type UnitTestPatchRead,
} from '../api/cicd';
import { listReviewHistory, type ReviewHistoryItem } from '../api/reviewHistory';

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
    unitTestPatch: null as UnitTestPatchRead | null,
    patchReviewStatus: '',
    newTestRun: null as CICDRunNewTestsRead | null,
    regressionPlan: null as CICDRegressionSelectRead | null,
    regressionRun: null as CICDRegressionRunRead | null,
    qualityGate: null as QualityGateDecisionRead | null,
    qualityReport: null as CICDQualityReportRead | null,
    patchReviewHistory: [] as ReviewHistoryItem[],
    gateReviewHistory: [] as ReviewHistoryItem[],
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
    async generatePatch() {
      if (!this.run) {
        this.errorMessage = '请先创建 CI/CD Run';
        return;
      }
      this.loading = true;
      this.errorMessage = '';
      try {
        this.unitTestPatch = await generateUnitTestPatch(this.run.id);
        this.patchReviewStatus = this.unitTestPatch.status;
        this.patchReviewHistory = [];
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'UnitTestPatch 生成失败';
      } finally {
        this.loading = false;
      }
    },
    async approvePatch() {
      if (!this.unitTestPatch) return;
      this.loading = true;
      this.errorMessage = '';
      try {
        const reviewed = await approveUnitTestPatch(this.unitTestPatch.id, '前端批准 UnitTestPatch');
        this.patchReviewStatus = reviewed.status;
        await this.loadPatchReviewHistory();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'UnitTestPatch 批准失败';
      } finally {
        this.loading = false;
      }
    },
    async rejectPatch() {
      if (!this.unitTestPatch) return;
      this.loading = true;
      this.errorMessage = '';
      try {
        const reviewed = await rejectUnitTestPatch(this.unitTestPatch.id, '前端拒绝 UnitTestPatch');
        this.patchReviewStatus = reviewed.status;
        await this.loadPatchReviewHistory();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'UnitTestPatch 拒绝失败';
      } finally {
        this.loading = false;
      }
    },
    async runNewTestsForPatch() {
      if (!this.run || !this.unitTestPatch) return;
      this.loading = true;
      this.errorMessage = '';
      try {
        this.newTestRun = await runNewTests(this.run.id, this.unitTestPatch.id);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '新增测试运行记录失败';
      } finally {
        this.loading = false;
      }
    },
    async selectRegressionPlan() {
      if (!this.run) return;
      this.loading = true;
      this.errorMessage = '';
      try {
        this.regressionPlan = await selectRegression(this.run.id);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '回归选择失败';
      } finally {
        this.loading = false;
      }
    },
    async runRegressionPlan() {
      if (!this.run || !this.regressionPlan) return;
      this.loading = true;
      this.errorMessage = '';
      try {
        this.regressionRun = await runRegression(
          this.run.id,
          this.regressionPlan.regression_plan_artifact_id,
          this.regressionPlan.recommended_test_command_ids,
        );
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '回归运行记录失败';
      } finally {
        this.loading = false;
      }
    },
    async computeGate() {
      if (!this.run) return;
      this.loading = true;
      this.errorMessage = '';
      try {
        this.qualityGate = await computeQualityGate(this.run.id);
        await this.loadGateReviewHistory();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '质量门禁计算失败';
      } finally {
        this.loading = false;
      }
    },
    async generateQualityReport() {
      if (!this.run) return;
      this.loading = true;
      this.errorMessage = '';
      try {
        this.qualityReport = await generateCICDQualityReport(this.run.id);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'CI/CD 质量报告生成失败';
      } finally {
        this.loading = false;
      }
    },
    async refreshRuns() {
      const listed = await listCICDRuns();
      this.runs = listed.items;
    },
    async loadPatchReviewHistory() {
      if (!this.unitTestPatch) {
        this.patchReviewHistory = [];
        return;
      }
      const history = await listReviewHistory({
        projectId: this.projectId,
        entityType: 'UnitTestPatch',
        entityId: this.unitTestPatch.id,
        limit: 20,
      });
      this.patchReviewHistory = history.items;
    },
    async loadGateReviewHistory() {
      if (!this.run) {
        this.gateReviewHistory = [];
        return;
      }
      const history = await listReviewHistory({
        projectId: this.projectId,
        relatedEntityType: 'CICDRun',
        relatedEntityId: this.run.id,
        limit: 20,
      });
      this.gateReviewHistory = history.items.filter((item) => item.entity_type === 'QualityGateDecision');
    },
  },
});
