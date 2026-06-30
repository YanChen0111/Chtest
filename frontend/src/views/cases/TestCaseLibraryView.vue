<template>
  <section class="test-case-library-page" aria-labelledby="test-case-library-title">
    <div class="test-case-library-heading">
      <div>
        <p class="eyebrow">Test Case Library</p>
        <h2 id="test-case-library-title">用例库</h2>
        <p>集中查看已经人工评审入库的用例，保留来源、步骤、预期结果和评审状态，作为后续自动化草稿的输入资产。</p>
      </div>
      <a-space>
        <a-tag color="green">已评审用例</a-tag>
        <a-tag color="blue">只读浏览</a-tag>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <div class="library-summary">
      <a-statistic title="已评审用例" :value="store.totalTestCases" />
      <label>
        <span>关键词</span>
        <a-input v-model="keyword" placeholder="按标题或标签筛选当前结果" allow-clear />
      </label>
    </div>

    <div class="library-layout">
      <a-card class="library-panel case-list-panel" :bordered="false">
        <template #title>用例列表</template>
        <a-spin :loading="store.loadingGeneration">
          <a-list v-if="filteredTestCases.length > 0" :data="filteredTestCases" :bordered="false">
            <template #item="{ item }">
              <a-list-item
                class="test-case-list-item"
                :class="{ active: item.id === selectedCase?.id }"
                @click="store.selectedTestCaseId = item.id"
              >
                <a-space direction="vertical" size="mini">
                  <strong>{{ item.title }}</strong>
                  <a-space wrap>
                    <a-tag color="red">{{ item.priority }}</a-tag>
                    <a-tag color="blue">{{ item.test_type }}</a-tag>
                    <a-tag>{{ item.review_status }}</a-tag>
                    <a-tag>{{ item.status }}</a-tag>
                  </a-space>
                </a-space>
              </a-list-item>
            </template>
          </a-list>
          <a-empty v-else-if="!store.loadingGeneration" description="暂无已评审用例" />
        </a-spin>
      </a-card>

      <a-card class="library-panel case-detail-panel" :bordered="false">
        <template #title>用例详情</template>
        <template v-if="selectedCase">
          <a-descriptions :column="2" bordered size="small">
            <a-descriptions-item label="标题">{{ selectedCase.title }}</a-descriptions-item>
            <a-descriptions-item label="状态">{{ selectedCase.status }}</a-descriptions-item>
            <a-descriptions-item label="优先级">{{ selectedCase.priority }}</a-descriptions-item>
            <a-descriptions-item label="类型">{{ selectedCase.test_type }}</a-descriptions-item>
            <a-descriptions-item label="评审状态">{{ selectedCase.review_status }}</a-descriptions-item>
            <a-descriptions-item label="来源">{{ selectedCase.source_type }}</a-descriptions-item>
            <a-descriptions-item label="候选来源" :span="2">
              {{ selectedCase.source_candidate_id ?? '手动或外部来源' }}
            </a-descriptions-item>
            <a-descriptions-item label="前置条件" :span="2">
              {{ selectedCase.precondition ?? '无' }}
            </a-descriptions-item>
            <a-descriptions-item label="标签" :span="2">{{ listText(selectedCase.tags) }}</a-descriptions-item>
          </a-descriptions>

          <div class="case-evidence-grid">
            <section>
              <h3>步骤</h3>
              <ol>
                <li v-for="step in selectedCase.steps" :key="step">{{ step }}</li>
              </ol>
            </section>
            <section>
              <h3>预期结果</h3>
              <ol>
                <li v-for="result in selectedCase.expected_results" :key="result">{{ result }}</li>
              </ol>
            </section>
          </div>
        </template>

        <a-empty v-else description="请选择用例" />
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';

import { useCasesStore } from '../../stores/cases';

const store = useCasesStore();
const keyword = ref('');

const filteredTestCases = computed(() => {
  const value = keyword.value.trim().toLowerCase();
  if (!value) {
    return store.testCases;
  }
  return store.testCases.filter((testCase) => {
    return [testCase.title, testCase.priority, testCase.test_type, testCase.review_status, ...testCase.tags]
      .join(' ')
      .toLowerCase()
      .includes(value);
  });
});

const selectedCase = computed(() => {
  if (filteredTestCases.value.some((testCase) => testCase.id === store.selectedTestCaseId)) {
    return store.selectedTestCase;
  }
  return filteredTestCases.value[0] ?? null;
});

function listText(items: string[]): string {
  return items.length > 0 ? items.join(', ') : '无';
}

onMounted(() => {
  void store.loadTestCases();
});
</script>

<style scoped>
.test-case-library-page {
  display: grid;
  gap: 18px;
}

.test-case-library-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.test-case-library-heading h2,
.test-case-library-heading p {
  margin: 0;
}

.test-case-library-heading h2 {
  font-size: 26px;
}

.test-case-library-heading p:not(.eyebrow) {
  margin-top: 10px;
  max-width: 780px;
  color: #5b6472;
  line-height: 1.7;
}

.library-summary {
  display: grid;
  grid-template-columns: minmax(180px, 240px) minmax(260px, 420px);
  gap: 16px;
  align-items: end;
}

.library-summary label {
  display: grid;
  gap: 7px;
  color: #344054;
  font-weight: 700;
}

.library-layout {
  display: grid;
  grid-template-columns: minmax(340px, 0.85fr) minmax(0, 1.35fr);
  gap: 16px;
}

.library-panel {
  border-radius: 8px;
}

.test-case-list-item {
  cursor: pointer;
  border-radius: 8px;
}

.test-case-list-item.active {
  background: #eff6ff;
}

.case-evidence-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.case-evidence-grid section {
  padding: 14px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.case-evidence-grid h3 {
  margin: 0 0 10px;
  font-size: 16px;
}

.case-evidence-grid ol {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 18px;
}

@media (max-width: 980px) {
  .library-summary,
  .library-layout,
  .case-evidence-grid {
    grid-template-columns: 1fr;
  }
}
</style>
