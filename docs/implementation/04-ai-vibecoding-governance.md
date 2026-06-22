# AI Vibecoding Governance

## 1. Goal

This document defines the mandatory engineering governance for AI-assisted development in Chtest.

The goal is to make long-running vibe coding stable, testable, reviewable, and recoverable. AI must behave like a reliable engineer: small steps, clear tests, frequent commits, clean handoff, and no uncontrolled scope expansion.

Core principles:

- Small-step development.
- Every step is testable.
- Every step serves one product value target.
- Every completed Task has a commit.
- Every commit is reviewable and reversible.
- Every session updates handoff memory when required by this document.
- Contracts guide code; code does not silently drift from contracts.

核心职责分工：

```text
Git 记录代码历史。
Memory 记录会话接续。
Contracts 记录实现真相。
```

三者职责不同，不能互相替代：

| 类型 | 主要职责 |
|---|---|
| Git | 记录代码如何变化、每个 Task 的可回滚点、测试提交记录 |
| Memory | 记录为什么这样做、当前做到哪里、下一轮 AI 如何接手 |
| Contracts | 记录数据模型、API、状态机、Artifact、Prompt/Skill 等实现真相 |

## 2. Source Of Truth

When documents disagree, follow this order:

1. `docs/product/01-positioning-and-scope.md`.
2. `docs/contracts/*`.
3. `docs/implementation/04-ai-vibecoding-governance.md`.
4. `docs/implementation/01-v1-delivery-plan.md`.
5. `memory/13-ai-readable-project-brief.md`.
6. `docs/fixtures/*`.
7. `docs/architecture/*`.
8. `docs/reference/*`, `docs/reviews/*`, and `docs/superpowers/*`.

If implementation needs behavior not covered by contracts, update contracts first, then implement.

## 3. Slice / Task / Commit Model

```text
Slice
  -> Task 1
      -> tests/smoke
      -> minimal implementation
      -> verification
      -> git commit
      -> task progress update
  -> Task 2
      -> same loop
  -> Slice completion gate
```

Rules:

- AI works on at most one Slice at a time.
- Within a Slice, AI works on 1-3 Tasks per session unless the user explicitly asks for more.
- Each Task must have one clear goal.
- Each completed Task must have one or more commits.
- A commit must not mix Tasks or Slices.
- A Slice is not complete until every Task has a commit or a documented blocked/unfinished reason.

A Task is too large if it cannot be explained in one sentence or verified with one focused test command.

## 4. Task Definition Of Ready

Before coding a Task, AI must define:

| Field | Required Content |
|---|---|
| Slice | Slice number and name |
| Task | One-sentence goal |
| Product value answer | What the user can understand, trust, execute, or decide after this Task |
| Source documents | Contracts, fixtures, architecture docs, or memory files needed |
| Expected files | Likely files to create or modify |
| Verification | Exact test or smoke command |
| Non-goals | What this Task must not do |
| Commit scope | Expected commit type and scope |

Do not start coding when the Task cannot name a verification command. If a verification command does not exist yet, the first step is to create a focused test or smoke check.

Do not start broad feature work that does not move `docs/fixtures/00-v1-demo-path.md` forward or explicitly maintain a contract needed by that path.

## 5. Mandatory Task Loop

Every Task must follow this loop:

```text
Read Task-specific docs
  -> inspect current workspace status
  -> write or update focused test/smoke
  -> run test and observe failure when applicable
  -> implement minimal code
  -> run focused verification
  -> fix failures
  -> run git diff self-review
  -> commit
  -> update Task progress
```

If the same verification fails after two to three focused repair attempts, stop changing code and write a failure report in `memory/08-session-handoff.md`:

```text
Failed verification:
Observed evidence:
Likely cause:
Rejected hypotheses:
Next smallest diagnostic step:
Risk if continued:
```

Do not continue speculative AI repair loops without new evidence.

Minimum command sequence before commit:

```bash
git status --short
git diff --check
git diff --name-only
```

Then run the Task-specific verification command.

## 6. Testing And Verification Rules

Every Task must have matching verification.

