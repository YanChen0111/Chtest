from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path(
    "docs/fixtures/38-knowledge-adapter-provider-evaluation-plan-golden.md"
)
SLICE_PATH = Path(
    "docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")
PROMPT_SKILL_CONTRACT_PATH = Path("docs/contracts/05-prompt-skill-contract.md")

EXPECTED_SURFACES = [
    "KnowledgeAdapter Provider Evaluation Plan",
    "evaluate_knowledge_adapter_provider_plan",
    "knowledge_adapter_provider_evaluation_plan",
    "provider evaluation",
    "provider candidate",
    "Haystack",
    "LlamaIndex",
    "GraphRAG",
    "KnowledgeEvidence",
    "provider_state",
    "fallback behavior",
    "license review",
    "reference intake",
    "disabled by default",
    "metrics",
    "provider suitability status",
    "ReviewHistory",
    "failure behavior",
]

REQUIRED_TERMS = [
    "knowledge_adapter_provider_evaluation_plan_action",
    "evaluate_knowledge_adapter_provider_plan",
    "evaluate_provider_candidate",
    "record_provider_evaluation",
    "block_provider_candidate",
    "request_provider_evaluation_revision",
    "enforce_disabled_by_default",
    "provider_candidate_not_evaluated",
    "provider_evaluation_pending",
    "provider_evaluation_recorded",
    "provider_evaluation_blocked",
    "provider_evaluation_needs_revision",
    "provider_candidate_disabled_by_default",
    "candidate provider name",
    "provider family",
    "adapter type",
    "provider version",
    "adapter version",
    "license name",
    "license URL",
    "license compatibility notes",
    "license review result",
    "reference intake URLs",
    "documentation snapshot artifact ids",
    "supported retrieval modes",
    "supported source types",
    "expected KnowledgeEvidence normalization fields",
    "provider_state",
    "provider_state recommendation",
    "disabled by default policy",
    "disabled by default decision",
    "network policy",
    "credential policy",
    "fallback behavior expectations",
    "fallback behavior summary",
    "metrics to collect",
    "metrics plan",
    "metric set",
    "evidence normalization completeness",
    "source traceability coverage",
    "redaction safety status",
    "fallback coverage",
    "safety and redaction requirements",
    "source hash requirements",
    "source manifest ids",
    "source hashes",
    "ReviewHistory ids",
    "ReviewHistory links",
    "provider evaluation plan id",
    "provider evaluation plan artifact id",
    "knowledge_adapter_provider_evaluation_plan_artifact_id",
    "knowledge_adapter_provider_evaluation_plan.json",
    "artifact_type=knowledge_adapter_provider_evaluation_plan",
    "manifest_kind=knowledge_adapter_provider_evaluation_plan",
    "provider suitability status",
    "not_evaluated",
    "suitable",
    "suitable_with_constraints",
    "blocked",
    "needs_revision",
    "unsupported",
    "KnowledgeEvidence normalization notes",
    "citation traceability requirements",
    "redaction and safety requirements",
    "blocker reasons",
    "unresolved safety questions",
    "fallback_required",
    "local_no_knowledge_fallback",
    "normalization_required",
    "citation_traceability_required",
    "license_review_required",
    "planning evidence only",
    "used_knowledge=true",
    "failure_code",
    "failure code",
    "visible_reason",
    "visible reason",
    "prompt_input.json",
    "missing, stale, unsafe, unlicensed",
    "license-unknown",
    "version-unknown",
    "reference-missing",
    "reference-mismatched",
    "normalization-unsupported",
    "redaction-failed",
    "provider-state-unsafe",
    "fallback-missing",
    "cross-project",
    "unbounded",
    "credential-required",
    "runtime-required",
    "provider-evaluation-mismatched input",
]

FORBIDDEN_SIDE_EFFECTS = [
    "Haystack provider integration",
    "LlamaIndex provider integration",
    "GraphRAG provider integration",
    "provider SDK",
    "provider SDK call",
    "external provider call",
    "API key handling",
    "credentials",
    "OAuth",
    "remote URL fetch",
    "external call",
    "network retrieval",
    "runtime retrieval",
    "provider-backed prompt context evidence",
    "prompt assembly implementation",
    "prompt runtime execution",
    "automatic used_knowledge=true marking",
    "vector database",
    "vector index",
    "embedding model",
    "embedding service",
    "embedding vectors",
    "embedding",
    "embeddings",
    "semantic index",
    "ANN search",
    "reranking service",
    "reranking",
    "background indexing job",
    "crawler",
    "document chunking pipeline",
    "graph runtime",
    "GraphRAG job",
    "MCP runtime",
    "frontend page",
    "report generation behavior",
    "export/download endpoint",
    "backend feature API",
    "endpoint",
    "router",
    "service",
    "worker",
    "queue",
    "scheduler",
    "migration",
    "package upgrade",
    "broad KnowledgeAdapter CRUD",
    "automatic provider enablement",
    "automatic knowledge ingestion",
    "TestKnowledgeCard CRUD",
    "automatic prompt eligibility",
    "artifact upload",
    "Artifact mutation",
    "artifact delete",
    "KnowledgeAdapterConfig runtime state mutation",
    "KnowledgeEvidence mutation",
    "TestKnowledgeCard mutation",
    "GeneratedCaseCandidate mutation",
    "TestCase auto-promotion",
    "generated-case auto-approval",
    "ToolInvocation rows",
    "execute AITasks",
    "runner behavior change",
    "remote CI provider behavior",
    "RBAC",
    "tenants",
    "permissions",
    "review bypass",
]


