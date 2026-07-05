# Chtest API Contract

## 1. Purpose

This document defines the Chtest V1 API contract. FastAPI routers, Pydantic schemas, frontend API clients, fixtures, and acceptance tests must follow this contract.

Common rules:

- Base path: `/api`.
- Content-Type: `application/json`.
- Time format: ISO 8601.
- id format: UUID string.
- Error response: `{"error_code": "string", "message": "string", "details": {}}`.
- V1 is single-user; API uses default user/workspace internally.

Context rules:

- V1 ContextArtifact is an API concept backed by the Artifact table, not a separate data table.
- `use_knowledge=false` only means external RAG/KnowledgeAdapter is not used.
- `context_artifact_ids` are still injected into prompts when provided, even when `use_knowledge=false`.
- AI responses that used local context must return `used_context_artifact_ids`.
- AI responses that used deterministic local KnowledgeAdapter retrieval must
  return `used_knowledge=true`; otherwise return `used_knowledge=false`.
- `used_knowledge=true` must be supported by retrieval evidence, not by model
  text alone.
- Generated case candidates that cite testing knowledge must expose normalized
  `KnowledgeEvidence` references, not provider-specific payloads.

Extension surface rules:

- The RAG 知识库 API is a ContextArtifact management and evidence-usage surface,
  not a built-in RAG runtime.
- KnowledgeAdapter APIs expose empty configuration state only in V1.
- MCP-ready ToolDefinition APIs expose stable schema metadata only; ToolInvocation
  remains the executable boundary.
- V1 APIs must not add vector indexing, embeddings, reranking, external
  KnowledgeAdapter calls, MCP server/client runtime calls, RBAC, tenants, or
  permissions.

Deterministic retrieval rules:

- V2 Slice 19 may expose deterministic local KnowledgeAdapter retrieval evidence
  through existing AI task and RAG 知识库 surfaces.
- Deterministic retrieval reads only same-project ContextArtifacts that are safe
  to show and allowed for prompt use.
- Retrieval evidence must include ContextArtifact ids, snippets, scores, matched
  terms, and query terms.
- APIs must not expose vector search controls, embedding configuration,
  external provider configuration, reranking controls, MCP runtime controls,
  RBAC, tenants, permissions, marketplace, cloud sync, or remote CI/CD provider
  controls.

Test knowledge card rules:

- Slice 30 may define TestKnowledgeCard and KnowledgeEvidence contract shapes
  for future APIs and generated-case evidence.
- TestKnowledgeCard represents structured testing knowledge, not generic chat
  chunks. It must cite same-project source artifacts or reviewed project data.
- KnowledgeEvidence is the normalized citation shape used by generated cases,
  agent review, and fixtures.
- TestKnowledgeCard and KnowledgeEvidence contract definitions must not enable
  vector indexing, embeddings, reranking, external provider calls, graph
  extraction, MCP runtime, RBAC, tenants, permissions, marketplace, cloud sync,
  or remote CI/CD provider behavior.

Newman execution rules:

- V2 Newman API execution reuses Test Run APIs and TestCommand settings.
- Newman execution must use configured `TestCommand.command_type=newman` and a
  ToolDefinition allowlist such as `newman_collection_run`.
- Newman execution returns TestRun, TestResult, stdout/stderr, `newman_json`,
  optional `junit`, and `parsed_result` evidence.
- Newman execution must not add a collection editor, Postman cloud integration,
  arbitrary shell execution, remote CI/CD provider control, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions.

Artifact access rules:

- V2 Slice 24 may add read-only local artifact access for persisted Artifact
  rows.
- Artifact access must use existing Artifact metadata and local artifact store
  paths; it must not accept arbitrary filesystem paths from the client.
- External imported artifact references remain inert labels and must not be
  fetched, proxied, downloaded, authenticated to, or exposed through the local
  artifact access endpoint.
- Artifact access must not add upload, mutation, delete, sharing, cloud storage,
  signed URL, RBAC, tenants, permissions, RAG runtime, MCP runtime, or
  marketplace behavior.

## 2. Project Settings APIs

### 2.1 Create Project

`POST /api/projects`

Request:

```json
{
  "name": "Checkout System",
  "description": "personal testing project",
  "default_language": "python",
  "default_test_type": "functional"
}
```

Response 201:

```json
{
  "id": "00000000-0000-0000-0000-000000000101",
  "name": "Checkout System",
  "default_language": "python",
  "default_test_type": "functional",
  "status": "active",
  "created_at": "2026-06-18T10:00:00Z"
}
```

### 2.2 Create Module

`POST /api/projects/{project_id}/modules`

Request:

```json
{
  "parent_id": null,
  "name": "Checkout",
  "sort_order": 10
}
```

Response 201 returns Module read model.

### 2.3 Create Repository

`POST /api/repositories`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "name": "sample-app",
  "local_path": "/Users/yanchen/VscodeProject/sample-app",
  "default_base_branch": "main",
  "language_hint": "python"
}
```

Response 201:

```json
{
  "id": "00000000-0000-0000-0000-000000000301",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "name": "sample-app",
  "local_path": "/Users/yanchen/VscodeProject/sample-app",
  "default_base_branch": "main",
  "language_hint": "python",
  "status": "active"
}
```

Validation rules:

- `local_path` must exist.
- `local_path` must be under configured allowlisted roots.
- `local_path` must contain `.git` when Git workflows are enabled.

### 2.4 Update Repository

`PATCH /api/repositories/{id}`

Request:

```json
{
  "name": "sample-app",
  "default_base_branch": "main",
  "language_hint": "python",
  "status": "active"
}
```

Response 200 returns Repository read model.

### 2.5 Create Environment

`POST /api/environments`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "name": "local",
  "variables_json": {
    "APP_ENV": "test",
    "BASE_URL": "http://127.0.0.1:8000"
  }
}
```

Response 201 returns Environment read model.

### 2.6 Update Environment

`PATCH /api/environments/{id}`

Request:

```json
{
  "name": "local",
  "variables_json": {
    "APP_ENV": "test",
    "BASE_URL": "http://127.0.0.1:8000"
  },
  "status": "active"
}
```

Response 200 returns Environment read model.

### 2.7 Create Test Command

`POST /api/test-commands`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "repository_id": "00000000-0000-0000-0000-000000000301",
  "environment_id": "00000000-0000-0000-0000-000000000351",
  "name": "pytest unit",
  "command": "pytest tests/unit -q --junitxml=artifacts/junit.xml",
  "working_directory": "/Users/yanchen/VscodeProject/sample-app",
  "command_type": "pytest",
  "timeout_seconds": 600,
  "parse_junit": true,
  "parse_coverage": false
}
```

Response 201 returns TestCommand read model.

### 2.8 Validate Test Command

`POST /api/test-commands/{id}/validate`

Request:

```json
{
  "dry_run": true
}
```

Response 200:

```json
{
  "test_command_id": "00000000-0000-0000-0000-000000000302",
  "valid": true,
  "allowlist_passed": true,
  "working_directory_passed": true,
  "messages": []
}
```

### 2.9 Get Project Settings

`GET /api/projects/{id}/settings`

Response 200:

```json
{
  "project": {
    "id": "00000000-0000-0000-0000-000000000101",
    "name": "Checkout System",
    "default_language": "python",
    "default_test_type": "functional"
  },
  "modules": [],
  "repositories": [],
  "environments": [],
  "test_commands": [],
  "tool_definitions": []
}
```

This endpoint powers the Project Settings page and gives the frontend one stable bootstrap contract.

### 2.10 Create Context Artifact

`POST /api/context-artifacts`

ContextArtifact is the V1 lightweight context mechanism before external RAG exists. It stores small requirement notes, API notes, OpenAPI snippets, logs, fixtures, or Markdown references that can be injected into AI prompts.

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "title": "coupon-api-notes.md",
  "artifact_type": "context_markdown",
  "mime_type": "text/markdown",
  "content": "# Coupon API Notes\nPOST /api/coupons/validate validates coupon availability.",
  "source_ref": "manual:coupon-api-notes.md"
}
```

Response 201:

```json
{
  "id": "00000000-0000-0000-0000-000000000371",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "owner_entity_type": "Project",
  "owner_entity_id": "00000000-0000-0000-0000-000000000101",
  "artifact_type": "context_markdown",
  "mime_type": "text/markdown",
  "file_path": "projects/00000000-0000-0000-0000-000000000101/context-artifacts/00000000-0000-0000-0000-000000000371/content.md",
  "sha256": "sha256:example",
  "metadata": {
    "title": "coupon-api-notes.md",
    "source_ref": "manual:coupon-api-notes.md",
    "safe_to_show": true,
    "redaction_applied": false
  }
}
```

Hard rules:

- The server must set `owner_entity_type=Project` and `owner_entity_id=project_id`.
- The client must not send or override owner fields.
- The server must run secret scan and redaction before saving and before display.
- `safe_to_show` is server-computed; a client-provided value is ignored.
- Allowed MIME types and size limits follow `docs/contracts/04-artifact-contract.md`.
- Unsafe MIME returns `CONTEXT_ARTIFACT_NOT_ALLOWED`.
- Size limit violations return `CONTEXT_ARTIFACT_TOO_LARGE`.
- High-risk secret detection returns `CONTEXT_ARTIFACT_SECRET_DETECTED`.

### 2.11 List Context Artifacts

`GET /api/projects/{project_id}/context-artifacts`

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000371",
      "title": "coupon-api-notes.md",
      "artifact_type": "context_markdown",
      "mime_type": "text/markdown",
      "safe_to_show": true,
      "redaction_applied": false
    }
  ],
  "total": 1
}
```

### 2.12 Get RAG 知识库 Surface

`GET /api/projects/{project_id}/knowledge-base`

The RAG 知识库 surface is backed by ContextArtifacts and KnowledgeAdapterConfig.
It is used to show project knowledge inventory, safety metadata, prompt
eligibility, and evidence usage. V2 Slice 19 may also show deterministic local
retrieval evidence. It must not perform semantic search or external retrieval.

Response 200:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "knowledge_adapter": {
    "adapter_name": "default",
    "status": "configured_stub",
    "provider_type": "deterministic_local",
    "used_knowledge": true,
    "retrieval_mode": "deterministic_local"
  },
  "context_artifacts": [
    {
      "id": "00000000-0000-0000-0000-000000000371",
      "title": "coupon-api-notes.md",
      "artifact_type": "context_markdown",
      "mime_type": "text/markdown",
      "source_ref": "manual:coupon-api-notes.md",
      "safe_to_show": true,
      "redaction_applied": false,
      "allowed_for_prompt": true,
      "usage_count": 2,
      "latest_used_at": "2026-06-18T10:00:00Z",
      "retrieved_count": 1,
      "latest_retrieved_at": "2026-06-30T10:00:00Z"
    }
  ],
  "latest_retrievals": [
    {
      "ai_task_id": "00000000-0000-0000-0000-000000000501",
      "retrieval_evidence_artifact_id": "00000000-0000-0000-0000-000000000391",
      "query_terms": ["coupon", "expired"],
      "used_context_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
      "snippet_count": 1,
      "created_at": "2026-06-30T10:00:00Z"
    }
  ],
  "test_knowledge_cards": [
    {
      "id": "00000000-0000-0000-0000-000000000821",
      "title": "Expired coupon boundary",
      "knowledge_type": "boundary_condition",
      "summary": "Expired coupons must be rejected before order submission.",
      "source_artifact_id": "00000000-0000-0000-0000-000000000371",
      "source_section": "coupon validation",
      "related_requirement_ids": ["00000000-0000-0000-0000-000000000401"],
      "related_risk_ids": ["00000000-0000-0000-0000-000000000411"],
      "test_type": "functional",
      "risk_level": "high",
      "confidence": 92,
      "safe_to_show": true,
      "allowed_for_prompt": true,
      "status": "active"
    }
  ],
  "non_goals": [
    "no_vector_index",
    "no_embedding",
    "no_reranking",
    "no_external_rag_runtime"
  ]
}
```

Hard rules:

- `context_artifacts` are Artifact rows with `owner_entity_type=Project`.
- `usage_count` and `latest_used_at` are derived from AITask
  `context_artifact_ids` or prompt input manifest evidence when available.
- `retrieved_count`, `latest_retrieved_at`, and `latest_retrievals` are derived
  from `knowledge_retrieval` artifacts and AITask output metadata when
  available.
- `knowledge_adapter.used_knowledge` must be `false` in V1. In V2 Slice 19 it
  may be `true` only when deterministic local retrieval evidence exists.
- `test_knowledge_cards`, when exposed by a future task, are local structured
  evidence records. Listing them must not trigger extraction, indexing,
  retrieval, embeddings, reranking, external provider calls, or graph jobs.
- The endpoint must not create vector indexes, chunk content, call embedding
  models, semantically rank results, or call external providers.

### 2.13 Get KnowledgeAdapter Config

`GET /api/projects/{project_id}/knowledge-adapter`

Response 200:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "adapter_name": "default",
  "status": "not_configured",
  "provider_type": "none",
  "config": {},
  "safety_policy": {},
  "last_checked_at": null,
  "used_knowledge": false
}
```

### 2.14 Update KnowledgeAdapter Config

`PUT /api/projects/{project_id}/knowledge-adapter`

Request:

```json
{
  "adapter_name": "default",
  "status": "configured_stub",
  "provider_type": "deterministic_local",
  "config": {
    "display_name": "Local deterministic knowledge adapter",
    "match_mode": "keyword_overlap",
    "max_results": 5,
    "max_snippet_chars": 320,
    "min_score": 1
  },
  "safety_policy": {
    "allowed_for_prompt": false
  },
  "notes": "V1 placeholder only"
}
```

Response 200 returns KnowledgeAdapter read model.

Hard rules:

- `provider_type` must be `none` or `stub` in V1.
- `provider_type=deterministic_local` is allowed only for the V2 Slice 19 local
  retrieval stub.
- KnowledgeAdapter safety treats `provider_state` as non-secret display or
  health metadata only. Allowed values include `disabled`, `configured`, and
  `unhealthy`; API handlers must not treat those values as permission to call
  an external provider.
- `status=disabled` or `provider_state=disabled` forces `used_knowledge=false`.
  `provider_state=unhealthy` requires local/no-knowledge fallback evidence
  unless the caller explicitly requires knowledge evidence and accepts failure.
- Any future provider result must normalize into `KnowledgeEvidence` plus
  persisted Artifact metadata before prompts, generated cases, or review
  surfaces cite it. Provider-specific payloads must not leak into response
  fields as business truth.
- Secret-like fields, remote provider URLs, vector DB settings, embedding model
  settings, OAuth state, and MCP transport settings are rejected.
- Updating KnowledgeAdapterConfig alone must not set `used_knowledge=true`.
  `used_knowledge=true` requires a later AI task to produce deterministic
  retrieval evidence.
- Updating KnowledgeAdapterConfig must not create TestKnowledgeCard rows,
  mutate artifacts, approve or reject GeneratedCaseCandidate rows, promote
  TestCase rows, create ToolInvocation rows, generate Reports, update CI/CD
  state, call provider SDKs, call MCP runtime, create vector indexes, create
  embeddings, rerank, or run graph jobs.

### 2.15 List MCP-ready ToolDefinitions

`GET /api/projects/{project_id}/tool-definitions`

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000801",
      "name": "pytest_runner",
      "tool_type": "test_runner",
      "description": "Run allowlisted pytest commands",
      "input_schema": {},
      "output_schema": {},
      "risk_level": "medium",
      "approval_required": false,
      "artifact_policy": {},
      "is_mcp_ready": true,
      "mcp_metadata": {
        "schema_version": "v1",
        "capability_name": "pytest_runner"
      },
      "status": "active"
    }
  ],
  "total": 1
}
```

Hard rules:

- The API exposes ToolDefinition schema/readiness only.
- ToolDefinition safety requires strict `input_schema`, `output_schema`,
  `risk_level`, `approval_required`, `timeout_seconds`, and `artifact_policy`
  metadata. Unknown free-form command strings, credentials, remote transport
  handles, provider-specific payloads, and shell fragments must not be exposed
  as valid inputs.
- `artifact_policy` must describe bounded expected artifacts such as stdout,
  stderr, structured runner output, runtime manifests, dependency snapshots,
  and environment snapshots. It must not authorize artifact upload, mutation,
  deletion, signed URLs, cloud storage, or broad artifact browsing.
- Tool execution still requires ToolInvocation and the internal allowlist rules.
- `is_mcp_ready=true` must not expose MCP transport controls or execute remote
  MCP calls.
- `mcp_metadata.provider_state` may display `disabled`, `configured`, or
  `unhealthy`, but it is not a runtime state and must not start MCP servers,
  install plugins, call provider SDKs, or perform external network calls.
- ToolDefinition listing must not create ToolInvocation rows, TestRun rows,
  Reports, QualityGateDecision results, GeneratedCaseCandidate review actions,
  TestCase promotions, artifacts, RAG retrieval, MCP runtime calls, remote CI
  provider calls, RBAC, tenants, or permissions.

### 2.16 MCP-Ready ToolDefinition And KnowledgeAdapter Safety Contract

This section is contract-only. It defines API response semantics for future
local tools, MCP-ready tools, and KnowledgeAdapter providers before any MCP
runtime, provider SDK, external retrieval provider, or transport control exists.

ToolDefinition safety response fields:

- `input_schema` and `output_schema`: strict JSON schemas for bounded inputs
  and normalized outputs.
- `risk_level`: low, medium, high, or critical risk classification used by
  ToolInvocation approval.
- `approval_required`: whether a human gate is required before running.
- `timeout_seconds`: upper execution bound copied into ToolInvocation.
- `artifact_policy`: expected artifact types, size limits, redaction rules, and
  persistence requirements.
- `mcp_metadata.provider_state`: display-only readiness such as `disabled`,
  `configured`, or `unhealthy`.

ToolInvocation safety response behavior:

- Invocation creation must snapshot ToolDefinition safety fields before
  execution.
- Medium/high-risk invocations with `approval_required=true` must remain in
  `waiting_approval` until a human approval action records
  `approval_status=approved`.
- Rejected, failed, timed-out, or cancelled invocations must preserve bounded
  error/stdout/stderr artifacts when available and must not rewrite previous
  successful evidence.
- ToolInvocation output is execution evidence only; it must not conclude
  Reports, approve cases, promote TestCase rows, bypass AutomationDraft review,
  or bypass QualityGateDecision evidence.

KnowledgeAdapter safety response behavior:

- `provider_state=disabled` or `status=disabled` forces `used_knowledge=false`.
- `provider_state=unhealthy` records provider health/fallback evidence and
  degrades to local/no-knowledge workflows unless the caller explicitly marks
  knowledge evidence as mandatory.
- Provider outputs must be normalized to Chtest `KnowledgeEvidence` and
  Artifact metadata before downstream prompts or review surfaces cite them.
- Raw provider payloads, provider schemas, credentials, OAuth state, tokens,
  remote URLs, vector DB settings, embedding model settings, reranker settings,
  graph runtime settings, and MCP transport settings must not appear in API
  responses except as redacted metadata saying they were rejected.

Forbidden side effects:

- The safety contract must not start MCP runtime, MCP server/client transport,
  plugin installation, provider SDK calls, external provider calls, vector
  indexes, embeddings, reranking, graph jobs, artifact mutation, Report
  generation, runner behavior changes, review bypass, generated-case
  auto-approval, TestCase auto-promotion, remote CI provider behavior, RBAC,
  tenants, or permissions.

### 2.17 KnowledgeAdapter Provider Evaluation Plan Contract

This section is contract-only. It defines future provider evaluation semantics
for KnowledgeAdapter candidates before any Haystack integration, LlamaIndex
integration, external retrieval provider, provider SDK, credential, external
call, vector database, embedding, reranking, background indexing, runtime
retrieval, provider-backed prompt context behavior, frontend page, migration,
package upgrade, RBAC, tenants, or permissions exists.

Allowed provider evaluation actions:

- `evaluate_knowledge_adapter_provider_plan`: future scoped evaluation action
  that packages provider candidate metadata, license review, reference intake,
  KnowledgeEvidence normalization requirements, provider_state, disabled by
  default policy, metrics, fallback behavior, ReviewHistory links, failure
  code, and visible reason.
- `evaluate_provider_candidate`, `record_provider_evaluation`,
  `block_provider_candidate`, and `request_provider_evaluation_revision` are
  evaluation labels only. They do not enable a provider, call a provider, run
  retrieval, create embeddings, or set `used_knowledge=true`.

KnowledgeAdapter provider evaluation plan payload shape:

```json
{
  knowledge_adapter_provider_evaluation_plan_action: evaluate_knowledge_adapter_provider_plan,
  project_id: 00000000-0000-0000-0000-000000000101,
  adapter_name: default,
  candidate_provider_name: haystack,
  provider_family: Haystack,
  adapter_type: external_retrieval_provider_candidate,
  provider_version: 2.x,
  adapter_version: evaluation-plan-v1,
  license_name: Apache-2.0,
  license_url: https://example.invalid/haystack-license,
  license_compatibility_notes: requires human review before integration,
  reference_intake_urls: [https://example.invalid/haystack-docs],
  documentation_snapshot_artifact_ids: [00000000-0000-0000-0000-000000000920],
  supported_retrieval_modes: [keyword, hybrid],
  supported_source_types: [context_artifact, test_knowledge_card],
  expected_knowledge_evidence_fields: [
    evidence_id,
    source_artifact_id,
    snippet,
    score,
    source_hash
  ],
  provider_state: disabled,
  disabled_by_default: true,
  network_policy: no_external_calls,
  credential_policy: credentials_forbidden,
  fallback_behavior: local_no_knowledge_fallback,
  metrics_to_collect: [
    evidence_normalization_completeness,
    source_traceability_coverage,
    redaction_safety_status
  ],
  safety_notes: provider output must normalize before citation,
  source_hash_requirements: source hash required for every cited item,
  review_history_ids: [00000000-0000-0000-0000-000000000895]
}
```

KnowledgeAdapter provider evaluation plan response shape for a future scoped
implementation:

```json
{
  knowledge_adapter_provider_evaluation_plan_action: evaluate_knowledge_adapter_provider_plan,
  knowledge_adapter_provider_evaluation_plan_artifact_id: 00000000-0000-0000-0000-000000000921,
  provider_suitability_status: needs_revision,
  provider_state_recommendation: disabled,
  disabled_by_default_decision: true,
  knowledge_evidence_normalization_notes: source trace fields required before future use,
  citation_traceability_requirements: source artifact id and source hash required,
  redaction_safety_requirements: safe bounded snippets only,
  metric_set: [
    evidence_normalization_completeness,
    source_traceability_coverage,
    fallback_coverage
  ],
  blocker_reasons: [license_review_required],
  fallback_behavior: local_no_knowledge_fallback,
  license_review_result: needs_license_review,
  reference_intake_summary: documentation snapshot captured for review,
  source_manifest_ids: [knowledge-adapter-provider-eval-source-manifest-001],
  source_hashes: [sha256:provider-docs-snapshot],
  review_history_links: [00000000-0000-0000-0000-000000000895],
  failure_code: null,
  visible_reason: null
}
```

KnowledgeAdapter Provider Evaluation Plan hard rules:

- Provider evaluation input must reference candidate provider name, provider
  family, adapter type, provider version, adapter version, license name,
  license URL, license compatibility notes, reference intake, documentation
  snapshot artifacts when available, supported modes, expected KnowledgeEvidence
  normalization fields, provider_state, disabled by default policy, network
  policy, credential policy, fallback behavior, metrics, source hash
  requirements, and ReviewHistory when human review exists.
- Provider evaluation output must be planning evidence only. It may record
  provider suitability status, KnowledgeEvidence normalization notes, citation
  traceability requirements, redaction and safety requirements, metric set,
  blocker reasons, fallback behavior, provider_state recommendation, disabled
  by default decision, license review result, reference intake summary,
  ReviewHistory links, source hashes, failure code, and visible reason.
- Provider suitability status values are `not_evaluated`, `suitable`,
  `suitable_with_constraints`, `blocked`, `needs_revision`, and
  `unsupported`. They do not create provider enablement, runtime connectivity,
  retrieval evidence, prompt eligibility, or `used_knowledge=true`.
- Missing, stale, unsafe, unlicensed, license-unknown, version-unknown,
  reference-missing, reference-mismatched, normalization-unsupported,
  redaction-failed, provider-state-unsafe, fallback-missing, cross-project,
  unbounded, credential-required, runtime-required, or provider-evaluation-
  mismatched input must return a failure code and visible reason and must not
  append a successful provider evaluation plan.
- `evaluate_knowledge_adapter_provider_plan` must not install packages, call
  providers, call provider SDKs, store credentials, fetch remote URLs, create
  vector indexes, create embeddings, rerank, run background indexing, run graph
  jobs, start MCP runtime, run runtime retrieval, create provider-backed prompt
  context evidence, assemble prompts, run AITasks, render frontend pages,
  generate reports, expose export/download endpoints, mutate Artifact rows
  outside declared evaluation evidence, mutate KnowledgeEvidence, mutate
  KnowledgeAdapterConfig outside declared evaluation evidence, mutate
  TestKnowledgeCard rows, approve or reject GeneratedCaseCandidate rows,
  promote TestCase rows, create ToolInvocation rows, enable a provider, add
  RBAC, create tenants, change permissions, or update remote CI provider
  behavior.

