<template>
  <a-layout class="workbench-layout">
    <a-layout-sider class="workbench-sidebar desktop-sidebar" :width="240">
      <div class="sidebar-inner">
        <RouterLink class="brand" :to="{ name: 'ai-workbench' }" aria-label="返回 AI 工作台">
          <span class="brand-mark" aria-hidden="true">CT</span>
          <span class="brand-copy">
            <strong>Chtest</strong>
            <small>AI 测试证据工作台</small>
          </span>
        </RouterLink>

        <WorkbenchNavigation @navigate="closeMobileNavigation" />

        <div class="sidebar-status" aria-live="polite">
          <span class="status-dot" :class="`status-dot--${readinessTone}`" aria-hidden="true"></span>
          <span class="sidebar-status__copy">
            <strong>{{ readinessLabel }}</strong>
            <small>后端与依赖服务</small>
          </span>
          <a-tooltip content="重新检查服务状态">
            <a-button
              class="icon-button"
              type="text"
              shape="circle"
              aria-label="重新检查服务状态"
              :loading="readinessLoading"
              @click="refreshReadiness"
            >
              <template #icon><IconRefresh /></template>
            </a-button>
          </a-tooltip>
        </div>
      </div>
    </a-layout-sider>

    <a-layout class="workbench-main">
      <a-layout-header class="workbench-header">
        <div class="header-leading">
          <a-tooltip content="打开导航">
            <a-button
              class="icon-button mobile-menu-button"
              type="text"
              shape="circle"
              aria-label="打开导航"
              @click="mobileNavOpen = true"
            >
              <template #icon><IconMenu /></template>
            </a-button>
          </a-tooltip>
          <div class="header-title">
            <p class="header-kicker">{{ currentSection }} / {{ currentTitle }}</p>
            <h1>{{ currentTitle }}</h1>
          </div>
        </div>

        <div class="header-actions">
          <span class="header-project">
            <IconSafe aria-hidden="true" />
            本地证据链
          </span>
          <span class="header-readiness" :title="readinessLabel">
            <span class="status-dot" :class="`status-dot--${readinessTone}`" aria-hidden="true"></span>
            {{ readinessShortLabel }}
          </span>
        </div>
      </a-layout-header>

      <a-layout-content class="workbench-content">
        <RouterView />
      </a-layout-content>
    </a-layout>

    <a-drawer
      v-model:visible="mobileNavOpen"
      class="mobile-navigation-drawer"
      placement="left"
      :width="304"
      :footer="false"
      unmount-on-close
    >
      <template #title>
        <RouterLink class="brand brand--drawer" :to="{ name: 'ai-workbench' }" @click="closeMobileNavigation">
          <span class="brand-mark" aria-hidden="true">CT</span>
          <span class="brand-copy">
            <strong>Chtest</strong>
            <small>AI 测试证据工作台</small>
          </span>
        </RouterLink>
      </template>
      <WorkbenchNavigation @navigate="closeMobileNavigation" />
      <div class="mobile-status-strip" aria-live="polite">
        <span class="status-dot" :class="`status-dot--${readinessTone}`" aria-hidden="true"></span>
        <span>{{ readinessLabel }}</span>
      </div>
    </a-drawer>
  </a-layout>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, ref, watch, type Component } from 'vue';
import { RouterLink, RouterView, useRoute } from 'vue-router';
import {
  IconArchive,
  IconBook,
  IconBranch,
  IconBug,
  IconDashboard,
  IconExperiment,
  IconFile,
  IconMenu,
  IconRefresh,
  IconRobot,
  IconSafe,
  IconSettings,
  IconStorage,
  IconThunderbolt,
} from '@arco-design/web-vue/es/icon';

import { getReadiness, type ReadinessRead } from '../api/readiness';
import { useWorkbenchStore, type NavigationItem } from '../stores';

interface NavigationGroup {
  readonly label: string;
  readonly routeNames: readonly string[];
}

