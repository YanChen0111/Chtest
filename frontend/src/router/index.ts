import { createRouter, createWebHistory } from 'vue-router';

import WorkbenchLayout from '../layouts/WorkbenchLayout.vue';
import AiWorkbenchView from '../views/ai-workbench/AiWorkbenchView.vue';
import ProjectSettingsView from '../views/settings/ProjectSettingsView.vue';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: WorkbenchLayout,
      children: [
        {
          path: '',
          name: 'ai-workbench',
          component: AiWorkbenchView,
          meta: {
            title: 'AI 工作台',
          },
        },
        {
          path: 'settings/project',
          name: 'project-settings',
          component: ProjectSettingsView,
          meta: {
            title: '项目设置',
          },
        },
      ],
    },
  ],
});
