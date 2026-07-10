import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { afterEach, describe, expect, it, vi } from 'vitest';

import ProjectSettingsView from './ProjectSettingsView.vue';

const projectSettingsResponse = {
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
};

const currentModelConnectionResponse = {
  configured: true,
  provider: 'OpenAI',
  model_name: 'gpt-5.5',
  base_url: 'https://lucen.cc',
  wire_api: 'responses',
  api_key_configured: true,
  api_key_hint: '***cret',
};

const successfulModelConnectionTestResponse = {
  ok: true,
  provider: 'OpenAI',
  model_name: 'gpt-5.5',
  base_url: 'https://lucen.cc',
  wire_api: 'responses',
  message: 'Model connection test succeeded.',
  error_code: null,
  http_status: null,
  diagnostic: null,
  suggestion: null,
};

describe('ProjectSettingsView', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('shows project settings and saves generic model connection config without echoing the key', async () => {
    let savedBody: unknown = null;
    let testedBody: unknown = null;
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? 'GET';

      if (url.endsWith('/settings/model-connection/test') && method === 'POST') {
        testedBody = JSON.parse(String(init?.body));
        return jsonResponse(successfulModelConnectionTestResponse);
      }
      if (url.endsWith('/settings/model-connection') && method === 'PUT') {
        savedBody = JSON.parse(String(init?.body));
        return jsonResponse(currentModelConnectionResponse);
      }
      if (url.endsWith('/settings/model-connection')) {
        return jsonResponse(currentModelConnectionResponse);
      }
      if (url.includes('/projects/') && url.endsWith('/settings')) {
        return jsonResponse(projectSettingsResponse);
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(ProjectSettingsView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('\u5927\u6a21\u578b\u63a5\u5165');
    expect(wrapper.text()).toContain('Checkout System');
    expect(wrapper.text()).toContain('OpenAI');
    expect(wrapper.text()).toContain('gpt-5.5');
    expect(wrapper.text()).toContain('https://lucen.cc');
    expect(wrapper.text()).toContain('responses');
    expect(wrapper.text()).toContain('***cret');
    expect(wrapper.text()).not.toContain('Codex');

    const inputs = wrapper.findAll('input');
    expect(inputs.length).toBeGreaterThanOrEqual(5);
    await inputs[inputs.length - 1].setValue('sk-local-secret');

    const saveButton = wrapper.findAll('button').find((button) => button.text().includes('\u4fdd\u5b58\u914d\u7f6e'));
    expect(saveButton).toBeTruthy();
    await saveButton!.trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(savedBody).toEqual({
      provider: 'OpenAI',
      model_name: 'gpt-5.5',
      base_url: 'https://lucen.cc',
      wire_api: 'responses',
      import_config_text: null,
      import_auth_json: null,
      api_key: 'sk-local-secret',
    });
    expect(wrapper.text()).toContain('\u5927\u6a21\u578b\u63a5\u5165\u914d\u7f6e\u5df2\u4fdd\u5b58');
    expect(wrapper.text()).not.toContain('sk-local-secret');

    const testButton = wrapper.findAll('button').find((button) => button.text().includes('\u6d4b\u8bd5\u8fde\u63a5'));
    expect(testButton).toBeTruthy();
    await testButton!.trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(testedBody).toEqual({
      provider: 'OpenAI',
      model_name: 'gpt-5.5',
      base_url: 'https://lucen.cc',
      wire_api: 'responses',
      import_config_text: null,
      import_auth_json: null,
      api_key: null,
    });
    expect(wrapper.text()).toContain('\u6a21\u578b\u8fde\u63a5\u6d4b\u8bd5\u901a\u8fc7');
    expect(wrapper.text()).toContain('OpenAI');
  });

  it('tests the current unsaved model connection form and shows failure diagnostics', async () => {
    let testedBody: unknown = null;
    const failedModelConnectionTestResponse = {
      ok: false,
      provider: 'OpenAI Compatible',
      model_name: 'gpt-unsaved',
      base_url: 'https://gateway.example.test/v1',
      wire_api: 'responses',
      message: 'Model gateway returned HTTP 403.',
      error_code: 'MODEL_CONNECTION_HTTP_403',
      http_status: 403,
      diagnostic: 'HTTP 403',
      suggestion: 'Check API key permissions, account access, model access, and gateway allowlists.',
    };
    const emptyModelConnectionResponse = {
      configured: false,
      provider: null,
      model_name: null,
      base_url: null,
      wire_api: 'responses',
      api_key_configured: false,
      api_key_hint: null,
    };
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? 'GET';

      if (url.endsWith('/settings/model-connection/test') && method === 'POST') {
        testedBody = JSON.parse(String(init?.body));
        return jsonResponse(failedModelConnectionTestResponse);
      }
      if (url.endsWith('/settings/model-connection')) {
        return jsonResponse(emptyModelConnectionResponse);
      }
      if (url.includes('/projects/') && url.endsWith('/settings')) {
        return jsonResponse(projectSettingsResponse);
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(ProjectSettingsView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    const inputs = wrapper.findAll('input');
    expect(inputs.length).toBeGreaterThanOrEqual(5);
    await inputs[0].setValue('OpenAI Compatible');
    await inputs[1].setValue('gpt-unsaved');
    await inputs[2].setValue('https://gateway.example.test/v1');
    await inputs[3].setValue('responses');
    await inputs[inputs.length - 1].setValue('sk-unsaved-secret');

    const testButton = wrapper.findAll('button').find((button) => button.text().includes('\u6d4b\u8bd5\u8fde\u63a5'));
    expect(testButton).toBeTruthy();
    await testButton!.trigger('click');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(testedBody).toEqual({
      provider: 'OpenAI Compatible',
      model_name: 'gpt-unsaved',
      base_url: 'https://gateway.example.test/v1',
      wire_api: 'responses',
      import_config_text: null,
      import_auth_json: null,
      api_key: 'sk-unsaved-secret',
    });
    expect(wrapper.text()).toContain('\u6a21\u578b\u8fde\u63a5\u6d4b\u8bd5\u672a\u901a\u8fc7');
    expect(wrapper.text()).toContain('Model gateway returned HTTP 403.');
    expect(wrapper.text()).toContain('MODEL_CONNECTION_HTTP_403');
    expect(wrapper.text()).toContain('HTTP 403');
    expect(wrapper.text()).toContain('Check API key permissions');
    expect(wrapper.text()).toContain('https://gateway.example.test/v1');
    expect(wrapper.text()).not.toContain('sk-unsaved-secret');
  });
});

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
}
