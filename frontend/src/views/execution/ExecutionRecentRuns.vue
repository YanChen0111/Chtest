<template>
  <section class="recent-runs" data-test="recent-runs" aria-labelledby="recent-runs-title">
    <div class="recent-runs-heading">
      <div>
        <p class="eyebrow">本次使用记录</p>
        <h3 id="recent-runs-title">最近运行</h3>
      </div>
      <a-tag v-if="staleCount" color="orange" data-test="recent-runs-stale-state">
        {{ staleCount }} 条待刷新
      </a-tag>
    </div>
    <div v-if="store.recentRuns.length" class="recent-runs-list" data-test="recent-runs-list">
      <article v-for="run in store.recentRuns" :key="run.id" class="recent-run-row">
        <div class="recent-run-copy">
          <strong>{{ run.name }}</strong>
          <span>{{ statusLabel(run.status) }}</span>
          <small :class="{ stale: isStale(run) }">
            {{ run.runner_mode }}<template v-if="isStale(run)"> · 结果可能已过期</template>
          </small>
        </div>
        <a-button
          size="small"
          type="secondary"
          :data-test="`resume-run-${run.id}`"
          :loading="store.loading && store.run?.id === run.id"
          @click="resume(run.id)"
        >
          查看结果
        </a-button>
      </article>
    </div>
    <a-empty v-else description="暂无运行记录" data-test="recent-runs-empty-state" />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';

import { useExecutionStore } from '../../stores/execution';
import type { TestRunRead } from '../../api/execution';

const store = useExecutionStore();

const isStale = (run: TestRunRead) => {
  // TestRunRead intentionally has no timestamp; an unfinished cached run is the
  // only stale signal available to the frontend until the API exposes one.
  return ['pending', 'running', 'execution_pending'].includes(run.status) && store.run?.id !== run.id;
};

const staleCount = computed(() => store.recentRuns.filter(isStale).length);

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: '等待运行',
    execution_pending: '等待运行',
    running: '运行中',
    succeeded: '已通过',
    passed: '已通过',
    failed: '失败',
    error: '异常',
    cancelled: '已取消',
  };
  return labels[status] ?? status;
}

function resume(runId: string) {
  void store.resumeRun(runId);
}

onMounted(() => store.hydrateRecentRuns());
</script>

<style scoped>
.recent-runs {
  display: grid;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e6eb;
}
.recent-runs-heading { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.recent-runs-heading h3, .recent-runs-heading p { margin: 0; }
.recent-runs-list { display: grid; gap: 8px; }
.recent-run-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 12px; border: 1px solid #e5e6eb; border-radius: 6px; }
.recent-run-copy { min-width: 0; display: grid; gap: 2px; }
.recent-run-copy strong, .recent-run-copy span, .recent-run-copy small { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.recent-run-copy span, .recent-run-copy small { color: #86909c; font-size: 12px; }
.recent-run-copy small.stale { color: #d46b08; }
@media (max-width: 600px) { .recent-run-row { align-items: flex-start; } .recent-run-row .arco-btn { flex: 0 0 auto; } }
</style>
