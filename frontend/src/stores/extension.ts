import { defineStore } from 'pinia';

import {
  createContextArtifact,
  extractAllTestKnowledgeCards,
  extractTestKnowledgeCards,
  getTestKnowledgeGraph,
  getTestKnowledgeIndex,
  getKnowledgeBase,
  listTestKnowledgeCards,
  listToolDefinitions,
  rebuildTestKnowledgeIndex,
  retrieveKnowledge,
  retrieveTestKnowledgeCards,
  reviewTestKnowledgeCard,
  updateKnowledgeAdapter,
  type ContextArtifactCreateRequest,
  type KnowledgeBaseRead,
  type KnowledgeRetrievalRead,
  type TestKnowledgeCardExtractRead,
  type TestKnowledgeCardExtractBatchRead,
  type TestKnowledgeCardRetrievalRead,
  type TestKnowledgeCardRead,
  type TestKnowledgeGraphRead,
  type TestKnowledgeIndexRead,
  type ToolDefinitionRead,
} from '../api/extension';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';

export const useExtensionStore = defineStore('extension', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    knowledgeBase: null as KnowledgeBaseRead | null,
    toolDefinitions: [] as ToolDefinitionRead[],
    testKnowledgeCards: [] as TestKnowledgeCardRead[],
    testKnowledgeGraph: null as TestKnowledgeGraphRead | null,
    testKnowledgeIndex: null as TestKnowledgeIndexRead | null,
    latestKnowledgeExtraction: null as TestKnowledgeCardExtractRead | null,
    knowledgeCardRetrieval: null as TestKnowledgeCardRetrievalRead | null,
    retrievalTest: null as KnowledgeRetrievalRead | null,
    loading: false,
    loadingMutation: false,
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
    testKnowledgeCardCount: (state) => state.testKnowledgeCards.length,
    approvedKnowledgeCardCount: (state) => state.testKnowledgeCards.filter((card) => card.status === 'approved').length,
    pendingKnowledgeCardCount: (state) => state.testKnowledgeCards.filter((card) => card.status === 'extracted').length,
    promptReadyKnowledgeCardCount: (state) =>
      state.testKnowledgeCards.filter(
        (card) => ['approved', 'extracted'].includes(card.status) && card.safe_to_show && card.allowed_for_prompt,
      ).length,
    knowledgeCoverageRatio: (state) => Number(state.testKnowledgeGraph?.coverage.knowledge_coverage_ratio ?? 0),
    coveredKnowledgeCardCount: (state) => Number(state.testKnowledgeGraph?.coverage.covered_knowledge_card_count ?? 0),
    vectorIndexCoverageRatio: (state) => Number(state.testKnowledgeGraph?.coverage.vector_index_coverage_ratio ?? 0),
    indexedKnowledgeCardCount: (state) => Number(state.testKnowledgeIndex?.indexed_count ?? 0),
    knowledgeIndexGapCount: (state) => {
      const promptReadyCount = state.testKnowledgeCards.filter(
        (card) => ['approved', 'extracted'].includes(card.status) && card.safe_to_show && card.allowed_for_prompt,
      ).length;
      const indexedCount = Number(state.testKnowledgeIndex?.indexed_count ?? 0);
      return Math.max(0, promptReadyCount - indexedCount);
    },
  },
  actions: {
    async loadExtensionSurface() {
      this.loading = true;
      this.errorMessage = '';
      try {
        const [knowledgeBase, tools, cards, graph, index] = await Promise.all([
          getKnowledgeBase(this.projectId),
          listToolDefinitions(this.projectId),
          listTestKnowledgeCards(this.projectId),
          getTestKnowledgeGraph(this.projectId),
          getTestKnowledgeIndex(this.projectId),
        ]);
        this.knowledgeBase = knowledgeBase;
        this.toolDefinitions = tools.items;
        this.testKnowledgeCards = cards.items;
        this.testKnowledgeGraph = graph;
        this.testKnowledgeIndex = index;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'RAG 知识库加载失败';
      } finally {
        this.loading = false;
      }
    },
    async uploadContextArtifact(data: {
      title: string;
      sourceRef: string;
      content: string;
      artifactType: 'context_markdown' | 'context_text';
    }) {
      this.loadingMutation = true;
      this.errorMessage = '';
      try {
        const payload: ContextArtifactCreateRequest = {
          project_id: this.projectId,
          title: data.title,
          artifact_type: data.artifactType,
          mime_type: data.artifactType === 'context_markdown' ? 'text/markdown' : 'text/plain',
          content: data.content,
          source_ref: data.sourceRef,
        };
        await createContextArtifact(payload);
        await this.loadExtensionSurface();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '知识导入失败';
      } finally {
        this.loadingMutation = false;
      }
    },
    async enableDeterministicRetrieval() {
      this.loadingMutation = true;
      this.errorMessage = '';
      try {
        await updateKnowledgeAdapter(this.projectId, {
          adapter_name: 'default',
          status: 'configured_stub',
          provider_type: 'deterministic_local',
          config: {
            match_mode: 'keyword_overlap',
            max_results: 5,
            max_snippet_chars: 320,
            min_score: 1,
          },
          safety_policy: {
            same_project_only: true,
            require_allowed_for_prompt: true,
          },
          notes: 'Deterministic local retrieval for Chtest ContextArtifacts.',
        });
        await this.loadExtensionSurface();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '本地检索启用失败';
      } finally {
        this.loadingMutation = false;
      }
    },
    async extractKnowledgeCards(sourceArtifactId: string) {
      this.loadingMutation = true;
      this.errorMessage = '';
      try {
        this.latestKnowledgeExtraction = await extractTestKnowledgeCards({
          project_id: this.projectId,
          source_artifact_id: sourceArtifactId,
        });
        await this.loadExtensionSurface();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '测试知识卡抽取失败';
      } finally {
        this.loadingMutation = false;
      }
    },
    async extractAllKnowledgeCards(sourceArtifactIds: string[]) {
      this.loadingMutation = true;
      this.errorMessage = '';
      try {
        const result: TestKnowledgeCardExtractBatchRead = await extractAllTestKnowledgeCards({
          project_id: this.projectId,
          source_artifact_ids: sourceArtifactIds,
        });
        this.latestKnowledgeExtraction =
          result.source_artifact_ids.length > 0
            ? {
                source_artifact_id: result.source_artifact_ids[0],
                created_count: result.created_count,
                skipped_count: result.skipped_count,
                items: result.items,
              }
            : null;
        await this.loadExtensionSurface();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '测试知识卡抽取失败';
      } finally {
        this.loadingMutation = false;
      }
    },
    async runKnowledgeCardRetrieval(queryText: string) {
      this.loadingMutation = true;
      this.errorMessage = '';
      this.knowledgeCardRetrieval = null;
      try {
        this.knowledgeCardRetrieval = await retrieveTestKnowledgeCards({
          project_id: this.projectId,
          query_text: queryText,
          limit: 5,
          approved_only: false,
        });
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '测试知识卡检索失败';
      } finally {
        this.loadingMutation = false;
      }
    },
    async rebuildKnowledgeIndex() {
      this.loadingMutation = true;
      this.errorMessage = '';
      try {
        await rebuildTestKnowledgeIndex({
          project_id: this.projectId,
          embedding_model: 'deterministic-hashing-v1',
          embedding_dim: 64,
        });
        await this.loadExtensionSurface();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'Vector index rebuild failed';
      } finally {
        this.loadingMutation = false;
      }
    },
    async reviewKnowledgeCard(cardId: string, status: string) {
      this.loadingMutation = true;
      this.errorMessage = '';
      try {
        await reviewTestKnowledgeCard(cardId, {
          project_id: this.projectId,
          status,
        });
        await this.loadExtensionSurface();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '测试知识卡审核失败';
      } finally {
        this.loadingMutation = false;
      }
    },
    async runRetrievalTest(queryText: string) {
      this.loadingMutation = true;
      this.errorMessage = '';
      this.retrievalTest = null;
      try {
        this.retrievalTest = await retrieveKnowledge(this.projectId, {
          query_text: queryText,
          adapter_name: 'default',
          max_results: 5,
          max_snippet_chars: 320,
        });
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '知识检索测试失败';
      } finally {
        this.loadingMutation = false;
      }
    },
  },
});
