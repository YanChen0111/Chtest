<template>
  <section class="run-manifest-section" data-test="execution-run-manifest" :aria-labelledby="titleId">
    <div class="section-heading">
      <h3 :id="titleId">执行运行清单</h3>
    </div>
    <a-descriptions class="run-manifest-context" :column="2" bordered size="small">
      <a-descriptions-item label="执行命令" :span="2">{{ run.command }}</a-descriptions-item>
      <a-descriptions-item label="工作目录" :span="2">{{ run.working_directory }}</a-descriptions-item>
      <a-descriptions-item label="运行器模式">{{ runnerModeLabel(run.runner_mode) }}</a-descriptions-item>
      <a-descriptions-item label="运行工作区">{{ run.run_workspace ?? '未记录' }}</a-descriptions-item>
      <a-descriptions-item label="仓库只读策略">
        {{ run.repository_readonly ? '只读挂载' : '非只读' }}
      </a-descriptions-item>
      <a-descriptions-item label="网络策略">
        {{ run.network_enabled ? '允许网络' : '网络关闭' }}
      </a-descriptions-item>
    </a-descriptions>
    <a-table
      class="run-manifest-table"
      :columns="manifestColumns"
      data-test="execution-run-manifest-table"
      :data="tableRows"
      :pagination="false"
      row-key="key"
      size="small"
    >
      <template #state="{ record }">
        <a-tag :color="record.tagColor">{{ record.stateLabel }}</a-tag>
      </template>
      <template #artifact="{ record }">
        <a
          v-if="record.artifactId && record.available"
          :href="artifactDownloadUrl(record.artifactId)"
          target="_blank"
          rel="noreferrer"
          :aria-label="openArtifactLabel(record)"
          :title="openArtifactLabel(record)"
        >
          打开
        </a>
        <span v-else>{{ record.artifactLabel }}</span>
      </template>
    </a-table>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { artifactDownloadUrl, type TestRunRead } from '../../api/execution';
import { runnerModeLabel, type ExecutionRunManifestRow } from './executionRunManifest';

const props = defineProps<{
  run: TestRunRead;
  rows: readonly ExecutionRunManifestRow[];
  titleId: string;
}>();

const manifestColumns = [
  { title: '清单项', dataIndex: 'label' },
  { title: '状态', slotName: 'state' },
  { title: '本地工件', slotName: 'artifact' },
  { title: '说明', dataIndex: 'description' },
];

const tableRows = computed(() => [...props.rows]);

function openArtifactLabel(row: ExecutionRunManifestRow): string {
  return `打开 ${row.label} 工件`;
}
</script>

<style scoped>
.run-manifest-section {
  margin-top: 18px;
}

.section-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.section-heading h3 {
  margin: 0;
  font-size: 16px;
}

.section-heading span {
  color: #86909c;
  font-size: 13px;
}

.run-manifest-context {
  margin-bottom: 12px;
}

.run-manifest-table :deep(.arco-table-cell) {
  vertical-align: top;
}
</style>
