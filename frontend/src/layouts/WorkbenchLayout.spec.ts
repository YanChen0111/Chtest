import { mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it } from 'vitest';

import { router } from '../router';
import WorkbenchLayout from './WorkbenchLayout.vue';

describe('WorkbenchLayout', () => {
  it('renders Chinese workbench navigation', async () => {
    await router.push({ name: 'ai-workbench' });
    await router.isReady();

    const wrapper = mount(WorkbenchLayout, {
      global: {
        plugins: [createPinia(), router, ArcoVue],
        stubs: {
          RouterView: true,
        },
      },
    });

    expect(wrapper.text()).toContain('AI 工作台');
    expect(wrapper.text()).toContain('需求评审');
    expect(wrapper.text()).toContain('用例生成评审');
    expect(wrapper.text()).toContain('提示词 / 技能中心');
    expect(wrapper.text()).toContain('RAG 知识库');
  });

  it('uses route title for project settings page', async () => {
    await router.push({ name: 'project-settings' });
    await router.isReady();

    const wrapper = mount(WorkbenchLayout, {
      global: {
        plugins: [createPinia(), router, ArcoVue],
        stubs: {
          RouterView: true,
        },
      },
    });

    expect(wrapper.find('.workbench-header h1').text()).toBe('项目设置');
    expect(wrapper.text()).toContain('CI/CD 质量中心');
    const settingsLink = wrapper.findAll('.nav-item').find((link) => link.text().includes('设置'));
    expect(settingsLink?.attributes('href')).toBe('/settings/project');
    const knowledgeLink = wrapper.findAll('.nav-item').find((link) => link.text().includes('RAG 知识库'));
    expect(knowledgeLink?.attributes('href')).toBe('/extension/knowledge-base');
  });
});
