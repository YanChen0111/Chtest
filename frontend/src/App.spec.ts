import { mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it } from 'vitest';

import App from './App.vue';
import { router } from './router';

describe('App', () => {
  it('renders the Chinese workbench entry screen', async () => {
    await router.push({ name: 'ai-workbench' });
    await router.isReady();

    const wrapper = mount(App, {
      global: {
        plugins: [createPinia(), router, ArcoVue],
      },
    });

    expect(wrapper.text()).toContain('AI 工作台');
    expect(wrapper.text()).toContain('AI 测试证据工作台');
    expect(wrapper.text()).toContain('需求评审');
  });
});
