"""Automatic Workspace Code Symbol Scanner for WhisperFlow Developer Mode.

Scans the active directory for code files (.py, .ts, .js, .json, .toml),
extracting class names, function names, and file basenames into a dynamic
vocabulary bias list for whisper.cpp.
"""

from __future__ import annotations

import os
import re
from typing import Set


def scan_workspace_symbols(workspace_dir: str = ".", max_files: int = 50) -> list[str]:
    """Scan code files in the directory and extract class, function, and file symbols."""
    symbols: Set[str] = set()
    scanned_count = 0

    if not os.path.exists(workspace_dir):
        return []

    # Target extension patterns
    valid_exts = {".py", ".ts", ".js", ".json", ".toml", ".sh", ".md", ".cpp", ".h"}

    for root, dirs, files in os.walk(workspace_dir):
        # Skip hidden/build dirs
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"node_modules", "dist", "__pycache__", "build", "target"}]

        for file in files:
            if scanned_count >= max_files:
                break

            ext = os.path.splitext(file)[1].lower()
            if ext not in valid_exts:
                continue

            # Add file basename itself
            symbols.add(file)

            filepath = os.path.join(root, file)
            scanned_count += 1

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(15000)  # Read first 15 KB

                # Extract Python/JS/TS class names: class ClassName
                classes = re.findall(r"\bclass\s+([A-Za-z0-9_]+)\b", content)
                symbols.update(classes)

                # Extract Python/JS/TS function names: def func_name or function func_name
                funcs = re.findall(r"\b(?:def|function|const|let|var)\s+([A-Za-z0-9_]+)\b", content)
                for fn in funcs:
                    if len(fn) > 3 and not fn.startswith("_"):
                        symbols.add(fn)

            except Exception:  # noqa: BLE001
                pass

    # Filter out short or standard keywords
    ignore_words = {"class", "function", "const", "return", "import", "export", "default", "index", "main", "test", "self", "true", "false", "none"}
    cleaned_symbols = [s for s in sorted(symbols) if s.lower() not in ignore_words and len(s) >= 3]

    return cleaned_symbols[:100]  # Cap top 100 symbols for STT prompt buffer
