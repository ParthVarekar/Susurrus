"""Fast Local RAG (Retrieval-Augmented Generation) Vocabulary Engine for WhisperFlow.

Provides sub-5ms local vector & term similarity search across thousands of
specialized domain terms, code symbols, and personal vocabulary items.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from typing import Any, Dict, List, Set, Tuple


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alpha-numeric tokens and 2-grams."""
    raw = re.findall(r"\b[A-Za-z0-9_.]+\b", text.lower())
    tokens = [t for t in raw if len(t) > 1]
    # Add bigrams for phrase matching (e.g., "claude 3.5", "zorin os")
    bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]
    return tokens + bigrams


def _cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """Calculate cosine similarity between two TF-IDF / term frequency vectors."""
    intersection = set(vec1.keys()) & set(vec2.keys())
    if not intersection:
        return 0.0

    dot_product = sum(vec1[k] * vec2[k] for k in intersection)
    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0

    return dot_product / (norm1 * norm2)


class RAGEngine:
    """Local vector & TF-IDF term retrieval index for vocabulary biasing."""

    def __init__(self, index_path: str | None = None) -> None:
        self.index_path = index_path
        self.terms: Dict[str, Dict[str, Any]] = {}  # term -> {domain, tf_vec, text}
        self.idf: Dict[str, float] = {}
        self.doc_count: int = 0

    def add_terms(self, terms: list[str], domain: str = "general") -> int:
        """Add terms to the vector index and compute TF-IDF feature vectors."""
        added_count = 0
        for term in terms:
            clean_term = term.strip()
            if not clean_term or clean_term in self.terms:
                continue

            tokens = _tokenize(clean_term)
            if not tokens:
                continue

            counts = Counter(tokens)
            total = len(tokens)
            tf_vec = {t: c / total for t, c in counts.items()}

            self.terms[clean_term] = {
                "domain": domain,
                "tf_vec": tf_vec,
                "text": clean_term,
            }
            added_count += 1

        if added_count > 0:
            self._recompute_idf()

        return added_count

    def _recompute_idf(self) -> None:
        """Recompute Inverse Document Frequency (IDF) weights across terms."""
        self.doc_count = len(self.terms)
        if self.doc_count == 0:
            self.idf = {}
            return

        doc_freq: Counter[str] = Counter()
        for meta in self.terms.values():
            doc_freq.update(meta["tf_vec"].keys())

        self.idf = {
            token: math.log((self.doc_count + 1) / (freq + 1)) + 1.0
            for token, freq in doc_freq.items()
        }

    def query(self, context_text: str, top_k: int = 30) -> list[str]:
        """Query top_k most relevant terms given query text or window title."""
        if not self.terms or not context_text.strip():
            return list(self.terms.keys())[:top_k]

        q_tokens = _tokenize(context_text)
        if not q_tokens:
            return list(self.terms.keys())[:top_k]

        q_counts = Counter(q_tokens)
        q_total = len(q_tokens)
        q_vec = {
            t: (c / q_total) * self.idf.get(t, 1.0)
            for t, c in q_counts.items()
        }

        scores: list[Tuple[float, str]] = []

        for term, meta in self.terms.items():
            doc_tf = meta["tf_vec"]
            doc_vec = {t: tf * self.idf.get(t, 1.0) for t, tf in doc_tf.items()}
            sim = _cosine_similarity(q_vec, doc_vec)

            # Boost exact substring matches in context_text
            if term.lower() in context_text.lower():
                sim += 1.5

            if sim > 0.0:
                scores.append((sim, term))

        # Sort by similarity score descending
        scores.sort(key=lambda x: x[0], reverse=True)
        
        selected: list[str] = []
        char_count = 0
        max_budget = 4000

        for _, term in scores:
            if len(selected) >= top_k or char_count + len(term) > max_budget:
                break
            selected.append(term)
            char_count += len(term)

        if len(selected) < top_k:
            remaining = [t for t in self.terms.keys() if t not in selected]
            for r in remaining:
                if len(selected) >= top_k or char_count + len(r) > max_budget:
                    break
                selected.append(r)
                char_count += len(r)

        return selected

    def save(self, path: str | None = None) -> None:
        """Persist index to JSON disk storage."""
        save_path = path or self.index_path
        if not save_path:
            return
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        data = {
            "doc_count": self.doc_count,
            "terms": {k: v["text"] for k, v in self.terms.items()},
        }
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: str | None = None) -> None:
        """Load persisted index from JSON disk storage."""
        load_path = path or self.index_path
        if not load_path or not os.path.exists(load_path):
            return
        with open(load_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        terms = list(data.get("terms", {}).values())
        self.add_terms(terms)
