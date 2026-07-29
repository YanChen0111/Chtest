import { mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { router } from '../router';
import WorkbenchLayout from './WorkbenchLayout.vue';

describe('WorkbenchLayout', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({
        status: 'ready',
        error_code: null,
        message: 'Chtest is ready.',
        checks: {},
      }),
    }));
  });

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
    expect(wrapper.text()).toContain('自动化草稿中心');
    expect(wrapper.text()).toContain('提示词 / 技能中心');
    expect(wrapper.text()).toContain('RAG 知识库');
    expect(wrapper.findAll('.nav-group-label').map((label) => label.text())).toEqual([
      '设计与评审',
      '自动化与证据',
      '知识与配置',
    ]);
    expect(wrapper.findAll('.nav-list .arco-tag')).toHaveLength(0);
    expect(wrapper.find('button[aria-label="打开导航"]').exists()).toBe(true);
    expect(wrapper.text()).not.toContain('Playwright 执行');
    expect(wrapper.text()).not.toContain('API 执行');
    expect(wrapper.text()).not.toContain('JMeter 执行');
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
    const automationLink = wrapper.findAll('.nav-item').find((link) => link.text().includes('自动化草稿中心'));
    expect(automationLink?.attributes('href')).toBe('/automation/drafts');
  });
});
