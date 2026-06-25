import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import AiWorkbenchView from './AiWorkbenchView.vue';

describe('AiWorkbenchView', () => {
  it('shows the backend health result', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('ok', { status: 200 })));

    const wrapper = mount(AiWorkbenchView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('后端健康');
    expect(wrapper.text()).toContain('正常');
  });

  it('shows a failure state when the backend health call fails', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('bad gateway', { status: 502 })));

    const wrapper = mount(AiWorkbenchView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('后端健康');
    expect(wrapper.text()).toContain('失败');
    expect(wrapper.text()).toContain('请求失败：502');
  });
});
