# Chtest Final Frontend Design

## Status

Approved by the user on 2026-06-26.

This spec records the final frontend design decision for later AI coding sessions. The implementation-facing source of truth is `docs/product/08-frontend-design-spec.md`.

## Decision Summary

Chtest V1 uses a light, professional workbench UI built on the existing Vue 3 + Arco Design Vue stack.

The selected direction is A with adjusted shallow light colors:

- Neutral page background.
- White content surfaces.
- Arco blue for primary actions.
- Green for evidence/pass/safe knowledge.
- Red for failure/reject/blocking risk.
- Amber for pending approval or optimization.
- Compact tables, drawers, split panes, and status strips.

The product must not become a landing page, broad enterprise admin console, decorative dashboard, or plugin marketplace.

## Final Navigation

1. AI 工作台
2. 需求评审
3. 用例生成评审
4. 用例库和测试套件
5. 自动化草稿中心
6. 执行中心
7. CI/CD 质量中心
8. 报告中心
9. RAG 知识库
10. Prompt / Skill 中心
11. 工具适配器 / MCP 中心
12. 设置

User-facing `CI/CD 质量中心` is the current page name. V1 still uses local diff and UnitTestPatch behavior; remote CI integrations remain V2.

`RAG 知识库` is added as the user-facing page for ContextArtifact and KnowledgeAdapter surfaces. V1 still does not build vector indexing, embeddings, reranking, or an internal RAG runtime.

## Reference Boundary

- Keep Arco Design Vue as the UI library.
- Use WHartTest and WHartTest_Vue as MIT references for Vue/Arco AI generation and review patterns. Small adapted code patterns are allowed with license attribution.
- Use MeterSphere only as a visual and interaction reference. Do not copy source.
- Use shadcn/ui, Nuxt UI, and Creative Tim only as design references. Do not migrate V1 to their stacks.

## Page-Level Requirements

The approved page details are captured in `docs/product/08-frontend-design-spec.md`.

Future frontend implementation should start from that file and then read:

1. `docs/product/03-user-journey-and-page-prd.md`
2. `docs/product/06-frontend-ui-guidelines.md`
3. `docs/contracts/*` for data and state behavior
4. `docs/reference/01-open-source-migration-map.md` before migrating any reference code

## Self-Review

- No placeholder sections remain.
- The design matches the existing Vue 3 + Arco stack.
- CI/CD 质量中心 and RAG 知识库 naming is explicit.
- V1 RAG and remote CI boundaries are explicit.
- The spec is scoped to frontend design and does not request broad implementation before the V0.1 evidence loop.
