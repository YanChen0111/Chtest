import { createRouter, createWebHistory } from 'vue-router';

import WorkbenchLayout from '../layouts/WorkbenchLayout.vue';
import AiWorkbenchView from '../views/ai-workbench/AiWorkbenchView.vue';
import CaseGenerationReviewView from '../views/cases/CaseGenerationReviewView.vue';
import PromptSkillCenterView from '../views/prompt-skill/PromptSkillCenterView.vue';
import RequirementReviewView from '../views/requirements/RequirementReviewView.vue';
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
          path: 'requirements/review',
          name: 'requirement-review',
          component: RequirementReviewView,
          meta: {
            title: '需求评审',
          },
        },
        {
          path: 'cases/generation-review',
          name: 'case-generation-review',
          component: CaseGenerationReviewView,
          meta: {
            title: '用例生成评审',
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
        {
          path: 'prompt-skill',
          name: 'prompt-skill-center',
          component: PromptSkillCenterView,
          meta: {
            title: 'Prompt / Skill 中心',
          },
        },
      ],
    },
  ],
});
