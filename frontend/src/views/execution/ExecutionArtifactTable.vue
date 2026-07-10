<template>
  <section class="execution-artifact-section" :aria-labelledby="titleId">
    <h3 :id="titleId">{{ title }}</h3>
    <a-table
      :columns="artifactColumns"
      :data="tableRows"
      :pagination="false"
      row-key="id"
      size="small"
    >
      <template #action="{ record }">
        <a
          :href="artifactDownloadUrl(record.id)"
          target="_blank"
          rel="noreferrer"
          :aria-label="openLabel(record)"
          :title="openLabel(record)"
        >
          打开
        </a>
      </template>
    </a-table>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { artifactDownloadUrl, type TestRunArtifactRead } from '../../api/execution';

const props = defineProps<{
  title: string;
  titleId: string;
  artifacts: readonly TestRunArtifactRead[];
}>();

const artifactColumns = [
  { title: '类型', dataIndex: 'artifact_type' },
  { title: '路径', dataIndex: 'file_path' },
  { title: 'MIME', dataIndex: 'mime_type' },
  { title: '大小', dataIndex: 'size_bytes' },
  { title: 'Artifact', slotName: 'action' },
];

const tableRows = computed(() => [...props.artifacts]);

function openLabel(record: TestRunArtifactRead): string {
  return `打开 ${record.artifact_type} 工件`;
}
</script>

<style scoped>
.execution-artifact-section {
  margin-top: 18px;
}

.execution-artifact-section h3 {
  margin: 0 0 10px;
  font-size: 16px;
}
</style>
