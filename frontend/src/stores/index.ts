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
      { label: '需求评审', routeName: 'requirement-review', status: '待接入' },
      { label: '用例生成评审', routeName: 'case-generation-review', status: '待接入' },
      { label: '用例库', routeName: 'test-case-library', status: '待接入' },
      { label: '自动化草稿中心', routeName: 'automation-draft-center', status: '待接入' },
      { label: '执行中心', routeName: 'execution-center', status: '待接入' },
      { label: 'CI/CD 质量中心', routeName: 'cicd-quality-center', status: '待接入' },
      { label: '报告中心', routeName: 'report-center', status: '待接入' },
      { label: 'Prompt / Skill 中心', routeName: 'prompt-skill-center', status: '待接入' },
      { label: '设置', routeName: 'project-settings', status: '就绪' },
    ] satisfies NavigationItem[],
  }),
});
