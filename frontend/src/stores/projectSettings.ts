import { defineStore } from 'pinia';

import { getProjectSettings, type ProjectSettings } from '../api/projects';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';

export const useProjectSettingsStore = defineStore('projectSettings', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    settings: null as ProjectSettings | null,
    loading: false,
    errorMessage: '',
  }),
  actions: {
    async loadSettings(projectId?: string) {
      const targetProjectId = projectId ?? this.projectId;
      this.loading = true;
      this.errorMessage = '';
      this.projectId = targetProjectId;
      try {
        this.settings = await getProjectSettings(targetProjectId);
      } catch (error) {
        this.settings = null;
        this.errorMessage = error instanceof Error ? error.message : '项目设置加载失败';
      } finally {
        this.loading = false;
      }
    },
  },
});
