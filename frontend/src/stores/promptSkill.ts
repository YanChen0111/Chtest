import { defineStore } from 'pinia';

import {
  listPromptVersions,
  listSkillVersions,
  type PromptVersion,
  type SkillVersion,
} from '../api/promptSkill';

export const usePromptSkillStore = defineStore('promptSkill', {
  state: () => ({
    prompts: [] as PromptVersion[],
    skills: [] as SkillVersion[],
    loading: false,
    errorMessage: '',
  }),
  getters: {
    activePromptCount: (state) => state.prompts.filter((prompt) => prompt.status === 'active').length,
    activeSkillCount: (state) => state.skills.filter((skill) => skill.status === 'active').length,
    applicableAgentCount: (state) =>
      new Set(state.skills.flatMap((skill) => skill.applicable_agents)).size,
  },
  actions: {
    async loadRegistry() {
      this.loading = true;
      this.errorMessage = '';
      try {
        const [promptList, skillList] = await Promise.all([listPromptVersions(), listSkillVersions()]);
        this.prompts = promptList.items;
        this.skills = skillList.items;
      } catch (error) {
        this.prompts = [];
        this.skills = [];
        this.errorMessage = error instanceof Error ? error.message : 'Prompt / Skill 注册表加载失败';
      } finally {
        this.loading = false;
      }
    },
  },
});
