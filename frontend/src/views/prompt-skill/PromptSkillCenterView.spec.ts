import { flushPromises, mount } from '@vue/test-utils';
import ArcoVue from '@arco-design/web-vue';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';

import PromptSkillCenterView from './PromptSkillCenterView.vue';

describe('PromptSkillCenterView', () => {
  it('loads prompt and skill versions into a read-only registry shell', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/prompt-versions')) {
        return new Response(
          JSON.stringify({
            total: 1,
            items: [
              {
                id: 'p1',
                name: 'requirement_review',
                version: 'v1',
                hash: 'sha256:aaaaaaaa',
                agent_name: 'RequirementReviewAgent',
                content: '# Prompt: requirement_review v1',
                input_schema_json: { type: 'object', required: ['requirement'] },
                output_schema_json: { type: 'object', required: ['scores'] },
                status: 'active',
                created_at: '2026-06-29T10:00:00Z',
                updated_at: '2026-06-29T10:00:00Z',
                created_by: null,
                updated_by: null,
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.endsWith('/skill-versions')) {
        return new Response(
          JSON.stringify({
            total: 1,
            items: [
              {
                id: 's1',
                name: 'requirement-review-skill',
                version: 'v1',
                hash: 'sha256:bbbbbbbb',
                applicable_agents: ['RequirementReviewAgent'],
                content: '# Skill: requirement-review-skill v1',
                quality_gates_json: ['All six dimensions must be present.'],
                forbidden_actions_json: ['Do not claim external RAG evidence.'],
                tool_permissions_json: ['No execution tools.'],
                status: 'active',
                created_at: '2026-06-29T10:00:00Z',
                updated_at: '2026-06-29T10:00:00Z',
                created_by: null,
                updated_by: null,
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const wrapper = mount(PromptSkillCenterView, {
      global: {
        plugins: [createPinia(), ArcoVue],
      },
    });

    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('Prompt / Skill 中心');
    expect(wrapper.text()).toContain('PromptVersion');
    expect(wrapper.text()).toContain('SkillVersion');
    expect(wrapper.text()).toContain('requirement_review');
    expect(wrapper.text()).toContain('requirement-review-skill');
    expect(wrapper.text()).toContain('RequirementReviewAgent');
    expect(wrapper.text()).toContain('sha256:aaaaaaaa');
    expect(wrapper.text()).toContain('sha256:bbbbbbbb');
    expect(wrapper.text()).toContain('必填：requirement');
    expect(wrapper.text()).toContain('All six dimensions must be present.');
    expect(wrapper.text()).toContain('No execution tools.');
  });
});