| Change Type | Minimum Verification |
|---|---|
| Backend model | Migration smoke + model test |
| Backend API | FastAPI TestClient test |
| Worker | Worker handler test with fake queue or mock provider |
| Tool Adapter | Mock subprocess/tool invocation test |
| Frontend route/page | Vitest, component smoke, or route smoke |
| Docker/deploy | `docker compose config` and relevant health check |
| Prompt/Skill | Schema example validation |
| Artifact/parser | Fixture parser test |
| Golden Path | Fixture-aligned acceptance or smoke test |
| Eval bench | Mock provider deterministic benchmark smoke |
| Documentation | Path/link self-check and keyword consistency check |

Verification levels:

| Gate | When | Required Verification |
|---|---|---|
| Task Gate | Every Task | Focused test or smoke command |
| Slice Gate | Slice completion | Slice-level related test set |
| Milestone Gate | Major workflow completion | Docker + API + worker + frontend smoke, plus relevant Golden Path |
| Release Gate | Release candidate | Full test suite, docker smoke, docs consistency, V1 Minimum Demo, Golden Paths |

If a test cannot run, record in `memory/08-session-handoff.md`:

```text
Unverified reason:
Risk:
Next verification command:
```

Do not claim a Task is complete without verification evidence.

## 7. Git Commit Governance

### 7.1 Basic Principles

Each commit must be:

- Small.
- Single-purpose.
- Tested or explicitly documented as unverified.
- Reversible.
- Reviewable.
- Free of unrelated formatting or generated noise.

Every commit must answer:

```text
If this commit is reverted, which exact behavior or change is removed?
```

If the answer is unclear, the commit is too large or too mixed.

### 7.2 Commit Frequency

- Every completed and verified Task must be committed.
- A Slice usually contains multiple commits.
- Do not wait until the whole Slice is complete to commit.
- Do not mix multiple Slices in one commit.
- Documentation and code may be in the same commit only when they serve the same Task.

### 7.3 Commit Message Format

Use Conventional Commits:

```text
<type>(<scope>): <summary>
```

Required fields:

- `type`: required.
- `scope`: required.
- `summary`: required.

Allowed types:

| Type | Use |
|---|---|
| feat | New behavior |
| fix | Bug fix |
| test | Tests only or test updates |
| docs | Documentation |
| refactor | Behavior-preserving restructuring |
| chore | Project config, scaffolding, maintenance |
| build | Build, Docker, packaging |
| ci | CI/CD |
| perf | Performance improvement |
| style | Formatting-only change |
| revert | Revert commit |
| wip | Interrupted checkpoint only |

Recommended scopes:

```text
repo, backend, frontend, worker, deploy, db, api, models, schemas,
ai-runtime, prompt, skill, tool, artifact, requirement, case,
automation, git-quality, report, docs, memory, test
```

Examples:

```text
feat(backend): add health check endpoint
feat(db): add project and module models
feat(ai-runtime): add mock llm provider
feat(automation): add automation draft state machine
feat(git-quality): add patch scope gate
test(api): cover requirement review creation
docs(contracts): add repository api contract
chore(deploy): add docker compose services
fix(tool): reject commands outside allowlist
refactor(report): split markdown renderer
```

Bad summaries:

```text
update docs
fix bug
add feature
change backend
```

Good summaries:

```text
docs(contracts): add automation draft state transitions
fix(api): reject unapproved automation draft execution
feat(tool): add pytest command allowlist validation
```

### 7.4 Commit Body Rules

Simple commits may omit the body.

Commit body is required when the change includes:

- State machine changes.
- Data model changes.
- API contract changes.
- Security or approval policy changes.
- Scope cuts.
- Technical debt notes.
- Verification that could not be run.

Template:

```text
<type>(<scope>): <summary>

Why:
- Why this change is needed.

What:
- What changed.

Validation:
- Command that was run.
- Result.

Refs:
- docs/contracts/xxx.md
- Slice N / Task M
```

Example:

