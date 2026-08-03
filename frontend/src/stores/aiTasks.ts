import { defineStore } from 'pinia';

import {
  getAITaskDetail,
  listProjectAITasks,
  type AITaskDetail,
  type AITaskListItem,
} from '../api/aiTasks';
import {
  listWorkflowQueue,
  type WorkflowQueueBucket,
  type WorkflowQueueRead,
} from '../api/workflowControl';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';

export const useAITasksStore = defineStore('aiTasks', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    tasks: [] as AITaskListItem[],
    workflowQueue: null as WorkflowQueueRead | null,
    selectedTask: null as AITaskDetail | null,
    loadingList: false,
    loadingWorkflowQueue: false,
    loadingDetail: false,
    errorMessage: '',
    workflowQueueError: '',
  }),
  getters: {
    totalTasks: (state) => state.tasks.length,
    runningTasks: (state) => state.tasks.filter((task) => task.status === 'running').length,
    failedTasks: (state) => state.tasks.filter((task) => task.status === 'failed').length,
    workflowQueueTotal: (state) => state.workflowQueue?.total ?? 0,
    waitingReviewCount: (state) => state.workflowQueue?.groups.waiting_review?.length ?? 0,
    waitingApprovalCount: (state) => state.workflowQueue?.groups.waiting_approval?.length ?? 0,
    continuableWorkflowCount: (state) => state.workflowQueue?.groups.can_continue?.length ?? 0,
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
    async loadWorkflowQueue(projectId?: string) {
      const targetProjectId = projectId ?? this.projectId;
      this.projectId = targetProjectId;
      this.loadingWorkflowQueue = true;
      this.workflowQueueError = '';
      try {
        this.workflowQueue = await listWorkflowQueue(targetProjectId);
      } catch (error) {
        this.workflowQueue = null;
        this.workflowQueueError = error instanceof Error ? error.message : 'Workflow queue loading failed';
      } finally {
        this.loadingWorkflowQueue = false;
      }
    },
    workflowQueueItems(bucket: WorkflowQueueBucket) {
      return this.workflowQueue?.groups[bucket] ?? [];
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
