# AI Task Evidence Artifact Links Golden Fixture

This fixture proves Slice 27 AI task evidence artifact links without changing
AI runtime behavior.

## Scenario

1. A succeeded `AITask` has two local artifacts:
   - `parsed_output.json` with `safe_to_show=true`.
   - `raw_output.json` with `artifact_type=raw_llm_output` and
     `safe_to_show=false`.
2. The AI task detail API returns artifact metadata and LLM call artifact ids.
3. The safe parsed output artifact is readable through local artifact access.
4. The raw LLM output artifact remains metadata-only for AI Workbench link
   rendering and is not inlined by the AI task detail API.

## Expected Evidence

- Safe AI task artifacts can be opened through the local artifact access
  endpoint.
- Unsafe raw LLM artifacts remain visible as metadata with `safe_to_show=false`.
- AI task detail responses do not inline artifact content or synthesize
  `download_url` fields.
- Artifact link display creates no AI task rerun, provider call, Report,
  FailureAnalysis, QualityGateDecision, TestRun, artifact mutation, RAG runtime,
  or MCP runtime behavior.

## Non-Goals

- No inline raw LLM output, prompt editing, prompt replay, model/provider
  integration, streaming logs, schema editor, upload, mutation, delete, sharing,
  signed URL, cloud storage, broad artifact browser, report generation,
  FailureAnalysis, QualityGateDecision, runner behavior, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions.
