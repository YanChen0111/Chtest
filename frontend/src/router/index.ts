import { createRouter, createWebHistory } from 'vue-router';

import WorkbenchLayout from '../layouts/WorkbenchLayout.vue';
import AiWorkbenchView from '../views/ai-workbench/AiWorkbenchView.vue';
import AutomationDraftReviewView from '../views/automation/AutomationDraftReviewView.vue';
import CaseGenerationReviewView from '../views/cases/CaseGenerationReviewView.vue';
import TestCaseLibraryView from '../views/cases/TestCaseLibraryView.vue';
import PlaywrightExecutionView from '../views/execution/PlaywrightExecutionView.vue';
import PytestExecutionView from '../views/execution/PytestExecutionView.vue';
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
          path: 'cases/library',
          name: 'test-case-library',
          component: TestCaseLibraryView,
          meta: {
            title: '用例库',
          },
        },
        {
          path: 'automation/drafts',
          name: 'automation-draft-center',
          component: AutomationDraftReviewView,
          meta: {
            title: '自动化草稿中心',
          },
        },
        {
          path: 'execution/pytest',
          name: 'execution-center',
          component: PytestExecutionView,
          meta: {
            title: '执行中心',
          },
        },
        {
          path: 'execution/playwright',
          name: 'playwright-execution-center',
          component: PlaywrightExecutionView,
          meta: {
            title: 'Playwright 执行',
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
