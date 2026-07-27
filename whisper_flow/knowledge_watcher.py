"""Knowledge Base Vault Watcher for WhisperFlow.

Monitors local Obsidian markdown vaults, Notion export folders, and workspace
documents, automatically parsing [[wikilinks]], #tags, and keyphrase headings
to index them into the RAGEngine vector store.
"""

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Set

if TYPE_CHECKING:
    from .rag_engine import RAGEngine


class KnowledgeVaultWatcher:
    """Parser & watcher for local markdown vaults and knowledge bases."""

    def __init__(self, vault_path: str = "") -> None:
        self.vault_path = vault_path
        self.extracted_terms: Set[str] = set()

    def scan_vault(self, vault_path: str | None = None) -> list[str]:
        """Scan markdown files in vault_path and extract wikilinks, tags, and titles."""
        target_dir = vault_path or self.vault_path
        if not target_dir or not os.path.exists(target_dir):
            return []

        terms: Set[str] = set()
        scanned_files = 0
        max_files = 100

        for root, dirs, files in os.walk(target_dir):
            # Skip hidden/build dirs
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"node_modules", ".obsidian", ".git"}]

            for file in files:
                if scanned_files >= max_files:
                    break

                ext = os.path.splitext(file)[1].lower()
                if ext not in {".md", ".txt", ".json", ".org"}:
                    continue

                # Add file title (without extension) as a proper noun
                title = os.path.splitext(file)[0]
                if len(title) > 2 and not title.startswith("Untitled"):
                    terms.add(title)

                filepath = os.path.join(root, file)
                scanned_files += 1

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(20000)

                    # Extract Obsidian [[wikilinks]]
                    wikilinks = re.findall(r"\[\[(.*?)\]\]", content)
                    for wl in wikilinks:
                        clean_link = wl.split("|")[0].split("#")[0].strip()
                        if len(clean_link) > 2:
                            terms.add(clean_link)

                    # Extract #tags
                    tags = re.findall(r"(?<=^|\s)#([A-Za-z0-9_/-]+)", content)
                    for tag in tags:
                        clean_tag = tag.replace("-", " ").replace("_", " ").strip()
                        if len(clean_tag) > 2:
                            terms.add(clean_tag)

                    # Extract Markdown H1/H2 headings
                    headings = re.findall(r"^#{1,2}\s+(.+)$", content, re.MULTILINE)
                    for h in headings:
                        clean_h = h.strip()
                        if 3 <= len(clean_h) <= 40:
                            terms.add(clean_h)

                except Exception:  # noqa: BLE001
                    pass

        self.extracted_terms = terms
        return sorted(terms)

    def sync_to_rag(self, rag_engine: RAGEngine, vault_path: str | None = None) -> int:
        """Scan vault and index extracted terms directly into the RAG vector store."""
        terms = self.scan_vault(vault_path)
        if terms and rag_engine:
            return rag_engine.add_terms(terms, domain="knowledge_base")
        return 0
