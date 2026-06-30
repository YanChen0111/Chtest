import { defineStore } from 'pinia';

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
    failureAnalysis: null as FailureAnalysisRead | null,
    report: null as ReportRead | null,
    loadingAnalysis: false,
    loadingReport: false,
    errorMessage: '',
  }),
  actions: {
    async startFailureAnalysis() {
      this.loadingAnalysis = true;
      this.errorMessage = '';
      try {
        await createFailureAnalysis(this.testRunId, {
          model_provider: 'mock',
          model_name: 'mock-failure-analysis',
        });
        this.failureAnalysis = await getFailureAnalysis(this.testRunId);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '失败分析生成失败';
      } finally {
        this.loadingAnalysis = false;
      }
    },
    async startReport() {
      this.loadingReport = true;
      this.errorMessage = '';
      try {
        const created = await createReport({
          project_id: this.projectId,
          report_type: 'automation_execution',
          related_entity_type: 'TestRun',
          related_entity_id: this.testRunId,
        });
        this.report = await getReport(created.report_id);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '报告生成失败';
      } finally {
        this.loadingReport = false;
      }
    },
  },
});
