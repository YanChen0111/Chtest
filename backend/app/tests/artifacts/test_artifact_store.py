from __future__ import annotations

import os
import hashlib
from pathlib import Path

import pytest

from backend.app.modules.ai_runtime.artifact_store import (
    ArtifactPathError,
    LocalArtifactStore,
)
from backend.app.modules.ai_runtime.schemas import ArtifactWriteResultRead


def test_write_bytes_uses_relative_path_and_returns_digest_and_size(tmp_path: Path) -> None:
    store = LocalArtifactStore(root=tmp_path)
    content = b'{"status":"ok"}\n'

    result = store.write_bytes(
        "projects/project-1/ai-tasks/task-1/raw_output.json",
        content,
    )

    assert result.file_path == "projects/project-1/ai-tasks/task-1/raw_output.json"
    assert result.size_bytes == len(content)
    assert result.sha256 == hashlib.sha256(content).hexdigest()
    assert (tmp_path / result.file_path).read_bytes() == content
    assert not list(tmp_path.rglob("*.tmp"))

    read_model = ArtifactWriteResultRead.model_validate(result, from_attributes=True)
    assert read_model.sha256 == result.sha256


def test_write_bytes_replaces_existing_file_atomically(tmp_path: Path) -> None:
    store = LocalArtifactStore(root=tmp_path)
    artifact_path = "projects/project-1/reports/report-1/report.json"

    first = store.write_bytes(artifact_path, b'{"version":1}')
    second = store.write_bytes(artifact_path, b'{"version":2}')

    assert first.file_path == second.file_path
    assert second.size_bytes == len(b'{"version":2}')
    assert second.sha256 == hashlib.sha256(b'{"version":2}').hexdigest()
    assert store.read_bytes(artifact_path) == b'{"version":2}'
    assert not list(tmp_path.rglob("*.tmp"))


def test_write_bytes_cleans_temp_file_when_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = LocalArtifactStore(root=tmp_path)

    def fail_replace(source: str | os.PathLike[str], destination: str | os.PathLike[str]) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(OSError, match="replace failed"):
        store.write_bytes("projects/project-1/ai-tasks/task-1/raw_output.json", b"partial")

    assert not list(tmp_path.rglob("*.tmp"))
    assert not list(tmp_path.rglob("raw_output.json"))


@pytest.mark.parametrize(
    "unsafe_path",
    [
        "../outside.json",
        "projects/../outside.json",
        "/tmp/outside.json",
        "projects/project-1/../../outside.json",
    ],
)
def test_rejects_paths_that_escape_artifact_root(tmp_path: Path, unsafe_path: str) -> None:
    store = LocalArtifactStore(root=tmp_path)

    with pytest.raises(ArtifactPathError):
        store.write_bytes(unsafe_path, b"unsafe")

    assert not (tmp_path.parent / "outside.json").exists()


def test_read_bytes_rejects_unsafe_paths(tmp_path: Path) -> None:
    store = LocalArtifactStore(root=tmp_path)

    with pytest.raises(ArtifactPathError):
        store.read_bytes("../outside.json")


def test_rejects_symlink_escape_inside_artifact_root(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "artifacts"
    root.mkdir()
    (root / "linked").symlink_to(outside, target_is_directory=True)
    store = LocalArtifactStore(root=root)

    with pytest.raises(ArtifactPathError):
        store.write_bytes("linked/escape.txt", b"unsafe")

    assert not (outside / "escape.txt").exists()


def test_root_is_created_when_missing(tmp_path: Path) -> None:
    root = tmp_path / "missing" / "artifacts"
    store = LocalArtifactStore(root=root)

    result = store.write_bytes("projects/project-1/test-runs/run-1/stdout.log", b"ok")

    assert root.is_dir()
    assert (root / result.file_path).read_bytes() == b"ok"