```text
feat(automation): add automation draft approval gate

Why:
- AutomationDraft must not execute before human approval.

What:
- Add approved status check before creating TestRun.
- Return DRAFT_NOT_APPROVED when draft is not approved.

Validation:
- pytest backend/app/tests/api/test_automation_drafts.py -q

Refs:
- docs/contracts/03-state-machines.md
- Slice 11 / Task 3
```

### 7.5 Validation Before Commit

Before every commit, AI must answer:

```text
Does this change belong only to the current Task?
Does it follow contracts and fixtures?
Is there a focused test or smoke check?
Did the verification pass?
Are there unrelated files?
Are generated/cache/log files excluded?
Are needed docs or memory updates included?
Does it preserve approval and safety boundaries?
```

Required pre-commit checks:

```bash
git status --short
git diff --check
git diff --name-only
```

Then run the Task-specific verification command.

### 7.6 Forbidden Commits

Do not commit when:

- Tests fail without a documented reason.
- Unrelated files are mixed in.
- Temporary logs, caches, local secrets, or generated runtime artifacts are included.
- The change bypasses contracts.
- The change bypasses approval strategy.
- Business source is modified to make generated tests pass.
- V1 out-of-scope functionality is introduced.
- The message is only `WIP` without exact purpose.
- Broad formatting is mixed with behavior changes.

### 7.7 WIP Commit Policy

Default: WIP commits are not allowed.

Allowed only when the session must stop and losing state would be worse than a checkpoint.

Format:

```text
wip(slice-3): checkpoint project core api skeleton

Status:
- incomplete

Known gaps:
- repository api not implemented

Do not build on this until:
- tests are added and pass
```

The next session must either complete the WIP Task or revert the checkpoint before building on it.

### 7.8 Branch Naming

Recommended branch names:

```text
feature/slice-<number>-<short-name>
fix/<short-name>
docs/<short-name>
chore/<short-name>
ai/slice-<number>-<short-name>
ai/docs-vibecoding-governance
```

Examples:

```text
feature/slice-01-platform-foundation
feature/slice-04-ai-runtime-core
feature/slice-11-automation-draft
fix/automation-draft-approval
docs/vibecoding-governance
```

### 7.9 Push Policy

- AI may create local commits when the user requests development work.
- AI must not push unless the user explicitly asks.
- Before push, summarize commit list and verification results.
- Force push is forbidden unless the user explicitly authorizes it.

## 8. Workspace Protection Rules

Before editing:

```bash
git status --short
```

Rules:

- Do not overwrite user changes.
- Do not include unrelated user changes in commits.
- If unrelated changes exist, work around them.
- If related uncommitted changes affect the Task, inspect them and continue carefully.
- Do not run destructive commands such as `git reset --hard`.
- Do not use broad formatting across files outside the current Task.
- Commit only the files belonging to the current Task.

Before commit, inspect:

```bash
git diff --name-only
git diff --cached --name-only
```

## 9. Database And Migration Rules

When changing database models:

- Update `docs/contracts/01-data-model-contract.md` first if the contract is missing or wrong.
- Add or update migration files.
- Migration must run on an empty database.
- Migration must not require manual data edits in V1.
- Model fields must match Pydantic schemas and API contracts.
- Add migration smoke or model tests.

Minimum verification:

```bash
alembic upgrade head
pytest backend/app/tests/db -q
```

If the project does not yet have Alembic or DB tests, the Task must create the minimal smoke path.

## 10. Prompt / Skill / AI Output Rules

Prompt and Skill changes are engineering changes.

Rules:

- Prompt/Skill files must have versioned names or version metadata.
- Prompt changes that affect output must update schema examples.
- Skill changes must list quality gates and forbidden actions.
- No secret, token, production credential, or private customer data may appear in Prompt/Skill.
- Example input and output must pass schema validation.
- Prompt/Skill behavior changes must be mentioned in commit body or session handoff.

Minimum verification:

```bash
pytest backend/app/tests/ai_runtime -q
```

If schema validation tooling does not exist yet, the Task must add a minimal validator or record the exact gap.

## 11. Tool And Runtime Safety Rules

