import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import App from './App.vue';

describe('App', () => {
  it('renders the Chinese workbench entry screen', () => {
    const wrapper = mount(App);

    expect(wrapper.text()).toContain('AI 测试工作台');
    expect(wrapper.text()).toContain('需求评审');
  });
});
