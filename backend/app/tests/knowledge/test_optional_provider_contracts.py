from __future__ import annotations

import uuid
from types import SimpleNamespace

from backend.app.modules.knowledge.optional_providers import search_optional_provider


CARD_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


class FakeQdrant:
    def search(self, **_kwargs):
        return [
            {
                "id": "provider-point-id",
                "score": 1.4,
                "payload": {
                    "knowledge_card_id": str(CARD_ID),
                    "source_locator": {"section": "4.2"},
                    "snippet": "safe card text",
                    "secret": "must not escape",
                },
            },
        ]


class FakeHaystack:
    def search(self, **_kwargs):
        return [
            SimpleNamespace(
                id="document-id",
                score=0.8,
                content="document body",
                meta={"knowledge_card_id": str(CARD_ID), "source_locator": {"line": 8}},
            ),
        ]


class FakeLlamaIndex:
    def search(self, **_kwargs):
        return [
            SimpleNamespace(
                node=SimpleNamespace(
                    node_id="node-id",
                    text="node body",
                    metadata={"knowledge_card_id": str(CARD_ID)},
                ),
                score=0.7,
            ),
        ]


def test_qdrant_match_is_clamped_and_provider_payload_is_private() -> None:
    result = search_optional_provider(
        "qdrant",
        FakeQdrant(),
        query_text="token refresh",
        limit=5,
        filters={"module_keys": ["auth"]},
        retrieval_mode="vector",
    )

    assert result.available is True
    assert result.degraded is False
    assert result.matches[0].knowledge_card_id == CARD_ID
    assert result.matches[0].vector_score == 1.0
    assert result.matches[0].source_locator == {"section": "4.2"}
    assert "secret" not in result.matches[0].source_locator
    assert "provider-point-id" not in repr(result.matches[0])


def test_haystack_and_llamaindex_normalize_to_the_same_private_shape() -> None:
    haystack = search_optional_provider(
        "haystack",
        FakeHaystack(),
        query_text="expiry",
        limit=5,
        filters={},
        retrieval_mode="hybrid",
    )
    llama = search_optional_provider(
        "llamaindex",
        FakeLlamaIndex(),
        query_text="expiry",
        limit=5,
        filters={},
        retrieval_mode="hybrid",
    )

    assert haystack.matches[0].knowledge_card_id == CARD_ID
    assert haystack.matches[0].vector_score == 0.8
    assert llama.matches[0].knowledge_card_id == CARD_ID
    assert llama.matches[0].vector_score == 0.7
    assert haystack.matches[0].retrieval_reason == "haystack_retrieval"
    assert llama.matches[0].retrieval_reason == "llamaindex_retrieval"


def test_missing_client_and_failing_client_have_stable_degraded_snapshots() -> None:
    unavailable = search_optional_provider(
        "qdrant",
        None,
        query_text="anything",
        limit=5,
        filters={},
        retrieval_mode="vector",
    )

    class Failing:
        def search(self, **_kwargs):
            raise TimeoutError("provider payload must not be persisted")

    failed = search_optional_provider(
        "qdrant",
        Failing(),
        query_text="anything",
        limit=5,
        filters={},
        retrieval_mode="vector",
    )

    assert unavailable.fallback_reason == "provider_unavailable"
    assert unavailable.capability_snapshot["reason"] == "client_not_configured"
    assert failed.fallback_reason == "provider_search_failed"
    assert failed.capability_snapshot["reason"] == "TimeoutError"
    assert "provider payload" not in repr(failed.capability_snapshot)


def test_invalid_provider_candidates_are_excluded_without_fabricated_scores() -> None:
    class Invalid:
        def search(self, **_kwargs):
            return [
                {"id": "not-a-card", "score": "not-a-score", "payload": {}},
                {"id": "also-not-a-card", "score": 0.9, "payload": {}},
            ]

    result = search_optional_provider(
        "qdrant",
        Invalid(),
        query_text="anything",
        limit=5,
        filters={},
        retrieval_mode="vector",
    )

    assert result.matches == ()
    assert result.degraded is True
    assert result.fallback_reason == "provider_candidate_unavailable"
    assert result.capability_snapshot["candidate_count"] == 0
