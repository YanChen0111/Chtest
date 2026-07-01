# Chtest Error Code Contract

## 1. Purpose

This document defines the first batch of stable API error codes for Chtest V1. Backend services, frontend clients, tests, and reports must use these codes instead of ad hoc error strings.

Common error response:

```json
{
  "error_code": "STRING_CODE",
  "message": "Human readable message",
  "details": {}
}
```

## 2. Error Code List

| Error Code | HTTP Status | Meaning | Typical Trigger |
|---|---:|---|---|
| DRAFT_NOT_APPROVED | 409 | AutomationDraft is not approved | Creating TestRun from unapproved draft |
| PATCH_SCOPE_REJECTED | 422 | UnitTestPatch modifies forbidden paths | PatchScopeGate rejects patch |
| TOOL_NOT_ALLOWED | 403 | Tool is not registered or disabled | ToolDefinition missing/disabled |
| TOOL_APPROVAL_REQUIRED | 409 | Tool invocation needs approval | Medium/high risk invocation without approval |
| TEST_COMMAND_NOT_ALLOWED | 422 | Test command violates allowlist | Command or working directory outside allowed scope |
| SCHEMA_VALIDATION_FAILED | 422 | AI output does not match schema | Agent output parser fails validation |
| AI_TASK_FAILED | 500 | AI task failed | Provider error, parser error, or worker failure |
| ARTIFACT_NOT_FOUND | 404 | Artifact does not exist | Report or detail page references missing artifact |
| CONTEXT_ARTIFACT_NOT_ALLOWED | 422 | ContextArtifact cannot be used for prompt input | Unsafe MIME, binary file, missing owner, or allowed_for_prompt=false |
| CONTEXT_ARTIFACT_TOO_LARGE | 413 | ContextArtifact exceeds V1 size limit | Single file > 1 MiB or AITask context total > 2 MiB |
| CONTEXT_ARTIFACT_SECRET_DETECTED | 422 | ContextArtifact contains high-risk secret | Secret scan finds token, credential, cookie, or production connection string |
| REPOSITORY_PATH_NOT_ALLOWED | 422 | Repository path is outside allowlist | Creating/updating Repository |
| REPORT_INSUFFICIENT_EVIDENCE | 409 | Report cannot make conclusion with available evidence | ReportAgent lacks required artifacts |
| INVALID_CI_IMPORT_PAYLOAD | 400 | CI import payload is malformed or unsupported | Missing required fields, invalid conclusion, invalid changed file |
| CI_IMPORT_CONTROL_FIELD_REJECTED | 400 | CI import contains remote-control fields | Webhook, trigger, rerun, cancel, schedule, PR comment, deploy, release, merge, tag, or status-update field |
| CI_IMPORT_CREDENTIAL_REJECTED | 400 | CI import contains credential-like fields | Token, secret, OAuth, PAT, private key, password, credential id, or organization permission field |
| CI_IMPORT_UNSUPPORTED_PROVIDER_OPERATION | 422 | CI import attempts provider behavior | Treating provider label as a remote CI operation |
| CI_IMPORT_EXTERNAL_FETCH_FORBIDDEN | 422 | CI import requests external fetch behavior | Asking Chtest to download artifact URLs, fetch logs, or access external URLs |
| CI_IMPORT_DUPLICATE_EXTERNAL_RUN | 409 | Imported CI run already exists | Same project/repository/provider/external_run_id was already imported |

## 3. Rules

- Error codes are stable API contract values.
- Adding an error code requires updating this file and related API tests.
- Frontend must branch on `error_code`, not message text.
- Logs may include detailed diagnostics, but API `message` must remain safe for UI display.
- Security-sensitive details must go into server logs or restricted artifacts, not user-facing error response.