Any Task that implements ToolDefinition, ToolInvocation, TestCommand execution, AutomationDraft execution, PatchScopeGate, or artifact runtime files must enforce these rules before execution:

- Use allowlisted TestCommand or ToolDefinition only.
- Execute through argv / non-shell mode; do not use `shell=True`.
- Reject shell operators: `;`, `&&`, `||`, `|`, `>`, `>>`, `<`, `$(`, and backticks.
- Canonicalize working directory and artifact path before use.
- Confirm canonical working directory is under the configured repository or tool allowlist.
- Confirm canonical artifact path is under artifact root.
- Enforce timeout and stdout/stderr size limits.
- Redact secrets before storing or displaying stdout, stderr, raw provider output, and reports.
- Require approval for medium/high risk tools and for AutomationDraft execution.
- Use an isolated per-run workspace/runtime directory.
- Treat repository paths as read-only unless the Task explicitly defines a writable output path.
- Record runner mode, dependency snapshot, environment snapshot, runtime artifacts, and network setting for every TestRun.
- Default runner network access to disabled unless TestCommand or Environment explicitly enables it.

Minimum verification for such Tasks:

```bash
pytest backend/app/tests/tools -q
```

If the tools test directory does not exist yet, the Task that first introduces tool execution must create focused allowlist and path-safety tests before implementing execution.

## 12. Dependency Change Rules

Adding dependencies requires an explicit reason.

Rules:

- Explain why the dependency is needed.
- Prefer existing stack and standard library when sufficient.
- Do not add a heavy framework for a small utility.
- Update lockfiles when dependency files change.
- Keep dependency changes in a dedicated commit when possible.
- Run install/build smoke after dependency changes.

Commit body must include:

```text
Why:
- What problem this dependency solves.

Alternatives considered:
- Existing code/standard library/other smaller option.

Validation:
- Install/build/test command and result.
```

## 13. Failure Handling

When verification fails:

1. First failure: read logs and identify the smallest likely cause.
2. Second failure: stop expanding implementation and debug the root cause.
3. Third failure: update handoff with evidence and mark the Task blocked or unfinished.

Forbidden failure handling:

- Do not remove assertions to pass tests.
- Do not add skip/xfail unless the Task explicitly concerns test quarantining policy.
- Do not silence errors without root cause.
- Do not make production behavior looser only to satisfy generated tests.

Handoff format for unresolved failure:

```text
Failed command:
Observed error:
Likely cause:
Attempts made:
Risk:
Next suggested command:
```

## 14. Rollback Rules

Every Task commit must be reversible.

Rules:

- Prefer `git revert <commit>` for rollback.
- Do not use `git reset --hard` unless the user explicitly requests it.
- If a Task introduces structural problems, revert the Task commit before redesigning.
- Record the latest known stable commit in handoff when a session ends after multiple commits.
- If a WIP checkpoint exists, the next session must complete or revert it first.

## 15. Memory Update Policy

Memory 不是 Git 的重复记录。Memory 的职责是让下一轮 AI 能快速、准确地接上当前项目状态。

最终规则：

```text
每个 Task：测试 + commit。
每个 Slice：测试汇总 + commit 汇总 + 更新 memory。
每个重大变化：立即更新 memory。
```

### 15.1 Task 级别

每个 Task 完成后必须：

- 运行测试，或记录未验证原因。
- 创建 git commit。
- 如果当前 Slice task table 已存在，更新该 Task 状态。

Task 完成后默认不强制更新 `memory/07-dev-log.md`，避免 memory 变成流水账。

但出现以下情况时，必须立即更新 memory：

- 产品定位变化。
- V1 范围变化。
- 技术栈变化。
- 数据模型契约变化。
- API 契约变化。
- 状态机变化。
- 安全或审批策略变化。
- 发现文档与实现冲突。
- 测试无法运行或连续失败。
- 出现阻塞，需要下一轮 AI 接手。
- 用户临时改变优先级。

### 15.2 Slice 级别

每个 Slice 完成后必须更新：

- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

必要时同步更新：

