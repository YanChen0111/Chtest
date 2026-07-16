from __future__ import annotations

import uuid
from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping, Protocol, Sequence


OPTIONAL_PROVIDER_TYPES = frozenset({"qdrant", "haystack", "llamaindex"})


class ProviderUnavailableError(RuntimeError):
    """Raised when an optional provider client is not configured."""


class ProviderSearchClient(Protocol):
    def search(
        self,
        *,
        query_text: str,
        limit: int,
        filters: Mapping[str, Any],
        retrieval_mode: str,
    ) -> Sequence[Any]: ...


@dataclass(frozen=True)
class OptionalProviderMatch:
    knowledge_card_id: uuid.UUID | None
    source_locator: dict[str, Any]
    snippet: str | None
    keyword_score: float | None
    vector_score: float | None
    rerank_score: float | None
    retrieval_reason: str


@dataclass(frozen=True)
class OptionalProviderResult:
    provider_type: str
    matches: tuple[OptionalProviderMatch, ...]
    available: bool
    degraded: bool
    fallback_reason: str | None
    capability_snapshot: dict[str, Any]


def search_optional_provider(
    provider_type: str,
    client: ProviderSearchClient | None,
    *,
    query_text: str,
    limit: int,
    filters: Mapping[str, Any],
    retrieval_mode: str,
) -> OptionalProviderResult:
    """Run a fake/provider client while keeping its response private.

    The adapter accepts the small common subset exposed by the three optional
    provider families. It intentionally drops unknown payloads and raw client
    identifiers before callers can persist or return the result.
    """
    if provider_type not in OPTIONAL_PROVIDER_TYPES:
        raise ValueError(f"unsupported optional provider: {provider_type}")
    base_snapshot = {
        "provider_type": provider_type,
        "contract_version": "optional-provider-v1",
        "available": False,
        "searchable": False,
        "supports_hybrid": provider_type != "qdrant",
    }
    if client is None:
        return OptionalProviderResult(
            provider_type=provider_type,
            matches=(),
            available=False,
            degraded=True,
            fallback_reason="provider_unavailable",
            capability_snapshot={**base_snapshot, "reason": "client_not_configured"},
        )
    try:
        raw_items = client.search(
            query_text=query_text,
            limit=max(1, min(limit, 50)),
            filters=dict(filters),
            retrieval_mode=retrieval_mode,
        )
        matches = tuple(
            match
            for item in raw_items
            if (match := normalize_provider_match(provider_type, item, retrieval_mode=retrieval_mode))
            is not None
        )
    except Exception as exc:
        return OptionalProviderResult(
            provider_type=provider_type,
            matches=(),
            available=True,
            degraded=True,
            fallback_reason="provider_search_failed",
            capability_snapshot={**base_snapshot, "available": True, "reason": type(exc).__name__},
        )
    return OptionalProviderResult(
        provider_type=provider_type,
        matches=matches,
        available=True,
        degraded=not bool(matches),
        fallback_reason="provider_candidate_unavailable" if not matches else None,
        capability_snapshot={
            **base_snapshot,
            "available": True,
            "searchable": True,
            "candidate_count": len(matches),
        },
    )


def normalize_provider_match(
    provider_type: str,
    item: Any,
    *,
    retrieval_mode: str,
) -> OptionalProviderMatch | None:
    if provider_type == "qdrant":
        raw_id = _read(item, "id")
        payload = _as_mapping(_read(item, "payload"))
        card_id = _parse_uuid(payload.get("knowledge_card_id") or raw_id)
        score = _score(_read(item, "score"))
        return _match(card_id, payload, score, retrieval_mode, "qdrant_similarity")
    if provider_type == "haystack":
        meta = _as_mapping(_read(item, "meta"))
        card_id = _parse_uuid(meta.get("knowledge_card_id"))
        score = _score(_read(item, "score"))
        return _match(card_id, meta, score, retrieval_mode, "haystack_retrieval")
    if provider_type == "llamaindex":
        node = _read(item, "node") or item
        metadata = _as_mapping(_read(node, "metadata"))
        card_id = _parse_uuid(metadata.get("knowledge_card_id"))
        score = _score(_read(item, "score"))
        return _match(card_id, metadata, score, retrieval_mode, "llamaindex_retrieval")
    return None


def _match(
    card_id: uuid.UUID | None,
    metadata: Mapping[str, Any],
    score: float | None,
    retrieval_mode: str,
    reason: str,
) -> OptionalProviderMatch | None:
    if card_id is None or score is None:
        return None
    vector_score = score if retrieval_mode in {"vector", "hybrid"} else None
    keyword_score = score if retrieval_mode == "keyword" else None
    return OptionalProviderMatch(
        knowledge_card_id=card_id,
        source_locator=_safe_locator(metadata.get("source_locator")),
        snippet=_safe_text(metadata.get("snippet") or metadata.get("content")),
        keyword_score=keyword_score,
        vector_score=vector_score,
        rerank_score=None,
        retrieval_reason=reason,
    )


def _read(value: Any, key: str) -> Any:
    if isinstance(value, Mapping):
        return value.get(key)
    return getattr(value, key, None)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _parse_uuid(value: Any) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(value)) if value else None
    except (TypeError, ValueError, AttributeError):
        return None


def _score(value: Any) -> float | None:
    try:
        if value is None:
            return None
        numeric = float(value)
        if not isfinite(numeric):
            return None
        return max(0.0, min(1.0, numeric))
    except (TypeError, ValueError):
        return None


def _safe_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return value[:1000]


def _safe_locator(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): item for key, item in value.items() if isinstance(key, str) and len(key) <= 80}
