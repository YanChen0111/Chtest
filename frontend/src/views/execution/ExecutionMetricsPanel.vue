<template>
  <div class="execution-metrics-panel" aria-label="执行指标">
    <div v-for="item in tableItems" :key="item.label" class="metric-tile">
      <span>{{ item.label }}</span>
      <strong>{{ item.value }}</strong>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

export interface ExecutionMetricItem {
  readonly label: string;
  readonly value: string | number;
}

const props = defineProps<{
  items: readonly ExecutionMetricItem[];
}>();

const tableItems = computed(() => [...props.items]);
</script>

<style scoped>
.execution-metrics-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(104px, 1fr));
  gap: 10px;
  margin-top: 16px;
}

.metric-tile {
  min-height: 72px;
  padding: 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.metric-tile span,
.metric-tile strong {
  display: block;
}

.metric-tile span {
  color: #64748b;
}

.metric-tile strong {
  margin-top: 8px;
  color: #0f172a;
  font-size: 22px;
}

@media (max-width: 720px) {
  .execution-metrics-panel {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
