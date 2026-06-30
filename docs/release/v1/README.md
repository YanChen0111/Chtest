# Chtest V1 Release Package

Date: 2026-06-30

## Positioning

Chtest V1 is a local-first AI testing evidence workbench for individual test
engineers and automation test engineers.

The release proves one practical loop: requirements and local code changes can
be analyzed by AI, reviewed by a human, executed in controlled runners, and
reported with traceable evidence.

## Package Contents

- `acceptance-evidence.md`: automated release gate and evidence links.
- `manual-walkthrough.md`: human-readable V1 walkthrough skeleton.
- `screenshots/`: optional local frontend screenshots for release notes.

## Acceptance Status

V1 automated acceptance is `GO`.

Evidence summary:

- Backend V1 golden release-acceptance suite: `10 passed`.
- Frontend workbench suite: `14` test files passed and `17` tests passed.
- `git diff --check`: clean.

Source reports:

- `docs/implementation/06-v1-completion-audit.md`
- `docs/implementation/07-v1-release-acceptance.md`
- `docs/implementation/08-v1-final-acceptance-handoff.md`

## V1 Non-Goals

This release package does not include:

- RAG runtime, vector indexing, embeddings, or reranking.
- MCP runtime, remote MCP calls, or plugin marketplace behavior.
- RBAC, tenants, permissions, or enterprise collaboration.
- Remote CI provider integration, deployment automation, or release automation.
- Unapproved AI changes to business source files.