### 2.18 KnowledgeAdapter Provider Evaluation Review Decision Contract

This section is contract-only. It defines future local review decision
semantics for KnowledgeAdapter provider evaluation plan artifacts before any
provider enablement, Haystack integration, LlamaIndex integration, GraphRAG
integration, provider SDK, credential, external call, vector database,
embedding, reranking, background indexing, runtime retrieval,
provider-backed prompt context behavior, frontend page, migration, package
upgrade, RBAC, tenants, or permissions exists.

Allowed provider evaluation review action:

- `review_knowledge_adapter_provider_evaluation`: future scoped review action
  that records a local review decision for a provider evaluation plan artifact
  while preserving license review, reference intake, KnowledgeEvidence
  normalization, provider_state, disabled by default, fallback behavior,
  metrics, ReviewHistory links, failure code, and visible reason.

KnowledgeAdapter provider evaluation review decision payload shape:

```json
{
  knowledge_adapter_provider_evaluation_review_decision_action: review_knowledge_adapter_provider_evaluation,
  project_id: 00000000-0000-0000-0000-000000000101,
  knowledge_adapter_provider_evaluation_plan_artifact_id: 00000000-0000-0000-0000-000000000921,
  candidate_provider_name: haystack,
  provider_family: Haystack,
  adapter_type: external_retrieval_provider_candidate,
  provider_version: 2.x,
  adapter_version: evaluation-plan-v1,
  provider_suitability_status: needs_revision,
  provider_state_recommendation: disabled,
  disabled_by_default_decision: true,
  license_review_result: needs_license_review,
  reference_intake_summary: documentation snapshot captured for review,
  knowledge_evidence_normalization_notes: source trace fields required before future use,
  fallback_behavior_summary: local_no_knowledge_fallback remains required,
  metrics_plan: [
    evidence_normalization_completeness,
    source_traceability_coverage,
    fallback_coverage
  ],
  blocker_reasons: [license_review_required],
  unresolved_safety_questions: [license compatibility must be reviewed],
  source_manifest_ids: [knowledge-adapter-provider-eval-source-manifest-001],
  source_hashes: [sha256:provider-docs-snapshot],
  review_history_ids: [00000000-0000-0000-0000-000000000895],
  review_decision: needs_revision,
  reviewer_label: local_reviewer,
  reviewer_note: license review is required before future planning acceptance
}
```

KnowledgeAdapter provider evaluation review decision response shape for a
future scoped implementation:

```json
{
  knowledge_adapter_provider_evaluation_review_decision_action: review_knowledge_adapter_provider_evaluation,
  knowledge_adapter_provider_evaluation_review_decision_artifact_id: 00000000-0000-0000-0000-000000000922,
  knowledge_adapter_provider_evaluation_plan_artifact_id: 00000000-0000-0000-0000-000000000921,
  review_decision: needs_revision,
  review_status: needs_revision,
  accepted_constraints: [],
  requested_revision_fields: [license_review_result],
  blocked_reasons: [],
  unsupported_reasons: [],
  unresolved_safety_questions: [license compatibility must be reviewed],
  provider_state_recommendation: disabled,
  disabled_by_default_decision: true,
  review_history_links: [00000000-0000-0000-0000-000000000895],
  source_manifest_ids: [knowledge-adapter-provider-eval-source-manifest-001],
  source_hashes: [sha256:provider-docs-snapshot],
  failure_code: null,
  visible_reason: null
}
```

KnowledgeAdapter Provider Evaluation Review Decision hard rules:

- Review input must reference a same-project provider evaluation plan artifact,
  `knowledge_adapter_provider_evaluation_plan_artifact_id`, candidate provider
  metadata, provider suitability status, license review result, reference
  intake, KnowledgeEvidence normalization notes, provider_state recommendation,
  disabled by default decision, fallback behavior, metrics, source hashes, and
  ReviewHistory when human review exists.
- Review output must be planning/audit evidence only. It may record review
  decision, review status, reviewer label, reviewer note, accepted
  constraints, requested revision fields, blocked reasons, unsupported reasons,
  unresolved safety questions, ReviewHistory links, source hashes, failure
  code, and visible reason.
- Review decision values are `accepted_for_planning`,
  `accepted_with_constraints`, `blocked`, `needs_revision`, and
  `unsupported`. Review status values may include `not_reviewed`,
  `accepted_for_planning`, `accepted_with_constraints`, `blocked`,
  `needs_revision`, `unsupported`, and `failed_validation`.
- Accepted decisions are accepted for future planning only. They do not create
  provider enablement, runtime connectivity, retrieval evidence, prompt
  eligibility, or `used_knowledge=true`.
- Missing, stale, unsafe, unlicensed, license-unknown, version-unknown,
  reference-missing, reference-mismatched, normalization-unsupported,
  provider-state-unsafe, fallback-missing, review-decision-invalid,
  evaluation-plan-mismatched, cross-project, unbounded, credential-required,
  or runtime-required input must return a failure code and visible reason and
  must not append a successful review decision.
- `review_knowledge_adapter_provider_evaluation` must not install packages,
  call providers, call provider SDKs, store credentials, fetch remote URLs,
  create vector indexes, create embeddings, rerank, run background indexing,
  run graph jobs, start MCP runtime, run runtime retrieval, create
  provider-backed prompt context evidence, assemble prompts, run AITasks,
  render frontend pages, generate reports, expose export/download endpoints,
  mutate Artifact rows outside declared review decision evidence, mutate the
  reviewed provider evaluation plan artifact, mutate KnowledgeEvidence, mutate
  KnowledgeAdapterConfig outside declared review decision evidence, mutate
  TestKnowledgeCard rows, approve or reject GeneratedCaseCandidate rows,
  promote TestCase rows, create ToolInvocation rows, enable a provider, add
  RBAC, create tenants, change permissions, or update remote CI provider
  behavior.

Allowed provider evaluation review summary export action:

- `export_knowledge_adapter_provider_evaluation_review_summary`: future scoped
  summary action that packages a local provider evaluation review decision
  artifact into audit evidence for future planning while preserving review
  decision/status labels, accepted constraints, blocked reasons, unsupported
  reasons, requested revision fields, unresolved safety questions, license
  review, reference intake, KnowledgeEvidence normalization, provider_state,
  fallback behavior, metrics, source hashes, ReviewHistory links, failure
  code, and visible reason.

KnowledgeAdapter provider evaluation review summary export payload shape:

```json
{
  knowledge_adapter_provider_evaluation_review_summary_export_action: export_knowledge_adapter_provider_evaluation_review_summary,
  project_id: 00000000-0000-0000-0000-000000000101,
  knowledge_adapter_provider_evaluation_review_decision_artifact_id: 00000000-0000-0000-0000-000000000922,
  knowledge_adapter_provider_evaluation_plan_artifact_id: 00000000-0000-0000-0000-000000000921,
  candidate_provider_name: haystack,
  provider_family: Haystack,
  adapter_type: external_retrieval_provider_candidate,
  provider_version: 2.x,
  adapter_version: evaluation-plan-v1,
  provider_suitability_status: needs_revision,
  review_decision: needs_revision,
  review_status: needs_revision,
  reviewer_notes: [license review is required before future planning acceptance],
  accepted_constraints: [],
  requested_revision_fields: [license_review_result],
  blocked_reasons: [],
  unsupported_reasons: [],
  unresolved_safety_questions: [license compatibility must be reviewed],
  license_review_result: needs_license_review,
  reference_intake_summary: documentation snapshot captured for review,
  knowledge_evidence_normalization_notes: source trace fields required before future use,
  provider_state_recommendation: disabled,
  disabled_by_default_decision: true,
  fallback_behavior_summary: local_no_knowledge_fallback remains required,
  metrics_plan: [
    evidence_normalization_completeness,
    source_traceability_coverage,
    fallback_coverage
  ],
  source_manifest_ids: [knowledge-adapter-provider-eval-source-manifest-001],
  source_hashes: [sha256:provider-docs-snapshot],
  review_history_links: [00000000-0000-0000-0000-000000000895]
}
```

KnowledgeAdapter provider evaluation review summary export response shape for
a future scoped implementation:

```json
{
  knowledge_adapter_provider_evaluation_review_summary_export_action: export_knowledge_adapter_provider_evaluation_review_summary,
  knowledge_adapter_provider_evaluation_review_summary_export_artifact_id: 00000000-0000-0000-0000-000000000923,
  knowledge_adapter_provider_evaluation_review_decision_artifact_id: 00000000-0000-0000-0000-000000000922,
  knowledge_adapter_provider_evaluation_plan_artifact_id: 00000000-0000-0000-0000-000000000921,
  review_summary_status: exported_for_planning,
  exported_decision_groups: [needs_revision],
  provider_suitability_summary: needs_revision,
  license_reference_summary: license review required; reference snapshot preserved,
  knowledge_evidence_normalization_summary: source trace fields required before future use,
  provider_state_summary: disabled,
  disabled_by_default_summary: true,
  fallback_summary: local_no_knowledge_fallback remains required,
  metrics_summary: evidence normalization and source traceability remain incomplete,
  source_traceability_summary: source hashes and source manifest ids preserved,
  review_history_summary: local review decision link preserved,
  failure_code: null,
  visible_reason: null
}
```

KnowledgeAdapter Provider Evaluation Review Summary Export hard rules:

- Summary export input must reference a same-project provider evaluation
  review decision artifact,
  `knowledge_adapter_provider_evaluation_review_decision_artifact_id`, a
  same-project provider evaluation plan artifact,
  `knowledge_adapter_provider_evaluation_plan_artifact_id`, candidate provider
  metadata, provider suitability status, review decision/status labels,
  reviewer notes, accepted constraints, blocked reasons, unsupported reasons,
  requested revision fields, unresolved safety questions, license review
  result, reference intake, KnowledgeEvidence normalization notes,
  provider_state recommendation, fallback behavior, metrics, source hashes,
  source manifest ids, and ReviewHistory links when available.
- Summary export output must be planning/audit evidence only. It may record
  export artifact id, review summary status, exported decision groups,
  provider suitability summary, license/reference summary, KnowledgeEvidence
  normalization summary, provider_state summary, disabled by default summary,
  fallback summary, metrics summary, source traceability summary,
  ReviewHistory summary, failure code, and visible reason.
- Summary export is not a report generator, not a frontend workflow, and not
  an export/download endpoint contract.
- Exported decision groups may include `accepted_for_planning`,
  `accepted_with_constraints`, `blocked`, `needs_revision`, and `unsupported`.
  Review summary status values may include `not_exported`,
  `exported_for_planning`, and `failed_validation`.
- Accepted review summaries are accepted for future planning only. They do not
  create provider enablement, runtime connectivity, retrieval evidence, prompt
  eligibility, report generation behavior, export/download endpoints, or
  `used_knowledge=true`.
- Missing, stale, unsafe, unlicensed, license-unknown, version-unknown,
  reference-missing, reference-mismatched, normalization-unsupported,
  provider-state-unsafe, fallback-missing, review-decision-missing,
  review-decision-invalid, summary-export-invalid,
  evaluation-plan-mismatched, review-decision-mismatched, cross-project,
  unbounded, credential-required, or runtime-required input must return a
  failure code and visible reason and must not append a successful summary
  export.
- `export_knowledge_adapter_provider_evaluation_review_summary` must not
  install packages, call providers, call provider SDKs, store credentials,
  fetch remote URLs, create vector indexes, create embeddings, rerank, run
  background indexing, run graph jobs, start MCP runtime, run runtime
  retrieval, create provider-backed prompt context evidence, assemble prompts,
  run AITasks, render frontend pages, generate reports, expose
  export/download endpoints, upload artifacts, mutate Artifact rows outside
  declared summary export evidence, mutate the reviewed provider evaluation
  review decision artifact, mutate the reviewed provider evaluation plan
  artifact, mutate KnowledgeEvidence, mutate KnowledgeAdapterConfig outside
  declared summary export evidence, mutate TestKnowledgeCard rows, approve or
  reject GeneratedCaseCandidate rows, promote TestCase rows, create
  ToolInvocation rows, enable a provider, add RBAC, create tenants, change
  permissions, or update remote CI provider behavior.

Allowed provider evaluation review audit handoff action:

- `build_knowledge_adapter_provider_evaluation_review_audit_handoff`: future
  scoped handoff action that packages provider evaluation review summary
  export evidence into an audit evidence-chain bundle for future planning
  while preserving summary export artifact linkage, review decision artifact
  linkage, provider evaluation plan artifact linkage, included artifact ids,
  excluded artifact reasons, evidence chain status, unresolved blocker
  summary, unresolved safety question summary, unresolved follow-up flags,
  source hashes, ReviewHistory links, failure code, and visible reason.

KnowledgeAdapter provider evaluation review audit handoff payload shape:

```json
{
  knowledge_adapter_provider_evaluation_review_audit_handoff_action: build_knowledge_adapter_provider_evaluation_review_audit_handoff,
  project_id: 00000000-0000-0000-0000-000000000101,
  knowledge_adapter_provider_evaluation_review_summary_export_artifact_id: 00000000-0000-0000-0000-000000000923,
  knowledge_adapter_provider_evaluation_review_decision_artifact_id: 00000000-0000-0000-0000-000000000922,
  knowledge_adapter_provider_evaluation_plan_artifact_id: 00000000-0000-0000-0000-000000000921,
  candidate_provider_name: haystack,
  provider_family: Haystack,
  adapter_type: external_retrieval_provider_candidate,
  provider_version: 2.x,
  adapter_version: evaluation-plan-v1,
  review_summary_status: exported_for_planning,
  review_decision: needs_revision,
  review_status: needs_revision,
  exported_decision_groups: [needs_revision],
  accepted_constraints: [],
  requested_revision_fields: [license_review_result],
  blocked_reasons: [],
  unsupported_reasons: [],
  unresolved_safety_questions: [license compatibility must be reviewed],
  unresolved_follow_up_flags: [license_review_required],
  provider_suitability_summary: needs_revision,
  license_reference_summary: license review required; reference snapshot preserved,
  knowledge_evidence_normalization_summary: source trace fields required before future use,
  provider_state_summary: disabled,
  disabled_by_default_summary: true,
  fallback_summary: local_no_knowledge_fallback remains required,
  metrics_summary: evidence normalization and source traceability remain incomplete,
  source_manifest_ids: [knowledge-adapter-provider-eval-source-manifest-001],
  source_hashes: [sha256:provider-docs-snapshot],
  review_history_links: [00000000-0000-0000-0000-000000000895]
}
```

KnowledgeAdapter provider evaluation review audit handoff response shape for a
future scoped implementation:

```json
{
  knowledge_adapter_provider_evaluation_review_audit_handoff_action: build_knowledge_adapter_provider_evaluation_review_audit_handoff,
  knowledge_adapter_provider_evaluation_review_audit_handoff_artifact_id: 00000000-0000-0000-0000-000000000924,
  knowledge_adapter_provider_evaluation_review_summary_export_artifact_id: 00000000-0000-0000-0000-000000000923,
  knowledge_adapter_provider_evaluation_review_decision_artifact_id: 00000000-0000-0000-0000-000000000922,
  knowledge_adapter_provider_evaluation_plan_artifact_id: 00000000-0000-0000-0000-000000000921,
  handoff_summary: provider evaluation review requires license revision before integration planning,
  evidence_chain_status: incomplete,
  included_artifact_ids: [
    00000000-0000-0000-0000-000000000921,
    00000000-0000-0000-0000-000000000922,
    00000000-0000-0000-0000-000000000923
  ],
  excluded_artifact_reasons: [],
  provider_review_decision_group_summary: needs_revision,
  unresolved_blocker_summary: none,
  unresolved_safety_question_summary: license compatibility must be reviewed,
  disabled_by_default_summary: true,
  source_traceability_summary: source hashes and source manifest ids preserved,
  review_history_links: [00000000-0000-0000-0000-000000000895],
  failure_code: null,
  visible_reason: null
}
```

KnowledgeAdapter Provider Evaluation Review Audit Handoff hard rules:

- Audit handoff input must reference a same-project provider evaluation review
  summary export artifact,
  `knowledge_adapter_provider_evaluation_review_summary_export_artifact_id`, a
  same-project provider evaluation review decision artifact,
  `knowledge_adapter_provider_evaluation_review_decision_artifact_id`, and a
  same-project provider evaluation plan artifact,
  `knowledge_adapter_provider_evaluation_plan_artifact_id`.
- Audit handoff output must be evidence-chain packaging only. It may record
  audit handoff artifact id, handoff summary, evidence chain status, included
  artifact ids, excluded artifact reasons, provider review decision group
  summary, unresolved blocker summary, unresolved safety question summary,
  unresolved follow-up flags, disabled by default summary, source
  traceability summary, ReviewHistory links, failure code, and visible reason.
- Evidence chain status values may include `complete`, `incomplete`,
  `blocked`, and `failed_validation`. They must not mutate
  `KnowledgeAdapterConfig.status`, create runtime connectivity, enable
  providers, create retrieval evidence, generate reports, expose
  export/download endpoints, or set `used_knowledge=true`.
- Missing, stale, unsafe, unlicensed, license-unknown, version-unknown,
  reference-missing, reference-mismatched, normalization-unsupported,
  provider-state-unsafe, fallback-missing, summary-export-missing,
  summary-export-invalid, review-decision-missing, review-decision-invalid,
  evaluation-plan-missing, evaluation-plan-mismatched,
  review-decision-mismatched, cross-project, unbounded, credential-required,
  runtime-required, or provider-enable-required input must return a failure
  code and visible reason and must not append a successful audit handoff.
- `build_knowledge_adapter_provider_evaluation_review_audit_handoff` must not
  install packages, call providers, call provider SDKs, store credentials,
  fetch remote URLs, create vector indexes, create embeddings, rerank, run
  background indexing, run graph jobs, start MCP runtime, run runtime
  retrieval, create provider-backed prompt context evidence, assemble prompts,
  run AITasks, render frontend pages, generate reports, expose
  export/download endpoints, upload artifacts, mutate Artifact rows outside
  declared audit handoff evidence, mutate the provider evaluation review
  summary export artifact, mutate the reviewed provider evaluation review
  decision artifact, mutate the reviewed provider evaluation plan artifact,
  mutate provider metadata, mutate KnowledgeEvidence, mutate
  KnowledgeAdapterConfig outside declared audit handoff evidence, mutate
  historical evidence, mutate TestKnowledgeCard rows, approve or reject
  GeneratedCaseCandidate rows, promote TestCase rows, create ToolInvocation
  rows, enable a provider, add RBAC, create tenants, change permissions, or
  update remote CI provider behavior.

## 3. Requirement To Case APIs

### 3.1 Create Requirement

`POST /api/requirements`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "module_id": "00000000-0000-0000-0000-000000000201",
  "title": "Coupon checkout rules",
  "content": "User can select one available coupon during checkout. Coupon cannot be used with points. Expired coupons cannot be used.",
  "source_type": "manual",
  "source_ref": "REQ-COUPON-001"
}
```

Response 201 returns Requirement read model.

### 3.2 Start Requirement Review

`POST /api/requirements/{id}/review`

Request:

```json
{
  "prompt_version": "requirement_review:v1",
  "skill_version": "requirement-review-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-requirement-review",
  "use_knowledge": false,
  "context_artifact_ids": ["00000000-0000-0000-0000-000000000371"]
}
```

Response 202:

```json
{
  "ai_task_id": "00000000-0000-0000-0000-000000000501",
  "requirement_id": "00000000-0000-0000-0000-000000000401",
  "status": "pending",
  "next_poll_url": "/api/ai-tasks/00000000-0000-0000-0000-000000000501",
  "used_knowledge": false,
  "used_context_artifact_ids": ["00000000-0000-0000-0000-000000000371"]
}
```

`use_knowledge=false` disables only external RAG/KnowledgeAdapter. The listed `context_artifact_ids` are still included in the prompt input and recorded on AITask.

### 3.3 Get Requirement Review

`GET /api/requirements/{id}/review`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000000601",
  "requirement_id": "00000000-0000-0000-0000-000000000401",
  "overall_score": 82,
  "scores": {
    "completeness": 78,
    "clarity": 85,
    "consistency": 88,
    "testability": 80,
    "feasibility": 84,
    "logic": 77
  },
  "issues": [
    {"type": "missing_boundary", "text": "Coupon minimum amount is not specified", "severity": "medium"}
  ],
  "clarification_questions": ["Can coupons be combined with campaign discounts?"],
  "risk_items": [
    {"title": "Coupon and points conflict", "risk_level": "high", "suggestion": "Cover the conflict path"}
  ],
  "used_knowledge": false,
  "used_context_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
  "context_manifest_artifact_id": "00000000-0000-0000-0000-000000000372",
  "status": "reviewed"
}
```

### 3.4 Create Case Generation Task

