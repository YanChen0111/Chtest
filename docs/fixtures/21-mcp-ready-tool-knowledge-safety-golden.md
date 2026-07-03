# MCP-Ready Tool And Knowledge Safety Golden

This fixture proves Slice 33 remains a contract-only safety definition for
ToolDefinition, ToolInvocation, KnowledgeAdapterConfig, KnowledgeEvidence, and
Artifact behavior. It is not an MCP runtime, not a provider integration, and
not a tool executor.

## Safety Contracts

| Contract | Required safety fields | Human gate | Output evidence | Fallback behavior |
|---|---|---|---|---|
| ToolDefinition | strict input_schema, strict output_schema, risk_level, approval_required, timeout_seconds, artifact_policy, mcp_metadata.provider_state | Medium/high risk tools require approval through ToolInvocation before running | Schema and readiness metadata only | disabled/configured/unhealthy provider_state is display metadata and must not start MCP transport |
| ToolInvocation | tool_name snapshot, risk_level, approval_required, approval_status, working_directory, command_snapshot, timeout, artifact policy | approval_status=approved is required before medium/high risk running | Bounded stdout, stderr, structured output, validation error, runtime manifest, dependency snapshot, environment snapshot | rejected, failed, timeout, and cancelled preserve evidence and do not rewrite successful artifacts |
| KnowledgeAdapterConfig | status, provider_type, provider_state, config_json, safety_policy_json, used_knowledge | No review bypass; knowledge does not approve generated cases | KnowledgeEvidence plus Artifact metadata after normalization | disabled and unhealthy force local/no-knowledge fallback unless knowledge is mandatory |
| KnowledgeEvidence | source artifact ids, evidence type, bounded snippet, confidence, redaction status | Human review remains the case promotion authority | Normalized evidence refs only | Provider payloads must normalize before any prompt or review cites them |
| Artifact | owner entity, artifact_type, file_path, mime_type, size limit, sha256, metadata | Artifact persistence is required for reviewable tool/provider output | Bounded files or metadata refs | Raw provider payloads, credentials, and transport settings are rejected or redacted |

## Required Terms

The contract must define:

- ToolDefinition safety.
- ToolInvocation safety.
- KnowledgeAdapter safety.
- strict input_schema and output_schema.
- risk_level.
- approval_required.
- timeout_seconds.
- artifact_policy.
- provider_state disabled.
- provider_state configured.
- provider_state unhealthy.
- local/no-knowledge fallback.
- KnowledgeEvidence normalization.
- Artifact persistence.
- human gate.

## Forbidden Side Effects

The contract must not create or trigger:

- MCP runtime.
- MCP server/client transport.
- remote MCP call.
- plugin installation.
- provider SDK call.
- external provider call.
- credentials storage.
- OAuth state.
- remote URL fetch.
- vector index.
- embedding.
- reranking.
- graph job.
- Artifact mutation.
- Report conclusion.
- runner behavior change.
- review bypass.
- generated-case auto-approval.
- TestCase auto-promotion.
- remote CI provider behavior.
- RBAC.
- tenants.
- permissions.

ToolDefinition readiness and KnowledgeAdapter provider_state are metadata only.
ToolInvocation output and KnowledgeEvidence are evidence only. Human review
remains required for generated-case acceptance and TestCase promotion.
