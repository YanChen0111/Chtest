import { defineStore } from 'pinia';

import {
  getKnowledgeBase,
  listToolDefinitions,
  type KnowledgeBaseRead,
  type ToolDefinitionRead,
} from '../api/extension';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';

export const useExtensionStore = defineStore('extension', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    knowledgeBase: null as KnowledgeBaseRead | null,
    toolDefinitions: [] as ToolDefinitionRead[],
    loading: false,
    errorMessage: '',
  }),
  getters: {
    contextArtifactCount: (state) => state.knowledgeBase?.context_artifacts.length ?? 0,
    safeContextArtifactCount: (state) =>
      state.knowledgeBase?.context_artifacts.filter((artifact) => artifact.safe_to_show).length ?? 0,
    promptEligibleCount: (state) =>
      state.knowledgeBase?.context_artifacts.filter((artifact) => artifact.allowed_for_prompt).length ?? 0,
    latestRetrievals: (state) => state.knowledgeBase?.latest_retrievals ?? [],
    mcpReadyToolCount: (state) => state.toolDefinitions.filter((tool) => tool.is_mcp_ready).length,
  },
  actions: {
    async loadExtensionSurface() {
      this.loading = true;
      this.errorMessage = '';
      try {
        const [knowledgeBase, tools] = await Promise.all([
          getKnowledgeBase(this.projectId),
          listToolDefinitions(this.projectId),
        ]);
        this.knowledgeBase = knowledgeBase;
        this.toolDefinitions = tools.items;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'RAG 知识库加载失败';
      } finally {
        this.loading = false;
      }
    },
  },
});