`POST /api/case-generation/tasks`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "requirement_id": "00000000-0000-0000-0000-000000000401",
  "requirement_review_id": "00000000-0000-0000-0000-000000000601",
  "target_test_types": ["functional", "ui"],
  "prompt_version": "case_generation:v1",
  "skill_version": "test-case-generation-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-case-generator",
  "use_knowledge": false,
  "context_artifact_ids": ["00000000-0000-0000-0000-000000000371"]
}
```

Response 202:

```json
{
  "case_generation_task_id": "00000000-0000-0000-0000-000000000701",
  "ai_task_id": "00000000-0000-0000-0000-000000000702",
  "status": "pending",
  "used_knowledge": false,
  "used_context_artifact_ids": ["00000000-0000-0000-0000-000000000371"]
}
```

### 3.4.1 Requirement To Reviewed Case Agent Workflow Contract

This is a contract-only workflow decomposition for requirement-to-reviewed-case
generation. It is exposed through existing requirement review, case generation,
candidate listing, candidate review, and AI task APIs. It must not add a new API
endpoint, add a new orchestrator runtime, add runtime code, automatically
promote a generated case into a TestCase, or enable RAG, MCP, external provider,
vector, embedding, reranking, or graph runtime behavior.

Workflow trace envelope:

```json
{
  "workflow_name": "requirement_to_reviewed_case",
  "workflow_version": "v1",
  "workflow_run_id": "00000000-0000-0000-0000-000000000701",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "requirement_id": "00000000-0000-0000-0000-000000000401",
  "case_generation_task_id": "00000000-0000-0000-0000-000000000701",
  "candidate_id": null,
  "agent_name": "RequirementUnderstandingAgent",
  "agent_step": "requirement_understanding",
  "step_status": "succeeded",
  "input_artifact_ids": ["00000000-0000-0000-0000-000000000372"],
  "output_artifact_ids": ["00000000-0000-0000-0000-000000000711"],
  "context_manifest_artifact_id": "00000000-0000-0000-0000-000000000372",
  "used_context_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
  "used_knowledge": false,
  "prompt_version": "requirement_understanding:v1",
  "skill_version": "requirement-review-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-requirement-workflow",
  "schema_version": "requirement_to_case_agent_trace:v1",
  "schema_validation_status": "valid",
  "human_gate": "not_required_for_step",
  "write_permission": "ai_task_artifacts_only",
  "fallback_applied": false,
  "failure_code": null
}
```

Required trace fields for every workflow step:

- `workflow_name`, `workflow_version`, `workflow_run_id`, `project_id`, and
  `requirement_id`.
- `agent_name`, `agent_step`, `step_status`, `prompt_version`,
  `skill_version`, `model_provider`, `model_name`, and `schema_version`.
- `input_artifact_ids`, `output_artifact_ids`,
  `context_manifest_artifact_id`, `used_context_artifact_ids`, and
  `used_knowledge`.
- `human_gate`, `write_permission`, `schema_validation_status`,
  `fallback_applied`, and `failure_code`.
- `case_generation_task_id` when the step belongs to a case generation task.
- `candidate_id` when the step evaluates or annotates a specific
  GeneratedCaseCandidate.

Agent step contracts:

| Agent | Inputs | Outputs/artifacts | write permission | human gate | failure behavior and fallback | Trace fields |
|---|---|---|---|---|---|---|
| RequirementUnderstandingAgent | Requirement read model, project/module metadata, prompt/skill versions, context manifest, allowed context artifact ids | `requirement_understanding` parsed artifact with normalized summary, acceptance criteria, constraints, assumptions, ambiguities, and source references; raw LLM output artifact when applicable | May write AITask artifacts and the parsed payload consumed by RequirementReview. Must not edit Requirement content, module, project settings, TestCase, or GeneratedCaseCandidate rows | No approval gate inside the agent. Human clarification happens by normal requirement editing or review outside this step | On schema failure, mark the AITask step failed, persist raw/error artifacts, and do not continue to case generation. On incomplete input, fallback is an artifact with `insufficient_requirement_detail` findings and no automatic promotion | `agent_step=requirement_understanding`, `requirement_id`, `context_manifest_artifact_id`, `ambiguity_count`, `acceptance_criteria_count`, `failure_code` |
| RiskAnalysisAgent | RequirementUnderstandingAgent output, RequirementReview scores/issues when available, same-project context artifacts, target test types | `risk_analysis` artifact with risk items, severity, likelihood, affected flows, suggested coverage, and traceable source refs | May write AITask artifacts and derived risk fields in RequirementReview or case generation output. Must not create TestCase records or approve candidates | No approval gate. Risk findings are shown to the later reviewer | If risk scoring fails, fallback to `risk_level=unknown` with an error finding; valid understanding output may still proceed, but high-risk unknowns must be visible to review | `agent_step=risk_analysis`, `risk_item_count`, `max_risk_level`, `source_requirement_understanding_artifact_id`, `fallback_applied` |
| CoverageAnalysisAgent | RequirementUnderstandingAgent output, RiskAnalysisAgent output, existing approved TestCase summaries when available, generated candidate summaries when retrying | `coverage_analysis` artifact with requirement-to-risk-to-case matrix, uncovered criteria, duplicate-sensitive areas, and gap notes | May write AITask artifacts and candidate evidence fields such as `covered_risk_ids` and `coverage_gap_notes` during validated case generation persistence. Must not mutate approved TestCase rows | No approval gate. Coverage gaps are review evidence | If coverage cannot be computed, fallback to `coverage_status=unknown`; candidate generation may continue only with visible gap findings and without auto approval | `agent_step=coverage_analysis`, `covered_requirement_ref_count`, `gap_count`, `matrix_artifact_id`, `failure_code` |
| TestDesignAgent | Understanding, risk, and coverage artifacts; target test types; project default language/test type; normalized KnowledgeEvidence when present | `test_design` artifact with scenario outlines, positive/negative/boundary partitions, data needs, priority rationale, and traceability refs | May write AITask artifacts and transient case generation design payloads. Must not create GeneratedCaseCandidate or TestCase rows directly | No approval gate | If design output is invalid, fail the step and do not call CaseGenerationAgent. If only some scenario outlines are invalid, fallback may drop invalid outlines and record `partial_design_used=true` | `agent_step=test_design`, `scenario_outline_count`, `target_test_types`, `partial_design_used`, `schema_validation_status` |
| CaseGenerationAgent | TestDesignAgent output, requirement read model, risk and coverage artifacts, target test types, prompt/skill versions, context manifest | `case_generation_output` artifact plus GeneratedCaseCandidate rows with `status=generated`, traceability fields, review findings, knowledge evidence refs, and raw/parsed output artifacts | May create GeneratedCaseCandidate rows and AITask artifacts through the existing case generation task. Must not create TestCase records, set candidate status to approved, execute automation, or generate reports | Human gate is required after generation; every candidate remains review-gated | Invalid candidates are rejected from persistence with validation findings. If no valid candidate remains, the case generation task fails or returns an empty candidate list with error artifacts. No fallback may create a TestCase | `agent_step=case_generation`, `case_generation_task_id`, `candidate_ids`, `valid_candidate_count`, `invalid_candidate_count`, `failure_code` |
| CaseReviewAgent | GeneratedCaseCandidate rows, case generation artifacts, risk/coverage/design artifacts, normalized KnowledgeEvidence, reviewer-visible candidate fields | `case_review` artifact with quality score, findings, optimization suggestions, missing evidence, and recommended reviewer action | May write AITask artifacts and candidate review evidence fields such as `quality_score`, `review_findings`, and optimization notes. Must not approve, reject, or promote a candidate | Human gate is required. Only explicit candidate review actions may approve, approve after edit, reject, or request optimization | If review analysis fails, leave candidate status unchanged and surface `case_review_unavailable`. Human review can still proceed from persisted candidate content, but without auto approval | `agent_step=case_review`, `candidate_id`, `quality_score`, `finding_count`, `recommended_action`, `human_gate=required` |
| DedupAgent | GeneratedCaseCandidate rows, candidate review artifacts, approved TestCase summaries, requirement refs, normalized steps/expected results | `dedup_analysis` artifact with duplicate clusters, similarity reasons, keep/drop recommendations, and affected candidate ids | May write AITask artifacts and candidate review findings. Must not delete, merge, archive, reject, or approve candidates and must not mutate TestCase rows | Human gate is required for any duplicate resolution that changes candidate status | If dedup fails, fallback to `dedup_status=unknown`; candidates remain reviewable and must not be auto-promoted because dedup evidence is missing | `agent_step=dedup`, `candidate_id`, `duplicate_cluster_id`, `duplicate_candidate_ids`, `dedup_status`, `fallback_applied` |
| AutomationReadinessAgent | Candidate content, TestDesignAgent output, project settings, ToolDefinition metadata, repository/language hints, existing TestCommand metadata when available | `automation_readiness` artifact and candidate field such as `automation_readiness` with blockers, suggested framework, required test data, and manual-only reasons | May write AITask artifacts and candidate readiness/review evidence. Must not create AutomationDraft, ToolInvocation, TestRun, TestCommand, repository changes, or code files | Human gate remains required for candidate approval. Automation draft creation is a later explicit workflow | If readiness analysis fails, fallback to `automation_readiness=unknown` with blocker findings. This must not block manual review or start automation | `agent_step=automation_readiness`, `candidate_id`, `readiness`, `blocker_count`, `suggested_framework`, `failure_code` |

Workflow boundary rules:

- This section defines artifact and state contracts only. It does not create
  `POST /api/agent-workflows`, `POST /api/agents/run`, or any other new API
  endpoint.
- The workflow reuses AITask evidence and existing case generation/review
  surfaces. It does not add a separate orchestrator runtime, queue, scheduler,
  graph executor, or provider runtime.
- GeneratedCaseCandidate may become TestCase only through the existing human
  review action in `POST /api/case-review/items/{id}/approve`.
- Agent recommendations, quality scores, dedup clusters, coverage matrices, and
  automation readiness values are review evidence only; they must not
  automatically promote, approve, reject, archive, merge, execute, or report.
- `used_knowledge=true` remains invalid unless existing deterministic local
  retrieval evidence is present. This workflow must not enable RAG runtime, MCP
  runtime, external provider calls, vector indexes, embeddings, reranking, graph
  extraction, RBAC, tenants, permissions, marketplace, cloud sync, or remote
  CI/CD provider behavior.

### 3.5 List Candidate Cases

`GET /api/case-generation/tasks/{id}/candidates`

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000801",
      "title": "Expired coupon cannot be used during checkout",
      "priority": "P0",
      "test_type": "functional",
      "steps": ["Login", "Open checkout", "Select expired coupon", "Submit order"],
      "expected_results": ["Submission is blocked", "Expired coupon message is shown"],
      "requirement_refs": ["Expired coupons cannot be used"],
      "source_knowledge_evidence_ids": ["ke-expired-coupon-boundary"],
      "knowledge_evidence_refs": [
        {
          "evidence_id": "ke-expired-coupon-boundary",
          "knowledge_card_id": "00000000-0000-0000-0000-000000000821",
          "source_artifact_id": "00000000-0000-0000-0000-000000000371",
          "snippet": "Expired coupons cannot be applied during checkout.",
          "score": 0.92,
          "retrieval_reason": "Supports the expired-coupon rejection path"
        }
      ],
      "covered_risk_ids": ["00000000-0000-0000-0000-000000000411"],
      "ai_reason": "Covers coupon expiration boundary",
      "generation_reason": "Boundary case for expired coupon validation",
      "automation_readiness": "suitable_for_playwright",
      "quality_score": 84,
      "review_findings": [
        {
          "type": "evidence_complete",
          "severity": "info",
          "message": "Candidate cites the coupon expiration boundary card"
        }
      ],
      "coverage_gap_notes": "Does not cover coupon and points conflict",
      "status": "generated"
    }
  ],
  "total": 1
}
```

Slice 30 candidate evidence rules:

- `source_knowledge_evidence_ids` must reference normalized KnowledgeEvidence
  ids present in the candidate, the case generation artifact, or a related
  AITask output artifact.
- `knowledge_evidence_refs` is display metadata. It must cite same-project
  TestKnowledgeCard or Artifact evidence and must not contain unbounded raw
  provider payloads.
- `quality_score` and `review_findings` are review aids only. They must not
  create TestCase records, approve candidates, execute automation, or generate
  reports.
- Missing or weak KnowledgeEvidence should appear as review findings or
  coverage gap notes instead of being hidden.
- Candidate listing must not run retrieval, indexing, embeddings, reranking,
  external provider calls, graph jobs, MCP runtime calls, artifact mutation, or
  remote CI provider behavior.

Slice 31 candidate persistence/display rules:

- Case generation persistence must copy normalized knowledge evidence fields
  from validated AI output when they are present.
- `GET /api/case-generation/tasks/{id}/candidates` must return the fields with
  safe defaults when absent:
  `source_knowledge_evidence_ids=[]`, `knowledge_evidence_refs=[]`,
  `covered_risk_ids=[]`, `generation_reason=null`,
  `automation_readiness="unknown"`, `quality_score=null`,
  `review_findings=[]`, and `coverage_gap_notes=null`.
- List responses must not imply a TestKnowledgeCard table or knowledge-card
  CRUD API exists. References may be historical ids, same-project Artifact ids,
  or normalized evidence ids from the owning case generation output.
- Returning persisted evidence fields must not create TestCase records, approve
  candidates, execute automation, generate reports, run retrieval, index
  vectors, create embeddings, run graph jobs, call external providers, mutate
  artifacts, invoke MCP runtime, or call remote CI providers.

### 3.5.1 Generated Case Human Review Evidence Package Contract

This section is contract-only. It defines future Generated Case Human Review
Evidence Package semantics for packaging GeneratedCaseCandidate review
evidence. It does not add a `POST /api/generated-case-review-packages`
endpoint, backend feature API, router, service, worker, queue, scheduler,
frontend page, report generation behavior, export/download endpoint,
migration, or package upgrade.

Allowed generated case human review evidence package action:

- `build_generated_case_human_review_evidence_package`: future scoped package
  action that packages GeneratedCaseCandidate content, knowledge evidence,
  prompt-context lineage, CaseReviewAgent findings, dedup findings,
  automation readiness, and ReviewHistory into a human review evidence bundle
  without approving or rejecting candidates.

Generated Case Human Review Evidence Package payload shape:

```json
{
  generated_case_human_review_evidence_package_action: build_generated_case_human_review_evidence_package,
  project_id: 00000000-0000-0000-0000-000000000101,
  generated_case_candidate_id: 00000000-0000-0000-0000-000000000801,
  candidate_status: generated,
  candidate_title: Expired coupon cannot be used during checkout,
  candidate_priority: P0,
  candidate_test_type: functional,
  candidate_precondition: user has an expired coupon,
  candidate_steps: [Login, Open checkout, Select expired coupon, Submit order],
  candidate_expected_results: [Submission is blocked, Expired coupon message is shown],
  candidate_input_data: { coupon_code: EXPIRED10 },
  candidate_tags: [checkout, coupon],
  requirement_refs: [Expired coupons cannot be used],
  risk_refs: [coupon-expiration-boundary],
  ai_reason: Covers coupon expiration boundary,
  generation_reason: Boundary case for expired coupon validation,
  covered_risk_ids: [00000000-0000-0000-0000-000000000411],
  duplicate_of_case_id: null,
  source_knowledge_evidence_ids: [ke-expired-coupon-boundary],
  knowledge_evidence_refs_json: [
    {
      evidence_id: ke-expired-coupon-boundary,
      knowledge_card_id: 00000000-0000-0000-0000-000000000821,
      source_artifact_id: 00000000-0000-0000-0000-000000000371,
      snippet: Expired coupons cannot be applied during checkout.,
      score: 0.92
    }
  ],
  quality_score: 84,
  review_findings_json: [{ type: evidence_complete, severity: info }],
  coverage_gap_notes: Does not cover coupon and points conflict,
  automation_readiness: suitable_for_playwright,
  dedup_findings: [{ duplicate_cluster_id: checkout-coupon-boundary }],
  duplicate_candidate_ids: [],
  automation_readiness_blockers: [],
  prompt_context_evidence_artifact_ids: [00000000-0000-0000-0000-000000000901],
  prompt_context_consumption_artifact_ids: [00000000-0000-0000-0000-000000000902],
  prompt_context_audit_summary_artifact_ids: [00000000-0000-0000-0000-000000000903],
  prompt_context_audit_review_decision_artifact_ids: [00000000-0000-0000-0000-000000000904],
  prompt_context_audit_review_summary_export_artifact_ids: [00000000-0000-0000-0000-000000000905],
  prompt_context_discrepancy_resolution_audit_handoff_artifact_ids: [00000000-0000-0000-0000-000000000906],
  source_manifest_ids: [generated-case-review-source-manifest-001],
  source_hashes: [sha256:generated-case-review-evidence],
  review_history_links: [00000000-0000-0000-0000-000000000895]
}
```

Generated Case Human Review Evidence Package response shape for a future
scoped implementation:

```json
{
  generated_case_human_review_evidence_package_action: build_generated_case_human_review_evidence_package,
  generated_case_human_review_evidence_package_artifact_id: 00000000-0000-0000-0000-000000000930,
  generated_case_candidate_id: 00000000-0000-0000-0000-000000000801,
  generated_case_human_review_evidence_package: generated_case_human_review_evidence_package,
  candidate_summary: expired coupon checkout boundary candidate with local evidence,
  evidence_chain_completeness: incomplete,
  missing_evidence_summary: coupon and points conflict not covered,
  conflicting_evidence_summary: none,
  review_blocker_summary: coverage gap remains visible,
  dedup_readiness_summary: no duplicate selected; suitable for Playwright after review,
  human_review_checklist: [check evidence refs, resolve coverage gap, confirm automation readiness],
  included_artifact_ids: [
    00000000-0000-0000-0000-000000000901,
    00000000-0000-0000-0000-000000000902,
    00000000-0000-0000-0000-000000000903
  ],
  excluded_artifact_reasons: [],
  review_history_links: [00000000-0000-0000-0000-000000000895],
  failure_code: null,
  visible_reason: null
}
```

Generated Case Human Review Evidence Package hard rules:

- Input must reference a same-project GeneratedCaseCandidate and may include
  same-project prompt-context artifact lineage, source manifest ids, source
  hashes, and ReviewHistory links.
- Output is human-review evidence only. It may record candidate summary,
  evidence chain completeness, missing evidence summary, conflicting evidence
  summary, review blocker summary, dedup/readiness summary, human review
  checklist, included artifact ids, excluded artifact reasons, ReviewHistory
  links, failure code, and visible reason.
- `quality_score`, `review_findings_json`, `coverage_gap_notes`,
  `automation_readiness`, dedup findings, evidence chain completeness, and
  human review checklist must not approve candidates, reject candidates,
  request optimization, promote TestCase rows, create AutomationDraft rows,
  execute automation, create reports, or set `used_knowledge=true`.
- Missing, stale, unsafe, cross-project, unbounded, evidence-missing,
  candidate-missing, candidate-mismatched, candidate-status-invalid,
  knowledge-evidence-missing, prompt-context-evidence-missing,
  review-findings-missing, dedup-inconclusive, readiness-unknown,
  review-history-missing, artifact-mismatched, source-hash-mismatched,
  credential-required, runtime-required, provider-required, approval-required,
  or promotion-required input must return failure code and visible reason and
  must not append a successful evidence package.
- `build_generated_case_human_review_evidence_package` must not create
  backend runtime APIs, endpoints, routers, services, workers, queues,
  schedulers, migrations, frontend pages, reports, export/download endpoints,
  provider integrations, provider SDK calls, external calls, credentials,
  remote URL fetches, vector indexes, embeddings, reranking, graph jobs, MCP
  runtime calls, prompt execution, AITask orchestration, TestCase promotion,
  GeneratedCaseCandidate approve/reject mutation, automation draft creation,
  ToolInvocation rows, TestRun/TestResult rows, artifact upload, Artifact rows
  outside declared evidence package output, prompt context evidence mutation,
  KnowledgeEvidence mutation, ReviewHistory mutation, historical evidence
  mutation, runner behavior changes, remote CI provider behavior, RBAC,
  tenants, permissions, or package upgrades.

### 3.5.2 Generated Case Human Review Decision Contract

This section is contract-only. It defines future Generated Case Human Review
Decision semantics for recording a human review decision over the Slice 54
Generated Case Human Review Evidence Package. It does not add a
`POST /api/generated-case-review-decisions` endpoint, backend feature API,
router, service, worker, queue, scheduler, frontend page, report generation
behavior, export/download endpoint, migration, or package upgrade.

Allowed generated case human review decision action:

- `review_generated_case_human_review_evidence_package`: future scoped action
  that records human review decision evidence from
  `generated_case_human_review_evidence_package_artifact_id`,
  GeneratedCaseCandidate id/status, candidate summary, evidence chain
  completeness, missing/conflicting evidence summaries, review blocker
  summary, dedup/readiness summary, human review checklist, review findings,
  automation readiness, source hashes, source manifest ids, and ReviewHistory
  links without approving or rejecting candidates.

Generated Case Human Review Decision payload shape:

```json
{
  generated_case_human_review_decision_action: review_generated_case_human_review_evidence_package,
  project_id: 00000000-0000-0000-0000-000000000101,
  generated_case_human_review_evidence_package_artifact_id: 00000000-0000-0000-0000-000000000930,
  generated_case_candidate_id: 00000000-0000-0000-0000-000000000801,
  candidate_status: generated,
  candidate_summary: expired coupon checkout boundary candidate with local evidence,
  evidence_chain_completeness: incomplete,
  missing_evidence_summary: coupon and points conflict not covered,
  conflicting_evidence_summary: none,
  review_blocker_summary: coverage gap remains visible,
  dedup_readiness_summary: no duplicate selected; suitable for Playwright after review,
  human_review_checklist: [check evidence refs, resolve coverage gap, confirm automation readiness],
  quality_score: 84,
  review_findings_json: [{ type: evidence_complete, severity: info }],
  coverage_gap_notes: Does not cover coupon and points conflict,
  automation_readiness: suitable_for_playwright,
  dedup_findings: [{ duplicate_cluster_id: checkout-coupon-boundary }],
  duplicate_candidate_ids: [],
  duplicate_of_case_id: null,
  prompt_context_lineage_artifact_ids: [
    00000000-0000-0000-0000-000000000901,
    00000000-0000-0000-0000-000000000902,
    00000000-0000-0000-0000-000000000903
  ],
  source_manifest_ids: [generated-case-review-source-manifest-001],
  source_hashes: [sha256:generated-case-review-evidence],
  review_history_links: [00000000-0000-0000-0000-000000000895],
  review_decision: accept_with_required_edits_before_future_promotion,
  decision_label: accepted_with_required_edits,
  reviewer_label: qa_lead,
  reviewer_comment: Accept after adding coupon and points conflict coverage,
  accepted_constraints: [same evidence package, no runtime execution],
  requested_edit_fields: [steps_json, expected_results_json, coverage_gap_notes],
  optimization_request_summary: null,
  rejection_reasons: [],
  blocker_reasons: [],
  duplicate_resolution_notes: none
}
```

Generated Case Human Review Decision response shape for a future scoped
implementation:

```json
{
  generated_case_human_review_decision_action: review_generated_case_human_review_evidence_package,
  generated_case_human_review_decision_artifact_id: 00000000-0000-0000-0000-000000000940,
  generated_case_human_review_evidence_package_artifact_id: 00000000-0000-0000-0000-000000000930,
  generated_case_candidate_id: 00000000-0000-0000-0000-000000000801,
  generated_case_human_review_decision: generated_case_human_review_decision,
  review_decision: accept_with_required_edits_before_future_promotion,
  decision_status: recorded,
  decision_label: accepted_with_required_edits,
  allowed_decision_labels: [
    accepted_for_future_promotion,
    accepted_with_required_edits,
    needs_optimization,
    rejected_for_insufficient_evidence,
    blocked,
    duplicate,
    needs_more_evidence,
    failed_validation
  ],
  reviewer_label: qa_lead,
  reviewer_comment: Accept after adding coupon and points conflict coverage,
  accepted_constraints: [same evidence package, no runtime execution],
  requested_edit_fields: [steps_json, expected_results_json, coverage_gap_notes],
  optimization_request_summary: null,
  rejection_reasons: [],
  blocker_reasons: [],
  duplicate_resolution_notes: none,
  review_history_links: [00000000-0000-0000-0000-000000000895],
  failure_code: null,
  visible_reason: null
}
```

Generated Case Human Review Decision hard rules:

- Input must reference a same-project
  `generated_case_human_review_evidence_package_artifact_id` and
  same-project GeneratedCaseCandidate. The decision must preserve candidate
  status, candidate summary, evidence chain completeness, missing evidence
  summary, conflicting evidence summary, review blocker summary,
  dedup/readiness summary, human review checklist, source hashes, source
  manifest ids, and ReviewHistory links.
- Output is human-review decision evidence only. It may record review
  decision, decision status, decision label, reviewer label, reviewer comment,
  accepted constraints, requested edit fields, optimization request summary,
  rejection reasons, blocker reasons, duplicate resolution notes,
  ReviewHistory links, failure code, and visible reason.
- Decision labels `accepted_for_future_promotion`,
  `accepted_with_required_edits`, `needs_optimization`,
  `rejected_for_insufficient_evidence`, `blocked`, `duplicate`,
  `needs_more_evidence`, and `failed_validation` must not approve candidates,
  reject candidates, request optimization, promote TestCase rows, create
  AutomationDraft rows, execute automation, create reports, or set
  `used_knowledge=true`.
- Missing, stale, unsafe, cross-project, unbounded, evidence-package-missing,
  evidence-package-mismatched, candidate-missing, candidate-mismatched,
  candidate-status-invalid, evidence-chain-incomplete, review-blocked,
  dedup-conflict, duplicate-resolution-missing, review-history-missing,
  artifact-mismatched, source-hash-mismatched, credential-required,
  runtime-required, provider-required, approval-required,
  optimization-required, or promotion-required input must return failure code
  and visible reason and must not append a successful decision.
- `review_generated_case_human_review_evidence_package` must not create
  backend runtime APIs, endpoints, routers, services, workers, queues,
  schedulers, migrations, frontend pages, reports, export/download endpoints,
  provider integrations, provider SDK calls, external calls, credentials,
  remote URL fetches, vector indexes, embeddings, reranking, graph jobs, MCP
  runtime calls, prompt execution, AITask orchestration, TestCase promotion,
  GeneratedCaseCandidate approve/reject mutation, request optimization
  mutation, automation draft creation, ToolInvocation rows, TestRun/TestResult
  rows, artifact upload, Artifact rows outside declared decision evidence,
  prompt context evidence mutation, KnowledgeEvidence mutation, ReviewHistory
  mutation, historical evidence mutation, runner behavior changes, remote CI
  provider behavior, RBAC, tenants, permissions, or package upgrades.

### 3.5.3 Knowledge Feedback Contract

This section is contract-only. It defines the API payload shape that a future
KnowledgeFeedbackAgent may return through existing AITask/artifact surfaces. It
does not add a `POST /api/knowledge-feedback` endpoint or runtime worker.

Knowledge feedback input evidence may include:

- accepted and rejected GeneratedCaseCandidate summaries;
- reviewed TestCase summaries;
- ReviewHistory comments, actions, reviewer labels, and evidence artifact ids;
- FailureAnalysis summaries;
- Report summaries and evidence manifests;
- TestRun/TestResult execution evidence summaries;
- normalized KnowledgeEvidence and existing TestKnowledgeCard summaries.

Draft feedback response shape:

```json
{
  "agent_name": "KnowledgeFeedbackAgent",
  "prompt_version": "knowledge_feedback:v1",
  "skill_version": "knowledge-feedback-skill:v1",
  "knowledge_feedback": [
    {
      "feedback_id": "kf-expired-coupon-boundary",
      "feedback_type": "positive_example",
      "draft_knowledge_type": "existing_test_case_pattern",
      "source_entity_type": "TestCase",
      "source_entity_id": "00000000-0000-0000-0000-000000000901",
      "source_quote_or_hash": "sha256:reviewed-case-expired-coupon",
      "source_span": "steps[1-4]",
      "recommendation": "Reuse this reviewed boundary pattern for expired coupon validation.",
      "confidence": 86,
      "used_knowledge_evidence_ids": ["ke-expired-coupon-boundary"],
      "unsupported_claims": [],
      "review_findings": ["Source TestCase is reviewed and cites evidence"],
      "prompt_eligible": false,
      "status": "draft"
    }
  ],
  "unsupported_claims": [],
  "failure_code": null
}
```

Knowledge feedback hard rules:

- KnowledgeFeedbackAgent output is draft feedback only. It must not create,
  approve, archive, or mutate TestKnowledgeCard rows.
- `prompt_eligible=false` is mandatory until a future human review workflow
  explicitly approves prompt eligibility.
- Every draft feedback item must cite a source entity, same-project Artifact,
  or normalized KnowledgeEvidence. Free-floating model text is not valid source
  evidence.
- Accepted and rejected examples must remain separately labeled. Rejected cases
  must not become positive knowledge without human review.
- Failure- and report-derived feedback must cite FailureAnalysis, Report,
  TestRun/TestResult, or artifact evidence.
- `confidence` and `review_findings` are review aids only. They must not mark
  feedback approved, prompt-eligible, or safe for automatic reuse.
- Insufficient source evidence returns
  `UNABLE_TO_CREATE_KNOWLEDGE_FEEDBACK` with visible `unsupported_claims` and
  no silent fallback knowledge.
