import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import ProjectSettingsView from './ProjectSettingsView.vue';

describe('ProjectSettingsView', () => {
  it('shows project settings bootstrap data in Chinese workbench sections', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        new Response(
          JSON.stringify({
            project: {
              id: '00000000-0000-0000-0000-000000000101',
              name: 'Checkout System',
              default_language: 'python',
              default_test_type: 'functional',
            },
            modules: [{ id: 'm1', name: 'Checkout', path: '/Checkout', level: 1, status: 'active' }],
            repositories: [
              {
                id: 'r1',
                name: 'sample-app',
                local_path: '/Users/yanchen/VscodeProject/sample-app',
                default_base_branch: 'main',
                language_hint: 'python',
                status: 'active',
              },
            ],
            environments: [
              {
                id: 'e1',
                name: 'local',
                variables_json: { APP_ENV: 'test' },
                status: 'active',
              },
            ],
            test_commands: [
              {
                id: 't1',
                name: 'pytest unit',
                command: 'pytest tests/unit -q',
                command_type: 'pytest',
                working_directory: '/Users/yanchen/VscodeProject/sample-app',
                timeout_seconds: 600,
                parse_junit: true,
                parse_coverage: false,
                status: 'active',
              },
            ],
            tool_definitions: [],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        ),
      ),
    );

    const wrapper = mount(ProjectSettingsView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('项目设置');
    expect(wrapper.text()).toContain('Checkout System');
    expect(wrapper.text()).toContain('模块树');
    expect(wrapper.text()).toContain('/Checkout');
    expect(wrapper.text()).toContain('仓库');
    expect(wrapper.text()).toContain('sample-app');
    expect(wrapper.text()).toContain('环境变量');
    expect(wrapper.text()).toContain('local');
    expect(wrapper.text()).toContain('测试命令');
    expect(wrapper.text()).toContain('pytest unit');
  });
});
