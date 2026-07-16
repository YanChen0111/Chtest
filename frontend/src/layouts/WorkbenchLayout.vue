<template>
  <a-layout class="workbench-layout">
    <a-layout-sider class="workbench-sidebar" :width="248">
      <div class="brand">
        <span class="brand-mark">CT</span>
        <div>
          <strong>Chtest</strong>
          <span>AI 测试证据工作台</span>
        </div>
      </div>

      <nav class="nav-list" aria-label="主导航">
        <RouterLink
          v-for="item in workbench.navigation"
          :key="item.routeName"
          class="nav-item"
          :class="{ active: item.routeName === activeRouteName }"
          :to="{ name: item.routeName }"
        >
          <span>{{ item.label }}</span>
          <a-tag size="small" :color="readinessColor">{{ readinessLabel }}</a-tag>
        </RouterLink>
      </nav>
    </a-layout-sider>

    <a-layout>
      <a-layout-header class="workbench-header">
        <div>
          <p class="header-kicker">本地优先 · 单用户模式</p>
          <h1>{{ currentTitle }}</h1>
        </div>
        <a-space>
          <a-tag color="blue">模拟模型提供方</a-tag>
          <a-tag>中文界面</a-tag>
        </a-space>
      </a-layout-header>

      <a-layout-content class="workbench-content">
        <RouterView />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { RouterLink, RouterView, useRoute } from 'vue-router';

import { useWorkbenchStore } from '../stores';
import { getReadiness, type ReadinessRead } from '../api/readiness';

const route = useRoute();
const workbench = useWorkbenchStore();
const readiness = ref<ReadinessRead | null>(null);
const readinessFailed = ref(false);

const activeRouteName = computed(() => String(route.name ?? 'ai-workbench'));
const readinessLabel = computed(() => {
  if (readiness.value?.status === 'ready') return '就绪';
  if (readiness.value?.status === 'degraded') return '部分可用';
  if (readiness.value?.status === 'not_ready' || readinessFailed.value) return '不可用';
  return '检查中';
});
const readinessColor = computed(() => {
  if (readiness.value?.status === 'ready') return 'green';
  if (readiness.value?.status === 'degraded') return 'orange';
  if (readiness.value?.status === 'not_ready' || readinessFailed.value) return 'red';
  return 'gray';
});
const currentTitle = computed(() => {
  if (typeof route.meta.title === 'string') {
    return route.meta.title;
  }
  const matched = workbench.navigation.find((item) => item.routeName === activeRouteName.value);
  return matched?.label ?? 'AI 工作台';
});

onMounted(async () => {
  try {
    readiness.value = await getReadiness();
  } catch {
    readinessFailed.value = true;
  }
});
</script>