- Knowledge feedback responses must preserve `prompt_version`, `skill_version`,
  input evidence ids, output artifact ids, schema validation status, and
  failure code on the owning AITask trace.
- The contract must not mutate ReviewHistory, FailureAnalysis, Report,
  TestRun, TestCase, GeneratedCaseCandidate, Artifact, or TestKnowledgeCard
  rows; create TestCase records; approve generated cases; generate reports;
  run retrieval; index vectors; create embeddings; rerank; run graph jobs;
  call external providers; invoke MCP runtime; call remote CI providers; add
  RBAC; create tenants; or change permissions.

### 3.5.2 Knowledge Feedback Review Gate Contract

This section is contract-only. It defines the future review payload semantics
for KnowledgeFeedbackDraft without adding a feedback review endpoint, frontend
page, TestKnowledgeCard CRUD, or review runtime.

Allowed review actions:

- `approve_feedback`: human accepts the draft feedback as reviewable knowledge
  input for a later TestKnowledgeCard workflow.
- `reject_feedback`: human rejects the draft; it remains auditable and cannot
  be reused as positive knowledge.
- `request_revision`: human asks for a revised draft while preserving source
  evidence, unsupported claims, and reviewer notes.
- `mark_prompt_eligible`: human explicitly marks already approved feedback as
  eligible for prompt use, subject to safe-to-show evidence and source
  citations.
- `create_knowledge_card_candidate`: optional future handoff payload only; it
  is not TestKnowledgeCard CRUD in this contract and follows the
  TestKnowledgeCard handoff contract below.

Review gate payload shape:

```json
{
  "feedback_id": "kf-expired-coupon-boundary",
  "action": "approve_feedback",
  "reviewer_label": "Default User",
  "review_comment": "Source case is reviewed and cites stable evidence.",
  "evidence_artifact_ids": ["00000000-0000-0000-0000-000000000391"],
  "prompt_eligible": false,
  "prompt_eligibility_reason": null,
  "handoff_payload": {
    "source_feedback_id": "kf-expired-coupon-boundary",
    "draft_knowledge_type": "existing_test_case_pattern",
    "source_quote_or_hash": "sha256:reviewed-case-expired-coupon",
    "test_knowledge_card_candidate": {
      "knowledge_type": "existing_test_case_pattern",
      "summary": "Expired coupon tests should cover checkout rejection.",
      "safe_to_show": true,
      "allowed_for_prompt": false
    }
  }
}
```

Review gate response shape:

```json
{
  "feedback_id": "kf-expired-coupon-boundary",
  "status": "approved_by_human",
  "review_action": "approve_feedback",
  "review_history_id": "00000000-0000-0000-0000-000000000861",
  "review_artifact_id": "00000000-0000-0000-0000-000000000862",
  "prompt_eligible": false,
  "prompt_eligibility_reason": null,
  "test_knowledge_card_id": null
}
```

Review gate hard rules:

- Every accepted, rejected, revised, or prompt-eligibility decision must be a
  human review action and must append or reference ReviewHistory when a future
  implementation owns the workflow.
- `mark_prompt_eligible` requires prior human approval, safe-to-show source
  evidence, reviewed source citations, and a non-empty
  `prompt_eligibility_reason`.
- `prompt_eligible=true` must not be inferred from model confidence,
  unsupported-claim absence, quality score, schema validity, or the existence
  of a draft feedback artifact.
- `create_knowledge_card_candidate` may produce a future handoff payload, but
  it must not create, approve, archive, delete, or mutate TestKnowledgeCard
  rows in this contract.
- Review gate responses must preserve `feedback_id`, action, reviewer label,
  evidence artifact ids, prompt eligibility decision, ReviewHistory id when
  present, and review artifact id when present.
- Rejected feedback and unsupported claims remain auditable and must not be
  reused as positive knowledge or prompt context.
- This contract must not mutate historical ReviewHistory, FailureAnalysis,
  Report, TestRun, TestResult, TestCase, GeneratedCaseCandidate, Artifact, or
  TestKnowledgeCard rows; call providers; invoke MCP runtime; create vector
  indexes; create embeddings; rerank; run graph jobs; generate reports; change
  runner behavior; add RBAC; create tenants; or change permissions.

### 3.5.3 TestKnowledgeCard Handoff Contract

This section is contract-only. It defines the future handoff payload semantics
for an approved KnowledgeFeedbackDraft and does not add an endpoint, router,
service, worker, queue, frontend page, migration, or `POST /api/test-knowledge-cards`.

Allowed handoff action:

- `create_knowledge_card_candidate`: human-reviewed action that prepares a
  `handoff_payload` for a future TestKnowledgeCard workflow. It must return
  `test_knowledge_card_id: null` in this contract.

Handoff payload shape:

```json
{
  "feedback_id": "kf-expired-coupon-boundary",
  "action": "create_knowledge_card_candidate",
  "status": "approved_by_human",
  "review_history_id": "00000000-0000-0000-0000-000000000861",
  "review_artifact_id": "00000000-0000-0000-0000-000000000862",
  "handoff_payload": {
    "source_feedback_id": "kf-expired-coupon-boundary",
    "source_entity_type": "TestCase",
    "source_entity_id": "00000000-0000-0000-0000-000000000931",
    "source_artifact_ids": ["00000000-0000-0000-0000-000000000391"],
    "source_quote_or_hash": "sha256:reviewed-case-expired-coupon",
    "source_span": "case.steps[3]-case.expected_results[0]",
    "candidate_fields": {
      "knowledge_type": "existing_test_case_pattern",
      "title": "Expired coupon checkout rejection",
      "summary": "Reviewed checkout cases should include expired coupon rejection.",
      "body": "Use a reviewed case source before turning this into reusable knowledge.",
      "source_type": "reviewed_case",
      "source_section": "checkout/coupon",
      "related_requirement_ids": ["00000000-0000-0000-0000-000000000121"],
      "related_risk_ids": ["00000000-0000-0000-0000-000000000221"],
      "related_test_case_ids": ["00000000-0000-0000-0000-000000000931"],
      "tags": ["checkout", "coupon", "regression"],
      "confidence": 84,
      "safe_to_show": true,
      "redaction_applied": false,
      "allowed_for_prompt": false,
      "evidence_artifact_ids": ["00000000-0000-0000-0000-000000000862"]
    },
    "duplicate_candidates": [
      {
        "knowledge_card_id": "00000000-0000-0000-0000-000000000781",
        "match_reason": "Same coupon boundary condition"
      }
    ],
    "merge_recommendation": "review_required",
    "unsupported_claims": []
  },
  "test_knowledge_card_id": null
}
```

TestKnowledgeCard handoff hard rules:

- Handoff input must come from an approved KnowledgeFeedbackDraft and must
  preserve ReviewHistory id, feedback review artifact id, same-project source
  artifact ids, source entity reference, source quote/hash, and unsupported
  claims.
- `candidate_fields` are a proposed TestKnowledgeCard shape only. They must
  not create, approve, archive, delete, or mutate TestKnowledgeCard rows.
- `allowed_for_prompt=false` is mandatory in candidate fields. Human card
  review must happen later before any TestKnowledgeCard can become prompt
  eligible.
- `safe_to_show=true` requires safe-to-show evidence and reviewed source
  citations. It must not be inferred from model confidence, schema validity,
  or absence of unsupported claims.
- Duplicate candidates and merge recommendations are review aids only. They
  must not automatically merge, archive, replace, or relabel existing cards.
- Unsafe, missing, cross-project, or unbounded source evidence must reject the
  handoff or request revision; no fallback knowledge or fabricated citation is
  allowed.
- This contract must not add a backend feature API, frontend review page,
  TestKnowledgeCard CRUD, automatic card creation, automatic prompt
  eligibility, automatic knowledge ingestion, provider call, MCP runtime,
  vector index, embedding, reranking, graph job, artifact mutation outside the
  declared handoff artifact, historical evidence mutation, generated-case
  auto-approval, TestCase auto-promotion, report generation behavior, runner
  behavior change, remote CI provider behavior, RBAC, tenants, or permissions.

### 3.5.4 TestKnowledgeCard Candidate Review Contract

This section is contract-only. It defines future candidate review payload
semantics for TestKnowledgeCard handoff candidates and does not add an endpoint,
router, service, worker, queue, frontend page, migration,
`POST /api/test-knowledge-cards`, or `POST /api/test-knowledge-card-candidates`.

Allowed candidate review actions:

- `approve_candidate_for_creation`: human accepts candidate quality and source
  evidence for a future card-creation workflow. It is not card creation here.
- `reject_candidate`: human rejects the candidate and keeps rationale
  auditable.
- `request_candidate_revision`: human requests better source evidence,
  safer content, or a corrected mapping.
- `flag_duplicate`: human routes the candidate to duplicate review.
- `request_merge_review`: human requests explicit merge review for existing
  duplicate card candidates.
- `defer_prompt_eligibility`: human or system records that prompt eligibility
  remains deferred and `allowed_for_prompt=false`.

Candidate review payload shape:

```json
{
  "candidate_review_action": "approve_candidate_for_creation",
  "candidate_review_decision": "approved_for_future_creation",
  "reviewer_label": "Default User",
  "review_comment": "Source evidence is reviewed; prompt eligibility stays deferred.",
  "source_handoff_artifact_id": "00000000-0000-0000-0000-000000000871",
  "source_feedback_id": "kf-expired-coupon-boundary",
  "candidate_card_json": {
    "knowledge_type": "existing_test_case_pattern",
    "title": "Expired coupon checkout rejection",
    "summary": "Reviewed checkout cases should include expired coupon rejection.",
    "safe_to_show": true,
    "allowed_for_prompt": false
  },
  "evidence_artifact_ids": ["00000000-0000-0000-0000-000000000862"],
  "duplicate_knowledge_card_ids": ["00000000-0000-0000-0000-000000000781"],
  "merge_hint": "possible_duplicate",
  "duplicate_review_required": true,
  "merge_review_required": false,
  "prompt_eligibility_decision": "deferred",
  "unsupported_claims": [],
  "failure_code": null
}
```

Candidate review response shape:

```json
{
  "candidate_review_action": "approve_candidate_for_creation",
  "candidate_review_decision": "approved_for_future_creation",
  "review_history_id": "00000000-0000-0000-0000-000000000881",
  "candidate_review_artifact_id": "00000000-0000-0000-0000-000000000882",
  "test_knowledge_card_id": null,
  "allowed_for_prompt": false,
  "prompt_eligibility_decision": "deferred"
}
```

TestKnowledgeCard Candidate Review hard rules:

- Candidate review input must come from a TestKnowledgeCard handoff candidate
  and must preserve source feedback id, handoff artifact id, candidate card
  JSON, source Artifact ids, source quote/hash, duplicate/merge hints, and
  unsupported claims.
- Candidate review actions must be human reviewer actions. Model confidence,
  schema validity, safe_to_show, or absence of unsupported claims must not
  approve a candidate.
- Candidate review may append or reference ReviewHistory and may produce a
  candidate review artifact, but invalid transitions must not append successful
  ReviewHistory.
- `approve_candidate_for_creation` must return `test_knowledge_card_id: null`
  in this contract. A later scoped workflow must own actual card creation.
- `defer_prompt_eligibility` is the default; reviewed candidates must keep
  `allowed_for_prompt=false`.
- Duplicate and merge actions are review routing only. They must not
  automatically merge, archive, replace, delete, relabel, or create
  TestKnowledgeCard rows.
- This contract must not add a backend feature API, frontend review page,
  TestKnowledgeCard CRUD, automatic card creation, automatic card approval,
  automatic prompt eligibility, automatic knowledge ingestion, provider call,
  MCP runtime, vector index, embedding, reranking, graph job, artifact mutation
  outside declared candidate review artifacts, historical evidence mutation,
  generated-case auto-approval, TestCase auto-promotion, runner behavior
  change, report generation behavior change, remote CI provider behavior,
  RBAC, tenants, or permissions.

### 3.5.5 Reviewed TestKnowledgeCard Creation Contract

This section is contract-only. It defines future reviewed creation semantics
for approved candidates and does not add an endpoint, router, service, worker,
queue, frontend page, migration, broad TestKnowledgeCard CRUD, list/update/
delete API, or `POST /api/test-knowledge-cards`.

Allowed future creation action:

- `create_reviewed_test_knowledge_card`: future scoped action that may create a
  TestKnowledgeCard only from an approved candidate review, reviewed source
  evidence, resolved duplicate/merge preconditions, and `allowed_for_prompt=false`.

Reviewed creation payload shape:

```json
{
  "creation_action": "create_reviewed_test_knowledge_card",
  "approved_candidate_review_action": "approve_candidate_for_creation",
  "candidate_review_artifact_id": "00000000-0000-0000-0000-000000000882",
  "source_handoff_artifact_id": "00000000-0000-0000-0000-000000000871",
  "source_feedback_id": "kf-expired-coupon-boundary",
  "review_history_ids": [
    "00000000-0000-0000-0000-000000000861",
    "00000000-0000-0000-0000-000000000881"
  ],
  "candidate_card_json": {
    "knowledge_type": "existing_test_case_pattern",
    "title": "Expired coupon checkout rejection",
    "summary": "Reviewed checkout cases should include expired coupon rejection.",
    "body": "Use reviewed source evidence before creating reusable knowledge.",
    "source_type": "reviewed_case",
    "source_section": "checkout/coupon",
    "source_quote_or_hash": "sha256:reviewed-case-expired-coupon",
    "related_requirement_ids": ["00000000-0000-0000-0000-000000000121"],
    "related_risk_ids": ["00000000-0000-0000-0000-000000000221"],
    "related_test_case_ids": ["00000000-0000-0000-0000-000000000931"],
    "tags": ["checkout", "coupon", "regression"],
    "confidence": 84,
    "safe_to_show": true,
    "redaction_applied": false,
    "allowed_for_prompt": false
  },
  "source_manifest": {
    "source_artifact_ids": ["00000000-0000-0000-0000-000000000391"],
    "source_hashes": ["sha256:reviewed-case-expired-coupon"],
    "source_span": "case.steps[3]-case.expected_results[0]"
  },
  "duplicate_merge_preconditions": {
    "duplicate_knowledge_card_ids": [],
    "merge_hint": null,
    "resolved": true
  },
  "unsupported_claims": [],
  "prompt_eligibility_decision": "deferred"
}
```

Reviewed creation response shape for a future scoped implementation:

```json
{
  "creation_action": "create_reviewed_test_knowledge_card",
  "creation_status": "ready_for_future_creation",
  "test_knowledge_card_id": null,
  "creation_artifact_id": "00000000-0000-0000-0000-000000000891",
  "review_history_id": "00000000-0000-0000-0000-000000000892",
  "allowed_for_prompt": false,
  "prompt_eligibility_decision": "deferred"
}
```

Reviewed TestKnowledgeCard Creation hard rules:

- Creation input must come from an approved candidate review artifact and must
  preserve the source handoff artifact, source feedback id, ReviewHistory ids,
  candidate_card_json, source manifest, duplicate/merge preconditions, and
  unsupported claims.
- `create_reviewed_test_knowledge_card` is a future scoped creation action,
  not broad CRUD. This contract must not add list/update/delete behavior or
  create rows by itself.
- Future creation must default `allowed_for_prompt=false`. Prompt eligibility
  remains deferred until a later explicit prompt-eligibility workflow.
- Duplicate/merge preconditions must be resolved before creation. Unresolved
  duplicate or merge conflicts must block creation and must not automatically
  merge, archive, replace, delete, relabel, or create card rows.
- Stale, rejected, revision-requested, cross-project, unsafe, unbounded, or
  unsupported source evidence must reject creation with a failure code and must
  not create fallback cards.
- This contract must not add a backend feature API, frontend page, migration,
  broad TestKnowledgeCard CRUD, automatic card creation from model output,
  automatic prompt eligibility, automatic knowledge ingestion, provider call,
  MCP runtime, vector index, embedding, reranking, graph job, artifact mutation
  outside declared creation artifacts, historical evidence mutation,
  generated-case auto-approval, TestCase auto-promotion, runner behavior
  change, report generation behavior change, remote CI provider behavior,
  RBAC, tenants, or permissions.

### 3.5.6 TestKnowledgeCard Prompt Eligibility Contract

This section is contract-only. It defines future human review semantics for
TestKnowledgeCard prompt eligibility and does not add an endpoint, router,
service, worker, queue, frontend page, migration, retrieval runtime change,
vector index, embedding job, reranking, graph job, or provider call.

Allowed prompt eligibility actions:

- `mark_card_prompt_eligible`: human marks a reviewed TestKnowledgeCard
  eligible for future prompt context.
- `deny_card_prompt_eligibility`: human denies eligibility and records why.
- `request_prompt_eligibility_revision`: human requests redaction, source
  evidence, or citation fixes before eligibility can be decided.
- `revoke_card_prompt_eligibility`: human revokes an existing prompt
  eligibility decision and records why the card must leave future prompt
  context.

Prompt eligibility payload shape:

```json
{
  "prompt_eligibility_action": "mark_card_prompt_eligible",
  "test_knowledge_card_id": "00000000-0000-0000-0000-000000000901",
  "reviewer_label": "Default User",
  "review_comment": "Source evidence and redaction were reviewed.",
  "prompt_eligibility_reason": "Reviewed checkout coupon rule is safe and reusable.",
  "creation_artifact_id": "00000000-0000-0000-0000-000000000891",
  "source_manifest_artifact_id": "00000000-0000-0000-0000-000000000892",
  "source_artifact_ids": ["00000000-0000-0000-0000-000000000391"],
  "source_quote_or_hash": "sha256:reviewed-case-expired-coupon",
  "redaction_report_artifact_id": "00000000-0000-0000-0000-000000000893",
  "safe_to_show": true,
  "redaction_applied": false,
  "unsupported_claims": [],
  "allowed_for_prompt": true
}
```

Prompt eligibility response shape for a future scoped implementation:

```json
{
  "prompt_eligibility_action": "mark_card_prompt_eligible",
  "prompt_eligibility_decision": "approved",
  "review_history_id": "00000000-0000-0000-0000-000000000894",
  "prompt_eligibility_artifact_id": "00000000-0000-0000-0000-000000000895",
  "test_knowledge_card_id": "00000000-0000-0000-0000-000000000901",
  "allowed_for_prompt": true
}
```

TestKnowledgeCard Prompt Eligibility hard rules:

- Prompt eligibility requires a reviewed TestKnowledgeCard record,
  safe-to-show evidence, reviewed redaction status, same-project source
  artifacts, source manifest, ReviewHistory ids, and a non-empty prompt
  eligibility reason.
- `allowed_for_prompt=true` must come only from `mark_card_prompt_eligible`
  after human review. It must not be inferred from card creation, model
  confidence, schema validity, source presence, or `safe_to_show=true`.
- `deny_card_prompt_eligibility`,
  `request_prompt_eligibility_revision`, and
  `revoke_card_prompt_eligibility` must keep or set `allowed_for_prompt=false`
  and preserve reviewer rationale.
- Revocation removes the card from future prompt eligibility only; it must not
  delete the TestKnowledgeCard row, mutate source artifacts, or rewrite
  historical ReviewHistory.
- This contract must not change prompt runtime retrieval, deterministic
  retrieval ranking, vector indexes, embeddings, reranking, graph jobs, MCP
  runtime, provider calls, broad TestKnowledgeCard CRUD, automatic
  eligibility, automatic knowledge ingestion, artifact mutation outside
  declared prompt eligibility artifacts, historical evidence mutation,
  generated-case auto-approval, runner behavior, report behavior, RBAC,
  tenants, or permissions.

### 3.5.7 TestKnowledgeCard Retrieval Boundary Contract

This section is contract-only. It defines future read-only selection semantics
for TestKnowledgeCard prompt-context eligibility and does not add an endpoint,
router, service, worker, queue, frontend page, migration, prompt runtime
retrieval implementation, deterministic retrieval behavior change, vector
index, embedding job, reranking, graph job, MCP runtime, or provider call.

Allowed retrieval-boundary action:

- `select_prompt_eligible_cards`: future scoped selection action that evaluates
  prompt-eligible TestKnowledgeCard evidence for prompt-context consideration.
  It records retrieval evidence and exclusion reasons only; it does not run
  retrieval runtime or assemble prompts.

Retrieval boundary payload shape:

```json
{
  "retrieval_boundary_action": "select_prompt_eligible_cards",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "prompt_request_id": "local-prompt-request-001",
  "candidate_test_knowledge_card_ids": [
    "00000000-0000-0000-0000-000000000901"
  ],
  "required_state": "prompt_eligible",
  "required_allowed_for_prompt": true,
  "required_safe_to_show": true,
  "source_manifest_artifact_id": "00000000-0000-0000-0000-000000000892",
  "prompt_eligibility_artifact_ids": [
    "00000000-0000-0000-0000-000000000895"
  ],
  "creation_artifact_ids": [
    "00000000-0000-0000-0000-000000000891"
  ],
  "source_artifact_ids": ["00000000-0000-0000-0000-000000000391"],
  "source_quote_or_hash": "sha256:reviewed-case-expired-coupon",
  "review_history_ids": [
    "00000000-0000-0000-0000-000000000894"
  ],
  "unsupported_claims": []
}
```

Retrieval boundary response shape for a future scoped implementation:

```json
{
  "retrieval_boundary_action": "select_prompt_eligible_cards",
  "selected_test_knowledge_card_ids": [
    "00000000-0000-0000-0000-000000000901"
  ],
  "excluded_cards": [
    {
      "test_knowledge_card_id": "00000000-0000-0000-0000-000000000902",
      "excluded_card_reason": "prompt_eligibility_revoked"
    }
  ],
  "retrieval_evidence_artifact_id": "00000000-0000-0000-0000-000000000896",
  "selection_reason": "Card is prompt_eligible with reviewed safe source evidence.",
  "allowed_for_prompt": true,
  "prompt_eligible": true,
  "safe_to_show": true
}
```

TestKnowledgeCard Retrieval Boundary hard rules:

- `allowed_for_prompt=true` is necessary but not sufficient for selection.
  The card must also be in a current `prompt_eligible` state, `safe_to_show`
  must be true, source manifest and same-project source artifacts must remain
  valid, redaction must be reviewed, and ReviewHistory plus prompt eligibility
  artifact evidence must be present.
- `allowed_for_prompt=false`, `prompt_eligibility_denied`,
  `prompt_eligibility_revision_requested`, `prompt_eligibility_revoked`,
  stale evidence, cross-project evidence, unsafe evidence, missing source
  evidence, unbounded evidence, unsupported claims, redaction failure, source
  manifest mismatch, missing ReviewHistory, or missing prompt eligibility
  artifact evidence must exclude the card and record `excluded_card_reason`.
- `select_prompt_eligible_cards` must not create, approve, archive, delete,
  relabel, merge, or mutate TestKnowledgeCard rows. It must not mutate source
  artifacts, prompt eligibility artifacts, ReviewHistory, KnowledgeEvidence, or
  historical evidence.
- This contract must not add prompt runtime retrieval, deterministic retrieval
  ranking changes, vector indexes, embeddings, reranking, graph jobs, MCP
  runtime, provider calls, broad TestKnowledgeCard CRUD, automatic
  eligibility, automatic knowledge ingestion, artifact mutation outside
  declared retrieval evidence, historical evidence mutation, generated-case
  auto-approval, runner behavior, report behavior, RBAC, tenants, or
  permissions.

### 3.5.8 TestKnowledgeCard Prompt Context Evidence Contract

This section is contract-only. It defines future prompt context evidence
semantics for selected TestKnowledgeCards and does not add an endpoint, router,
service, worker, queue, frontend page, migration, prompt assembly
implementation, prompt runtime execution, provider call, deterministic
retrieval behavior change, vector index, embedding job, reranking, graph job,
MCP runtime, broad CRUD, RBAC, tenants, or permissions.

Allowed prompt-context evidence action:

- `build_prompt_context_evidence`: future scoped evidence action that converts
  retrieval boundary selections into bounded prompt context evidence. It
  records safe entries, source hashes, context manifest links, PromptVersion /
  SkillVersion trace, and omission reason values only; it does not assemble a
  runtime prompt or call a provider.

Prompt context evidence payload shape:

```json
{
  "prompt_context_evidence_action": "build_prompt_context_evidence",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "prompt_request_id": "local-prompt-request-001",
  "ai_task_id": "00000000-0000-0000-0000-000000000701",
  "prompt_version_id": "00000000-0000-0000-0000-000000000711",
  "skill_version_id": "00000000-0000-0000-0000-000000000712",
  "retrieval_boundary_artifact_id": "00000000-0000-0000-0000-000000000896",
  "selected_test_knowledge_card_ids": [
    "00000000-0000-0000-0000-000000000901"
  ],
  "prompt_eligibility_artifact_ids": [
    "00000000-0000-0000-0000-000000000895"
  ],
  "source_manifest_artifact_ids": [
    "00000000-0000-0000-0000-000000000892"
  ],
  "source_artifact_ids": ["00000000-0000-0000-0000-000000000391"],
  "review_history_ids": [
    "00000000-0000-0000-0000-000000000894"
  ],
  "context_manifest_artifact_id": null,
  "max_snippet_chars": 600,
  "safe_to_show": true,
  "redaction_status": "reviewed"
}
```

