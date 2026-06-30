from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath


@dataclass
class ParsedChangedFile:
    path: str
    old_path: str | None
    change_type: str
    language: str | None
    file_role: str
    risk_level: str
    risk_reasons: list[str] = field(default_factory=list)
    lines_added: int = 0
    lines_deleted: int = 0

    def to_manifest_item(self) -> dict:
        return {
            "path": self.path,
            "old_path": self.old_path,
            "change_type": self.change_type,
            "language": self.language,
            "file_role": self.file_role,
            "risk_level": self.risk_level,
            "risk_reasons": self.risk_reasons,
            "lines_added": self.lines_added,
            "lines_deleted": self.lines_deleted,
        }


def parse_local_diff(diff_text: str) -> list[ParsedChangedFile]:
    changed_files: list[ParsedChangedFile] = []
    current: dict | None = None

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            if current is not None:
                changed_files.append(build_changed_file(current))
            current = start_file_block(line)
            continue
        if current is None:
            continue
        if line.startswith("new file mode"):
            current["change_type"] = "added"
            continue
        if line.startswith("deleted file mode"):
            current["change_type"] = "deleted"
            continue
        if line.startswith("rename from "):
            current["old_path"] = line.removeprefix("rename from ").strip()
            current["change_type"] = "renamed"
            continue
        if line.startswith("rename to "):
            current["path"] = line.removeprefix("rename to ").strip()
            current["change_type"] = "renamed"
            continue
        if line.startswith("+++") and not line.startswith("++++"):
            new_path = normalize_diff_path(line.removeprefix("+++ ").strip())
            if new_path is not None:
                current["path"] = new_path
            continue
        if line.startswith("---") and not line.startswith("----"):
            old_path = normalize_diff_path(line.removeprefix("--- ").strip())
            if old_path is not None and current.get("change_type") == "deleted":
                current["path"] = old_path
            continue
        if line.startswith("+") and not line.startswith("+++"):
            current["lines_added"] += 1
            continue
        if line.startswith("-") and not line.startswith("---"):
            current["lines_deleted"] += 1

    if current is not None:
        changed_files.append(build_changed_file(current))
    return changed_files


def start_file_block(line: str) -> dict:
    parts = line.split()
    old_path = normalize_diff_path(parts[2]) if len(parts) > 2 else None
    path = normalize_diff_path(parts[3]) if len(parts) > 3 else old_path
    return {
        "path": path or "unknown",
        "old_path": old_path if old_path != path else None,
        "change_type": "modified",
        "lines_added": 0,
        "lines_deleted": 0,
    }


def build_changed_file(block: dict) -> ParsedChangedFile:
    path = block["path"]
    old_path = block.get("old_path")
    change_type = block["change_type"]
    lines_added = block["lines_added"]
    lines_deleted = block["lines_deleted"]
    file_role = classify_file_role(path, old_path)
    language = detect_language(path)
    risk_level, risk_reasons = classify_risk(file_role, change_type, lines_added, lines_deleted, path)
    return ParsedChangedFile(
        path=path,
        old_path=old_path,
        change_type=change_type,
        language=language,
        file_role=file_role,
        risk_level=risk_level,
        risk_reasons=risk_reasons,
        lines_added=lines_added,
        lines_deleted=lines_deleted,
    )


def normalize_diff_path(path: str) -> str | None:
    if path == "/dev/null":
        return None
    if path.startswith("a/") or path.startswith("b/"):
        return path[2:]
    return path


def classify_file_role(path: str, old_path: str | None = None) -> str:
    pure_path = PurePosixPath(path)
    old_name = PurePosixPath(old_path).name.lower() if old_path else ""
    parts = set(pure_path.parts)
    name = pure_path.name.lower()
    suffix = pure_path.suffix.lower()
    if "tests" in parts or "test" in parts or name.startswith("test_") or name.endswith(".spec.ts"):
        return "test"
    if "docs" in parts or suffix in {".md", ".mdx", ".rst"}:
        return "docs"
    if "migrations" in parts or "migration" in parts:
        return "migration"
    if "fixtures" in parts or "fixture" in parts:
        return "fixture"
    build_names = {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "pyproject.toml", "poetry.lock"}
    if name in build_names or old_name in build_names:
        return "build"
    if suffix in {".yml", ".yaml", ".toml", ".ini", ".cfg", ".json"}:
        return "config"
    if suffix in {".py", ".ts", ".tsx", ".js", ".jsx", ".vue", ".go", ".java"}:
        return "source"
    return "unknown"


def detect_language(path: str) -> str | None:
    suffix = PurePosixPath(path).suffix.lower()
    return {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".vue": "vue",
        ".go": "go",
        ".java": "java",
        ".md": "markdown",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
    }.get(suffix)


def classify_risk(
    file_role: str,
    change_type: str,
    lines_added: int,
    lines_deleted: int,
    path: str,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    total_changed = lines_added + lines_deleted
    if file_role == "source":
        reasons.append("source file changed")
    elif file_role == "test":
        reasons.append("test file changed")
    elif file_role == "docs":
        reasons.append("documentation changed")
    elif file_role in {"config", "build", "migration"}:
        reasons.append(f"{file_role} file changed")
    else:
        reasons.append("unknown file role")

    if change_type == "deleted":
        reasons.append("file deleted")
    if change_type == "renamed":
        reasons.append("file renamed")
    if total_changed >= 80:
        reasons.append("large change")

    if file_role in {"migration", "config"} or total_changed >= 80:
        return "high", reasons
    if file_role in {"source", "build"} or (change_type in {"deleted", "renamed"} and file_role not in {"docs", "test"}):
        return "medium", reasons
    return "low", reasons
