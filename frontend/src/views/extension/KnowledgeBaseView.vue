<template>
  <section class="knowledge-base-page" aria-labelledby="knowledge-base-title">
    <div class="settings-heading">
      <div>
        <p class="eyebrow">扩展表面</p>
        <h2 id="knowledge-base-title">RAG 知识库</h2>
        <p>查看项目上下文、提示词可用性、AI 使用记录和 MCP-ready 工具结构；V1 仅保留扩展表面。</p>
      </div>
      <a-space>
        <a-tag color="blue">ContextArtifact</a-tag>
        <a-tag color="gray">无 RAG 运行时</a-tag>
        <a-button type="primary" :loading="store.loading" @click="store.loadExtensionSurface()">刷新</a-button>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <div class="knowledge-metrics">
      <a-card class="settings-panel" :bordered="false">
        <span>ContextArtifact</span>
        <strong>{{ store.contextArtifactCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>可安全展示</span>
        <strong>{{ store.safeContextArtifactCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>允许进入提示词</span>
        <strong>{{ store.promptEligibleCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>MCP-ready 工具</span>
        <strong>{{ store.mcpReadyToolCount }}</strong>
      </a-card>
    </div>

    <a-spin :loading="store.loading" class="settings-spin">
      <div class="knowledge-grid">
        <a-card class="settings-panel knowledge-adapter-panel" :bordered="false">
          <template #title>KnowledgeAdapter</template>
          <div class="adapter-state">
            <div>
              <span>状态</span>
              <strong>{{ adapterStatusLabel(adapterState.status) }}</strong>
            </div>
            <a-tag :color="adapterState.used_knowledge ? 'orange' : 'green'">
              使用知识={{ adapterState.used_knowledge ? '是' : '否' }}
            </a-tag>
          </div>
          <a-descriptions :column="1" size="small" bordered>
            <a-descriptions-item label="适配器">{{ adapterState.adapter_name }}</a-descriptions-item>
            <a-descriptions-item label="提供方">{{ adapterState.provider_type }}</a-descriptions-item>
            <a-descriptions-item label="最近检查">{{ adapterState.last_checked_at ?? '未检查' }}</a-descriptions-item>
            <a-descriptions-item label="备注">{{ adapterState.notes ?? 'V1 空适配器外壳' }}</a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card class="settings-panel" :bordered="false">
          <template #title>V1 非目标</template>
          <div class="non-goal-list">
            <a-tag v-for="goal in store.knowledgeBase?.non_goals ?? []" :key="goal" color="gray">{{ goal }}</a-tag>
          </div>
          <a-empty v-if="(store.knowledgeBase?.non_goals.length ?? 0) === 0" description="暂无边界声明" />
        </a-card>
      </div>

      <div class="knowledge-grid knowledge-main-grid">
        <a-card class="settings-panel" :bordered="false">
          <template #title>ContextArtifact 清单</template>
          <a-table
            :columns="contextColumns"
            :data="contextRows"
            :pagination="false"
            :scroll="{ x: 980 }"
            row-key="id"
            size="small"
          >
            <template #safe="{ record }">
              <a-tag :color="record.safe_to_show ? 'green' : 'orange'">{{ record.safe_to_show ? '安全' : '需复核' }}</a-tag>
            </template>
            <template #prompt="{ record }">
              <a-tag :color="record.allowed_for_prompt ? 'blue' : 'gray'">
                {{ record.allowed_for_prompt ? '允许' : '阻止' }}
              </a-tag>
            </template>
          </a-table>
          <a-empty v-if="!store.loading && contextRows.length === 0" description="暂无 ContextArtifact" />
        </a-card>

        <a-card class="settings-panel" :bordered="false">
          <template #title>MCP-ready ToolDefinition</template>
          <a-table
            :columns="toolColumns"
            :data="toolRows"
            :pagination="false"
            :scroll="{ x: 920 }"
            row-key="id"
            size="small"
          >
            <template #ready="{ record }">
              <a-tag :color="record.is_mcp_ready ? 'green' : 'gray'">
                {{ record.is_mcp_ready ? '就绪' : '仅结构' }}
              </a-tag>
            </template>
            <template #approval="{ record }">
              <a-tag :color="record.approval_required ? 'orange' : 'blue'">
                {{ record.approval_required ? '需审批' : '已列入白名单' }}
              </a-tag>
            </template>
          </a-table>
          <a-empty v-if="!store.loading && toolRows.length === 0" description="暂无 ToolDefinition" />
        </a-card>
      </div>
    </a-spin>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';

import { useExtensionStore } from '../../stores/extension';

const store = useExtensionStore();

const emptyAdapter = {
  adapter_name: 'default',
  status: 'not_configured',
  provider_type: 'none',
  last_checked_at: null,
  notes: null,
  used_knowledge: false,
};

const adapterState = computed(() => store.knowledgeBase?.knowledge_adapter ?? emptyAdapter);

const contextColumns = [
  { title: '标题', dataIndex: 'title', width: 220 },
  { title: '来源', dataIndex: 'source_ref', width: 260 },
  { title: '文件格式', dataIndex: 'mime_type', width: 150 },
  { title: '展示安全', slotName: 'safe', width: 120 },
  { title: '提示词', slotName: 'prompt', width: 110 },
  { title: '使用次数', dataIndex: 'usage_count', width: 110 },
  { title: '最近使用', dataIndex: 'latestUsedAt', width: 180 },
];

const toolColumns = [
  { title: '名称', dataIndex: 'name', width: 220 },
  { title: '类型', dataIndex: 'tool_type', width: 150 },
  { title: '风险', dataIndex: 'risk_level', width: 100 },
  { title: '审批', slotName: 'approval', width: 150 },
  { title: 'MCP', slotName: 'ready', width: 110 },
  { title: '能力', dataIndex: 'capability', width: 190 },
];

const contextRows = computed(() =>
  (store.knowledgeBase?.context_artifacts ?? []).map((artifact) => ({
    ...artifact,
    latestUsedAt: artifact.latest_used_at ?? '未使用',
  })),
);

const toolRows = computed(() =>
  store.toolDefinitions.map((tool) => ({
    ...tool,
    capability: typeof tool.mcp_metadata.capability_name === 'string' ? tool.mcp_metadata.capability_name : '未声明',
  })),
);

function adapterStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    not_configured: '未配置',
    disabled: '已禁用',
    configured_stub: '已配置占位',
  };
  return labels[status] ?? status;
}

onMounted(() => {
  void store.loadExtensionSurface();
});
</script>
