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
import { computed, onMounted } from 'vue';

import { useProjectSettingsStore } from '../../stores/projectSettings';

const store = useProjectSettingsStore();

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

onMounted(() => {
  void store.loadSettings();
});
</script>
