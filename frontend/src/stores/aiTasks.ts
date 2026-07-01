import { defineStore } from 'pinia';

import {
  getAITaskDetail,
  listProjectAITasks,
  type AITaskDetail,
  type AITaskListItem,
} from '../api/aiTasks';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';

export const useAITasksStore = defineStore('aiTasks', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    tasks: [] as AITaskListItem[],
    selectedTask: null as AITaskDetail | null,
    loadingList: false,
    loadingDetail: false,
    errorMessage: '',
  }),
  getters: {
    totalTasks: (state) => state.tasks.length,
    runningTasks: (state) => state.tasks.filter((task) => task.status === 'running').length,
    failedTasks: (state) => state.tasks.filter((task) => task.status === 'failed').length,
    contextArtifactCount: (state) =>
      new Set(state.tasks.flatMap((task) => task.context_artifact_ids)).size,
  },
  actions: {
    async loadRecentTasks(projectId?: string) {
      const targetProjectId = projectId ?? this.projectId;
      this.projectId = targetProjectId;
      this.loadingList = true;
      this.errorMessage = '';
      try {
        const response = await listProjectAITasks(targetProjectId);
        this.tasks = response.items;
        if (this.tasks[0]) {
          await this.loadTaskDetail(this.tasks[0].id);
        } else {
          this.selectedTask = null;
        }
      } catch (error) {
        this.tasks = [];
        this.selectedTask = null;
        this.errorMessage = error instanceof Error ? error.message : 'AI 任务加载失败';
      } finally {
        this.loadingList = false;
      }
    },
    async loadTaskDetail(aiTaskId: string) {
      this.loadingDetail = true;
      this.errorMessage = '';
      try {
        this.selectedTask = await getAITaskDetail(aiTaskId);
      } catch (error) {
        this.selectedTask = null;
        this.errorMessage = error instanceof Error ? error.message : 'AI 任务详情加载失败';
      } finally {
        this.loadingDetail = false;
      }
    },
  },
});