Prompt context evidence response shape for a future scoped implementation:

```json
{
  "prompt_context_evidence_action": "build_prompt_context_evidence",
  "prompt_context_evidence_artifact_id": "00000000-0000-0000-0000-000000000897",
  "context_manifest_artifact_id": "00000000-0000-0000-0000-000000000372",
  "prompt_trace": {
    "prompt_version_id": "00000000-0000-0000-0000-000000000711",
    "skill_version_id": "00000000-0000-0000-0000-000000000712"
  },
  "context_entries": [
    {
      "test_knowledge_card_id": "00000000-0000-0000-0000-000000000901",
      "knowledge_type": "business_rule",
      "title": "Expired coupon cannot submit order",
      "bounded_snippet": "Expired coupons are rejected during checkout.",
      "source_hash": "sha256:reviewed-case-expired-coupon",
      "retrieval_boundary_artifact_id": "00000000-0000-0000-0000-000000000896",
      "prompt_eligibility_artifact_id": "00000000-0000-0000-0000-000000000895",
      "review_history_id": "00000000-0000-0000-0000-000000000894",
      "source_trace_label": "reviewed-card:expired-coupon",
      "selection_reason": "Prompt-eligible reviewed source evidence."
    }
  ],
  "omitted_cards": [
    {
      "test_knowledge_card_id": "00000000-0000-0000-0000-000000000902",
      "omission_reason": "snippet_bounds_unproven"
    }
  ]
}
```

TestKnowledgeCard Prompt Context Evidence hard rules:

- Prompt context evidence input must come from a retrieval boundary artifact
  and selected TestKnowledgeCard ids. It must preserve PromptVersion,
  SkillVersion, prompt request or AITask id when available, source manifests,
  source artifacts, prompt eligibility artifacts, ReviewHistory, and context
  manifest links.
- Text can enter a prompt context entry only when `safe_to_show=true`,
  redaction is reviewed, source evidence is same-project, retrieval boundary
  evidence is present, and prompt eligibility artifact evidence is present. A
  source hash or source quote/hash pointer must be used instead of text when a
  bounded snippet cannot be proven safe.
- Omitted selected cards must be represented by omitted-card summaries with an
  `omission_reason`; omission must not revoke prompt eligibility, mutate card
  rows, mutate retrieval boundary artifacts, or rewrite ReviewHistory.
- `build_prompt_context_evidence` must not write a runtime `prompt_input.json`,
  call providers, run AITasks, change retrieval ranking, create vector indexes,
  create embeddings, rerank, run graph jobs, invoke MCP runtime, approve cases,
  or mutate historical evidence.
- This contract must not add prompt assembly implementation, prompt runtime
  execution, provider calls, broad TestKnowledgeCard CRUD, automatic
  eligibility, automatic knowledge ingestion, artifact mutation outside
  declared prompt context evidence, historical evidence mutation,
  generated-case auto-approval, runner behavior, report behavior, RBAC,
  tenants, or permissions.

### 3.5.9 TestKnowledgeCard Prompt Context Consumption Contract

This section is contract-only. It defines future prompt context consumption
semantics for AI outputs that cite TestKnowledgeCard prompt context evidence
and does not add an endpoint, router, service, worker, queue, frontend page,
migration, prompt assembly implementation, prompt runtime execution, provider
call, deterministic retrieval behavior change, vector index, embedding job,
reranking, graph job, MCP runtime, broad CRUD, RBAC, tenants, or permissions.

Allowed prompt-context consumption action:

- `consume_prompt_context_evidence`: future scoped citation action that records
  which prompt context evidence entries a future agent consumed, how output
  citations point back to source hashes/context entries, and whether
  `used_knowledge=true` is valid. It does not assemble a runtime prompt, run an
  AITask, call a provider, or generate model citations.

Prompt context consumption payload shape:

```json
{
  prompt_context_consumption_action: consume_prompt_context_evidence,
  project_id: 00000000-0000-0000-0000-000000000101,
  prompt_request_id: local-prompt-request-001,
  ai_task_id: 00000000-0000-0000-0000-000000000701,
  agent_step: case_generation,
  intended_output_artifact_type: case_generation_output,
  prompt_version_id: 00000000-0000-0000-0000-000000000711,
  skill_version_id: 00000000-0000-0000-0000-000000000712,
  prompt_context_evidence_artifact_id: 00000000-0000-0000-0000-000000000897,
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  consumed_context_entry_ids: [ctx-entry-expired-coupon],
  consumed_test_knowledge_card_ids: [
    00000000-0000-0000-0000-000000000901
  ],
  consumed_source_hashes: [sha256:reviewed-case-expired-coupon],
  review_history_ids: [
    00000000-0000-0000-0000-000000000894
  ]
}
```

Prompt context consumption response shape for a future scoped implementation:

```json
{
  prompt_context_consumption_action: consume_prompt_context_evidence,
  prompt_context_consumption_artifact_id: 00000000-0000-0000-0000-000000000898,
  used_knowledge: true,
  prompt_trace: {
    prompt_version_id: 00000000-0000-0000-0000-000000000711,
    skill_version_id: 00000000-0000-0000-0000-000000000712
  },
  citations: [
    {
      citation_id: knowledge-citation-expired-coupon,
      test_knowledge_card_id: 00000000-0000-0000-0000-000000000901,
      prompt_context_evidence_artifact_id: 00000000-0000-0000-0000-000000000897,
      context_entry_id: ctx-entry-expired-coupon,
      source_hash: sha256:reviewed-case-expired-coupon,
      source_artifact_id: 00000000-0000-0000-0000-000000000391,
      source_section: checkout/coupon/reviewed-case,
      review_history_id: 00000000-0000-0000-0000-000000000894,
      citation_status: valid
    }
  ],
  skipped_evidence: [
    {
      context_entry_id: ctx-entry-unsafe-note,
      skip_reason: safe_to_show_false
    }
  ]
}
```

TestKnowledgeCard Prompt Context Consumption hard rules:

- Prompt context consumption input must reference a prompt context evidence
  artifact, context manifest, consumed context entries, consumed
  TestKnowledgeCard ids, source hashes, PromptVersion, SkillVersion,
  ReviewHistory, and intended output artifact type.
- `used_knowledge=false` remains required when no valid prompt context evidence
  is consumed. `used_knowledge=true` is valid only when at least one output
  citation points to consumed prompt context evidence, a consumed source hash or
  source quote/hash pointer, a same-project source artifact, PromptVersion,
  SkillVersion, and ReviewHistory trace.
- Output citations must reference prompt context evidence artifact id,
  context entry id, TestKnowledgeCard id, source hash or source quote/hash
  pointer, source artifact id, source section, and citation status. Unsupported
  claims must remain marked as unsupported instead of being treated as
  knowledge-backed facts.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, or evidence-mismatched input must
  produce skipped evidence summaries, `used_knowledge=false`, or a failure code
  without mutating historical evidence.
- `consume_prompt_context_evidence` must not write runtime `prompt_input.json`,
  assemble prompts, call providers, run AITasks, change retrieval ranking,
  create vector indexes, create embeddings, rerank, run graph jobs, invoke MCP
  runtime, approve cases, or mutate prompt context evidence artifacts.
- This contract must not add prompt assembly implementation, prompt runtime
  execution, provider calls, broad TestKnowledgeCard CRUD, automatic
  eligibility, automatic knowledge ingestion, artifact mutation outside
  declared prompt context consumption, historical evidence mutation,
  generated-case auto-approval, runner behavior, report behavior, RBAC,
  tenants, or permissions.

### 3.5.10 TestKnowledgeCard Prompt Context Audit Summary Contract

This section is contract-only. It defines future read-only audit summary
semantics for prompt context consumption evidence and does not add an endpoint,
router, service, worker, queue, frontend page, report generation behavior,
migration, prompt assembly implementation, prompt runtime execution, provider
call, deterministic retrieval behavior change, vector index, embedding job,
reranking, graph job, MCP runtime, broad CRUD, RBAC, tenants, or permissions.

Allowed prompt-context audit summary action:

- `summarize_prompt_context_consumption`: future scoped summary action that
  records usage status, cited entries, skipped entries, unsupported claims, and
  failure reasons from prompt context consumption evidence. It does not render
  a UI, generate reports, assemble a runtime prompt, run an AITask, call a
  provider, or generate model citations.

Prompt context audit summary payload shape:

```json
{
  prompt_context_audit_summary_action: summarize_prompt_context_consumption,
  project_id: 00000000-0000-0000-0000-000000000101,
  prompt_request_id: local-prompt-request-001,
  ai_task_id: 00000000-0000-0000-0000-000000000701,
  agent_step: case_generation,
  intended_output_artifact_type: case_generation_output,
  prompt_context_consumption_artifact_id: 00000000-0000-0000-0000-000000000898,
  prompt_context_evidence_artifact_id: 00000000-0000-0000-0000-000000000897,
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  used_knowledge: true,
  output_citation_ids: [knowledge-citation-expired-coupon],
  skipped_evidence_ids: [ctx-entry-unsafe-note],
  unsupported_claim_count: 1,
  prompt_version_id: 00000000-0000-0000-0000-000000000711,
  skill_version_id: 00000000-0000-0000-0000-000000000712,
  review_history_ids: [
    00000000-0000-0000-0000-000000000894
  ]
}
```

Prompt context audit summary response shape for a future scoped implementation:

```json
{
  prompt_context_audit_summary_action: summarize_prompt_context_consumption,
  prompt_context_audit_summary_artifact_id: 00000000-0000-0000-0000-000000000899,
  usage_status: knowledge_used,
  used_knowledge: true,
  prompt_trace: {
    prompt_version_id: 00000000-0000-0000-0000-000000000711,
    skill_version_id: 00000000-0000-0000-0000-000000000712
  },
  cited_entries: [
    {
      citation_id: knowledge-citation-expired-coupon,
      test_knowledge_card_id: 00000000-0000-0000-0000-000000000901,
      context_entry_id: ctx-entry-expired-coupon,
      source_hash: sha256:reviewed-case-expired-coupon,
      citation_status: valid
    }
  ],
  skipped_entries: [
    {
      context_entry_id: ctx-entry-unsafe-note,
      skip_reason: safe_to_show_false
    }
  ],
  unsupported_claims_summary: [
    {
      claim_id: claim-without-source,
      reason: missing_consumed_citation
    }
  ],
  review_flags: []
}
```

TestKnowledgeCard Prompt Context Audit Summary hard rules:

- Audit summary input must reference prompt context consumption artifact,
  prompt context evidence artifact, context manifest, `used_knowledge` decision,
  output citations, skipped evidence, unsupported claims, PromptVersion,
  SkillVersion, source hash, and ReviewHistory.
- Audit summary output must be read-only. It may summarize usage status, cited
  entries, skipped entries, unsupported claim summaries, failure reasons, and
  review flags, but it must not invent citations, rewrite `used_knowledge`, or
  mutate prompt context consumption evidence.
- `used_knowledge=true` in an audit summary is valid only when the referenced
  prompt context consumption evidence already recorded valid output citations.
  When consumption evidence is missing, failed, skipped, unsafe, stale,
  mismatched, or citation-incomplete, the summary must use a failure flag,
  skipped entry, or `knowledge_not_used` status.
- Unsupported claims must remain visible as unsupported claims or review
  findings. They must not be converted into cited knowledge by this contract.
- `summarize_prompt_context_consumption` must not write runtime
  `prompt_input.json`, render frontend pages, generate reports, assemble
  prompts, call providers, run AITasks, change retrieval ranking, create vector
  indexes, create embeddings, rerank, run graph jobs, invoke MCP runtime,
  approve cases, or mutate historical evidence.
- This contract must not add frontend page, report generation behavior, prompt
  assembly implementation, prompt runtime execution, provider calls, broad
  TestKnowledgeCard CRUD, automatic eligibility, automatic knowledge ingestion,
  artifact mutation outside declared prompt context audit summary, historical
  evidence mutation, generated-case auto-approval, runner behavior, RBAC,
  tenants, or permissions.

### 3.5.11 TestKnowledgeCard Prompt Context Audit Review Decision Contract

This section is contract-only. It defines future human review decision
semantics for prompt context audit summaries and does not add an endpoint,
router, service, worker, queue, frontend page, report generation behavior,
migration, prompt assembly implementation, prompt runtime execution, provider
call, deterministic retrieval behavior change, vector index, embedding job,
reranking, graph job, MCP runtime, broad CRUD, RBAC, tenants, or permissions.

Allowed prompt-context audit review decision action:

- `review_prompt_context_audit_summary`: future scoped human review action that
  records whether the audit summary evidence is accepted, needs clarification,
  or is rejected for missing evidence, unsupported claim, citation mismatch,
  stale evidence, or cross-project evidence. It does not render a UI, generate
  reports, assemble a runtime prompt, run an AITask, call a provider, create
  prompt eligibility, or generate model citations.

Allowed review actions:

- `accepted`
- `needs_clarification`
- `rejected_for_missing_evidence`
- `rejected_for_unsupported_claim`
- `rejected_for_citation_mismatch`
- `rejected_for_stale_evidence`
- `rejected_for_cross_project_evidence`

Prompt context audit review decision payload shape:

```json
{
  prompt_context_audit_review_decision_action: review_prompt_context_audit_summary,
  project_id: 00000000-0000-0000-0000-000000000101,
  prompt_request_id: local-prompt-request-001,
  ai_task_id: 00000000-0000-0000-0000-000000000701,
  prompt_context_audit_summary_artifact_id: 00000000-0000-0000-0000-000000000899,
  prompt_context_consumption_artifact_id: 00000000-0000-0000-0000-000000000898,
  prompt_context_evidence_artifact_id: 00000000-0000-0000-0000-000000000897,
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  used_knowledge: true,
  usage_status: knowledge_used,
  output_citation_ids: [knowledge-citation-expired-coupon],
  skipped_evidence_ids: [ctx-entry-unsafe-note],
  unsupported_claim_ids: [claim-without-source],
  review_flags: [],
  review_action: accepted,
  reviewer_label: local-reviewer-001,
  reviewer_comment: cited evidence matches consumed prompt context,
  accepted_citation_ids: [knowledge-citation-expired-coupon],
  questioned_citation_ids: [],
  rejected_citation_ids: [],
  follow_up_flags: [],
  prompt_version_id: 00000000-0000-0000-0000-000000000711,
  skill_version_id: 00000000-0000-0000-0000-000000000712,
  review_history_ids: [
    00000000-0000-0000-0000-000000000894
  ]
}
```

Prompt context audit review decision response shape for a future scoped
implementation:

```json
{
  prompt_context_audit_review_decision_action: review_prompt_context_audit_summary,
  prompt_context_audit_review_decision_artifact_id: 00000000-0000-0000-0000-000000000900,
  prompt_context_audit_summary_artifact_id: 00000000-0000-0000-0000-000000000899,
  review_action: accepted,
  reviewer_label: local-reviewer-001,
  review_history_id: 00000000-0000-0000-0000-000000000895,
  accepted_citations: [
    {
      citation_id: knowledge-citation-expired-coupon,
      test_knowledge_card_id: 00000000-0000-0000-0000-000000000901,
      context_entry_id: ctx-entry-expired-coupon,
      source_hash: sha256:reviewed-case-expired-coupon,
      citation_status: accepted
    }
  ],
  questioned_citations: [],
  rejected_citations: [],
  follow_up_flags: [],
  requested_clarification: null,
  prompt_trace: {
    prompt_version_id: 00000000-0000-0000-0000-000000000711,
    skill_version_id: 00000000-0000-0000-0000-000000000712
  },
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  failure_code: null
}
```

TestKnowledgeCard Prompt Context Audit Review Decision hard rules:

- Review decision input must reference prompt context audit summary artifact,
  prompt context consumption artifact, prompt context evidence artifact,
  context manifest, `used_knowledge` decision, usage status, output citations,
  skipped evidence, unsupported claims, PromptVersion, SkillVersion, source
  hash, and ReviewHistory.
- Review decision output must be human review decision evidence only. It may
  record review action, reviewer comment, accepted/questioned/rejected
  citations, follow-up flags, requested clarification, ReviewHistory link,
  failure reasons, and source hash/context manifest references, but it must
  not invent citations, rewrite `used_knowledge`, or mutate audit summary
  evidence.
- `accepted` validates only the audit summary evidence for the scoped review.
  It must not create prompt eligibility, approve TestKnowledgeCard content,
  approve generated cases, alter prompt context consumption evidence, or mark
  skipped evidence as cited.
- `needs_clarification` and rejected actions must preserve cited evidence,
  skipped evidence, unsupported claims, source hashes, PromptVersion,
  SkillVersion, context manifest links, and ReviewHistory instead of deleting
  or rewriting them.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, evidence-mismatched, or audit
  summary-mismatched input must return a failure code and must not append a
  successful ReviewHistory decision.
- `review_prompt_context_audit_summary` must not write runtime
  `prompt_input.json`, render frontend pages, generate reports, assemble
  prompts, call providers, run AITasks, change retrieval ranking, create vector
  indexes, create embeddings, rerank, run graph jobs, invoke MCP runtime,
  approve cases, create prompt eligibility, or mutate historical evidence.
- This contract must not add frontend page, report generation behavior, prompt
  assembly implementation, prompt runtime execution, provider calls, broad
  TestKnowledgeCard CRUD, automatic eligibility, automatic knowledge ingestion,
  artifact mutation outside declared prompt context audit review decision,
  historical evidence mutation, generated-case auto-approval, runner behavior,
  RBAC, tenants, or permissions.

### 3.5.12 TestKnowledgeCard Prompt Context Audit Review Summary Export Contract

This section is contract-only. It defines future summary export semantics for
prompt context audit review decisions and does not add an endpoint, router,
service, worker, queue, frontend page, report generation behavior,
export/download endpoint, migration, prompt assembly implementation, prompt
runtime execution, provider call, deterministic retrieval behavior change,
vector index, embedding job, reranking, graph job, MCP runtime, broad CRUD,
RBAC, tenants, or permissions.

Allowed prompt-context audit review summary export action:

- `export_prompt_context_audit_review_summary`: future scoped summary export
  action that packages review outcome summaries, accepted citation groups,
  questioned citation groups, rejected citation groups, unresolved follow-up
  flags, unsupported claim references, source hashes, context manifest links,
  PromptVersion/SkillVersion trace, and ReviewHistory links from audit review
  decision evidence. It does not render a UI, generate reports, expose a
  download endpoint, assemble a runtime prompt, run an AITask, call a provider,
  create prompt eligibility, or generate model citations.

Prompt context audit review summary export payload shape:

```json
{
  prompt_context_audit_review_summary_export_action: export_prompt_context_audit_review_summary,
  project_id: 00000000-0000-0000-0000-000000000101,
  prompt_request_id: local-prompt-request-001,
  ai_task_id: 00000000-0000-0000-0000-000000000701,
  prompt_context_audit_review_decision_artifact_id: 00000000-0000-0000-0000-000000000900,
  prompt_context_audit_summary_artifact_id: 00000000-0000-0000-0000-000000000899,
  prompt_context_consumption_artifact_id: 00000000-0000-0000-0000-000000000898,
  prompt_context_evidence_artifact_id: 00000000-0000-0000-0000-000000000897,
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  used_knowledge: true,
  usage_status: knowledge_used,
  review_action: accepted,
  review_outcome_summary: accepted_with_one_citation,
  accepted_citation_ids: [knowledge-citation-expired-coupon],
  questioned_citation_ids: [],
  rejected_citation_ids: [],
  unresolved_follow_up_flags: [],
  unsupported_claim_ids: [claim-without-source],
  prompt_version_id: 00000000-0000-0000-0000-000000000711,
  skill_version_id: 00000000-0000-0000-0000-000000000712,
  review_history_ids: [
    00000000-0000-0000-0000-000000000895
  ]
}
```

Prompt context audit review summary export response shape for a future scoped
implementation:

```json
{
  prompt_context_audit_review_summary_export_action: export_prompt_context_audit_review_summary,
  prompt_context_audit_review_summary_export_artifact_id: 00000000-0000-0000-0000-000000000901,
  prompt_context_audit_review_decision_artifact_id: 00000000-0000-0000-0000-000000000900,
  review_outcome_summary: accepted_with_one_citation,
  accepted_citation_group: [
    {
      citation_id: knowledge-citation-expired-coupon,
      test_knowledge_card_id: 00000000-0000-0000-0000-000000000901,
      context_entry_id: ctx-entry-expired-coupon,
      source_hash: sha256:reviewed-case-expired-coupon,
      citation_status: accepted
    }
  ],
  questioned_citation_group: [],
  rejected_citation_group: [],
  unresolved_follow_up_flags: [],
  unsupported_claim_references: [
    {
      claim_id: claim-without-source,
      status: unsupported
    }
  ],
  review_history_links: [
    00000000-0000-0000-0000-000000000895
  ],
  prompt_trace: {
    prompt_version_id: 00000000-0000-0000-0000-000000000711,
    skill_version_id: 00000000-0000-0000-0000-000000000712
  },
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  failure_code: null
}
```

TestKnowledgeCard Prompt Context Audit Review Summary Export hard rules:

- Summary export input must reference prompt context audit review decision
  artifact, prompt context audit summary artifact, prompt context consumption
  artifact, prompt context evidence artifact, context manifest,
  `used_knowledge` decision, usage status, review action, accepted/questioned/
  rejected citations, unresolved follow-up flags, unsupported claims,
  PromptVersion, SkillVersion, source hash, and ReviewHistory.
- Summary export output must be evidence packaging only. It may record review
  outcome summary, accepted citation group, questioned citation group, rejected
  citation group, unresolved follow-up flags, unsupported claim references,
  reviewer comment summary, ReviewHistory links, failure reasons, and source
  hash/context manifest references, but it must not invent citations, rewrite
  `used_knowledge`, or mutate audit review decision evidence.
- Accepted citation groups validate only the reviewed evidence for the scoped
  summary export. They must not create prompt eligibility, approve
  TestKnowledgeCard content, approve generated cases, alter prompt context
  consumption evidence, or mark skipped evidence as cited.
- Questioned/rejected citation groups, needs_clarification, unresolved
  follow-up flags, skipped evidence, and unsupported claims must remain visible
  instead of being deleted, filtered, or rewritten.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, evidence-mismatched,
  audit-summary-mismatched, or review-decision-mismatched input must return a
  failure code and must not append a successful summary export.
- `export_prompt_context_audit_review_summary` must not write runtime
  `prompt_input.json`, render frontend pages, generate reports, expose
  export/download endpoints, assemble prompts, call providers, run AITasks,
  change retrieval ranking, create vector indexes, create embeddings, rerank,
  run graph jobs, invoke MCP runtime, approve cases, create prompt eligibility,
  or mutate historical evidence.
- This contract must not add frontend page, report generation behavior,
  export/download endpoint, prompt assembly implementation, prompt runtime
  execution, provider calls, broad TestKnowledgeCard CRUD, automatic
  eligibility, automatic knowledge ingestion, artifact mutation outside
  declared prompt context audit review summary export, historical evidence
  mutation, generated-case auto-approval, runner behavior, RBAC, tenants, or
  permissions.

### 3.5.13 TestKnowledgeCard Prompt Context Review Discrepancy Tracking Contract

This section is contract-only. It defines future discrepancy tracking semantics
for prompt context review evidence and does not add an endpoint, router,
service, worker, queue, frontend page, report generation behavior,
export/download endpoint, migration, prompt assembly implementation, prompt
runtime execution, provider call, deterministic retrieval behavior change,
vector index, embedding job, reranking, graph job, MCP runtime, broad CRUD,
RBAC, tenants, or permissions.

Allowed prompt-context review discrepancy action:

- `track_prompt_context_review_discrepancy`: future scoped discrepancy action
  that records discrepancy type, affected citation ids, evidence gap summary,
  mismatch reason, reviewer note, severity, resolution status, unresolved
  follow-up flags, unsupported claim references, source hashes, context
  manifest links, PromptVersion/SkillVersion trace, and ReviewHistory links
  from review summary export, audit review decision, audit summary, and prompt
  context consumption evidence. It does not render a UI, generate reports,
  expose a download endpoint, assemble a runtime prompt, run an AITask, call a
  provider, create prompt eligibility, auto-resolve discrepancies, or generate
  model citations.

Prompt context review discrepancy payload shape:

```json
{
  prompt_context_review_discrepancy_action: track_prompt_context_review_discrepancy,
  project_id: 00000000-0000-0000-0000-000000000101,
  prompt_request_id: local-prompt-request-001,
  ai_task_id: 00000000-0000-0000-0000-000000000701,
  prompt_context_audit_review_summary_export_artifact_id: 00000000-0000-0000-0000-000000000901,
  prompt_context_audit_review_decision_artifact_id: 00000000-0000-0000-0000-000000000900,
  prompt_context_audit_summary_artifact_id: 00000000-0000-0000-0000-000000000899,
  prompt_context_consumption_artifact_id: 00000000-0000-0000-0000-000000000898,
  prompt_context_evidence_artifact_id: 00000000-0000-0000-0000-000000000897,
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  used_knowledge: true,
  usage_status: knowledge_used,
  review_action: accepted,
  review_outcome_summary: accepted_with_one_citation,
  discrepancy_type: citation_mismatch,
  affected_citation_ids: [knowledge-citation-expired-coupon],
  evidence_gap_summary: cited source hash differs from audit summary,
  mismatch_reason: source_hash_mismatch,
  reviewer_note: verify cited source before reuse,
  severity: medium,
  resolution_status: open,
  unresolved_follow_up_flags: [verify-source-hash],
  unsupported_claim_ids: [claim-without-source],
  prompt_version_id: 00000000-0000-0000-0000-000000000711,
  skill_version_id: 00000000-0000-0000-0000-000000000712,
  review_history_ids: [
    00000000-0000-0000-0000-000000000895
  ]
}
```

