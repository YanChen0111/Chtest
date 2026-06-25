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
          :to="item.routeName === 'ai-workbench' ? { name: item.routeName } : routeFallback"
        >
          <span>{{ item.label }}</span>
          <a-tag size="small" :color="item.status === '就绪' ? 'green' : 'gray'">{{ item.status }}</a-tag>
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
          <a-tag color="blue">Mock Provider</a-tag>
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
import { computed } from 'vue';
import { RouterLink, RouterView, useRoute } from 'vue-router';

import { useWorkbenchStore } from '../stores';

const route = useRoute();
const workbench = useWorkbenchStore();
const routeFallback = { name: 'ai-workbench' };

const activeRouteName = computed(() => String(route.name ?? 'ai-workbench'));
const currentTitle = computed(() => {
  const matched = workbench.navigation.find((item) => item.routeName === activeRouteName.value);
  return matched?.label ?? 'AI 工作台';
});
</script>
