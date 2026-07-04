# TestKnowledgeCard Prompt Eligibility Golden

This fixture proves Slice 39 remains a contract-only TestKnowledgeCard Prompt
Eligibility definition. It is not broad TestKnowledgeCard CRUD, not a backend
feature API, not a frontend page, not a migration, and not prompt runtime
retrieval automation.

## Prompt Eligibility Scenario

A reviewed TestKnowledgeCard may become eligible for prompt context only after a
human review gate validates source evidence, source manifest, safe-to-show
status, redaction, ReviewHistory, and prompt eligibility artifact evidence. The
review starts from a reviewed TestKnowledgeCard id and the
reviewed_test_knowledge_card_creation.json creation artifact. The approval
action is `mark_card_prompt_eligible`, and it is the only action that can grant
`allowed_for_prompt=true`.

| Surface | Required boundary |
|---|---|
| TestKnowledgeCard Prompt Eligibility | Human review of prompt reuse only |
| reviewed TestKnowledgeCard | Source card must already exist and be reviewed |
| mark_card_prompt_eligible | Human approval action for prompt reuse |
| deny_card_prompt_eligibility | Human denial action keeps cards out of prompts |
| request_prompt_eligibility_revision | Human revision action blocks reuse |
| revoke_card_prompt_eligibility | Human revocation action removes reuse |
| allowed_for_prompt | Prompt eligibility flag owned by this review gate |
| safe_to_show | Display safety must be true before approval |
| redaction | Redaction status must be reviewed |
| source evidence | Evidence must remain same-project and cited |
| source manifest | Source manifest links artifact evidence |
| ReviewHistory | ReviewHistory id records the decision |
| prompt eligibility reason | Non-empty reviewer reason is required |
| prompt eligibility artifact | Artifact records bounded approval evidence |
| revocation/failure behavior | Denial, revision, and revoke keep prompt reuse off |

## Review Actions

The contract must define:

- human review.
- prompt_eligibility_action.
- mark_card_prompt_eligible.
- deny_card_prompt_eligibility.
- request_prompt_eligibility_revision.
- revoke_card_prompt_eligibility.
- prompt_eligibility_decision.
- prompt_eligible.
- prompt_eligibility_denied.
- prompt_eligibility_revision_requested.
- prompt_eligibility_revoked.
- allowed_for_prompt=true.
- allowed_for_prompt=false.

## Eligibility Input

Prompt eligibility input must preserve:

- reviewed TestKnowledgeCard id.
- creation artifact id.
- reviewed_test_knowledge_card_creation.json.
- source_manifest.
- source manifest.
- same-project source Artifact.
- source_artifact_ids.
- source_quote_or_hash.
- source span.
- redaction report artifact id.
- redaction status reviewed.
- safe_to_show=true.
- reviewed source citations.
- unsupported claims.
- ReviewHistory id.
- prompt_eligibility_reason.

## Eligibility Evidence

Prompt eligibility evidence must preserve:

- test_knowledge_card_prompt_eligibility.json.
- artifact_type=test_knowledge_card_prompt_eligibility.
- owner_entity_type=TestKnowledgeCard.
- manifest_kind=test_knowledge_card_prompt_eligibility.
- prompt eligibility reason.
- prompt eligibility artifact.
- redaction_applied.
- safe_to_show.
- source evidence.
- source quote/hash.
- source manifest artifact id.
- source artifact ids.
- reviewer_label.
- reviewer_comment.
- failure_code.

## Prompt Context Boundary

Approval is not automatic:

- `allowed_for_prompt=true` must come only from human approval.
- safe_to_show=true does not automatically grant prompt eligibility.
- model confidence does not automatically grant prompt eligibility.
- schema validity does not automatically grant prompt eligibility.
- source presence does not automatically grant prompt eligibility.
- card creation does not automatically grant prompt eligibility.
- denied/revoked cards must not enter prompt context.
- cards denied for unsafe, stale, cross-project, missing, unbounded,
  unsupported, or redaction failed evidence keep `allowed_for_prompt=false`.

## Revocation/Failure Boundary

Revocation and failed review must remain auditable:

- revoke_card_prompt_eligibility records a prompt eligibility reason.
- prompt_eligibility_revoked sets or keeps allowed_for_prompt=false.
- prompt_eligibility_denied keeps allowed_for_prompt=false.
- prompt_eligibility_revision_requested keeps allowed_for_prompt=false.
- failure_code records denial, revision, revoke, or invalid evidence.
- source evidence and ReviewHistory remain append-only references.
- historical ReviewHistory mutation is forbidden.
- historical evidence mutation is forbidden.

## Forbidden Side Effects

The contract must not create or trigger:

- broad TestKnowledgeCard CRUD.
- TestKnowledgeCard CRUD.
- TestKnowledgeCard auto-creation.
- automatic card creation from model output.
- automatic card creation.
- automatic card approval.
- automatic prompt eligibility.
- allowed_for_prompt=true auto-marking.
- automatic knowledge ingestion.
- KnowledgeIngestionAgent runtime.
- backend feature API.
- frontend page.
- migration.
- card table change.
- list/update/delete API.
- prompt runtime retrieval change.
- deterministic retrieval behavior change.
- vector index.
- vector database.
- embedding.
- embeddings.
- reranking.
- background indexing.
- graph job.
- GraphRAG job.
- MCP runtime.
- provider call.
- provider SDK.
- credentials.
- OAuth.
- remote URL fetch.
- queue.
- scheduler.
- background worker.
- artifact upload.
- Artifact mutation.
- artifact delete.
- historical evidence mutation.
- historical ReviewHistory mutation.
- FailureAnalysis mutation.
- Report mutation.
- TestRun mutation.
- TestResult mutation.
- TestCase mutation.
- GeneratedCaseCandidate mutation.
- KnowledgeEvidence mutation.
- existing TestKnowledgeCard content mutation.
- review bypass.
- automatic merge.
- automatic archive.
- automatic replace.
- automatic relabel.
- automatic delete.
- generated-case auto-approval.
- TestCase auto-promotion.
- runner behavior change.
- report generation behavior change.
- remote CI provider behavior.
- RBAC.
- tenants.
- permissions.
- package upgrades.

TestKnowledgeCard Prompt Eligibility remains auditable prompt reuse evidence.
It preserves reviewed TestKnowledgeCard creation evidence, source manifest,
redaction, safe_to_show, ReviewHistory, unsupported claims, prompt eligibility
reason, revocation/failure behavior, and `allowed_for_prompt=false` until a
human reviewer explicitly grants prompt reuse.
