# Newman API Execution Golden Fixture

## Purpose

This fixture proves the first V2 runner expansion without broadening Chtest into
Postman parity, arbitrary shell execution, or remote CI/CD control.

The golden path is:

```text
Project
  -> configured TestCommand(command_type=newman)
  -> TestRun(runner_mode=newman_local)
  -> Newman stdout/stderr/newman_json/parsed_output artifacts
  -> assertion-level TestResult rows
```

## Golden TestCommand

Name: `newman coupon api`

Command:

```bash
npx newman run collections/coupon.postman_collection.json --reporters json --reporter-json-export newman-report.json
```

Expected command properties:

- `command_type`: `newman`
- `runner_mode`: `newman_local`
- `status`: `active`
- command passes allowlist validation
- no shell chaining, redirection, command substitution, or pipes

## Golden Newman Report

Collection name: `coupon-api`

Expected parsed result:

```json
{
  "total": 4,
  "passed": 3,
  "failed": 1,
  "skipped": 0,
  "error": 0,
  "request_count": 2,
  "assertion_count": 4,
  "collection_name": "coupon-api"
}
```

Expected failing assertion:

```text
coupon-api/Reject expired coupon::message is explicit
```

Failure message:

```text
expected clear message
```

## Expected Artifacts

The TestRun must persist:

- `runtime_manifest`
- `stdout`
- `stderr`
- `newman_json`
- `parsed_output`

Optional JUnit output may be persisted as `junit` in later fixtures, but it is
not required for this minimal golden smoke.

## Expected State

- TestRun status is `failed` because Newman completed and one API assertion
  failed.
- TestRun `exit_code` is recorded from the local runner.
- Assertion-level TestResult rows are visible.
- Failed assertion evidence is not hidden only in stdout/stderr logs.
- `network_enabled=false` for the deterministic fixture.

## Non-goals

The golden path must not create or require:

- arbitrary shell execution
- Postman workspace, account, monitor, mock server, or cloud sync
- collection editor
- environment secret manager
- remote CI/CD provider calls, PR comments, deployment, or release automation
- RAG runtime
- MCP runtime
- RBAC
- tenants
- permissions
- runner marketplace
