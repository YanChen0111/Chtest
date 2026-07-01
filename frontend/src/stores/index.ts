import { defineStore } from 'pinia';

export interface NavigationItem {
  readonly label: string;
  readonly routeName: string;
  readonly status: string;
}

export const useWorkbenchStore = defineStore('workbench', {
  state: () => ({
    navigation: [
      { label: 'AI 工作台', routeName: 'ai-workbench', status: '就绪' },
      { label: '需求评审', routeName: 'requirement-review', status: '就绪' },
      { label: '用例生成评审', routeName: 'case-generation-review', status: '就绪' },
      { label: '用例库', routeName: 'test-case-library', status: '就绪' },
      { label: '自动化草稿中心', routeName: 'automation-draft-center', status: '就绪' },
      { label: '执行中心', routeName: 'execution-center', status: '就绪' },
      { label: 'Playwright 执行', routeName: 'playwright-execution-center', status: '就绪' },
      { label: 'API 执行', routeName: 'newman-execution-center', status: '就绪' },
      { label: 'JMeter 执行', routeName: 'jmeter-execution-center', status: '就绪' },
      { label: 'CI/CD 质量中心', routeName: 'cicd-quality-center', status: '就绪' },
      { label: '报告中心', routeName: 'report-center', status: '就绪' },
      { label: '提示词 / 技能中心', routeName: 'prompt-skill-center', status: '就绪' },
      { label: 'RAG 知识库', routeName: 'knowledge-base', status: '就绪' },
      { label: '设置', routeName: 'project-settings', status: '就绪' },
    ] satisfies NavigationItem[],
  }),
});
