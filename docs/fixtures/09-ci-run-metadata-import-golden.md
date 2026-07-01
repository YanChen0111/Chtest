# Golden Path: CI Run Metadata Import

## 1. Purpose

This fixture proves the smallest V2 CI import evidence loop:

```text
static CI metadata JSON
  -> POST /api/cicd/runs/import
  -> CICDRun + CICDChangedFile rows
  -> ci_run_metadata + changed_files evidence artifacts
  -> CI/CD quality center readable import evidence
```

The goal is to prove imported CI status is evidence only. Chtest must not call,
authenticate to, trigger, rerun, cancel, schedule, deploy, release, comment on,
or fetch from a remote CI provider.

## 2. Seed Data

Required seed data:

- Project: `Checkout System`.
- Repository: `sample-app`.
- Static CI provider label: `github_actions`.
- External run id: `123456`.
- Pipeline: `CI`.
- Job: `pytest`.
- CI conclusion: `success`.
- Base ref: `main`.
- Head ref: `feature/coupon-boundary`.
- Changed files:
  - `app/coupon.py`, modified source file.
  - `tests/test_coupon.py`, added test file.
- Artifact reference:
  - `pytest report`, kind `test_report`, external URL stored as inert reference.

## 3. Minimum Flow

1. Create Project.
2. Create Repository for that Project.
3. Import the static CI metadata payload through `POST /api/cicd/runs/import`.
4. Confirm response returns `source_type=ci_import`, `trigger_type=imported`,
   `import_status=imported`, and `quality_gate_status=pending`.
5. Confirm `CICDRun` stores only import source metadata columns.
6. Confirm imported changed files persist as `CICDChangedFile` rows with
   deterministic role/risk classification.
7. Confirm `ci_run_metadata` and `changed_files` evidence Artifacts are created.
8. Confirm `ci_run_metadata` content includes CI conclusion and inert artifact
   references.
9. Confirm `GET /api/cicd/runs/{id}` exposes frontend-readable import evidence.
10. Confirm no QualityGateDecision, UnitTestPatch, TestRun, Report, remote
    fetch, or remote provider operation exists.

## 4. Success Criteria

- Import response status is `202`.
- Import response contains:
  - `source_type=ci_import`;
  - `provider=github_actions`;
  - `trigger_type=imported`;
  - `import_status=imported`;
  - `quality_gate_status=pending`;
  - `ci_conclusion=success`;
  - created artifact entries for `ci_run_metadata.json` and
    `changed_files.json`.
- Persisted `CICDRun`:
  - has `source_type=ci_import`;
  - has `trigger_type=imported`;
  - stores provider as inert label;
  - has `status=imported`;
  - keeps `quality_gate_status=pending`.
- Persisted `ci_run_metadata` Artifact metadata:
  - records `created_by_component=CICDRunMetadataImport`;
  - records `provider_is_inert_label=true`;
  - records `remote_fetch_performed=false`;
  - records `quality_gate_auto_decision=false`;
  - includes `content_json.conclusion=success`;
  - includes one `artifact_references` item with `inert_reference=true`.
- Run detail response exposes the `ci_run_metadata` artifact in
  `analysis_artifacts` so the CI/CD quality center can display it.

## 5. Out Of Scope

- Remote CI provider API calls.
- Webhook receiver.
- Pipeline trigger, rerun, cancel, or schedule.
- PR comments, commit status updates, branch protection, merge, push, tag,
  deploy, or release management.
- Provider credentials, OAuth, PAT, private key, secret, token, or organization
  permission fields.
- External artifact or log download.
- Automatic QualityGateDecision pass from imported CI conclusion.
- RBAC, tenants, permissions, marketplace, RAG runtime, MCP runtime, cloud sync,
  or release automation.
