import { createRouter, createWebHistory } from 'vue-router';

import WorkbenchLayout from '../layouts/WorkbenchLayout.vue';
import AiWorkbenchView from '../views/ai-workbench/AiWorkbenchView.vue';
import AutomationDraftReviewView from '../views/automation/AutomationDraftReviewView.vue';
import CaseGenerationReviewView from '../views/cases/CaseGenerationReviewView.vue';
import TestCaseLibraryView from '../views/cases/TestCaseLibraryView.vue';
import CicdQualityCenterView from '../views/cicd/CicdQualityCenterView.vue';
import JMeterExecutionView from '../views/execution/JMeterExecutionView.vue';
import NewmanExecutionView from '../views/execution/NewmanExecutionView.vue';
import PlaywrightExecutionView from '../views/execution/PlaywrightExecutionView.vue';
import PytestExecutionView from '../views/execution/PytestExecutionView.vue';
import KnowledgeBaseView from '../views/extension/KnowledgeBaseView.vue';
import PromptSkillCenterView from '../views/prompt-skill/PromptSkillCenterView.vue';
import ReportFailureAnalysisView from '../views/reporting/ReportFailureAnalysisView.vue';
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
          path: 'execution/newman',
          name: 'newman-execution-center',
          component: NewmanExecutionView,
          meta: {
            title: 'API 执行',
          },
        },
        {
          path: 'execution/jmeter',
          name: 'jmeter-execution-center',
          component: JMeterExecutionView,
          meta: {
            title: 'JMeter 执行',
          },
        },
        {
          path: 'cicd/quality',
          name: 'cicd-quality-center',
          component: CicdQualityCenterView,
          meta: {
            title: 'CI/CD 质量中心',
          },
        },
        {
          path: 'reports/failure-analysis',
          name: 'report-center',
          component: ReportFailureAnalysisView,
          meta: {
            title: '报告中心',
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
            title: '提示词 / 技能中心',
          },
        },
        {
          path: 'extension/knowledge-base',
          name: 'knowledge-base',
          component: KnowledgeBaseView,
          meta: {
            title: 'RAG 知识库',
          },
        },
      ],
    },
  ],
});
