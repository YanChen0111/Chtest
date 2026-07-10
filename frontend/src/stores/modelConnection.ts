import { defineStore } from 'pinia';

import {
  getModelConnectionConfig,
  saveModelConnectionConfig,
  testModelConnectionConfig,
  type ModelConnectionConfig,
  type ModelConnectionConfigUpdate,
  type ModelConnectionTestResult,
} from '../api/modelConnection';

export const useModelConnectionStore = defineStore('modelConnection', {
  state: () => ({
    config: null as ModelConnectionConfig | null,
    loading: false,
    saving: false,
    testing: false,
    testResult: null as ModelConnectionTestResult | null,
    errorMessage: '',
    savedMessage: '',
  }),
  actions: {
    async loadConfig() {
      this.loading = true;
      this.errorMessage = '';
      try {
        this.config = await getModelConnectionConfig();
      } catch (error) {
        this.config = null;
        this.errorMessage =
          error instanceof Error ? error.message : '\u5927\u6a21\u578b\u63a5\u5165\u914d\u7f6e\u52a0\u8f7d\u5931\u8d25';
      } finally {
        this.loading = false;
      }
    },
    async saveConfig(data: ModelConnectionConfigUpdate) {
      this.saving = true;
      this.errorMessage = '';
      this.savedMessage = '';
      try {
        this.config = await saveModelConnectionConfig(data);
        this.testResult = null;
        this.savedMessage = '\u5927\u6a21\u578b\u63a5\u5165\u914d\u7f6e\u5df2\u4fdd\u5b58';
      } catch (error) {
        this.errorMessage =
          error instanceof Error ? error.message : '\u5927\u6a21\u578b\u63a5\u5165\u914d\u7f6e\u4fdd\u5b58\u5931\u8d25';
        throw error;
      } finally {
        this.saving = false;
      }
    },
    async testConfig(data: ModelConnectionConfigUpdate = {}) {
      this.testing = true;
      this.errorMessage = '';
      this.savedMessage = '';
      try {
        this.testResult = await testModelConnectionConfig(data);
      } catch (error) {
        this.testResult = null;
        this.errorMessage =
          error instanceof Error ? error.message : '\u5927\u6a21\u578b\u8fde\u63a5\u6d4b\u8bd5\u5931\u8d25';
        throw error;
      } finally {
        this.testing = false;
      }
    },
  },
});