const navigationGroups: readonly NavigationGroup[] = [
  {
    label: '设计与评审',
    routeNames: ['ai-workbench', 'requirement-review', 'case-generation-review', 'test-case-library'],
  },
  {
    label: '自动化与证据',
    routeNames: ['automation-draft-center', 'execution-center', 'cicd-quality-center', 'report-center'],
  },
  {
    label: '知识与配置',
    routeNames: ['knowledge-base', 'prompt-skill-center', 'project-settings'],
  },
] as const;

const routeIcons: Record<string, Component> = {
  'ai-workbench': IconDashboard,
  'requirement-review': IconFile,
  'case-generation-review': IconExperiment,
  'test-case-library': IconBook,
  'automation-draft-center': IconRobot,
  'execution-center': IconThunderbolt,
  'cicd-quality-center': IconBranch,
  'report-center': IconBug,
  'knowledge-base': IconStorage,
  'prompt-skill-center': IconArchive,
  'project-settings': IconSettings,
};

const WorkbenchNavigation = defineComponent({
  name: 'WorkbenchNavigation',
  emits: ['navigate'],
  setup(_, { emit }) {
    const route = useRoute();
    const workbench = useWorkbenchStore();
    const groupedNavigation = computed(() => navigationGroups.map((group) => ({
      ...group,
      items: group.routeNames
        .map((routeName) => workbench.navigation.find((item) => item.routeName === routeName))
        .filter((item): item is NavigationItem => Boolean(item)),
    })));

    return () => h('nav', { class: 'nav-list', 'aria-label': '主导航' }, groupedNavigation.value.map((group) =>
      h('section', { class: 'nav-group', key: group.label }, [
        h('p', { class: 'nav-group-label' }, group.label),
        ...group.items.map((item) => h(RouterLink, {
          class: ['nav-item', { active: item.routeName === String(route.name ?? 'ai-workbench') }],
          to: { name: item.routeName },
          'aria-current': item.routeName === String(route.name ?? 'ai-workbench') ? 'page' : undefined,
          onClick: () => emit('navigate'),
        }, {
          default: () => [
            h(routeIcons[item.routeName] ?? IconFile, { class: 'nav-item__icon', 'aria-hidden': 'true' }),
            h('span', { class: 'nav-item__label' }, item.label),
          ],
        })),
      ]),
    ));
  },
});

const route = useRoute();
const workbench = useWorkbenchStore();
const readiness = ref<ReadinessRead | null>(null);
const readinessFailed = ref(false);
const readinessLoading = ref(false);
const mobileNavOpen = ref(false);

const activeRouteName = computed(() => String(route.name ?? 'ai-workbench'));
const currentTitle = computed(() => {
  if (typeof route.meta.title === 'string') return route.meta.title;
  return workbench.navigation.find((item) => item.routeName === activeRouteName.value)?.label ?? 'AI 工作台';
});
const currentSection = computed(() => (
  navigationGroups.find((group) => group.routeNames.includes(activeRouteName.value))?.label ?? '工作台'
));
const readinessLabel = computed(() => {
  if (readiness.value?.status === 'ready') return '系统就绪';
  if (readiness.value?.status === 'degraded') return '部分服务可用';
  if (readiness.value?.status === 'not_ready' || readinessFailed.value) return '服务连接异常';
  return '正在检查服务';
});
const readinessShortLabel = computed(() => {
  if (readiness.value?.status === 'ready') return '就绪';
  if (readiness.value?.status === 'degraded') return '降级';
  if (readiness.value?.status === 'not_ready' || readinessFailed.value) return '异常';
  return '检查中';
});
const readinessTone = computed(() => {
  if (readiness.value?.status === 'ready') return 'success';
  if (readiness.value?.status === 'degraded') return 'warning';
  if (readiness.value?.status === 'not_ready' || readinessFailed.value) return 'danger';
  return 'neutral';
});

function closeMobileNavigation() {
  mobileNavOpen.value = false;
}

async function refreshReadiness() {
  readinessLoading.value = true;
  readinessFailed.value = false;
  try {
    readiness.value = await getReadiness();
  } catch {
    readiness.value = null;
    readinessFailed.value = true;
  } finally {
    readinessLoading.value = false;
  }
}

watch(() => route.fullPath, closeMobileNavigation);
onMounted(refreshReadiness);
</script>
