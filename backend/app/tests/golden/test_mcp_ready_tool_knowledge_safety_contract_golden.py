from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path("docs/fixtures/21-mcp-ready-tool-knowledge-safety-golden.md")
SLICE_PATH = Path(
    "docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")

EXPECTED_CONTRACTS = [
    "ToolDefinition",
    "ToolInvocation",
    "KnowledgeAdapterConfig",
    "KnowledgeEvidence",
    "Artifact",
]

REQUIRED_SAFETY_TERMS = [
    "ToolDefinition safety",
    "ToolInvocation safety",
    "KnowledgeAdapter safety",
    "input_schema",
    "output_schema",
    "risk_level",
    "approval_required",
    "timeout_seconds",
    "artifact_policy",
    "provider_state",
    "disabled",
    "configured",
    "unhealthy",
    "local/no-knowledge fallback",
    "KnowledgeEvidence",
    "Artifact",
    "human gate",
]

FORBIDDEN_SIDE_EFFECTS = [
    "MCP runtime",
    "MCP server/client transport",
    "remote MCP call",
    "plugin installation",
    "provider SDK call",
    "external provider call",
    "credentials storage",
    "OAuth state",
    "remote URL fetch",
    "vector index",
    "embedding",
    "reranking",
    "graph job",
    "Artifact mutation",
    "Report conclusion",
    "runner behavior change",
    "review bypass",
    "generated-case auto-approval",
    "TestCase auto-promotion",
    "remote CI provider behavior",
    "RBAC",
    "tenants",
    "permissions",
]


def test_golden_mcp_ready_tool_knowledge_safety_names_contracts() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for contract in EXPECTED_CONTRACTS:
        assert contract in fixture
        assert contract in slice_plan
        assert contract in contracts


def test_golden_mcp_ready_tool_knowledge_safety_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_SAFETY_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_normalized_contains(slice_plan, _slice_alias(term))
        _assert_any_contract_contains(contracts, term)


def test_golden_mcp_ready_tool_knowledge_safety_forbids_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()
    api_contract = _read(API_CONTRACT_PATH)
    state_contract = _read(STATE_CONTRACT_PATH)

    for side_effect in FORBIDDEN_SIDE_EFFECTS:
        _assert_normalized_contains(fixture, side_effect)

    _assert_normalized_contains(slice_plan, "No MCP runtime")
    _assert_normalized_contains(api_contract, "must not start MCP runtime")
    _assert_normalized_contains(api_contract, "provider SDK calls")
    _assert_normalized_contains(api_contract, "generated-case auto-approval")
    _assert_normalized_contains(state_contract, "must not create TestKnowledgeCard rows")
    _assert_normalized_contains(contracts, "provider-specific payloads")
    _assert_normalized_contains(contracts, "must not create ToolInvocation rows")
    _assert_normalized_contains(contracts, "must not approve GeneratedCaseCandidate rows")


def _slice_alias(term: str) -> str:
    if term == "input_schema":
        return "strict JSON input/output schema"
    if term == "output_schema":
        return "strict JSON input/output schema"
    if term == "timeout_seconds":
        return "timeout"
    if term == "risk_level":
        return "risk level"
    if term == "approval_required":
        return "approval requirement"
    if term == "artifact_policy":
        return "artifact policy"
    if term == "provider_state":
        return "provider state"
    if term == "local/no-knowledge fallback":
        return "fallback"
    return term


def _assert_any_contract_contains(contracts: str, expected: str) -> None:
    aliases = {
        "input_schema": ["input_schema", "input_schema_json", "input_schema"],
        "output_schema": ["output_schema", "output_schema_json", "output_schema"],
        "artifact_policy": ["artifact_policy", "artifact_policy_json"],
        "local/no-knowledge fallback": ["local/no-knowledge fallback"],
        "human gate": ["human gate", "approval_status=approved"],
    }
    for alias in aliases.get(expected, [expected]):
        if _normalized_contains(contracts, alias):
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
        ]
    )


def _read(path: Path) -> str:
    assert path.exists(), f"{path} is missing"
    return path.read_text(encoding="utf-8")