Prompt context review discrepancy response shape for a future scoped
implementation:

```json
{
  prompt_context_review_discrepancy_action: track_prompt_context_review_discrepancy,
  prompt_context_review_discrepancy_artifact_id: 00000000-0000-0000-0000-000000000902,
  prompt_context_audit_review_summary_export_artifact_id: 00000000-0000-0000-0000-000000000901,
  discrepancy_type: citation_mismatch,
  affected_citation_ids: [knowledge-citation-expired-coupon],
  evidence_gap_summary: cited source hash differs from audit summary,
  mismatch_reason: source_hash_mismatch,
  reviewer_note: verify cited source before reuse,
  severity: medium,
  resolution_status: open,
  unresolved_follow_up_flags: [verify-source-hash],
  unsupported_claim_references: [
    {
      claim_id: claim-without-source,
      status: unsupported
    }
  ],
  review_history_links: [
    00000000-0000-0000-0000-000000000895
  ],
  prompt_trace: {
    prompt_version_id: 00000000-0000-0000-0000-000000000711,
    skill_version_id: 00000000-0000-0000-0000-000000000712
  },
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  failure_code: null
}
```

TestKnowledgeCard Prompt Context Review Discrepancy Tracking hard rules:

- Discrepancy input must reference review summary export artifact, audit
  review decision artifact, audit summary artifact, prompt context consumption
  artifact, prompt context evidence artifact, context manifest,
  `used_knowledge` decision, usage status, affected citation ids, unresolved
  follow-up flags, unsupported claim references, PromptVersion, SkillVersion,
  source hash, and ReviewHistory.
- Discrepancy output must be mismatch evidence only. It may record discrepancy
  type, affected citation ids, evidence gap summary, mismatch reason, reviewer
  note, severity, resolution status, unresolved follow-up flags, unsupported
  claim references, ReviewHistory links, failure reasons, and source
  hash/context manifest references, but it must not invent citations, rewrite
  `used_knowledge`, auto-resolve discrepancies, or mutate review summary
  export evidence.
- Resolution status values `open`, `needs_clarification`, `acknowledged`,
  `rejected`, and `resolved_by_later_review` are audit labels only. They must
  not create prompt eligibility, approve TestKnowledgeCard content, approve
  generated cases, alter prompt context consumption evidence, or mark skipped
  evidence as cited.
- Affected citation ids, questioned/rejected citation groups, unresolved
  follow-up flags, skipped evidence, and unsupported claims must remain visible
  instead of being deleted, filtered, or rewritten.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, evidence-mismatched,
  audit-summary-mismatched, review-decision-mismatched, or
  summary-export-mismatched input must return a failure code and must not
  append a successful discrepancy record.
- `track_prompt_context_review_discrepancy` must not write runtime
  `prompt_input.json`, render frontend pages, generate reports, expose
  export/download endpoints, assemble prompts, call providers, run AITasks,
  change retrieval ranking, create vector indexes, create embeddings, rerank,
  run graph jobs, invoke MCP runtime, approve cases, create prompt eligibility,
  auto-resolve discrepancies, or mutate historical evidence.
- This contract must not add frontend page, report generation behavior,
  export/download endpoint, prompt assembly implementation, prompt runtime
  execution, provider calls, broad TestKnowledgeCard CRUD, automatic
  eligibility, automatic knowledge ingestion, artifact mutation outside
  declared prompt context review discrepancy tracking, historical evidence
  mutation, generated-case auto-approval, runner behavior, RBAC, tenants, or
  permissions.

### 3.5.14 TestKnowledgeCard Prompt Context Discrepancy Resolution Review Contract

This section is contract-only. It defines future resolution review semantics
for prompt context discrepancy records and does not add an endpoint, router,
service, worker, queue, frontend page, report generation behavior,
export/download endpoint, migration, prompt assembly implementation, prompt
runtime execution, provider call, deterministic retrieval behavior change,
vector index, embedding job, reranking, graph job, MCP runtime, broad CRUD,
RBAC, tenants, or permissions.

Allowed prompt-context discrepancy resolution review action:

- `review_prompt_context_discrepancy_resolution`: future scoped resolution
  review action that records resolution action, accepted discrepancy ids,
  rejected discrepancy ids, acknowledged discrepancy ids, clarification
  requested fields, reviewer note, resulting resolution status, follow-up
  flags, source hashes, context manifest links, PromptVersion/SkillVersion
  trace, and ReviewHistory links from prompt context review discrepancy,
  review summary export, audit review decision, audit summary, and prompt
  context consumption evidence. It does not render a UI, generate reports,
  expose a download endpoint, assemble a runtime prompt, run an AITask, call a
  provider, create prompt eligibility, auto-resolve discrepancies, or generate
  model citations.

Prompt context discrepancy resolution review payload shape:

```json
{
  prompt_context_discrepancy_resolution_review_action: review_prompt_context_discrepancy_resolution,
  project_id: 00000000-0000-0000-0000-000000000101,
  prompt_request_id: local-prompt-request-001,
  ai_task_id: 00000000-0000-0000-0000-000000000701,
  prompt_context_review_discrepancy_artifact_id: 00000000-0000-0000-0000-000000000902,
  prompt_context_audit_review_summary_export_artifact_id: 00000000-0000-0000-0000-000000000901,
  prompt_context_audit_review_decision_artifact_id: 00000000-0000-0000-0000-000000000900,
  prompt_context_audit_summary_artifact_id: 00000000-0000-0000-0000-000000000899,
  prompt_context_consumption_artifact_id: 00000000-0000-0000-0000-000000000898,
  prompt_context_evidence_artifact_id: 00000000-0000-0000-0000-000000000897,
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  used_knowledge: true,
  usage_status: knowledge_used,
  discrepancy_type: citation_mismatch,
  affected_citation_ids: [knowledge-citation-expired-coupon],
  evidence_gap_summary: cited source hash differs from audit summary,
  mismatch_reason: source_hash_mismatch,
  reviewer_note_from_discrepancy_tracking: verify cited source before reuse,
  severity: medium,
  current_resolution_status: open,
  resolution_action: acknowledge_discrepancy,
  accepted_discrepancy_ids: [discrepancy-citation-mismatch-001],
  rejected_discrepancy_ids: [],
  acknowledged_discrepancy_ids: [discrepancy-citation-mismatch-001],
  clarification_requested_fields: [],
  resulting_resolution_status: acknowledged,
  unresolved_follow_up_flags: [verify-source-hash],
  unsupported_claim_references: [claim-without-source],
  prompt_version_id: 00000000-0000-0000-0000-000000000711,
  skill_version_id: 00000000-0000-0000-0000-000000000712,
  review_history_ids: [
    00000000-0000-0000-0000-000000000895
  ]
}
```

Prompt context discrepancy resolution review response shape for a future
scoped implementation:

```json
{
  prompt_context_discrepancy_resolution_review_action: review_prompt_context_discrepancy_resolution,
  prompt_context_discrepancy_resolution_review_artifact_id: 00000000-0000-0000-0000-000000000903,
  prompt_context_review_discrepancy_artifact_id: 00000000-0000-0000-0000-000000000902,
  resolution_action: acknowledge_discrepancy,
  accepted_discrepancy_ids: [discrepancy-citation-mismatch-001],
  rejected_discrepancy_ids: [],
  acknowledged_discrepancy_ids: [discrepancy-citation-mismatch-001],
  affected_citation_ids: [knowledge-citation-expired-coupon],
  evidence_gap_summary: cited source hash differs from audit summary,
  mismatch_reason: source_hash_mismatch,
  reviewer_note: discrepancy accepted for later evidence refresh,
  severity: medium,
  resulting_resolution_status: acknowledged,
  review_history_links: [
    00000000-0000-0000-0000-000000000896
  ],
  prompt_trace: {
    prompt_version_id: 00000000-0000-0000-0000-000000000711,
    skill_version_id: 00000000-0000-0000-0000-000000000712
  },
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  failure_code: null,
  visible_reason: null
}
```

TestKnowledgeCard Prompt Context Discrepancy Resolution Review hard rules:

- Resolution review input must reference prompt context review discrepancy
  artifact, review summary export artifact, audit review decision artifact,
  audit summary artifact, prompt context consumption artifact, prompt context
  evidence artifact, context manifest, `used_knowledge` decision, usage
  status, discrepancy type, affected citation ids, evidence gap summary,
  mismatch reason, severity, current resolution status, unresolved follow-up
  flags, unsupported claim references, PromptVersion, SkillVersion, source
  hash, and ReviewHistory.
- Resolution review output must be human review evidence only. It may record
  resolution action, accepted discrepancy ids, rejected discrepancy ids,
  acknowledged discrepancy ids, clarification requested fields, reviewer note,
  resulting resolution status, follow-up flags, ReviewHistory links, failure
  reasons, visible reason, and source hash/context manifest references, but it
  must not invent citations, rewrite `used_knowledge`, auto-resolve
  discrepancies, or mutate discrepancy tracking evidence.
- Resolution action values `acknowledge_discrepancy`,
  `reject_discrepancy_resolution`, `request_discrepancy_clarification`, and
  `mark_resolved_by_later_review` are audit labels only. They must not create
  prompt eligibility, approve TestKnowledgeCard content, approve generated
  cases, alter prompt context consumption evidence, or mark skipped evidence
  as cited.
- Accepted discrepancy ids, rejected discrepancy ids, acknowledged discrepancy
  ids, affected citation ids, unresolved follow-up flags, skipped evidence,
  evidence gap summary, mismatch reason, and unsupported claims must remain
  visible instead of being deleted, filtered, or rewritten.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, discrepancy-mismatched,
  evidence-mismatched, audit-summary-mismatched, review-decision-mismatched,
  or summary-export-mismatched input must return a failure code and visible
  reason and must not append a successful resolution review.
- `review_prompt_context_discrepancy_resolution` must not write runtime
  `prompt_input.json`, render frontend pages, generate reports, expose
  export/download endpoints, assemble prompts, call providers, run AITasks,
  change retrieval ranking, create vector indexes, create embeddings, rerank,
  run graph jobs, invoke MCP runtime, approve cases, create prompt eligibility,
  auto-resolve discrepancies, or mutate historical evidence.
- This contract must not add frontend page, report generation behavior,
  export/download endpoint, prompt assembly implementation, prompt runtime
  execution, provider calls, broad TestKnowledgeCard CRUD, automatic
  eligibility, automatic knowledge ingestion, artifact mutation outside
  declared prompt context discrepancy resolution review, historical evidence
  mutation, generated-case auto-approval, runner behavior, RBAC, tenants, or
  permissions.

### 3.5.15 TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export Contract

This section is contract-only. It defines future summary export semantics for
prompt context discrepancy resolution review evidence and does not add an
endpoint, router, service, worker, queue, frontend page, report generation
behavior, export/download endpoint, migration, prompt assembly implementation,
prompt runtime execution, provider call, deterministic retrieval behavior
change, vector index, embedding job, reranking, graph job, MCP runtime, broad
CRUD, RBAC, tenants, or permissions.

Allowed prompt-context discrepancy resolution summary export action:

- `export_prompt_context_discrepancy_resolution_summary`: future scoped
  summary export action that packages resolution outcome summary,
  accepted discrepancy group, rejected discrepancy group, acknowledged
  discrepancy group, clarification requested field group, unresolved follow-up
  flag group, reviewer comment summary, resulting resolution status group,
  source hashes, context manifest links, PromptVersion/SkillVersion trace, and
  ReviewHistory links from discrepancy resolution review, prompt context review
  discrepancy, review summary export, audit review decision, audit summary,
  and prompt context consumption evidence. It does not render a UI, generate
  reports, expose a download endpoint, assemble a runtime prompt, run an
  AITask, call a provider, create prompt eligibility, auto-resolve
  discrepancies, or generate model citations.

Prompt context discrepancy resolution summary export payload shape:

```json
{
  prompt_context_discrepancy_resolution_summary_export_action: export_prompt_context_discrepancy_resolution_summary,
  project_id: 00000000-0000-0000-0000-000000000101,
  prompt_request_id: local-prompt-request-001,
  ai_task_id: 00000000-0000-0000-0000-000000000701,
  prompt_context_discrepancy_resolution_review_artifact_id: 00000000-0000-0000-0000-000000000903,
  prompt_context_review_discrepancy_artifact_id: 00000000-0000-0000-0000-000000000902,
  prompt_context_audit_review_summary_export_artifact_id: 00000000-0000-0000-0000-000000000901,
  prompt_context_audit_review_decision_artifact_id: 00000000-0000-0000-0000-000000000900,
  prompt_context_audit_summary_artifact_id: 00000000-0000-0000-0000-000000000899,
  prompt_context_consumption_artifact_id: 00000000-0000-0000-0000-000000000898,
  prompt_context_evidence_artifact_id: 00000000-0000-0000-0000-000000000897,
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  used_knowledge: true,
  usage_status: knowledge_used,
  resolution_action: acknowledge_discrepancy,
  resulting_resolution_status: acknowledged,
  accepted_discrepancy_ids: [],
  rejected_discrepancy_ids: [],
  acknowledged_discrepancy_ids: [discrepancy-citation-mismatch-001],
  clarification_requested_fields: [],
  affected_citation_ids: [knowledge-citation-expired-coupon],
  evidence_gap_summary: cited source hash differs from audit summary,
  mismatch_reason: source_hash_mismatch,
  reviewer_note: discrepancy accepted for later evidence refresh,
  unresolved_follow_up_flags: [verify-source-hash],
  unsupported_claim_references: [claim-without-source],
  prompt_version_id: 00000000-0000-0000-0000-000000000711,
  skill_version_id: 00000000-0000-0000-0000-000000000712,
  review_history_ids: [
    00000000-0000-0000-0000-000000000895,
    00000000-0000-0000-0000-000000000896
  ]
}
```

Prompt context discrepancy resolution summary export response shape for a
future scoped implementation:

```json
{
  prompt_context_discrepancy_resolution_summary_export_action: export_prompt_context_discrepancy_resolution_summary,
  prompt_context_discrepancy_resolution_summary_export_artifact_id: 00000000-0000-0000-0000-000000000904,
  prompt_context_discrepancy_resolution_review_artifact_id: 00000000-0000-0000-0000-000000000903,
  prompt_context_review_discrepancy_artifact_id: 00000000-0000-0000-0000-000000000902,
  resolution_outcome_summary: acknowledged_discrepancy_with_follow_up,
  accepted_discrepancy_group: [],
  rejected_discrepancy_group: [],
  acknowledged_discrepancy_group: [
    {
      discrepancy_id: discrepancy-citation-mismatch-001,
      affected_citation_ids: [knowledge-citation-expired-coupon]
    }
  ],
  clarification_requested_field_group: [],
  unresolved_follow_up_flag_group: [verify-source-hash],
  reviewer_comment_summary: discrepancy accepted for later evidence refresh,
  resulting_resolution_status_group: [
    {
      status: acknowledged,
      discrepancy_id: discrepancy-citation-mismatch-001
    }
  ],
  review_history_links: [
    00000000-0000-0000-0000-000000000895,
    00000000-0000-0000-0000-000000000896
  ],
  prompt_trace: {
    prompt_version_id: 00000000-0000-0000-0000-000000000711,
    skill_version_id: 00000000-0000-0000-0000-000000000712
  },
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  source_hashes: [sha256:knowledge-source-hash],
  failure_code: null,
  visible_reason: null
}
```

TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export hard
rules:

- Resolution summary export input must reference prompt context discrepancy
  resolution review artifact, prompt context review discrepancy artifact,
  review summary export artifact, audit review decision artifact, audit summary
  artifact, prompt context consumption artifact, prompt context evidence
  artifact, context manifest, `used_knowledge` decision, usage status,
  resolution action, resulting resolution status, accepted discrepancy ids,
  rejected discrepancy ids, acknowledged discrepancy ids, clarification
  requested fields, affected citation ids, evidence gap summary, mismatch
  reason, unresolved follow-up flags, unsupported claim references,
  PromptVersion, SkillVersion, source hash, and ReviewHistory.
- Resolution summary export output must be evidence packaging only. It may
  record resolution outcome summary, accepted discrepancy group, rejected
  discrepancy group, acknowledged discrepancy group, clarification requested
  field group, unresolved follow-up flag group, reviewer comment summary,
  resulting resolution status group, ReviewHistory links, failure reasons,
  visible reason, and source hash/context manifest references, but it must not
  invent citations, rewrite `used_knowledge`, auto-resolve discrepancies, or
  mutate resolution review evidence.
- Resolution outcome groups and resulting resolution status group are audit
  labels only. They must not create prompt eligibility, approve
  TestKnowledgeCard content, approve generated cases, alter prompt context
  consumption evidence, or mark skipped evidence as cited.
- Accepted discrepancy group, rejected discrepancy group, acknowledged
  discrepancy group, clarification requested field group, unresolved follow-up
  flag group, affected citation ids, skipped evidence, evidence gap summary,
  mismatch reason, and unsupported claims must remain visible instead of being
  deleted, filtered, or rewritten.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, discrepancy-mismatched,
  resolution-review-mismatched, evidence-mismatched, audit-summary-mismatched,
  review-decision-mismatched, or summary-export-mismatched input must return a
  failure code and visible reason and must not append a successful resolution
  summary export.
- `export_prompt_context_discrepancy_resolution_summary` must not write runtime
  `prompt_input.json`, render frontend pages, generate reports, expose
  export/download endpoints, assemble prompts, call providers, run AITasks,
  change retrieval ranking, create vector indexes, create embeddings, rerank,
  run graph jobs, invoke MCP runtime, approve cases, create prompt eligibility,
  auto-resolve discrepancies, or mutate historical evidence.
- This contract must not add frontend page, report generation behavior,
  export/download endpoint, prompt assembly implementation, prompt runtime
  execution, provider calls, broad TestKnowledgeCard CRUD, automatic
  eligibility, automatic knowledge ingestion, artifact mutation outside
  declared prompt context discrepancy resolution summary export, historical
  evidence mutation, generated-case auto-approval, runner behavior, RBAC,
  tenants, or permissions.

### 3.5.16 TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff Contract

This section is contract-only. It defines future audit handoff semantics for
prompt context discrepancy resolution summary export evidence and does not add
an endpoint, router, service, worker, queue, frontend page, report generation
behavior, export/download endpoint, external archive integration, migration,
prompt assembly implementation, prompt runtime execution, provider call,
deterministic retrieval behavior change, vector index, embedding job,
reranking, graph job, MCP runtime, broad CRUD, RBAC, tenants, or permissions.

Allowed prompt-context discrepancy resolution audit handoff action:

- `build_prompt_context_discrepancy_resolution_audit_handoff`: future scoped
  audit handoff action that packages handoff summary, evidence chain status,
  included artifact ids, excluded artifact reasons, unresolved follow-up
  flags, unresolved evidence gaps, unsupported claim references, source
  hashes, context manifest links, PromptVersion/SkillVersion trace, and
  ReviewHistory links from discrepancy resolution summary export, discrepancy
  resolution review, prompt context review discrepancy, review summary export,
  audit review decision, audit summary, prompt context consumption, and prompt
  context evidence. It does not render a UI, generate reports, expose a
  download endpoint, integrate with an external archive, assemble a runtime
  prompt, run an AITask, call a provider, upload artifacts, create prompt
  eligibility, auto-resolve discrepancies, or generate model citations.

Prompt context discrepancy resolution audit handoff payload shape:

```json
{
  prompt_context_discrepancy_resolution_audit_handoff_action: build_prompt_context_discrepancy_resolution_audit_handoff,
  project_id: 00000000-0000-0000-0000-000000000101,
  prompt_request_id: local-prompt-request-001,
  ai_task_id: 00000000-0000-0000-0000-000000000701,
  prompt_context_discrepancy_resolution_summary_export_artifact_id: 00000000-0000-0000-0000-000000000904,
  prompt_context_discrepancy_resolution_review_artifact_id: 00000000-0000-0000-0000-000000000903,
  prompt_context_review_discrepancy_artifact_id: 00000000-0000-0000-0000-000000000902,
  prompt_context_audit_review_summary_export_artifact_id: 00000000-0000-0000-0000-000000000901,
  prompt_context_audit_review_decision_artifact_id: 00000000-0000-0000-0000-000000000900,
  prompt_context_audit_summary_artifact_id: 00000000-0000-0000-0000-000000000899,
  prompt_context_consumption_artifact_id: 00000000-0000-0000-0000-000000000898,
  prompt_context_evidence_artifact_id: 00000000-0000-0000-0000-000000000897,
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  used_knowledge: true,
  usage_status: knowledge_used,
  resolution_outcome_summary: acknowledged_discrepancy_with_follow_up,
  accepted_discrepancy_group: [],
  rejected_discrepancy_group: [],
  acknowledged_discrepancy_group: [
    {
      discrepancy_id: discrepancy-citation-mismatch-001,
      affected_citation_ids: [knowledge-citation-expired-coupon]
    }
  ],
  clarification_requested_fields: [],
  clarification_requested_field_group: [],
  resulting_resolution_status_group: [
    {
      status: acknowledged,
      discrepancy_id: discrepancy-citation-mismatch-001
    }
  ],
  affected_citation_ids: [knowledge-citation-expired-coupon],
  evidence_gap_summary: cited source hash differs from audit summary,
  mismatch_reason: source_hash_mismatch,
  unresolved_follow_up_flags: [verify-source-hash],
  unsupported_claim_references: [claim-without-source],
  source_hashes: [sha256:knowledge-source-hash],
  prompt_version_id: 00000000-0000-0000-0000-000000000711,
  skill_version_id: 00000000-0000-0000-0000-000000000712,
  review_history_ids: [
    00000000-0000-0000-0000-000000000895,
    00000000-0000-0000-0000-000000000896
  ]
}
```

Prompt context discrepancy resolution audit handoff response shape for a
future scoped implementation:

```json
{
  prompt_context_discrepancy_resolution_audit_handoff_action: build_prompt_context_discrepancy_resolution_audit_handoff,
  prompt_context_discrepancy_resolution_audit_handoff_artifact_id: 00000000-0000-0000-0000-000000000905,
  prompt_context_discrepancy_resolution_summary_export_artifact_id: 00000000-0000-0000-0000-000000000904,
  handoff_summary: final handoff preserves acknowledged discrepancy and follow-up evidence,
  evidence_chain_status: complete,
  included_artifact_ids: [
    00000000-0000-0000-0000-000000000904,
    00000000-0000-0000-0000-000000000903,
    00000000-0000-0000-0000-000000000902
  ],
  excluded_artifact_reasons: [],
  unresolved_follow_up_flags: [verify-source-hash],
  unresolved_evidence_gaps: [source hash refresh pending],
  unsupported_claim_references: [claim-without-source],
  review_history_links: [
    00000000-0000-0000-0000-000000000895,
    00000000-0000-0000-0000-000000000896
  ],
  prompt_trace: {
    prompt_version_id: 00000000-0000-0000-0000-000000000711,
    skill_version_id: 00000000-0000-0000-0000-000000000712
  },
  context_manifest_artifact_id: 00000000-0000-0000-0000-000000000372,
  source_manifest_ids: [knowledge-source-manifest-001],
  source_hashes: [sha256:knowledge-source-hash],
  failure_code: null,
  visible_reason: null
}
```

TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff hard
rules:

- Audit handoff input must reference prompt context discrepancy resolution
  summary export artifact, prompt context discrepancy resolution review
  artifact, prompt context review discrepancy artifact, review summary export
  artifact, audit review decision artifact, audit summary artifact, prompt
  context consumption artifact, prompt context evidence artifact, context
  manifest, `used_knowledge` decision, usage status, resolution outcome
  summary, accepted discrepancy group, rejected discrepancy group,
  acknowledged discrepancy group, clarification requested fields,
  clarification requested field group, resulting resolution status group,
  affected citation ids, evidence gap summary, mismatch reason, unresolved
  follow-up flags, unsupported claim references, PromptVersion, SkillVersion,
  source hash, and ReviewHistory.
- Audit handoff output must be evidence chain packaging only. It may record
  handoff summary, evidence chain status, included artifact ids, excluded
  artifact reasons, unresolved evidence gaps, unresolved follow-up flags,
  ReviewHistory links, failure reasons, visible reason, source hash, source
  manifest, and context manifest references, but it must not invent citations,
  rewrite `used_knowledge`, auto-resolve discrepancies, mutate resolution
  summary export evidence, or upload artifacts.
- Evidence chain status values are `complete`, `incomplete`, `blocked`, and
  `failed_validation`. They are audit labels only. They must not create prompt
  eligibility, approve TestKnowledgeCard content, approve generated cases,
  alter prompt context consumption evidence, or mark skipped evidence as
  cited.
