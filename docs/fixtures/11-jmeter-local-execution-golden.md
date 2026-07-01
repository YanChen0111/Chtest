# JMeter Local Execution Golden Fixture

## Purpose

This fixture proves the narrow JMeter runner expansion without turning Chtest
into a load-testing platform, JMX editor, distributed runner, or arbitrary shell
surface.

The golden path is:

```text
Project
  -> configured TestCommand(command_type=jmeter)
  -> TestRun(runner_mode=jmeter_local)
  -> JMeter stdout/stderr/jmeter_jtl/parsed_output artifacts
  -> sampler-level TestResult rows
```

## Golden TestCommand

Name: `jmeter coupon smoke`

Command:

```bash
jmeter -n -t plans/coupon.jmx -l results.jtl
```

Expected command properties:

- `command_type`: `jmeter`
- `runner_mode`: `jmeter_local`
- `status`: `active`
- command uses JMeter non-GUI mode
- command passes allowlist validation
- no shell chaining, redirection, command substitution, pipes, or remote runner
  controls

## Golden JTL

The deterministic fake JMeter executable writes three sampler rows:

- `GET /coupons`: passed
- `POST /coupons`: failed with `500 Internal Server Error`
- `GET /health`: passed

Expected parsed result:

```json
{
  "total": 3,
  "passed": 2,
  "failed": 1,
  "skipped": 0,
  "error": 0,
  "sampler_count": 3,
  "assertion_count": 3,
  "duration_ms": 450,
  "average_latency_ms": 103
}
```

Expected failing sampler:

```text
jmeter/POST /coupons
```

Failure message:

```text
500 Internal Server Error
```

## Expected Artifacts

The TestRun must persist:

- `runtime_manifest`
- `stdout`
- `stderr`
- `jmeter_jtl`
- `parsed_output`

## Expected State

- TestRun status is `failed` because JMeter completed and one sampler failed.
- TestRun `exit_code` is recorded from the local runner.
- Sampler-level TestResult rows are visible.
- Failed sampler evidence is not hidden only in stdout/stderr logs.
- `repository_readonly=true`.
- `network_enabled=false` for the deterministic fixture.
- No Report, FailureAnalysis, or QualityGateDecision is created automatically.

## Non-goals

The golden path must not create or require:

- arbitrary shell execution
- JMX editor, recorder, or test-plan authoring workflow
- performance trend dashboard, capacity analysis, SLA management, or benchmark
  platform
- distributed JMeter, remote agents, Kubernetes runner, or cloud load testing
- secret manager
- remote CI/CD provider calls, PR comments, deployment, or release automation
- RAG runtime
- MCP runtime
- RBAC
- tenants
- permissions
- runner marketplace
