"""Automated Repository Crawler & Vocabulary Synthesizer for WhisperFlow.

Crawls open-source GitHub repositories, fetching source code, READMEs,
and documentation, extracting terms, prompt tricks, and symbols into
reusable domain vocabulary packs.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from typing import Set


class RepoCrawler:
    """GitHub repository crawler & vocabulary term extractor."""

    def __init__(self, repo_slug: str = "zachlatta/freeflow") -> None:
        self.repo_slug = repo_slug.strip().strip("/")

    def fetch_raw_file(self, relative_path: str = "README.md") -> str:
        """Fetch raw content of a file from GitHub default branch."""
        url = f"https://raw.githubusercontent.com/{self.repo_slug}/main/{relative_path.lstrip('/')}"
        req = urllib.request.Request(url, headers={"User-Agent": "WhisperFlow-Crawler/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return f"# Error fetching {relative_path}: {e}"

    def extract_symbols_and_terms(self, raw_content: str) -> list[str]:
        """Extract code symbols, technical terms, and proper nouns from raw text."""
        terms: Set[str] = set()

        # Extract code identifiers (e.g., camelCase, PascalCase, snake_case)
        pascal_camel = re.findall(r"\b[A-Z][a-zA-Z0-9_]{2,}\b", raw_content)
        snake_case = re.findall(r"\b[a-z0-9]+_[a-z0-9_]{2,}\b", raw_content)
        terms.update(pascal_camel)
        terms.update(snake_case)

        # Extract backticked terms `term`
        backticked = re.findall(r"`([A-Za-z0-9_.-]+)`", raw_content)
        terms.update([b for b in backticked if len(b) >= 3])

        # Filter out common markdown/code noise
        ignore_set = {"https", "http", "github", "com", "main", "master", "README", "LICENCE", "LICENSE"}
        cleaned = [t for t in sorted(terms) if t not in ignore_set and len(t) >= 3]

        return cleaned[:80]

    def crawl_repo_summary(self, paths: list[str] | None = None) -> dict[str, Any]:
        """Crawl multiple files from a repository and compile a vocabulary summary."""
        target_paths = paths or ["README.md", "Sources/AppState.swift", "pyproject.toml", "Cargo.toml"]
        all_terms: Set[str] = set()
        crawled_files: dict[str, int] = {}

        for p in target_paths:
            content = self.fetch_raw_file(p)
            if not content.startswith("# Error"):
                extracted = self.extract_symbols_and_terms(content)
                all_terms.update(extracted)
                crawled_files[p] = len(extracted)

        return {
            "repo": self.repo_slug,
            "files_crawled": list(crawled_files.keys()),
            "total_vocabulary_terms": len(all_terms),
            "terms": sorted(all_terms),
        }