def test_golden_knowledge_adapter_provider_evaluation_plan_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_knowledge_adapter_provider_evaluation_plan_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_knowledge_adapter_provider_evaluation_plan_forbids_runtime_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    contracts = _contracts_text()
    data_contract = _read(DATA_CONTRACT_PATH)
    api_contract = _read(API_CONTRACT_PATH)
    state_contract = _read(STATE_CONTRACT_PATH)
    artifact_contract = _read(ARTIFACT_CONTRACT_PATH)
    prompt_skill_contract = _read(PROMPT_SKILL_CONTRACT_PATH)

    for side_effect in FORBIDDEN_SIDE_EFFECTS:
        _assert_normalized_contains(fixture, side_effect)

    _assert_normalized_contains(data_contract, "evaluate_knowledge_adapter_provider_plan")
    _assert_normalized_contains(data_contract, "must not create provider enablement")
    _assert_normalized_contains(data_contract, "raw provider payloads")
    _assert_normalized_contains(api_contract, "must not install packages")
    _assert_normalized_contains(api_contract, "provider-backed prompt context evidence")
    _assert_normalized_contains(
        state_contract, "provider_candidate_disabled_by_default"
    )
    _assert_normalized_contains(state_contract, "evaluate_knowledge_adapter_provider_plan")
    _assert_normalized_contains(
        artifact_contract, "artifact_type=knowledge_adapter_provider_evaluation_plan"
    )
    _assert_normalized_contains(artifact_contract, "runtime `prompt_input.json`")
    _assert_normalized_contains(artifact_contract, "raw provider payloads")
    _assert_normalized_contains(
        prompt_skill_contract, "must not write runtime `prompt_input.json`"
    )
    _assert_normalized_contains(
        prompt_skill_contract, "must not start runtime retrieval"
    )
    _assert_normalized_contains(contracts, "provider SDKs")
    _assert_normalized_contains(contracts, "vector indexes")
    _assert_normalized_contains(contracts, "KnowledgeAdapterConfig")
    _assert_normalized_contains(contracts, "display/health metadata")
    _assert_normalized_contains(contracts, "used_knowledge=true")


def _alias(term: str) -> str:
    aliases = {
        "provider candidate": "candidate providers",
        "disabled by default": "disabled by default policy",
        "knowledge_adapter_provider_evaluation_plan": (
            "knowledge_adapter_provider_evaluation_plan_action"
        ),
        "knowledge_adapter_provider_evaluation_plan_action": (
            "knowledge_adapter_provider_evaluation_plan_action=evaluate_knowledge_adapter_provider_plan"
        ),
        "metrics": "metrics to collect",
        "failure behavior": "failure code and visible reason",
        "provider evaluation plan artifact id": "provider evaluation plan id or artifact id",
        "KnowledgeEvidence normalization": (
            "KnowledgeEvidence normalization fields"
        ),
        "redaction safety status": "redaction_safety_status",
        "fallback coverage": "fallback_coverage",
        "safety and redaction requirements": "redaction and safety requirements",
        "failure_code": "failure code",
        "provider-evaluation-mismatched input": "provider-evaluation- mismatched input",
    }
    return aliases.get(term, term)


def _assert_any_contains(texts: list[str], expected: str) -> None:
    if any(_normalized_contains(text, expected) for text in texts):
        return
    raise AssertionError(expected)


def _assert_normalized_contains(text: str, expected: str) -> None:
    assert _normalized_contains(text, expected), expected


def _normalized_contains(text: str, expected: str) -> bool:
    normalized_text = " ".join(text.split()).lower()
    normalized_expected = " ".join(expected.split()).lower()
    return normalized_expected in normalized_text


def _contracts_text() -> str:
    return "\n".join(
        _read(path)
        for path in [
            DATA_CONTRACT_PATH,
            API_CONTRACT_PATH,
            STATE_CONTRACT_PATH,
            ARTIFACT_CONTRACT_PATH,
            PROMPT_SKILL_CONTRACT_PATH,
        ]
    )


def _read(path: Path) -> str:
    assert path.exists(), f"{path} is missing"
    return path.read_text(encoding="utf-8")
