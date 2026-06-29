<template>
  <section class="prompt-skill-page" aria-labelledby="prompt-skill-title">
    <div class="settings-heading">
      <div>
        <p class="eyebrow">PromptVersion / SkillVersion</p>
        <h2 id="prompt-skill-title">Prompt / Skill 中心</h2>
        <p>只读查看内置 Prompt 与 Skill 版本、hash、适用 Agent 和契约元数据，为后续 AI 任务追踪提供依据。</p>
      </div>
      <a-space>
        <a-tag color="blue">只读注册表</a-tag>
        <a-button type="primary" :loading="store.loading" @click="store.loadRegistry()">刷新</a-button>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <div class="prompt-skill-metrics">
      <a-card class="settings-panel" :bordered="false">
        <span>PromptVersion</span>
        <strong>{{ store.prompts.length }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>SkillVersion</span>
        <strong>{{ store.skills.length }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>Active Prompt</span>
        <strong>{{ store.activePromptCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>适用 Agent</span>
        <strong>{{ store.applicableAgentCount }}</strong>
      </a-card>
    </div>

    <a-spin :loading="store.loading" class="settings-spin">
      <div class="prompt-skill-grid">
        <a-card class="settings-panel" :bordered="false">
          <template #title>PromptVersion</template>
          <a-table :columns="promptColumns" :data="promptRows" :pagination="false" row-key="id" size="small">
            <template #status="{ record }">
              <a-tag :color="record.status === 'active' ? 'green' : 'gray'">{{ record.status }}</a-tag>
            </template>
          </a-table>
          <a-empty v-if="!store.loading && store.prompts.length === 0" description="暂无 PromptVersion" />
        </a-card>

        <a-card class="settings-panel" :bordered="false">
          <template #title>SkillVersion</template>
          <a-table :columns="skillColumns" :data="skillRows" :pagination="false" row-key="id" size="small">
            <template #status="{ record }">
              <a-tag :color="record.status === 'active' ? 'green' : 'gray'">{{ record.status }}</a-tag>
            </template>
          </a-table>
          <a-empty v-if="!store.loading && store.skills.length === 0" description="暂无 SkillVersion" />
        </a-card>
      </div>
    </a-spin>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';

import { usePromptSkillStore } from '../../stores/promptSkill';

const store = usePromptSkillStore();

const promptColumns = [
  { title: '名称', dataIndex: 'name' },
  { title: '版本', dataIndex: 'version' },
  { title: 'Agent', dataIndex: 'agent_name' },
  { title: 'Hash', dataIndex: 'hash' },
  { title: '状态', slotName: 'status' },
  { title: '输入契约', dataIndex: 'inputContract' },
  { title: '输出契约', dataIndex: 'outputContract' },
];

const skillColumns = [
  { title: '名称', dataIndex: 'name' },
  { title: '版本', dataIndex: 'version' },
  { title: '适用 Agent', dataIndex: 'applicableAgents' },
  { title: 'Hash', dataIndex: 'hash' },
  { title: '状态', slotName: 'status' },
  { title: '质量门禁', dataIndex: 'qualityGates' },
  { title: '工具权限', dataIndex: 'toolPermissions' },
];

const promptRows = computed(() =>
  store.prompts.map((prompt) => ({
    ...prompt,
    inputContract: requiredText(prompt.input_schema_json),
    outputContract: requiredText(prompt.output_schema_json),
  })),
);

const skillRows = computed(() =>
  store.skills.map((skill) => ({
    ...skill,
    applicableAgents: skill.applicable_agents.join(', '),
    qualityGates: skill.quality_gates_json.join(' / '),
    toolPermissions: skill.tool_permissions_json.join(' / '),
  })),
);

function requiredText(schema: Record<string, unknown>): string {
  const required = schema.required;
  if (!Array.isArray(required) || required.length === 0) {
    return 'required: none';
  }
  return `required: ${required.join(', ')}`;
}

onMounted(() => {
  void store.loadRegistry();
});
</script>