- Included artifact ids, excluded artifact reasons, unresolved evidence gaps,
  unresolved follow-up flags, affected citation ids, skipped evidence,
  evidence gap summary, mismatch reason, and unsupported claims must remain
  visible instead of being deleted, filtered, or rewritten.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, discrepancy-mismatched,
  resolution-review-mismatched, summary-export-mismatched,
  evidence-mismatched, audit-summary-mismatched, review-decision-mismatched,
  or audit-handoff-mismatched input must return a failure code and visible
  reason and must not append a successful audit handoff.
- `build_prompt_context_discrepancy_resolution_audit_handoff` must not write
  runtime `prompt_input.json`, render frontend pages, generate reports, expose
  export/download endpoints, integrate with an external archive, assemble
  prompts, call providers, run AITasks, change retrieval ranking, create
  vector indexes, create embeddings, rerank, run graph jobs, invoke MCP
  runtime, approve cases, create prompt eligibility, auto-resolve
  discrepancies, upload artifacts, or mutate historical evidence.
- This contract must not add frontend page, report generation behavior,
  export/download endpoint, external archive integration, prompt assembly
  implementation, prompt runtime execution, provider calls, broad
  TestKnowledgeCard CRUD, automatic eligibility, automatic knowledge ingestion,
  artifact mutation outside declared prompt context discrepancy resolution
  audit handoff, historical evidence mutation, generated-case auto-approval,
  runner behavior, RBAC, tenants, or permissions.

### 3.6 Review Candidate Case

`POST /api/case-review/items/{id}/approve`

Request:

```json
{
  "action": "approve_after_edit",
  "edited_case": {
    "title": "Expired coupon cannot submit order",
    "priority": "P0",
    "steps": ["Prepare expired coupon", "Login", "Open checkout", "Select expired coupon", "Submit order"],
    "expected_results": ["Coupon is unavailable or submit fails", "Clear error message is shown"]
  },
  "review_comment": "Added test data preparation step"
}
```

Response 200:

```json
{
  "candidate_id": "00000000-0000-0000-0000-000000000801",
  "status": "approved_after_edit",
  "test_case_id": "00000000-0000-0000-0000-000000000901"
}
```

### 3.7 Test Case Library

`GET /api/test-cases`

Query filters:

| Name | Required | Notes |
|---|---:|---|
| project_id | yes | Limit library results to one project |
| module_id | no | Limit results to one module |
| status | no | TestCase entity status, default includes active records |
| test_type | no | Filter by functional, ui, api, etc. |
| priority | no | Filter by P0/P1/P2/P3 |
| keyword | no | Case-insensitive match against title, steps, expected results, tags, or requirement refs where available |

Response model: `TestCaseListRead`.

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000901",
      "project_id": "00000000-0000-0000-0000-000000000101",
      "module_id": "00000000-0000-0000-0000-000000000201",
      "source_candidate_id": "00000000-0000-0000-0000-000000000801",
      "title": "Expired coupon cannot submit order",
      "priority": "P0",
      "test_type": "functional",
      "precondition": "User has an expired coupon",
      "steps": ["Prepare expired coupon", "Login", "Open checkout", "Select expired coupon", "Submit order"],
      "expected_results": ["Coupon is unavailable or submit fails", "Clear error message is shown"],
      "input_data": {"coupon_state": "expired"},
      "tags": ["coupon", "boundary"],
      "source_type": "ai",
      "review_status": "approved_after_edit",
      "status": "active"
    }
  ],
  "total": 1
}
```

Contract boundary:

- The library lists reviewed TestCase records only. It does not list generated
  candidates that have not been approved.
- V1 does not create or mutate TestCase records through this endpoint.
- AutomationDraft creation, execution, reports, CI/CD quality, RAG runtime, MCP
  runtime, RBAC, tenants, and permissions are outside this API.

## 4. Automation Draft APIs

### 4.1 Create Automation Draft

`POST /api/automation/drafts`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "test_case_id": "00000000-0000-0000-0000-000000000901",
  "requirement_id": null,
  "target_framework": "pytest",
  "prompt_version": "automation_draft_generation:v1",
  "skill_version": "automation-draft-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-automation-draft"
}
```

Response 202:

```json
{
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "ai_task_id": "00000000-0000-0000-0000-000000001002",
  "status": "pending"
}
```

### 4.2 Get Automation Draft

`GET /api/automation/drafts/{id}`

Response 200 returns AutomationDraft read model with `draft_code`, `target_framework`, `suggested_file_path`, `execution_notes`, `risk_notes`, and artifacts.

### 4.3 Edit Automation Draft

`PATCH /api/automation/drafts/{id}`

Request:

```json
{
  "draft_code": "def test_coupon_rule():
    assert True
",
  "suggested_file_path": "tests/test_coupon_rule.py",
  "review_comment": "Adjusted fixture name"
}
```

Response 200:

```json
{
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "status": "edited"
}
```

### 4.4 Approve Automation Draft

`POST /api/automation/drafts/{id}/approve`

Request:

```json
{
  "action": "approve",
  "review_comment": "Draft is safe to execute"
}
```

Response 200:

```json
{
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "status": "approved"
}
```

AutomationDraft uses `edit -> edited -> approve -> approved`. It does not use `approve_after_edit`.

Review history side effect:

- Successful candidate review, AutomationDraft edit/approval, UnitTestPatch
  approval/rejection, and QualityGateDecision compute/recompute actions append
  local ReviewHistory records where Slice 21 implements the hook.
- The history side effect must not change whether the original action is
  allowed. Existing state-machine validation remains authoritative.
- Failed validation, forbidden transitions, missing entities, and rejected
  payloads must not append successful ReviewHistory records.

## 5. CI/CD Quality APIs

CI/CD Quality APIs are the page-level workflow contract for `CI/CD 质量中心`.
They may create or return generic `AITask`, `TestRun`, `FailureAnalysis`, and
`Report` records, but the endpoint names stay under `/api/cicd` so the frontend
can drive the CI/CD quality workflow without guessing cross-module orchestration.

Slice 15 foundation boundary:

- Slice 15 implements only local-first CI/CD evidence setup:
  `POST /api/cicd/runs`, `GET /api/cicd/runs`,
  `GET /api/cicd/runs/{id}`, and `POST /api/cicd/runs/{id}/analyze`.
- Slice 15 supports `source_type=local_diff` and manual local inputs only,
  `trigger_type=manual`, and `provider=local`.
- Slice 15 may create `CICDRun`, `CICDChangedFile`, `AITask`, `Artifact`, and
  risk analysis evidence.
- Slice 15 must not create `UnitTestPatch`, `TestRun`, `QualityGateDecision`,
  `FailureAnalysis`, or `Report` records.
- Endpoints in sections 5.5-5.13 are Slice 16+ unless a later task explicitly
  narrows and activates them.
- V1 does not integrate remote CI providers, webhooks, PR comments, merge,
  push, release, deployment, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions in Slice 15.
- Slice 20 adds import-only CI metadata evidence through
  `POST /api/cicd/runs/import`. It stores remote CI facts as local evidence but
  must not call remote CI provider APIs, receive webhooks, trigger pipelines,
  rerun jobs, post PR comments, deploy, release, store credentials, or update
  remote statuses.

### 5.1 Create CI/CD Run

`POST /api/cicd/runs`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "repository_id": "00000000-0000-0000-0000-000000000301",
  "source_type": "local_diff",
  "diff_text": "diff --git a/app/coupon.py b/app/coupon.py\n...",
  "base_ref": "main",
  "head_ref": "HEAD"
}
```

Rules:

- `diff_text` is optional but recommended in Slice 15. When supplied, the API
  persists CICDChangedFile rows and a `changed_files.json` artifact.
- If `diff_text` is omitted, the run remains `created` with no changed files
  until manual changed-file evidence is supplied by a later task.
- `source_type` must be `local_diff` or `manual_check`.
- `trigger_type` is implicitly `manual`; `provider` is implicitly `local`.
- Requests for `github_actions`, `gitlab_ci`, `jenkins`, webhook, PR, scheduled,
  merge, release, or deployment behavior must be rejected or ignored as
  out-of-scope for Slice 15.

Response 202:

```json
{
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "status": "created"
}
```

### 5.2 List CI/CD Runs

`GET /api/cicd/runs`

Query parameters:

```text
project_id optional uuid
repository_id optional uuid
status optional string
quality_gate_status optional pending|passed|failed|needs_review
```

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000001101",
      "project_id": "00000000-0000-0000-0000-000000000101",
      "repository_id": "00000000-0000-0000-0000-000000000301",
      "source_type": "local_diff",
      "trigger_type": "manual",
      "provider": "local",
      "base_ref": "main",
      "head_ref": "HEAD",
      "overall_risk": "medium",
      "quality_gate_status": "pending",
      "status": "created"
    }
  ],
  "total": 1
}
```

### 5.3 Get CI/CD Run

`GET /api/cicd/runs/{id}`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000001101",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "repository_id": "00000000-0000-0000-0000-000000000301",
  "summary": "Coupon amount boundary change",
  "overall_risk": "medium",
  "quality_gate_status": "pending",
  "status": "analyzed",
  "changed_files": [
    {
      "path": "app/coupon.py",
      "old_path": null,
      "change_type": "modified",
      "language": "python",
      "file_role": "source",
      "risk_level": "medium",
      "risk_reasons": ["source file changed"],
      "lines_added": 12,
      "lines_deleted": 4
    }
  ],
  "analysis_artifacts": [
    {
      "artifact_type": "risk_analysis",
      "file_path": "artifacts/projects/00000000-0000-0000-0000-000000000101/cicd-quality/00000000-0000-0000-0000-000000001101/risk_analysis.json"
    }
  ],
  "unit_test_patches": [],
  "test_runs": [],
  "quality_gate_decision": null,
  "reports": []
}
```

### 5.4 Analyze CI/CD Run

`POST /api/cicd/runs/{id}/analyze`

Request:

```json
{
  "prompt_version": "cicd_change_analysis:v1",
  "skill_version": "regression-selection-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-cicd-analysis"
}
```

Response 202 returns AITask reference.

Rules:

- Analyze uses deterministic mock output in V1.
- Analyze creates a succeeded AITask and a `risk_analysis.json` artifact owned by
  the CICDRun.
- Analyze updates `CICDRun.status` to `analyzed`.
- Analyze may update `CICDRun.overall_risk` from changed file risks.
- Analyze does not create UnitTestPatch, TestRun, QualityGateDecision,
  FailureAnalysis, or Report records in Slice 15.

### 5.4b Import CI Run Metadata

`POST /api/cicd/runs/import`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "repository_id": "00000000-0000-0000-0000-000000000301",
  "source_type": "ci_import",
  "provider": "github_actions",
  "trigger_type": "imported",
  "external_run_id": "123456",
  "pipeline_name": "CI",
  "job_name": "pytest",
  "conclusion": "success",
  "status": "completed",
  "base_ref": "main",
  "head_ref": "feature/coupon-boundary",
  "commit_sha": "abc123",
  "started_at": "2026-07-01T01:00:00Z",
  "finished_at": "2026-07-01T01:05:00Z",
  "external_url": "https://example.invalid/runs/123456",
  "changed_files": [
    {
      "path": "app/coupon.py",
      "old_path": null,
      "change_type": "modified",
      "lines_added": 12,
      "lines_deleted": 4
    }
  ],
  "artifact_references": [
    {
      "name": "pytest report",
      "kind": "test_report",
      "external_url": "https://example.invalid/artifacts/1"
    }
  ]
}
```

Response 202:

```json
{
  "cicd_run_id": "00000000-0000-0000-0000-000000001201",
  "source_type": "ci_import",
  "provider": "github_actions",
  "trigger_type": "imported",
  "import_status": "imported",
  "quality_gate_status": "pending",
  "ci_conclusion": "success",
  "created_artifacts": [
    {
      "artifact_type": "ci_run_metadata",
      "file_name": "ci_run_metadata.json"
    },
    {
      "artifact_type": "changed_files",
      "file_name": "changed_files.json"
    }
  ]
}
```

Rules:

- `source_type` must be `ci_import`.
- `trigger_type` is `imported` for persisted imported CI runs. The server may
  default it to `imported` when omitted, but it must not store imported runs as
  webhook, PR, scheduled, or remote-triggered runs.
- `provider` is an inert label. Allowed labels may include `imported`,
  `github_actions`, `gitlab_ci`, `jenkins`, `circleci`, `buildkite`, and
  `other`, but the label must not enable provider behavior.
- `conclusion` may be `success`, `failure`, `cancelled`, `skipped`,
  `timed_out`, or `unknown`.
- Imported CI conclusion, external run id, job name, commit SHA, external URL,
  timestamps, duration, and provider status are written to
  `ci_run_metadata.json` Artifact content and metadata. They are not CICDRun
  columns unless a later contract explicitly promotes them.
- The endpoint may create CICDRun, CICDChangedFile, `ci_run_metadata`, and
  `changed_files` evidence.
- The endpoint must not create QualityGateDecision, TestRun, UnitTestPatch,
  FailureAnalysis, Report, merge/release records, or remote status updates.
- Artifact references are inert references only. Chtest stores the reference
  metadata but must not download, authenticate to, fetch logs from, execute, or
  mutate `external_url` targets.
- Imported artifact reference display is a read-only UI concept. Each reference
  is an external metadata label, not a local Artifact file, unless a separate
  persisted local Artifact row explicitly exists.
- Imported artifact reference rows must show inert status, local-openability
  status, `remote_fetch_performed=false` from the owning `ci_run_metadata`
  artifact metadata, and the external URL as reference text only.
- Imported artifact references are not locally openable and must not receive
  `GET /api/artifacts/{artifact_id}/download` links.
- Duplicate imported external runs may be rejected per project/repository/
  provider/external_run_id with `CI_IMPORT_DUPLICATE_EXTERNAL_RUN`.

Rejection rules:

- Malformed payloads, missing required fields, unsupported conclusions, or
  invalid changed files return `INVALID_CI_IMPORT_PAYLOAD`.
- Webhook payload fields, event action fields, signatures, delivery ids, or
  callback URLs return `CI_IMPORT_CONTROL_FIELD_REJECTED`.
- Trigger, rerun, cancel, workflow dispatch, schedule, PR comment, commit status
  update, branch protection, merge, deploy, release, tag, publish, or environment
  promotion fields return `CI_IMPORT_CONTROL_FIELD_REJECTED`.
- Tokens, secrets, OAuth fields, PATs, private keys, passwords, credential ids,
  or organization permission fields return `CI_IMPORT_CREDENTIAL_REJECTED`.
- Requests that treat provider labels as remote operations return
  `CI_IMPORT_UNSUPPORTED_PROVIDER_OPERATION`.
- Requests to fetch external artifacts, logs, or remote URLs return
  `CI_IMPORT_EXTERNAL_FETCH_FORBIDDEN`.

### 5.5+ Slice 16 And Later Endpoints

The endpoints below are contract placeholders for Slice 16+ work:

- `POST /api/cicd/runs/{id}/unit-test-patches`
- `POST /api/cicd/unit-test-patches/{id}/approve`
- `POST /api/cicd/unit-test-patches/{id}/reject`
- `POST /api/cicd/unit-test-patches/{id}/apply`
- `POST /api/cicd/runs/{id}/run-new-tests`
- `POST /api/cicd/runs/{id}/select-regression`
- `POST /api/cicd/runs/{id}/run-regression`
- `POST /api/cicd/runs/{id}/quality-gate`
- `POST /api/cicd/runs/{id}/generate-report`

Do not implement these endpoints in Slice 15.

### 5.5 Generate Unit Test Patch

`POST /api/cicd/runs/{id}/unit-test-patches`

Request:

```json
{
  "target_framework": "pytest",
  "prompt_version": "unit_test_generation:v1",
  "skill_version": "unit-test-generation-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-unit-test-generator"
}
```

Response 202:

```json
{
  "unit_test_patch_id": "00000000-0000-0000-0000-000000001201",
  "status": "generated"
}
```

Rules:

- The endpoint creates a succeeded mock UnitTestAgent AITask in V1.
- The endpoint must run PatchScopeGate before returning the candidate.
- Generated UnitTestPatch records start as `generated`, `scope_validated`,
  or `scope_rejected` depending on gate result.
- The patch must remain review-gated; this endpoint must not apply patches or
  mutate repository files.
- `scope_gate_result_json` must be returned by the read model for review UI.
- The endpoint must not create TestRun, QualityGateDecision, Report, merge,
  push, release, deployment, or remote CI provider side effects.

### 5.6 Approve Unit Test Patch

`POST /api/cicd/unit-test-patches/{id}/approve`

Request:

```json
{
  "action": "approve",
  "review_comment": "Only tests/ is modified"
}
```

Response 200:

```json
{
  "unit_test_patch_id": "00000000-0000-0000-0000-000000001201",
  "status": "approved"
}
```

### 5.7 Reject Unit Test Patch

`POST /api/cicd/unit-test-patches/{id}/reject`

Request:

```json
{
  "review_comment": "Patch does not cover the changed branch."
}
```

Response 200:

```json
{
  "unit_test_patch_id": "00000000-0000-0000-0000-000000001201",
  "status": "rejected"
}
```

### 5.8 Apply Unit Test Patch

`POST /api/cicd/unit-test-patches/{id}/apply`

Request:

```json
{
  "confirm_scope_gate_result": true
}
```

Response 200:

```json
{
  "unit_test_patch_id": "00000000-0000-0000-0000-000000001201",
  "status": "applied",
  "applied_artifact_id": "00000000-0000-0000-0000-000000001211"
}
```

Rules:

- Only `awaiting_review` or `scope_validated` patches can be approved.
- `scope_rejected` patches cannot be approved.
- Approval records the user's review comment and keeps the patch immutable.
- Only `approved` UnitTestPatch records can be applied.
- PatchScopeGate must pass before application.
- Application must fail with `PATCH_SCOPE_REJECTED` when the patch modifies paths outside allowed test directories.

### 5.9 Run New Tests

`POST /api/cicd/runs/{id}/run-new-tests`

Request:

```json
{
  "unit_test_patch_id": "00000000-0000-0000-0000-000000001201",
  "test_command_id": "00000000-0000-0000-0000-000000000302"
}
```

Response 202:

```json
{
  "test_run_id": "00000000-0000-0000-0000-000000001301",
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "status": "queued"
}
```

Rules:

- The endpoint creates a generic TestRun with `cicd_run_id` set.
- The endpoint requires an applied UnitTestPatch when `unit_test_patch_id` is provided.
- TestRun evidence must include stdout/stderr/runtime artifacts through the
  existing TestRun artifact contract.
- This endpoint must not compute QualityGateDecision or create Reports.

### 5.10 Select Regression

`POST /api/cicd/runs/{id}/select-regression`

Request:

```json
{
  "skill_version": "regression-selection-skill:v1",
  "candidate_test_command_ids": ["00000000-0000-0000-0000-000000000302"]
}
```

Response 200:

```json
{
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "regression_plan_artifact_id": "00000000-0000-0000-0000-000000001221",
  "recommended_test_command_ids": ["00000000-0000-0000-0000-000000000302"],
  "reasons": ["Changed source branch is covered by pytest unit command."]
}
```

RegressionPlan is stored as `regression_plan.json` artifact in V1, not as a separate database table.

### 5.11 Run Regression

`POST /api/cicd/runs/{id}/run-regression`

Request:

```json
{
  "regression_plan_artifact_id": "00000000-0000-0000-0000-000000001221",
  "test_command_ids": ["00000000-0000-0000-0000-000000000302"]
}
```

Response 202:

```json
{
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "test_run_ids": ["00000000-0000-0000-0000-000000001302"],
  "status": "tests_running"
}
```

Rules:

- Each regression command creates a generic TestRun with `cicd_run_id` set.
- V1 regression execution must use allowed TestCommand records.
- Regression execution must not run arbitrary shell strings.
- This endpoint must not compute QualityGateDecision or create Reports.

### 5.12 Compute Quality Gate

`POST /api/cicd/runs/{id}/quality-gate`

Request:

```json
{
  "include_failure_analysis": true
}
```

Response 200:

```json
{
  "quality_gate_decision_id": "00000000-0000-0000-0000-000000001401",
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "status": "passed",
  "summary": "Patch scope, new tests, and regression passed with evidence.",
  "blocking_reasons": []
}
```

Rules:

- A recompute always creates a new QualityGateDecision record and updates `CICDRun.quality_gate_status`.
- Missing required evidence returns `needs_review`, not `passed`.
- `passed` requires PatchScopeGate pass evidence, new-test evidence, regression
  evidence or a documented low-risk waiver, and no failed TestRun evidence.
- `failed` requires blocking reasons, including scope rejection, failed tests,
  failed regression, or high-risk uncovered changes.
- QualityGateDecision does not trigger merge, push, release, deployment, remote
  CI provider status updates, or PR comments.

### 5.12.1 Quality Gate Evidence Summary

Slice 28 may show a read-only quality gate evidence summary in the CI/CD
Quality Center. The summary is derived from the latest `QualityGateDecision`,
its `status_detail`, `blocking_reasons`, `evidence_artifact_ids`, and existing
Artifact metadata. It does not require a new endpoint.

Frontend summary rows may preserve:

```json
{
  "evidence_key": "unit_test_patch",
  "label": "UnitTestPatch",
  "status": "applied",
  "required": true,
  "blocking": false,
  "artifact_id": "00000000-0000-0000-0000-000000001211",
  "download_url": "/api/artifacts/00000000-0000-0000-0000-000000001211/download",
  "availability": "local_artifact"
}
```

Rules:

- Quality gate evidence summary rows are presentation-only and derived from
  existing `QualityGateDecisionRead` fields and Artifact metadata already
  available to the UI.
- Required evidence rows must cover UnitTestPatch/PatchScopeGate, new-test
  evidence, and regression evidence.
- `blocking_reasons` must remain visible and must not be hidden behind a
  passed/failed badge.
- Missing required evidence must remain visible as unavailable evidence and
  must not be shown as downloadable or passing evidence.
- Rows may expose local open links only for persisted local Artifact ids through
  `GET /api/artifacts/{artifact_id}/download`.
- TestRun ids, metric-like status details, and missing evidence are structured
  evidence references, not local Artifact files, unless they explicitly cite a
  persisted Artifact id.
- This summary must not mutate QualityGateDecision, CICDRun, UnitTestPatch,
  TestRun, Artifact, Report, FailureAnalysis, CI metadata, or review history.
- Slice 28 must not change quality gate computation, report generation, runner
  execution, remote CI provider behavior, external artifact fetch, PR comments,
  commit statuses, deploy/release controls, credentials, RBAC, tenants,
  permissions, RAG runtime, or MCP runtime.

### 5.13 Generate CI/CD Quality Report

`POST /api/cicd/runs/{id}/generate-report`

Request:

```json
{
  "report_format": ["markdown", "html", "json"]
}
```

Response 202:

```json
{
  "report_id": "00000000-0000-0000-0000-000000001501",
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "status": "generating"
}
```

Rules:

- The endpoint creates a generic Report with `report_type=cicd_quality`.
- The report conclusion must cite QualityGateDecision and evidence artifacts.
- The report must include `quality_gate.json`, test/regression evidence, and
  UnitTestPatch/PatchScopeGate artifacts when available.
- The report must not override QualityGateDecision status without evidence.

## 6. Test Run APIs

Test Run APIs execute approved pytest, minimal Playwright, Newman API, or
JMeter non-GUI work and return evidence records. They are local-first and
allowlisted: the backend assembles or validates commands from an approved
AutomationDraft or configured TestCommand. Clients must not submit arbitrary
shell strings.

### 6.1 Create Test Run

