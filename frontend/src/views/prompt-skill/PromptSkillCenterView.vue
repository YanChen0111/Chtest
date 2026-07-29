<template>
  <section class="prompt-skill-page" aria-labelledby="prompt-skill-title">
    <div class="settings-heading">
      <div>
        <p class="eyebrow">PromptVersion / SkillVersion</p>
        <h2 id="prompt-skill-title">Prompt / Skill 中心</h2>
        <p>选择评审或生成用例时使用的 Prompt 与 Skill，展开即可查看输入和质量要求。</p>
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
        <span>启用 Prompt</span>
        <strong>{{ store.activePromptCount }}</strong>
      </a-card>
      <a-card class="settings-panel" :bordered="false">
        <span>适用 Agent</span>
        <strong>{{ store.applicableAgentCount }}</strong>
      </a-card>
    </div>

    <a-spin :loading="store.loading" class="settings-spin">
      <div class="registry-switcher">
        <a-radio-group v-model="activeTab" type="button">
          <a-radio value="skills">Skill 选择</a-radio>
          <a-radio value="prompts">Prompt 注册表</a-radio>
        </a-radio-group>
        <span>{{ activeTab === 'skills' ? '先选择当前 Agent 要遵循的测试技能' : '查看 AI 任务使用的 Prompt 契约' }}</span>
      </div>

      <a-card v-if="activeTab === 'skills'" class="settings-panel skill-selection-panel" :bordered="false">
        <template #title>
          <span class="panel-title-with-note"><b>选择 Skill</b><small>例如展开“需求评审 Skill”，确认质量门禁后即可用于对应 Agent</small></span>
        </template>
        <a-collapse v-if="store.skills.length" v-model:active-key="expandedSkillKeys" accordion>
          <a-collapse-item v-for="skill in store.skills" :key="skill.id" :name="skill.id">
            <template #header>
              <div class="skill-row-header">
                <div>
                  <strong>{{ skill.name }}</strong>
                  <small>{{ skill.version }} · {{ skill.applicable_agents.join('、') || '未声明 Agent' }}</small>
                </div>
                <a-tag :color="skill.status === 'active' ? 'green' : 'gray'">{{ statusLabel(skill.status) }}</a-tag>
              </div>
            </template>
            <div class="skill-expanded-content">
              <div class="skill-chip-group">
                <span>版本</span>
                <a-tag color="gray">{{ skill.version }}</a-tag>
              </div>
              <div class="skill-chip-group">
                <span>质量门禁</span>
                <a-tag v-for="gate in skill.quality_gates_json" :key="gate" color="blue">{{ gate }}</a-tag>
                <em v-if="!skill.quality_gates_json.length">未声明</em>
              </div>
              <div class="skill-chip-group">
                <span>禁止动作</span>
                <a-tag v-for="action in skill.forbidden_actions_json" :key="action" color="orange">{{ action }}</a-tag>
                <em v-if="!skill.forbidden_actions_json.length">未声明</em>
              </div>
              <div class="skill-chip-group">
                <span>工具权限</span>
                <a-tag v-for="tool in skill.tool_permissions_json" :key="tool" color="gray">{{ tool }}</a-tag>
                <em v-if="!skill.tool_permissions_json.length">无</em>
              </div>
              <div v-if="linkedPrompts(skill).length" class="skill-chip-group">
                <span>关联 Prompt</span>
                <a-tag v-for="prompt in linkedPrompts(skill)" :key="prompt.id" color="purple">
                  {{ prompt.name }} · {{ requiredText(prompt.input_schema_json) }}
                </a-tag>
              </div>
              <a-button size="small" type="primary" @click="openSkill(skill)">查看完整 Skill</a-button>
            </div>
          </a-collapse-item>
        </a-collapse>
        <a-empty v-else description="暂无 SkillVersion" />
      </a-card>

      <a-card v-else class="settings-panel prompt-registry-panel" :bordered="false">
        <template #title>
          <span class="panel-title-with-note"><b>选择 Prompt</b><small>展开 Prompt 查看输入字段、输出契约和完整内容</small></span>
        </template>
        <a-collapse v-if="store.prompts.length" v-model:active-key="expandedPromptKeys" accordion>
          <a-collapse-item v-for="prompt in store.prompts" :key="prompt.id" :name="prompt.id">
            <template #header>
              <div class="skill-row-header">
                <div>
                  <strong>{{ prompt.name }}</strong>
                  <small>{{ prompt.version }} · {{ prompt.agent_name }}</small>
                </div>
                <a-tag :color="prompt.status === 'active' ? 'green' : 'gray'">{{ statusLabel(prompt.status) }}</a-tag>
              </div>
            </template>
            <div class="skill-expanded-content">
              <div class="skill-chip-group">
                <span>版本</span>
                <a-tag color="gray">{{ prompt.version }}</a-tag>
              </div>
              <div class="skill-chip-group">
                <span>输入字段</span>
                <a-tag color="blue">{{ requiredText(prompt.input_schema_json) }}</a-tag>
              </div>
              <div class="skill-chip-group">
                <span>输出契约</span>
                <a-tag color="purple">{{ requiredText(prompt.output_schema_json) }}</a-tag>
              </div>
              <a-button size="small" type="primary" @click="openPrompt(prompt)">查看完整 Prompt</a-button>
            </div>
          </a-collapse-item>
        </a-collapse>
        <a-empty v-if="!store.loading && store.prompts.length === 0" description="暂无 PromptVersion" />
      </a-card>
    </a-spin>

    <a-drawer v-model:visible="detailVisible" :width="560" unmount-on-close>
      <template #title>
        {{ selectedPrompt ? 'Prompt 详情' : 'Skill 详情' }}
      </template>
      <template v-if="selectedPrompt">
        <div class="prompt-detail-header">
          <div>
            <h3>{{ selectedPrompt.name }}</h3>
            <p>{{ selectedPrompt.agent_name }} · {{ selectedPrompt.version }}</p>
          </div>
          <a-tag :color="selectedPrompt.status === 'active' ? 'green' : 'gray'">{{ statusLabel(selectedPrompt.status) }}</a-tag>
        </div>
        <a-descriptions :column="1" bordered size="small">
          <a-descriptions-item label="输入必填项">{{ requiredText(selectedPrompt.input_schema_json) }}</a-descriptions-item>
          <a-descriptions-item label="输出契约">{{ requiredText(selectedPrompt.output_schema_json) }}</a-descriptions-item>
        </a-descriptions>
        <h4>Prompt 内容</h4>
        <pre class="prompt-detail-content">{{ selectedPrompt.content }}</pre>
      </template>
      <template v-else-if="selectedSkill">
        <div class="prompt-detail-header">
          <div>
            <h3>{{ selectedSkill.name }}</h3>
            <p>{{ selectedSkill.version }}</p>
          </div>
          <a-tag :color="selectedSkill.status === 'active' ? 'green' : 'gray'">{{ statusLabel(selectedSkill.status) }}</a-tag>
        </div>
        <a-descriptions :column="1" bordered size="small">
          <a-descriptions-item label="适用 Agent">{{ selectedSkill.applicable_agents.join('、') || '未声明' }}</a-descriptions-item>
          <a-descriptions-item label="质量门禁">{{ selectedSkill.quality_gates_json.join('、') || '未声明' }}</a-descriptions-item>
          <a-descriptions-item label="工具权限">{{ selectedSkill.tool_permissions_json.join('、') || '无' }}</a-descriptions-item>
          <a-descriptions-item label="禁止动作">{{ selectedSkill.forbidden_actions_json.join('、') || '未声明' }}</a-descriptions-item>
        </a-descriptions>
        <h4>Skill 内容</h4>
        <pre class="prompt-detail-content">{{ selectedSkill.content }}</pre>
      </template>
    </a-drawer>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import type { PromptVersion, SkillVersion } from '../../api/promptSkill';

