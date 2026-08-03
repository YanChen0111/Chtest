import { defineStore } from 'pinia';

import { ApiError } from '../api/client';
import { getProjectSettings, type ProjectSettings } from '../api/projects';
import {
  approveTestCampaign,
  completeTestCampaignReview,
  continueTestCampaign,
  createTestCampaign,
  editTestCampaign,
  getTestCampaign,
  listTestCampaigns,
  rejectTestCampaign,
  submitTestCampaign,
  type TestCampaignRead,
  type TestCampaignScopeInput,
} from '../api/testCampaigns';
import { DEFAULT_PROJECT_ID } from './workflowContext';

const DEFAULT_REVIEWER = 'Default User';

export const useTestCampaignStore = defineStore('testCampaigns', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    settings: null as ProjectSettings | null,
    campaigns: [] as TestCampaignRead[],
    campaign: null as TestCampaignRead | null,
    loading: false,
    saving: false,
    stale: false,
    errorMessage: '',
    successMessage: '',
  }),
  getters: {
    workflow: (state) => state.campaign?.workflow ?? null,
    canSave: (state) => !state.stale && (!state.campaign || state.campaign.workflow.stage === 'scope'),
    canSubmit: (state) => !state.stale && state.campaign?.workflow.stage === 'scope'
      && state.campaign.workflow.state === 'draft',
    canCompleteReview: (state) => !state.stale && state.campaign?.workflow.stage === 'scope'
      && state.campaign.workflow.state === 'waiting_review',
    canDecide: (state) => !state.stale && state.campaign?.workflow.stage === 'scope'
      && ['waiting_review', 'waiting_approval'].includes(state.campaign.workflow.state),
    canContinue: (state) => !state.stale && Boolean(
      state.campaign?.workflow.stage === 'scope'
      && state.campaign.workflow.state === 'approved'
      && state.campaign.workflow.can_continue
      && state.campaign.workflow.approval_decision_id,
    ),
  },
  actions: {
    async load(projectId?: string) {
      this.loading = true;
      this.errorMessage = '';
      this.successMessage = '';
      this.stale = false;
      this.projectId = projectId ?? this.projectId;
      try {
        const [settings, campaigns] = await Promise.all([
          getProjectSettings(this.projectId),
          listTestCampaigns(this.projectId),
        ]);
        this.settings = settings;
        this.campaigns = campaigns;
        this.campaign = campaigns[0] ?? null;
      } catch (error) {
        this.errorMessage = messageFromError(error, '测试范围加载失败');
      } finally {
        this.loading = false;
      }
    },
    async refresh() {
      if (!this.campaign) {
        await this.load();
        return;
      }
      this.loading = true;
      this.errorMessage = '';
      try {
        this.campaign = await getTestCampaign(this.projectId, this.campaign.id);
        this.stale = false;
        this.successMessage = '已刷新为服务器最新版本';
      } catch (error) {
        this.errorMessage = messageFromError(error, '测试范围刷新失败');
      } finally {
        this.loading = false;
      }
    },
    async saveScope(input: TestCampaignScopeInput, comment?: string) {
      return this.runMutation(async () => {
        if (!this.campaign) {
          return createTestCampaign(this.projectId, { ...input, created_by: DEFAULT_REVIEWER });
        }
        return editTestCampaign(this.projectId, this.campaign.id, {
          ...input,
          expected_version: this.campaign.workflow.lock_version,
          reviewer: DEFAULT_REVIEWER,
          comment: comment || null,
        });
      }, '范围草稿已保存');
    },
    async submit() {
      return this.withCurrentCampaign((campaign) => submitTestCampaign(this.projectId, campaign.id, {
        expected_version: campaign.workflow.lock_version,
      }), '范围已提交评审');
    },
    async completeReview(comment?: string) {
      return this.withCurrentCampaign((campaign) => completeTestCampaignReview(this.projectId, campaign.id, {
        expected_version: campaign.workflow.lock_version,
        reviewer: DEFAULT_REVIEWER,
        comment: comment || null,
      }), '人工评审已完成');
    },
    async approve(comment?: string) {
      return this.withCurrentCampaign((campaign) => approveTestCampaign(this.projectId, campaign.id, {
        expected_version: campaign.workflow.lock_version,
        reviewer: DEFAULT_REVIEWER,
        comment: comment || null,
      }), '当前范围已批准');
    },
    async reject(comment?: string) {
      return this.withCurrentCampaign((campaign) => rejectTestCampaign(this.projectId, campaign.id, {
        expected_version: campaign.workflow.lock_version,
        reviewer: DEFAULT_REVIEWER,
        comment: comment || null,
      }), '当前范围已拒绝');
    },
    async continueWorkflow() {
      return this.withCurrentCampaign((campaign) => continueTestCampaign(
        this.projectId,
        campaign.id,
        campaign.workflow.lock_version,
        campaign.workflow.approval_decision_id!,
      ), '范围批准已消费，进入需求阶段');
    },
    async withCurrentCampaign(
      action: (campaign: TestCampaignRead) => Promise<TestCampaignRead>,
      successMessage: string,
    ) {
      if (!this.campaign) return null;
      return this.runMutation(() => action(this.campaign!), successMessage);
    },
    async runMutation(action: () => Promise<TestCampaignRead>, successMessage: string) {
      this.saving = true;
      this.errorMessage = '';
      this.successMessage = '';
      try {
        const campaign = await action();
        this.campaign = campaign;
        this.campaigns = [campaign, ...this.campaigns.filter((item) => item.id !== campaign.id)];
        this.successMessage = successMessage;
        this.stale = false;
        return campaign;
      } catch (error) {
        if (error instanceof ApiError && error.status === 409) {
          this.stale = true;
          this.errorMessage = '服务器状态已变化，请刷新后再继续';
        } else {
          this.errorMessage = messageFromError(error, '测试范围操作失败');
        }
        return null;
      } finally {
        this.saving = false;
      }
    },
  },
});

function messageFromError(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback;
}
