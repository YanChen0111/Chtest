from __future__ import annotations

import os
import sys
from pathlib import Path


def executable_argv(executable: str, *arguments: str) -> list[str]:
    """Run explicit extensionless Python shims on Windows during local execution."""
    path = Path(executable)
    if os.name == "nt" and path.is_file() and not path.suffix:
        return [sys.executable, executable, *arguments]
    return [executable, *arguments]