`POST /api/test-runs`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "test_command_id": "00000000-0000-0000-0000-000000000302",
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "reason": "run approved automation draft",
  "runner_mode": "local_subprocess"
}
```

Request rules:

- Exactly one execution source is required: approved `automation_draft_id` or
  configured `test_command_id`.
- `automation_draft_id` must reference an AutomationDraft with
  `status=approved` and `target_framework` matching the requested runner:
  `pytest` for `local_subprocess`, `playwright` for `playwright_local`.
- `test_command_id` must reference a configured TestCommand with
  `command_type=pytest`, `command_type=playwright`, `command_type=newman`, or
  `command_type=jmeter` and passing allowlist validation.
- `runner_mode` is optional and defaults to `local_subprocess` for pytest.
  Playwright minimal execution uses `runner_mode=playwright_local`. Newman API
  execution uses `runner_mode=newman_local`. JMeter local execution uses
  `runner_mode=jmeter_local`.
- V1 does not expose Docker runner or browser grid selection through this
  endpoint.
- `cicd_run_id` is not accepted by this workbench endpoint. CI/CD
  orchestration stays under `/api/cicd`.

Response 202:

```json
{
  "id": "00000000-0000-0000-0000-000000001301",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "test_command_id": null,
  "tool_invocation_id": "00000000-0000-0000-0000-000000001302",
  "status": "queued",
  "name": "pytest approved draft",
  "command": "python -m pytest tests/test_coupon_rule.py -q --junitxml=artifacts/junit.xml",
  "working_directory": "/Users/yanchen/VscodeProject/sample-app",
  "runner_mode": "local_subprocess",
  "run_workspace": "artifacts/projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/workspace",
  "repository_readonly": true,
  "network_enabled": false,
  "runtime_artifact_ids": ["00000000-0000-0000-0000-000000001201"],
  "dependency_snapshot_artifact_id": "00000000-0000-0000-0000-000000001202",
  "environment_snapshot_artifact_id": "00000000-0000-0000-0000-000000001203",
  "exit_code": null,
  "duration_ms": null,
  "parsed_result": {},
  "test_results": [],
  "artifacts": []
}
```

The created TestRun must record runner sandbox metadata: `runner_mode`,
`run_workspace`, `repository_readonly`, `network_enabled`,
`runtime_artifact_ids`, `dependency_snapshot_artifact_id`, and
`environment_snapshot_artifact_id`.

### 6.2 Get Test Run

`GET /api/test-runs/{id}`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000001301",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "test_command_id": null,
  "tool_invocation_id": "00000000-0000-0000-0000-000000001302",
  "status": "passed",
  "name": "pytest approved draft",
  "command": "python -m pytest tests/test_coupon_rule.py -q --junitxml=artifacts/junit.xml",
  "working_directory": "/Users/yanchen/VscodeProject/sample-app",
  "runner_mode": "local_subprocess",
  "run_workspace": "artifacts/projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/workspace",
  "repository_readonly": true,
  "network_enabled": false,
  "runtime_artifact_ids": ["00000000-0000-0000-0000-000000001201"],
  "dependency_snapshot_artifact_id": "00000000-0000-0000-0000-000000001202",
  "environment_snapshot_artifact_id": "00000000-0000-0000-0000-000000001203",
  "exit_code": 0,
  "duration_ms": 3560,
  "parsed_result": {
    "total": 3,
    "passed": 3,
    "failed": 0,
    "skipped": 0,
    "error": 0
  },
  "test_results": [
    {
      "id": "00000000-0000-0000-0000-000000001331",
      "project_id": "00000000-0000-0000-0000-000000000101",
      "test_run_id": "00000000-0000-0000-0000-000000001301",
      "test_name": "tests/test_coupon.py::test_expired_coupon",
      "test_file": "tests/test_coupon.py",
      "status": "passed",
      "duration_ms": 123,
      "failure_message": null,
      "failure_artifact_ids": [],
      "metadata": {"classname": "tests.test_coupon"}
    }
  ],
  "artifacts": [
    {"artifact_type": "runtime_manifest", "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/runtime_manifest.json"},
    {"artifact_type": "dependency_snapshot", "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/dependency_snapshot.json"},
    {"artifact_type": "environment_snapshot", "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/environment_snapshot.json"},
    {"artifact_type": "stdout", "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/stdout.log"}
  ]
}
```

Response model: `TestRunRead` with embedded `TestResultRead` items.

### 6.2.1 Execution Run Manifest

Slice 29 may show a read-only execution run manifest in execution pages. The
manifest is derived from existing `TestRunRead` fields, `TestRunRead.artifacts`,
and existing Artifact metadata. It does not require a new endpoint.

Frontend manifest rows may preserve:

```json
{
  "manifest_key": "runtime_manifest",
  "label": "Runtime manifest",
  "status": "available",
  "required": true,
  "artifact_id": "00000000-0000-0000-0000-000000001201",
  "artifact_type": "runtime_manifest",
  "download_url": "/api/artifacts/00000000-0000-0000-0000-000000001201/download",
  "availability": "local_artifact"
}
```

Rules:

- Execution run manifest rows are presentation-only and derived from existing
  `TestRunRead` fields and Artifact metadata already available to the UI.
- Manifest must show command, working directory, `runner_mode`,
  `run_workspace`, repository read-only policy, network policy, exit code,
  duration, parsed result summary, and artifact availability.
- Manifest must keep runtime artifact ids, dependency snapshot id, and
  environment snapshot id visible. Missing snapshot ids must be shown as
  unavailable evidence, not hidden.
- `network_enabled=false` should be displayed as local network disabled.
  `network_enabled=true` must remain visible as an explicit network policy; it
  must not be converted into a generic passed/safe badge.
- Rows may expose local open links only for persisted local Artifact ids through
  `GET /api/artifacts/{artifact_id}/download`.
- TestResult rows, parsed result metrics, missing snapshot ids, and raw command
  metadata are structured evidence references, not local Artifact files, unless
  they explicitly cite a persisted Artifact id.
- This manifest must not mutate TestRun, TestResult, Artifact, Report,
  FailureAnalysis, QualityGateDecision, AutomationDraft, ToolDefinition,
  ToolInvocation, CI metadata, or review history.
- Slice 29 must not change runner execution, command assembly, allowlists,
  TestRun state transitions, report generation, failure analysis, quality gate
  computation, remote provider behavior, PR comments, deploy/release controls,
  credentials, RBAC, tenants, permissions, RAG runtime, or MCP runtime.

### 6.3 List Test Results

`GET /api/test-runs/{id}/results`

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000001331",
      "test_name": "tests/test_coupon.py::test_expired_coupon",
      "test_file": "tests/test_coupon.py",
      "status": "passed",
      "duration_ms": 123,
      "failure_message": null
    }
  ],
  "total": 1
}
```

Contract boundary:

- V1 Test Run APIs execute pytest and minimal Playwright work only through
  backend-controlled command assembly or configured TestCommand allowlists.
- The target repository is readonly when possible; generated AutomationDraft
  code is copied to a Chtest-managed runtime artifact/workspace before
  execution.
- Network access is disabled by default and must be represented in
  `network_enabled`.
- Runtime manifest, dependency snapshot, environment snapshot, stdout, stderr,
  and JUnit files are represented as artifact metadata when available.
- Playwright minimal execution may additionally return `playwright_trace` and
  `screenshot` artifacts.
- Newman API execution may additionally return `newman_json` and optional
  `junit` artifacts.
- This API does not create reports, QualityGateDecision records, CI/CD workflow
  state, FailureAnalysis records, RAG runtime calls, MCP runtime dependencies,
  RBAC, tenants, or permissions.

### 6.4 Local Artifact Access

`GET /api/artifacts/{artifact_id}/download`

Purpose: return the content of a persisted local Artifact as read-only evidence.

Response 200:

- Body: raw artifact bytes.
- `Content-Type`: recorded Artifact `mime_type`, defaulting to
  `application/octet-stream` if missing.
- `Content-Disposition`: attachment with a safe filename derived from Artifact
  `file_path`.

Rules:

- The server must load the Artifact row by id and read only its persisted
  `file_path` through the local artifact store.
- The request body must be empty; clients must not provide a path.
- The resolved path must stay under the configured artifact root.
- Missing Artifact rows return `ARTIFACT_NOT_FOUND`.
- Missing files return `ARTIFACT_FILE_NOT_FOUND`.
- Unsafe paths return `ARTIFACT_PATH_UNSAFE`.
- External imported artifact references, including CI import `external_url`
  references, return `ARTIFACT_NOT_LOCAL`.
- The endpoint is read-only and must not mutate Artifact rows, artifact files,
  TestRun state, Report, FailureAnalysis, QualityGateDecision, remote providers,
  or imported CI metadata.
- The endpoint must not fetch external URLs, call remote CI providers, download
  remote artifact content, create signed URLs, upload files, delete files,
  expose arbitrary local filesystem paths, or introduce RBAC/tenant/permission
  behavior.

### 6.5 Playwright Minimal Execution

Playwright minimal execution reuses `POST /api/test-runs` and
`GET /api/test-runs/{id}`. It does not introduce a separate
`POST /api/playwright-runs` endpoint in V1.

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "automation_draft_id": "00000000-0000-0000-0000-000000001011",
  "test_command_id": null,
  "reason": "run approved Playwright smoke draft",
  "runner_mode": "playwright_local"
}
```

Request rules:

- Exactly one execution source is required: approved Playwright
  `automation_draft_id` or configured Playwright `test_command_id`.
- `automation_draft_id` must reference an AutomationDraft with
  `status=approved` and `target_framework=playwright`.
- `test_command_id` must reference a configured TestCommand with
  `command_type=playwright` and passing allowlist validation.
- Playwright commands are backend assembled or validated from allowlisted
  `npx playwright test ...` style commands.
- V1 supports local Playwright smoke execution only. It does not expose
  browser grid, device matrix, or low-code step editing.

Response model: `TestRunRead` with embedded `TestResultRead` items and
Playwright artifact metadata.

Response artifact examples:

```json
[
  {
    "artifact_type": "stdout",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001311/stdout.log"
  },
  {
    "artifact_type": "stderr",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001311/stderr.log"
  },
  {
    "artifact_type": "playwright_trace",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001311/trace.zip"
  },
  {
    "artifact_type": "screenshot",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001311/screenshot.png"
  }
]
```

Contract boundary:

- Playwright minimal execution records TestRun, TestResult, stdout/stderr,
  trace, screenshot, and runtime artifact metadata.
- It does not create reports, FailureAnalysis, QualityGateDecision, CI/CD
  workflow state, RAG runtime calls, MCP runtime dependencies, RBAC, tenants, or
  permissions.

### 6.5 Newman API Execution

Newman API execution reuses `POST /api/test-runs` and
`GET /api/test-runs/{id}`. It does not introduce a separate
`POST /api/newman-runs` endpoint in Slice 18.

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "automation_draft_id": null,
  "test_command_id": "00000000-0000-0000-0000-000000000322",
  "reason": "run approved API collection",
  "runner_mode": "newman_local"
}
```

Request rules:

- Exactly one execution source is required. For Newman in Slice 18 it must be a
  configured `test_command_id`.
- `test_command_id` must reference a configured TestCommand with
  `command_type=newman` and passing allowlist validation.
- Newman commands are backend assembled or validated from allowlisted
  `npx newman run ... --reporters json,junit` style command templates.
- Collection and environment file paths must be under the repository path or a
  Chtest-managed runtime workspace.
- Secret values in environment variables must be redacted in
  `environment_snapshot`.
- Slice 18 supports local Newman collection execution only. It does not expose
  a collection editor, environment secret manager, Postman cloud account,
  monitor, mock server, or remote CI/CD trigger.

Response model: `TestRunRead` with embedded `TestResultRead` items and Newman
artifact metadata.

Expected `parsed_result` shape:

```json
{
  "total": 4,
  "passed": 3,
  "failed": 1,
  "skipped": 0,
  "error": 0,
  "request_count": 2,
  "assertion_count": 4,
  "collection_name": "coupon-api",
  "duration_ms": 812
}
```

Response artifact examples:

```json
[
  {
    "artifact_type": "stdout",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001321/stdout.log"
  },
  {
    "artifact_type": "stderr",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001321/stderr.log"
  },
  {
    "artifact_type": "newman_json",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001321/newman-report.json"
  },
  {
    "artifact_type": "parsed_output",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001321/parsed_result.json"
  }
]
```

Contract boundary:

- Newman API execution records TestRun, TestResult, stdout/stderr,
  `newman_json`, parsed result, runtime manifest, dependency snapshot, and
  environment snapshot artifact metadata.
- Assertion failures map to TestResult rows. Parser/runtime failures map to
  TestRun `error`.
- It does not create reports, FailureAnalysis, QualityGateDecision, CI/CD
  workflow state, RAG runtime calls, MCP runtime dependencies, RBAC, tenants, or
  permissions.

### 6.4 JMeter Local Execution Evidence

JMeter execution is a local TestRun mode exposed through the same
`POST /api/test-runs` workbench endpoint. Slice 22 must not add a separate JMX
editor, performance dashboard API, distributed runner API, cloud load testing
API, or remote CI/CD provider API.

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "automation_draft_id": null,
  "test_command_id": "00000000-0000-0000-0000-000000000332",
  "reason": "run approved JMeter smoke plan",
  "runner_mode": "jmeter_local"
}
```

Request rules:

- Exactly one execution source is required. For JMeter in Slice 22 it must be a
  configured `test_command_id`.
- `test_command_id` must reference a configured TestCommand with
  `command_type=jmeter` and passing allowlist validation.
- JMeter commands are backend assembled or validated from allowlisted non-GUI
  command templates equivalent to `jmeter -n -t <plan.jmx> -l <result.jtl>`.
- JMX and JTL file paths must be under the repository path or a Chtest-managed
  runtime workspace.
- Secret values in environment variables must be redacted in
  `environment_snapshot`.
- Slice 22 supports local JMeter non-GUI execution only. It does not expose a
  JMX editor, recorder, parameterization UI, distributed load agents, cloud load
  testing, SLA dashboards, or performance trend analysis.

Response model: `TestRunRead` with embedded `TestResultRead` items when sampler
or assertion names can be derived, plus JMeter artifact metadata.

Expected `parsed_result` shape:

```json
{
  "total": 5,
  "passed": 4,
  "failed": 1,
  "skipped": 0,
  "error": 0,
  "sampler_count": 5,
  "assertion_count": 5,
  "duration_ms": 1240,
  "average_latency_ms": 82
}
```

Response artifact examples:

```json
[
  {
    "artifact_type": "stdout",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001331/stdout.log"
  },
  {
    "artifact_type": "stderr",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001331/stderr.log"
  },
  {
    "artifact_type": "jmeter_jtl",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001331/results.jtl"
  },
  {
    "artifact_type": "parsed_output",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001331/parsed_result.json"
  }
]
```

Contract boundary:

- JMeter local execution records TestRun, optional TestResult rows,
  stdout/stderr, `jmeter_jtl`, parsed result, runtime manifest, dependency
  snapshot, and environment snapshot artifact metadata.
- Sampler/assertion failures map to TestRun `failed`. Process launch failure,
  timeout, allowlist rejection, missing JMX/JTL, malformed JTL, or parser
  failure maps to TestRun `error` unless the run was cancelled or timed out by
  the user/runtime.
- It does not create reports, FailureAnalysis, QualityGateDecision, CI/CD
  workflow state, RAG runtime calls, MCP runtime dependencies, RBAC, tenants, or
  permissions.

## 7. Failure Analysis APIs

### 7.1 Start Failure Analysis

`POST /api/test-runs/{id}/failure-analysis`

Request:

```json
{
  "prompt_version": "failure_analysis:v1",
  "skill_version": "failure-analysis-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-failure-analysis"
}
```

Rules:

- The TestRun must exist and belong to the default V1 workspace.
- FailureAnalysis is evidence-first. It must inspect TestRun parsed_result,
  TestResult rows, stdout/stderr/JUnit/trace/screenshot artifacts when
  available.
- Missing or weak evidence must produce
  `classification=insufficient_evidence` and low confidence.
- V1 uses deterministic mock provider output unless a later task explicitly
  enables a real provider.
- This endpoint does not create AutomationRepairTask or Report records.

Response 202:

```json
{
  "ai_task_id": "00000000-0000-0000-0000-000000001501",
  "failure_analysis_id": "00000000-0000-0000-0000-000000001502",
  "status": "draft"
}
```

### 7.2 Get Failure Analysis

`GET /api/test-runs/{id}/failure-analysis`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000001502",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "test_run_id": "00000000-0000-0000-0000-000000001301",
  "test_result_id": null,
  "ai_task_id": "00000000-0000-0000-0000-000000001501",
  "classification": "test_script_issue",
  "confidence": 0.82,
  "summary": "The test failed because fixture coupon_client is not defined.",
  "root_cause": "pytest fixture lookup failed before business assertion ran.",
  "evidence_artifact_ids": ["00000000-0000-0000-0000-000000001601"],
  "suggested_actions": ["Add fixture coupon_client or update the test to use existing fixture api_client"],
  "status": "draft"
}
```

Response model: `FailureAnalysisRead`.

### 7.3 Create Automation Repair Task

`POST /api/automation-repair-tasks`

Request:

```json
{
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "failed_test_run_id": "00000000-0000-0000-0000-000000001301",
  "failure_analysis_id": "00000000-0000-0000-0000-000000001501",
  "prompt_version": "automation_draft_generation:v1",
  "skill_version": "automation-draft-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-automation-repair"
}
```

Response 202:

```json
{
  "automation_repair_task_id": "00000000-0000-0000-0000-000000001701",
  "ai_task_id": "00000000-0000-0000-0000-000000001702",
  "status": "running"
}
```

Repair tasks cannot automatically overwrite an approved AutomationDraft. Any repaired draft candidate remains review-gated.

## 8. Report APIs

### 8.1 Create Report

`POST /api/reports`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "report_type": "automation_execution",
  "related_entity_type": "TestRun",
  "related_entity_id": "00000000-0000-0000-0000-000000001301"
}
```

Rules:

- Slice 14 supports `report_type=automation_execution` only.
- `related_entity_type` must be `TestRun`.
- The related TestRun must have TestResult rows or execution artifacts.
- Report generation must create `evidence_manifest.json` artifact metadata.
- Report conclusion must be derived from TestRun parsed_result, TestResult
  rows, FailureAnalysis when available, and artifact evidence.
- If required evidence is missing, conclusion must be
  `insufficient_evidence`; reports must not mark execution as passed without
  evidence.
- This endpoint does not create CI/CD quality reports or QualityGateDecision
  records.

Response 202:

```json
{
  "report_id": "00000000-0000-0000-0000-000000001401",
  "status": "generating",
  "evidence_manifest_artifact_id": "00000000-0000-0000-0000-000000001402"
}
```

### 8.2 Get Report

`GET /api/reports/{id}`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000001401",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "report_type": "automation_execution",
  "title": "Automation execution report",
  "related_entity_type": "TestRun",
  "related_entity_id": "00000000-0000-0000-0000-000000001301",
  "status": "ready",
  "conclusion": "passed",
  "summary": "3 pytest tests passed.",
  "metrics": {"total": 3, "passed": 3, "failed": 0},
  "artifact_ids": [
    "00000000-0000-0000-0000-000000001402",
    "00000000-0000-0000-0000-000000001403"
  ],
  "evidence_manifest": {
    "report_id": "00000000-0000-0000-0000-000000001401",
    "conclusion": "passed",
    "evidence": [
      {
        "artifact_id": "00000000-0000-0000-0000-000000001601",
        "artifact_type": "stdout",
        "supports_claim": "pytest command completed successfully",
        "required": true
      }
    ],
    "missing_evidence": []
  },
  "artifacts": [
    {"artifact_type": "report_md", "file_path": "projects/00000000-0000-0000-0000-000000000101/reports/00000000-0000-0000-0000-000000001401/report.md"},
    {"artifact_type": "report_json", "file_path": "projects/00000000-0000-0000-0000-000000000101/reports/00000000-0000-0000-0000-000000001401/report.json"},
    {"artifact_type": "report_json", "file_path": "projects/00000000-0000-0000-0000-000000000101/reports/00000000-0000-0000-0000-000000001401/evidence_manifest.json"}
  ]
}
```

Response model: `ReportRead`.

### 8.3 Execution Evidence Summary

Execution evidence summary is a read-only presentation concept derived from
`ReportRead.evidence_manifest`, `ReportRead.artifacts`, and Artifact metadata.
Slice 25 does not require a new endpoint.

Frontend summary rows must preserve these fields when present:

```json
{
  "artifact_id": "00000000-0000-0000-0000-000000001601",
  "artifact_type": "stdout",
  "supports_claim": "pytest command completed successfully",
  "required": true,
  "download_url": "/api/artifacts/00000000-0000-0000-0000-000000001601/download",
  "downloadable": true,
  "availability": "local_artifact"
}
```

Rules:

- Summary rows are derived from `evidence_manifest.evidence[]` in response
  order.
- When an evidence item has an `artifact_id` that matches a local Artifact row
  returned by Report/TestRun APIs, the row may expose `download_url` using
  `GET /api/artifacts/{artifact_id}/download`.
- When an evidence item is a metric or TestResult reference, it must remain a
  structured evidence row and must not be shown as downloadable.
- `evidence_manifest.missing_evidence[]` must remain visible as missing
  evidence and must not be converted into a passing or downloadable row.
- Report-owned artifacts returned in `ReportRead.artifacts` may expose the same
  local download URL when they are persisted local Artifact rows.
- External imported artifact references remain inert and not locally openable.
- This summary must not mutate Report, TestRun, TestResult, Artifact,
  FailureAnalysis, QualityGateDecision, CI metadata, or review history.
- Slice 25 must not change report generation, runner execution, failure
  analysis, quality gate decisions, artifact storage, or remote provider
  behavior.

## 9. AI Task API

`GET /api/ai-tasks/{id}`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000000501",
  "agent_name": "RequirementReviewAgent",
  "task_type": "requirement_review",
  "status": "succeeded",
  "prompt_version": "requirement_review:v1",
  "skill_version": "requirement-review-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-requirement-review",
  "token_usage": {"input_tokens": 1200, "output_tokens": 800},
  "used_knowledge": false,
  "used_context_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
  "context_manifest_artifact_id": "00000000-0000-0000-0000-000000000372",
  "artifacts": [
    {"artifact_type": "raw_llm_output", "file_path": "projects/00000000-0000-0000-0000-000000000101/ai-tasks/00000000-0000-0000-0000-000000000501/raw.json"}
  ]
}
```

### 9.1 AI Task Evidence Artifact Links

Slice 27 may expose local open links for safe AI task evidence artifacts in the
AI Workbench. The links are a read-only presentation of existing Artifact rows;
they do not create a new artifact API.

Frontend rows may derive:

```json
{
  "artifact_id": "00000000-0000-0000-0000-000000000902",
  "artifact_type": "parsed_output",
  "download_url": "/api/artifacts/00000000-0000-0000-0000-000000000902/download",
  "downloadable": true,
  "availability": "local_artifact"
}
```

Rules:

- AI task evidence artifact links are derived from `AITaskRead.artifacts[]`,
  Artifact metadata, and the existing `GET /api/artifacts/{artifact_id}/download`
  endpoint.
- A row may expose a local open link only when the Artifact is a persisted local
  Artifact row and `safe_to_show=true`.
- Artifacts with `safe_to_show=false`, including raw LLM output, must remain
  visible as metadata but must not receive direct UI open links.
- Raw LLM output content must not be inlined into the AI Workbench.
- LLM call logs may continue to cite request, response, parsed, and schema
  validation artifact ids without inlining artifact content.
- This display must not mutate AITask, Artifact, LLMCallLog, prompt/skill
  versions, context artifacts, Report, FailureAnalysis, QualityGateDecision, or
  review history.
- Slice 27 must not add AI task rerun, prompt editing, provider integration,
  streaming logs, schema editing, artifact upload/mutation/delete, RAG runtime,
  MCP runtime, RBAC, tenants, permissions, broad artifact browser, cloud
  storage, signed URLs, sharing, or remote runtime controls.

## 10. Local Review History APIs

Local Review History APIs expose append-only local review attribution evidence.
They are read surfaces for existing review-gated workflows, not a user
management, RBAC, tenant, assignment, notification, or enterprise audit system.

### 10.1 List Review History

`GET /api/review-history`

Query filters:

| Name | Required | Notes |
|---|---:|---|
| project_id | yes | Limit history to one local project |
| entity_type | no | GeneratedCaseCandidate, TestCase, AutomationDraft, UnitTestPatch, CICDRun, QualityGateDecision, AutomationRepairTask |
| entity_id | no | Entity id matching `entity_type` |
| related_entity_type | no | Optional relation query, for example CICDRun |
| related_entity_id | no | Related entity id matching `related_entity_type` |
| limit | no | Default 50, maximum 200 |

Response model: `ReviewHistoryListRead`.

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000001701",
      "project_id": "00000000-0000-0000-0000-000000000101",
      "entity_type": "UnitTestPatch",
      "entity_id": "00000000-0000-0000-0000-000000001201",
      "related_entity_type": "CICDRun",
      "related_entity_id": "00000000-0000-0000-0000-000000001101",
      "action": "approve",
      "from_status": "awaiting_review",
      "to_status": "approved",
      "reviewer": "Default User",
      "comment": "Only tests/ is modified",
      "evidence_artifact_ids": ["00000000-0000-0000-0000-000000001211"],
      "created_at": "2026-07-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

Rules:

- At least one of `entity_type/entity_id` or
  `related_entity_type/related_entity_id` should be supplied for focused UI
  panels. Project-wide history may be used for diagnostics but must remain
  paginated.
- `reviewer` is a local display label. `Default User` is the deterministic V1
  value unless a later local-only contract adds an explicit reviewer label
  field to a workflow payload.
- This API does not create, update, delete, redact, sign, export, or lock
  ReviewHistory records.
- There is no generic `POST /api/review-history` in Slice 21. Records are
  appended internally only after existing review or quality-gate actions
  succeed.
- Listing history must not grant permissions, change action authority, assign
  work, send notifications, create comment threads, call remote CI providers,
  publish PR comments, update commit statuses, merge, deploy, release, or read
  credentials.

### 10.2 Entity Display Rules

- Generated case approval history is written against GeneratedCaseCandidate.
  TestCase detail or library views may display that source history through
  `source_candidate_id` but should not expect duplicate TestCase history rows
  for the same approval.
- QualityGateDecision compute history is written against the
  QualityGateDecision and may be queried from its related CICDRun. The status
  transition in the history record describes the CICDRun
  `quality_gate_status` before and after recompute.
- Evidence artifact ids are references to existing Artifact rows. The API must
  not inline raw artifact content, secrets, tokens, or external provider
  credentials in ReviewHistory responses.
