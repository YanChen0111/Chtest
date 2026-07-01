from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass
from pathlib import Path


class ArtifactPathError(ValueError):
    """Raised when an artifact-relative path is unsafe."""


@dataclass(frozen=True)
class ArtifactWriteResult:
    file_path: str
    size_bytes: int
    sha256: str


class LocalArtifactStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()

    def write_bytes(self, file_path: str, content: bytes) -> ArtifactWriteResult:
        destination = self._resolve_relative_path(file_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp_path = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")

        try:
            temp_path.write_bytes(content)
            os.replace(temp_path, destination)
        finally:
            if temp_path.exists():
                temp_path.unlink()

        return ArtifactWriteResult(
            file_path=self._normalize_relative_path(file_path),
            size_bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
        )

    def read_bytes(self, file_path: str) -> bytes:
        return self._resolve_relative_path(file_path).read_bytes()

    def _resolve_relative_path(self, file_path: str) -> Path:
        normalized_path = self._normalize_relative_path(file_path)
        destination = (self.root / normalized_path).resolve()
        if destination != self.root and self.root not in destination.parents:
            raise ArtifactPathError("Artifact path must stay inside the artifact root.")
        return destination

    def _normalize_relative_path(self, file_path: str) -> str:
        path = Path(file_path)
        if path.is_absolute():
            raise ArtifactPathError("Artifact path must be relative.")

        parts = path.parts
        if not parts or any(part in {"", ".", ".."} for part in parts):
            raise ArtifactPathError("Artifact path contains unsafe segments.")

        return Path(*parts).as_posix()
