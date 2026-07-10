<template>
  <section class="project-settings-page" aria-labelledby="project-settings-title">
    <div class="settings-heading">
      <div>
        <p class="eyebrow">项目上下文</p>
        <h2 id="project-settings-title">项目设置</h2>
        <p>维护项目、模块、仓库、环境和测试命令，让后续 AI 任务和执行证据使用同一套上下文。</p>
      </div>
      <a-space>
        <a-tag color="blue">本地项目</a-tag>
        <a-button type="primary" :loading="store.loading" @click="store.loadSettings()">刷新</a-button>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />
    <a-alert v-if="modelConnectionStore.errorMessage" type="error" show-icon>
      {{ modelConnectionStore.errorMessage }}
    </a-alert>
    <a-alert v-if="modelConnectionStore.savedMessage" type="success" show-icon>
      {{ modelConnectionStore.savedMessage }}
    </a-alert>

    <a-card class="settings-panel model-connection-panel" :bordered="false">
      <template #title>&#22823;&#27169;&#22411;&#25509;&#20837;</template>
      <a-spin :loading="modelConnectionStore.loading" class="settings-spin">
        <a-descriptions :column="4" bordered size="small" class="model-connection-status">
          <a-descriptions-item label="&#25509;&#20837;&#29366;&#24577;">
            <a-tag :color="modelConnectionStore.config?.configured ? 'green' : 'orange'">
              {{ modelConnectionStore.config?.configured ? modelConnectionConfiguredText : modelConnectionNotConfiguredText }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="Provider">
            {{ modelConnectionStore.config?.provider ?? modelConnectionUnsetText }}
          </a-descriptions-item>
          <a-descriptions-item label="Model">
            {{ modelConnectionStore.config?.model_name ?? modelConnectionUnsetText }}
          </a-descriptions-item>
          <a-descriptions-item label="Wire API">
            {{ modelConnectionStore.config?.wire_api ?? 'responses' }}
          </a-descriptions-item>
          <a-descriptions-item label="Base URL" :span="2">
            {{ modelConnectionStore.config?.base_url ?? modelConnectionUnsetText }}
          </a-descriptions-item>
          <a-descriptions-item label="API Key" :span="2">
            {{ modelConnectionStore.config?.api_key_hint ?? modelConnectionUnsetText }}
          </a-descriptions-item>
        </a-descriptions>

        <div class="model-connection-form">
          <p class="model-connection-note">
            &#36825;&#37324;&#37197;&#32622; Chtest AI runtime &#20351;&#29992;&#30340;&#27169;&#22411;&#26381;&#21153;&#65292;&#20445;&#23384;&#21518;&#20250;&#34987;&#21518;&#32493; AI &#20219;&#21153;&#30452;&#25509;&#20351;&#29992;&#12290;
          </p>
          <div class="model-connection-fields">
            <label class="settings-field">
              <span>&#26381;&#21153;&#20379;&#24212;&#21830;</span>
              <a-input
                v-model="modelConnectionForm.provider"
                aria-label="Model provider"
                placeholder="OpenAI / OpenAI Compatible / Local Gateway"
                allow-clear
              />
            </label>
            <label class="settings-field">
              <span>&#27169;&#22411;&#21517;&#31216;</span>
              <a-input
                v-model="modelConnectionForm.modelName"
                aria-label="Model name"
                placeholder="gpt-5.5 / gpt-4.1 / your-model-name"
                allow-clear
              />
            </label>
            <label class="settings-field">
              <span>Base URL</span>
              <a-input
                v-model="modelConnectionForm.baseUrl"
                aria-label="Base URL"
                placeholder="https://api.openai.com/v1 or https://your-gateway.example"
                allow-clear
              />
            </label>
            <label class="settings-field">
              <span>&#25509;&#21475;&#21327;&#35758;</span>
              <a-input
                v-model="modelConnectionForm.wireApi"
                aria-label="Wire API"
                placeholder="responses"
                allow-clear
              />
            </label>
            <label class="settings-field">
              <span>API Key</span>
              <a-input-password
                v-model="modelConnectionForm.apiKey"
                aria-label="API Key"
                placeholder="sk-... / gateway token"
                allow-clear
              />
            </label>
          </div>
          <div class="model-connection-import">
            <p class="model-connection-note">
              &#21487;&#36873;&#65306;&#20174;&#24050;&#26377;&#24037;&#20855;&#30340; TOML &#37197;&#32622;&#21644; JSON &#35748;&#35777;&#25991;&#20214;&#20013;&#23548;&#20837;&#12290;
            </p>
            <label class="settings-field">
              <span>&#23548;&#20837;&#37197;&#32622;&#25991;&#26412;</span>
              <a-textarea
                v-model="modelConnectionForm.importConfigText"
                aria-label="Import config text"
                :auto-size="{ minRows: 4, maxRows: 8 }"
                placeholder="model_provider = &quot;OpenAI&quot;&#10;model = &quot;gpt-5.5&quot;&#10;[model_providers.OpenAI]&#10;base_url = &quot;https://api.example.test&quot;&#10;wire_api = &quot;responses&quot;"
                allow-clear
              />
            </label>
            <label class="settings-field">
              <span>&#23548;&#20837;&#35748;&#35777; JSON</span>
              <a-textarea
                v-model="modelConnectionForm.importAuthJson"
                aria-label="Import auth JSON"
                :auto-size="{ minRows: 3, maxRows: 6 }"
                placeholder="{&quot;OPENAI_API_KEY&quot;:&quot;sk-...&quot;}"
                allow-clear
              />
            </label>
          </div>
          <div class="model-connection-actions">
            <a-space>
              <a-button :loading="modelConnectionStore.loading" @click="modelConnectionStore.loadConfig()">
                &#21047;&#26032;&#37197;&#32622;
              </a-button>
              <a-button :loading="modelConnectionStore.testing" @click="testModelConnection">
                &#27979;&#35797;&#36830;&#25509;
              </a-button>
              <a-button type="primary" :loading="modelConnectionStore.saving" @click="saveModelConnection">
                &#20445;&#23384;&#37197;&#32622;
              </a-button>
            </a-space>
          </div>
          <a-alert
            v-if="modelConnectionStore.testResult"
            :type="modelConnectionStore.testResult.ok ? 'success' : 'warning'"
            show-icon
          >
            <div class="model-connection-test-feedback">
              <strong>
                {{ modelConnectionStore.testResult.ok ? modelConnectionTestSucceededText : modelConnectionTestFailedText }}
              </strong>
              <span>{{ modelConnectionStore.testResult.message }}</span>
              <div class="model-connection-test-grid">
                <span>目标</span>
                <span>
                  {{ modelConnectionStore.testResult.provider ?? modelConnectionUnsetText }} /
                  {{ modelConnectionStore.testResult.model_name ?? modelConnectionUnsetText }}
                </span>
                <span>Base URL</span>
                <span>{{ modelConnectionStore.testResult.base_url ?? modelConnectionUnsetText }}</span>
                <template v-if="modelConnectionStore.testResult.error_code">
                  <span>错误码</span>
                  <code>{{ modelConnectionStore.testResult.error_code }}</code>
                </template>
                <template v-if="modelConnectionStore.testResult.http_status">
                  <span>HTTP</span>
                  <span>{{ modelConnectionStore.testResult.http_status }}</span>
                </template>
                <template v-if="modelConnectionStore.testResult.diagnostic">
                  <span>诊断</span>
                  <span>{{ modelConnectionStore.testResult.diagnostic }}</span>
                </template>
              </div>
              <p v-if="modelConnectionStore.testResult.suggestion" class="model-connection-test-suggestion">
                建议：{{ modelConnectionStore.testResult.suggestion }}
              </p>
            </div>
          </a-alert>
        </div>
      </a-spin>
    </a-card>

    <a-spin :loading="store.loading" class="settings-spin">
      <template v-if="store.settings">
        <a-card class="settings-panel" :bordered="false">
          <template #title>项目概览</template>
          <a-descriptions :column="4" bordered size="small">
            <a-descriptions-item label="项目名称">{{ store.settings.project.name }}</a-descriptions-item>
            <a-descriptions-item label="默认语言">
              {{ store.settings.project.default_language ?? '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="默认测试类型">
              {{ store.settings.project.default_test_type ?? '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="项目 ID">{{ store.settings.project.id }}</a-descriptions-item>
          </a-descriptions>
        </a-card>

        <div class="settings-grid">
          <a-card class="settings-panel" :bordered="false">
            <template #title>模块树</template>
            <a-table :columns="moduleColumns" :data="store.settings.modules" :pagination="false" size="small" row-key="id" />
          </a-card>

          <a-card class="settings-panel" :bordered="false">
            <template #title>仓库</template>
            <a-table
              :columns="repositoryColumns"
              :data="store.settings.repositories"
              :pagination="false"
              size="small"
              row-key="id"
            />
          </a-card>

          <a-card class="settings-panel" :bordered="false">
            <template #title>环境变量</template>
            <a-table
              :columns="environmentColumns"
              :data="environmentRows"
              :pagination="false"
              size="small"
              row-key="id"
            />
          </a-card>

          <a-card class="settings-panel" :bordered="false">
            <template #title>测试命令</template>
            <a-table
              :columns="testCommandColumns"
              :data="store.settings.test_commands"
              :pagination="false"
              size="small"
              row-key="id"
            />
          </a-card>
        </div>
      </template>

      <a-empty v-else-if="!store.loading" description="暂无项目设置数据" />
    </a-spin>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, watch } from 'vue';

import type { ModelConnectionConfigUpdate } from '../../api/modelConnection';
import { useModelConnectionStore } from '../../stores/modelConnection';
import { useProjectSettingsStore } from '../../stores/projectSettings';

const store = useProjectSettingsStore();
const modelConnectionStore = useModelConnectionStore();

const modelConnectionForm = reactive({
  provider: '',
  modelName: '',
  baseUrl: '',
  wireApi: 'responses',
  importConfigText: '',
  importAuthJson: '',
  apiKey: '',
});

const modelConnectionConfiguredText = '\u5df2\u914d\u7f6e';
const modelConnectionNotConfiguredText = '\u672a\u914d\u7f6e';
const modelConnectionUnsetText = '\u672a\u8bbe\u7f6e';
const modelConnectionTestSucceededText = '\u6a21\u578b\u8fde\u63a5\u6d4b\u8bd5\u901a\u8fc7';
const modelConnectionTestFailedText = '\u6a21\u578b\u8fde\u63a5\u6d4b\u8bd5\u672a\u901a\u8fc7';

const moduleColumns = [
  { title: '模块', dataIndex: 'name' },
  { title: '路径', dataIndex: 'path' },
  { title: '层级', dataIndex: 'level' },
  { title: '状态', dataIndex: 'status' },
];

const repositoryColumns = [
  { title: '仓库', dataIndex: 'name' },
  { title: '本地路径', dataIndex: 'local_path' },
  { title: '默认分支', dataIndex: 'default_base_branch' },
  { title: '语言', dataIndex: 'language_hint' },
];

const environmentColumns = [
  { title: '环境', dataIndex: 'name' },
  { title: '变量键', dataIndex: 'variableKeys' },
  { title: '状态', dataIndex: 'status' },
];

const testCommandColumns = [
  { title: '命令名', dataIndex: 'name' },
  { title: '类型', dataIndex: 'command_type' },
  { title: '命令', dataIndex: 'command' },
  { title: '超时', dataIndex: 'timeout_seconds' },
];

const environmentRows = computed(() =>
  (store.settings?.environments ?? []).map((environment) => ({
    ...environment,
    variableKeys: Object.keys(environment.variables_json).join(', ') || '无变量',
  })),
);

const emptyToNull = (value: string): string | null => {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
};

const modelConnectionPayload = (): ModelConnectionConfigUpdate => ({
  provider: emptyToNull(modelConnectionForm.provider),
  model_name: emptyToNull(modelConnectionForm.modelName),
  base_url: emptyToNull(modelConnectionForm.baseUrl),
  wire_api: emptyToNull(modelConnectionForm.wireApi),
  import_config_text: emptyToNull(modelConnectionForm.importConfigText),
  import_auth_json: emptyToNull(modelConnectionForm.importAuthJson),
  api_key: emptyToNull(modelConnectionForm.apiKey),
});

const saveModelConnection = async () => {
  await modelConnectionStore.saveConfig(modelConnectionPayload());
  modelConnectionForm.importAuthJson = '';
  modelConnectionForm.apiKey = '';
};

const testModelConnection = async () => {
  await modelConnectionStore.testConfig(modelConnectionPayload());
};

watch(
  () => modelConnectionStore.config,
  (config) => {
    if (!config?.configured) {
      return;
    }
    modelConnectionForm.provider = config.provider ?? '';
    modelConnectionForm.modelName = config.model_name ?? '';
    modelConnectionForm.baseUrl = config.base_url ?? '';
    modelConnectionForm.wireApi = config.wire_api || 'responses';
  },
);

onMounted(() => {
  void store.loadSettings();
  void modelConnectionStore.loadConfig();
});
</script>

<style scoped>
.model-connection-status {
  margin-bottom: 16px;
  overflow-wrap: anywhere;
}

.model-connection-form {
  display: grid;
  gap: 16px;
}

.model-connection-fields {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.model-connection-import {
  border-top: 1px solid var(--color-border-2);
  display: grid;
  gap: 16px;
  padding-top: 16px;
}

.model-connection-note {
  color: var(--color-text-2);
  margin: 0;
}

.settings-field {
  display: grid;
  gap: 8px;
  font-weight: 600;
}

.model-connection-actions {
  display: flex;
  justify-content: flex-end;
}

.model-connection-test-feedback {
  display: grid;
  gap: 8px;
  overflow-wrap: anywhere;
}

.model-connection-test-grid {
  display: grid;
  gap: 6px 12px;
  grid-template-columns: minmax(64px, max-content) minmax(0, 1fr);
}

.model-connection-test-grid > span:nth-child(odd) {
  color: var(--color-text-2);
}

.model-connection-test-suggestion {
  margin: 0;
}
</style>
