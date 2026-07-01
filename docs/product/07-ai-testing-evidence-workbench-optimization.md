# AI Testing Evidence Workbench Optimization

## 1. Purpose

This document turns the latest product review into the current V1 optimization plan.

Chtest V1 should not compete as a generic test management platform or a simple AI test-case generator. The stronger wedge is an AI testing evidence workbench: it helps one test engineer turn requirements and code changes into reviewed, executable, traceable, and measurable testing evidence.

The product value is the closed loop, not the generation count.

```text
Requirement or code change
  -> AI risk and test analysis
  -> reviewed test assets
  -> approved automation draft
  -> sandboxed execution
  -> evidence artifacts
  -> failure analysis or repair candidate
  -> report
  -> AI quality metrics
```

## 2. Market And Enterprise Landing Read

Large-scale AI engineering tools are converging on the same pattern:

- AI is embedded into engineering workflows such as issue, pull request, local repository, CI, and code review.
- AI output is executed in an isolated or controlled environment.
- Logs, test results, lint results, artifacts, and diffs are first-class evidence.
- Human review remains the promotion gate.
- AI quality is measured by usefulness, acceptance, execution success, and repair success rather than token output volume.

Chtest V1 should follow this pattern for testing work:

- AI can propose test assets.
- AI cannot silently promote assets.
- Runner output is the source of execution truth.
- Reports must cite evidence.
- Metrics must expose whether AI improved testing efficiency and reliability.

## 3. V1 Strategy

Use Strategy B: evidence closed loop first.

V1 must prioritize the shortest credible path from requirement or change to testing evidence:

1. Create project context.
2. Add requirement or code-change context.
3. Run AI analysis.
4. Review generated cases.
5. Approve an AutomationDraft.
6. Execute it through the controlled runner.
7. Persist runtime and evidence artifacts.
8. Generate a report that explains what happened and what to do next.

The first release should feel narrow but trustworthy. It is acceptable for V1 to have fewer integrations if the evidence loop is reliable.

## 4. P0 Optimizations

### 4.1 Evidence Workbench Positioning

Update all V1 product language to emphasize:

- reviewed assets;
- controlled execution;
- traceable artifacts;
- evidence-backed reports;
- measurable AI quality.

Avoid positioning Chtest as only a case generator, chatbot, or test management replacement.

### 4.2 Minimum Demo As Release Spine

`docs/fixtures/00-v1-demo-path.md` is the release spine. V1 is not acceptable until that path runs end to end with the mock provider.

The demo must answer:

- What requirement or change did AI analyze?
- Which context artifacts were used?
- Which cases were approved or edited?
- Which AutomationDraft was executed?
- Which runtime file, dependency snapshot, environment snapshot, and runner mode were used?
- What evidence supports the report?
- What happens next if the run fails?

### 4.3 Docker Runner As Product Trust Boundary

`local_subprocess` can remain a development mode. `docker_runner` is the preferred trustworthy V1 execution mode for product acceptance.

Every TestRun must record:

- runner mode;
- isolated run workspace;
- repository readonly setting;
- network setting;
- runtime manifest;
- dependency snapshot;
- environment snapshot;
- stdout, stderr, JUnit, coverage, screenshot, trace, or other execution artifacts.

### 4.4 Model And Prompt Eval Bench

V1 needs a small deterministic evaluation bench before broad model optimization.

Minimum bench:

- 10 requirement samples.
- 5 code-change samples.
- 5 failed execution samples.
- 3 historical bug-style samples.

Minimum metrics:

- schema valid rate;
- case usefulness rate;
- first-run pass rate;
- manual edit rate;
- repair success rate;
- evidence complete rate;
- unsafe output rate.

The bench can run with the mock provider first. Real provider baselines can be added after the core loop is stable.

### 4.5 Context Artifacts Before RAG

V1 should not build a full RAG system, vector database, or reranking pipeline. It should support lightweight `ContextArtifact` inputs:

- requirement documents;
- Markdown notes;
- OpenAPI files;
- interface samples;
- logs;
- fixtures;
- historical bug summaries.

Every AI task should record which context artifacts were used. When no context artifact is used, the task should explicitly record an empty context list instead of implying hidden knowledge.

## 5. P1 Optimizations

After the minimum evidence loop is stable:

- Productize AutomationRepairTask as failed evidence -> AI repair candidate -> human review -> new draft.
- Export Markdown, HTML, JSON, JUnit XML, and CSV/Excel-friendly reports.
- Add Prompt/Skill/model effectiveness views.
- Add CI/CD quality report as a supporting local diff/change validation workflow.
- Add flaky retry and unresolved failure metrics.

## 6. P2 Deferred Work

Do not put these in V1 critical path:

- multi-user collaboration;
- RBAC, SSO, enterprise audit;
- full test management replacement;
- complex RAG platform;
- MCP marketplace;
- complete low-code UI automation;
- Newman, JMeter, Appium, and traffic capture beyond adapter-ready contracts.

## 7. Slice Impact

| Area | Optimization |
|---|---|
| Slice 1-2 | Keep platform foundation narrow and runnable. |
| Slice 2.5 | Frontend scaffold is required before product pages. |
| Slice 3 | Project Settings should support the future evidence loop, but avoid dashboard breadth. |
| Slice 4-5 | Add mock-provider eval bench and context artifact metadata contracts. |
| Slice 6-10 | Requirement-to-case must prove reviewability and traceability, not only generation. |
| Slice 11-12 | AutomationDraft execution must record runtime artifact, runner sandbox metadata, and snapshots. |
| Slice 12 | Docker runner should be the preferred product acceptance path when available. |
| Slice 13-14 | Failure analysis and reports must cite evidence before drawing conclusions. |
| Slice 15-16 | CI/CD Quality Center remains a support workflow and must not overtake the main evidence loop. |

## 8. Vibe Coding Constraints

Every implementation task must serve one measurable product value target.

Hard rules:

- One Slice, one primary value goal.
- Every task names a verification command or smoke check.
- Every AI-generated test asset remains review-gated.
- Every runner execution records artifacts and snapshots.
- After two or three failed repair attempts, stop generating changes and write a failure report.
- Do not add broad platform features before `docs/fixtures/00-v1-demo-path.md` passes.

## 9. Current Product Definition

Chtest V1 is an AI testing evidence workbench for individual test engineers and automation test engineers. It helps users turn requirements and code changes into human-reviewed, sandbox-executed, evidence-backed, and quality-measured testing assets.
