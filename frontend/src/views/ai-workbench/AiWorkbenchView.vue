<template>
  <section class="workbench-page" aria-labelledby="ai-workbench-title">
    <div class="page-heading">
      <p class="eyebrow">Evidence Loop</p>
      <h2 id="ai-workbench-title">AI 工作台</h2>
      <p>从需求评审开始，把 AI 输出、人工决策、执行工件和报告结论串成可信证据链。</p>
    </div>

    <a-card class="health-card" :bordered="false">
      <div class="health-row">
        <div>
          <p class="health-label">后端健康</p>
          <strong>{{ healthLabel }}</strong>
        </div>
        <span class="health-detail">{{ healthDetail }}</span>
      </div>
    </a-card>

    <div class="metric-grid">
      <a-card v-for="metric in metrics" :key="metric.label" class="metric-card" :bordered="false">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
      </a-card>
    </div>

    <div class="flow-grid">
      <a-card v-for="item in flows" :key="item.title" class="flow-card" :bordered="false">
        <template #title>{{ item.title }}</template>
        <p>{{ item.description }}</p>
        <a-button type="primary" disabled>{{ item.action }}</a-button>
      </a-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

import { getBackendHealth } from '../../api/health';

interface MetricCard {
  readonly label: string;
  readonly value: string;
}

interface FlowCard {
  readonly title: string;
  readonly description: string;
  readonly action: string;
}

const metrics: MetricCard[] = [
  { label: '待评审用例', value: '0' },
  { label: '待审批自动化草稿', value: '0' },
  { label: '最近 AI 任务', value: '0' },
  { label: '可追溯工件', value: '0' },
];

const flows: FlowCard[] = [
  {
    title: '需求到用例',
    description: '需求评审、风险项、候选用例和人工评审会在这里形成主线闭环。',
    action: '开始需求评审',
  },
  {
    title: '用例到自动化',
    description: '已评审用例生成自动化草稿，审批后再进入 pytest 或 Playwright 执行。',
    action: '生成自动化草稿',
  },
  {
    title: 'Git 到质量报告',
    description: '本地 diff 生成单测补丁，审批后执行回归并沉淀质量结论。',
    action: '创建 Git 质量分析',
  },
];

const healthLabel = ref('检测中');
const healthDetail = ref('正在检查后端 /health');

onMounted(async () => {
  const result = await getBackendHealth();
  healthLabel.value = result.state;
  healthDetail.value = result.rawText;
});
</script>
