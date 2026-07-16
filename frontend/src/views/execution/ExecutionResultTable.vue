<template>
  <section class="execution-result-table-section" data-test="execution-results" :aria-labelledby="titleId">
    <h3 :id="titleId">{{ title }}</h3>
    <a-table
      data-test="execution-result-table"
      :columns="tableColumns"
      :data="tableRows"
      :pagination="false"
      row-key="id"
      size="small"
    />
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type TableColumn = Record<string, unknown>;
type TableRow = Record<string, unknown>;

const props = defineProps<{
  title: string;
  titleId: string;
  columns: readonly TableColumn[];
  rows: readonly TableRow[];
}>();

const tableColumns = computed(() => [...props.columns]);
const tableRows = computed(() => [...props.rows]);
</script>

<style scoped>
.execution-result-table-section {
  margin-top: 18px;
}

.execution-result-table-section h3 {
  margin: 0 0 10px;
  font-size: 16px;
}
</style>
