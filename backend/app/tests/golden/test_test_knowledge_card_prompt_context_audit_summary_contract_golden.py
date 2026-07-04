from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path(
    "docs/fixtures/31-test-knowledge-card-prompt-context-audit-summary-golden.md"
)
SLICE_PATH = Path(
    "docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")
PROMPT_SKILL_CONTRACT_PATH = Path("docs/contracts/05-prompt-skill-contract.md")

EXPECTED_SURFACES = [
    "TestKnowledgeCard Prompt Context Audit Summary",
    "summarize_prompt_context_consumption",
    "prompt_context_audit_summary",
    "prompt context consumption artifact",
    "prompt context evidence artifact",
    "used_knowledge",
    "output citations",
    "skipped evidence",
    "unsupported claims",
    "source hash",
    "context manifest",
    "PromptVersion",
    "SkillVersion",
    "ReviewHistory",
    "failure behavior",
]

REQUIRED_TERMS = [
    "prompt_context_audit_summary_action",
    "summarize_prompt_context_consumption",
    "prompt request id",
    "AITask id",
    "consuming agent step",
    "intended output artifact type",
    "prompt context consumption artifact id",
    "test_knowledge_card_prompt_context_consumption.json",
    "prompt context evidence artifact id",
    "test_knowledge_card_prompt_context_evidence.json",
    "context manifest artifact id",
    "context_manifest",
    "context_manifest.json",
    "used_knowledge decision",
    "used_knowledge=true",
    "used_knowledge=false",
    "output citation ids",
    "cited TestKnowledgeCard ids",
    "cited context entry ids",
    "cited source hashes",
    "source hash",
    "source quote/hash pointer",
    "skipped evidence ids",
    "skipped evidence",
    "skip reasons",
    "unsupported claims",
    "unsupported claim summaries",
    "PromptVersion id",
    "SkillVersion id",
    "PromptVersion name/version",
    "SkillVersion name/version",
    "ReviewHistory ids",
    "failure_code",
    "prompt context audit summary artifact id",
    "test_knowledge_card_prompt_context_audit_summary.json",
    "artifact_type=test_knowledge_card_prompt_context_audit_summary",
    "usage status",
    "knowledge_used",
    "knowledge_not_used",
    "knowledge_skipped",
    "knowledge_failed",
    "cited entries",
    "cited evidence summaries",
    "skipped entries",
    "skipped evidence summaries",
    "review flags",
    "failure reasons",
    "source manifest ids",
    "source hashes",
    "PromptVersion/SkillVersion trace",
    "context manifest links",
    "ReviewHistory links",
    "prompt_input.json",
]

FORBIDDEN_SIDE_EFFECTS = [
    "broad TestKnowledgeCard CRUD",
    "TestKnowledgeCard CRUD",
    "TestKnowledgeCard auto-creation",
    "automatic card creation from model output",
    "automatic card creation",
    "automatic card approval",
    "automatic prompt eligibility",
    "allowed_for_prompt=true auto-marking",
    "automatic knowledge ingestion",
    "KnowledgeIngestionAgent runtime",
    "backend feature API",
    "frontend page",
    "frontend rendering",
    "report generation behavior",
    "report renderer",
    "report export behavior",
    "migration",
    "card table change",
    "list/update/delete API",
    "prompt assembly implementation",
    "prompt runtime execution",
    "prompt runtime retrieval implementation",
    "deterministic retrieval behavior change",
    "deterministic retrieval ranking change",
    "retrieval ranking change",
    "vector index",
    "vector database",
    "embedding",
    "embeddings",
    "reranking",
    "background indexing",
    "graph job",
    "GraphRAG job",
    "MCP runtime",
    "provider call",
    "provider SDK",
    "credentials",
    "OAuth",
    "remote URL fetch",
    "prompt runner",
    "queue",
    "scheduler",
    "background worker",
    "artifact upload",
    "Artifact mutation",
    "artifact delete",
    "source artifact mutation",
    "prompt context consumption artifact mutation",
    "prompt context evidence artifact mutation",
    "retrieval boundary artifact mutation",
    "prompt eligibility artifact mutation",
    "historical evidence mutation",
    "historical ReviewHistory mutation",
    "PromptVersion mutation",
    "SkillVersion mutation",
    "FailureAnalysis mutation",
    "Report mutation",
    "TestRun mutation",
    "TestResult mutation",
    "TestCase mutation",
    "GeneratedCaseCandidate mutation",
    "KnowledgeEvidence mutation",
    "existing TestKnowledgeCard content mutation",
    "review bypass",
    "automatic merge",
    "automatic archive",
    "automatic replace",
    "automatic relabel",
    "automatic delete",
    "generated-case auto-approval",
    "TestCase auto-promotion",
    "runner behavior change",
    "remote CI provider behavior",
    "RBAC",
    "tenants",
    "permissions",
    "package upgrades",
]


def test_golden_test_knowledge_card_prompt_context_audit_summary_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_test_knowledge_card_prompt_context_audit_summary_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_test_knowledge_card_prompt_context_audit_summary_forbids_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()
    data_contract = _read(DATA_CONTRACT_PATH)
    api_contract = _read(API_CONTRACT_PATH)
    state_contract = _read(STATE_CONTRACT_PATH)
    artifact_contract = _read(ARTIFACT_CONTRACT_PATH)
    prompt_skill_contract = _read(PROMPT_SKILL_CONTRACT_PATH)

    for side_effect in FORBIDDEN_SIDE_EFFECTS:
        _assert_normalized_contains(fixture, side_effect)

    _assert_normalized_contains(slice_plan, "No frontend page")
    _assert_normalized_contains(data_contract, "summarize_prompt_context_consumption")
    _assert_normalized_contains(api_contract, "must not invent citations")
    _assert_normalized_contains(
        state_contract, "prompt_context_audit_summary_failed"
    )
    _assert_normalized_contains(
        artifact_contract, "artifact_type=test_knowledge_card_prompt_context_audit_summary"
    )
    _assert_normalized_contains(
        prompt_skill_contract, "rewrite `used_knowledge`"
    )
    _assert_normalized_contains(contracts, "output citations")
    _assert_normalized_contains(contracts, "skipped evidence")
    _assert_normalized_contains(contracts, "unsupported claims")


def _alias(term: str) -> str:
    aliases = {
        "prompt_context_audit_summary": "prompt_context_audit_summary_action",
        "prompt context consumption artifact": (
            "prompt context consumption artifact id"
        ),
        "prompt context evidence artifact": "prompt context evidence artifact id",
        "context manifest": "context manifest artifact id",
        "used_knowledge": "used_knowledge",
        "used_knowledge decision": "`used_knowledge` decision",
        "output citations": "output citations",
        "skipped evidence": "skipped evidence",
        "unsupported claims": "unsupported claims",
        "source hash": "source hash",
        "failure behavior": "failure behavior",
        "test_knowledge_card_prompt_context_consumption.json": (
            "test_knowledge_card_prompt_context_consumption"
        ),
        "test_knowledge_card_prompt_context_evidence.json": (
            "test_knowledge_card_prompt_context_evidence"
        ),
        "context_manifest.json": "context_manifest.json",
        "test_knowledge_card_prompt_context_audit_summary.json": (
            "test_knowledge_card_prompt_context_audit_summary.json"
        ),
        "artifact_type=test_knowledge_card_prompt_context_audit_summary": (
            "artifact_type=test_knowledge_card_prompt_context_audit_summary"
        ),
        "PromptVersion/SkillVersion trace": "PromptVersion/SkillVersion trace",
        "prompt_input.json": "prompt_input.json",
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