import { usePromptSkillStore } from '../../stores/promptSkill';

const store = usePromptSkillStore();
const activeTab = ref<'skills' | 'prompts'>('skills');
const expandedSkillKeys = ref<string[]>([]);
const expandedPromptKeys = ref<string[]>([]);
const detailVisible = ref(false);
const selectedPrompt = ref<PromptVersion | null>(null);
const selectedSkill = ref<SkillVersion | null>(null);

function requiredText(schema: Record<string, unknown>): string {
  const required = schema.required;
  if (!Array.isArray(required) || required.length === 0) {
    return '必填：无';
  }
  return `必填：${required.join(', ')}`;
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    active: '启用',
    inactive: '停用',
    deprecated: '已废弃',
  };
  return labels[status] ?? status;
}

function linkedPrompts(skill: SkillVersion): PromptVersion[] {
  return store.prompts
    .filter((prompt) => skill.applicable_agents.includes(prompt.agent_name));
}

function openPrompt(record: any) {
  selectedPrompt.value = store.prompts.find((prompt) => prompt.id === record?.id) ?? null;
  selectedSkill.value = null;
  detailVisible.value = Boolean(selectedPrompt.value);
}

function openSkill(record: any) {
  selectedPrompt.value = null;
  selectedSkill.value = store.skills.find((skill) => skill.id === record?.id) ?? null;
  detailVisible.value = Boolean(selectedSkill.value);
}

onMounted(() => {
  void store.loadRegistry().then(() => {
    const requirementSkill = store.skills.find((skill) => /requirement[-_ ]review/i.test(skill.name));
    if (requirementSkill) expandedSkillKeys.value = [requirementSkill.id];
    const requirementPrompt = store.prompts.find((prompt) => /requirement[-_ ]review/i.test(prompt.name));
    if (requirementPrompt) expandedPromptKeys.value = [requirementPrompt.id];
  });
});
</script>

<style scoped>
.registry-switcher {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 14px;
  padding: 10px 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #ffffff;
  color: #667085;
  font-size: 12px;
}

.panel-title-with-note {
  display: grid;
  gap: 3px;
}

.panel-title-with-note small {
  color: #98a2b3;
  font-size: 11px;
  font-weight: 400;
}

.skill-row-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 14px;
}

.skill-row-header > div {
  display: grid;
  gap: 3px;
  min-width: 0;
}

.skill-row-header small {
  overflow: hidden;
  color: #667085;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.skill-expanded-content {
  display: grid;
  gap: 12px;
  padding: 4px 8px 10px 34px;
}

.skill-chip-group {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 6px;
}

.skill-chip-group > span {
  width: 64px;
  padding-top: 3px;
  color: #667085;
  font-size: 12px;
}

.skill-chip-group em {
  padding-top: 3px;
  color: #98a2b3;
  font-size: 12px;
  font-style: normal;
}

.prompt-detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.prompt-detail-header h3,
.prompt-detail-header p {
  margin: 0;
}

.prompt-detail-header p {
  margin-top: 4px;
  color: #667085;
  font-size: 12px;
}

.prompt-detail-content {
  max-height: 420px;
  overflow: auto;
  margin: 0;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #344054;
  background: #f8fafc;
  font: 12px/1.65 ui-monospace, SFMono-Regular, Consolas, monospace;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

h4 {
  margin: 18px 0 8px;
  font-size: 14px;
}

@media (max-width: 720px) {
  .registry-switcher {
    align-items: flex-start;
    flex-direction: column;
  }

  .skill-expanded-content {
    padding-left: 8px;
  }
}
</style>