- `memory/11-implementation-slices.md`
- `memory/05-roadmap.md`
- `docs/implementation/02-v1-slice-plan.md`

Slice 结束时，handoff 必须记录：

- 当前 Slice 状态。
- 本轮完成内容。
- 本轮验证命令和结果。
- 本轮 commit 表。
- 未完成问题。
- 风险提醒。
- 下一轮推荐 Task。
- 最新稳定 commit。

### 15.3 Memory 写作规范

- `memory/07-dev-log.md` 写长期摘要，不写每个小改动。
- `memory/08-session-handoff.md` 写给下一轮 AI，必须具体、可执行。
- `memory/README.md` 只在新增、删除、调整关键文档时更新。
- contracts/docs 只在事实变化时更新，不因为普通实现进度更新。
- memory 不重复粘贴完整 git diff，只记录 commit hash、结论、风险和下一步。

### 15.4 立即更新 Memory 的判断门禁

开发过程中只要出现下面任意一个问题答案为“是”，AI 必须暂停 coding，先更新 memory 或对应 docs：

```text
如果不写下来，下一轮 AI 是否会误解当前项目状态？
本次实现原因是否发生变化？
contracts、范围或状态机是否发生变化？
是否出现 git log 无法解释清楚的阻塞？
是否需要下一轮 AI 特别注意某个风险？
```

## 16. Task Progress Table

Each active Slice should maintain a progress table in `memory/08-session-handoff.md` or the relevant implementation plan:

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Backend health API | done | `pytest backend/app/tests/test_health.py -q` | `abc123` | pass |
| Redis ready check | doing | `pytest backend/app/tests/test_ready.py -q` | - | investigating timeout |

Allowed statuses:

```text
planned, doing, blocked, done, reverted
```

## 17. Handoff Requirements

At the end of each Slice or when immediate memory update conditions are met, update `memory/08-session-handoff.md` with:

```text
Current Slice:
Current Task:
Completed:
Verification:
Changed files:
Commits:
Unverified items:
Risks:
Next recommended Task:
Latest stable commit:
```

Commit table template:

| Commit | Content | Verification |
|---|---|---|
| `abc123` | `feat(backend): add health check endpoint` | `pytest backend/app/tests/test_health.py -q` |
| `def456` | `docs(memory): update slice handoff` | doc self-check |

`memory/07-dev-log.md` records long-term Slice summaries. `memory/08-session-handoff.md` records operational details for the next session.

## 18. Standard Start Prompt

```text
Please start by reading:
- memory/README.md
- memory/13-ai-readable-project-brief.md
- memory/08-session-handoff.md
- docs/product/01-positioning-and-scope.md
- docs/contracts/*
- docs/implementation/04-ai-vibecoding-governance.md
- the fixture related to this Task

Work on only one Slice and one Task unless I explicitly ask otherwise.
Before coding, define the Task Definition Of Ready.
For the Task, write or run focused verification, implement the minimal change, verify, inspect git diff, commit, and update handoff.
Do not push unless I explicitly ask.
```

## 19. Standard Finish Checklist

Before ending a session, AI must confirm:

```text
Current Slice:
Current Task:
Task status:
Verification command:
Verification result:
Commit hash:
Changed files:
Docs updated:
Memory updated:
Unverified items:
Risks:
Next Task:
```

If there is no commit, explain why the Task is not complete or why the session only changed planning documents.

## 20. Examples

### 20.1 Good Task Commit

```bash
git status --short
pytest backend/app/tests/test_health.py -q
git add backend/app/main.py backend/app/tests/test_health.py
git commit -m "feat(backend): add health check endpoint"
```

### 20.2 Good Contract-Then-Code Sequence

```text
docs(contracts): add tool definition model contract
feat(tool): implement tool definition model
test(tool): cover tool definition allowlist validation
docs(memory): record slice 8 completion handoff
```

### 20.3 Good Slice Commit Series

```text
chore(repo): initialize backend workspace
feat(backend): add health check endpoint
feat(backend): add database ready check
feat(worker): add redis queue smoke worker
feat(frontend): add base layout and health probe
```
