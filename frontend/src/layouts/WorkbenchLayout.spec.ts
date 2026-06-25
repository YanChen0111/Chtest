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
    expect(wrapper.text()).toContain('Prompt / Skill 中心');
  });
});
