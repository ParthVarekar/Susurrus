"""Unit tests for WhisperFlow RAGEngine local vector retrieval."""

import os
import tempfile
import time
from whisper_flow.rag_engine import RAGEngine


def test_rag_engine_indexing_and_query():
    rag = RAGEngine()

    dev_terms = [
        "Convolutional Networks", "RAG", "embeddings", "TypeScript",
        "Python", "VS Code", "daemon.py", "OverlayNotifier",
    ]
    med_terms = [
        "cardiology", "pathology", "pharmacology", "arrhythmia", "biopsy",
    ]

    rag.add_terms(dev_terms, domain="developer")
    rag.add_terms(med_terms, domain="medical")

    # Query with medical context
    res_med = rag.query("The patient presented with arrhythmia and required cardiology consultation.", top_k=3)
    assert "arrhythmia" in res_med
    assert "cardiology" in res_med

    # Query with developer context
    res_dev = rag.query("Editing overlay notifier in VS Code with TypeScript and daemon.py", top_k=4)
    assert "OverlayNotifier" in res_dev or "daemon.py" in res_dev


def test_rag_engine_speed_benchmark():
    rag = RAGEngine()
    terms = [f"SpecializedTerm_{i}" for i in range(500)]
    rag.add_terms(terms)

    start = time.monotonic()
    results = rag.query("SpecializedTerm_42 and SpecializedTerm_100", top_k=20)
    elapsed_ms = (time.monotonic() - start) * 1000

    assert len(results) == 20
    assert elapsed_ms < 10.0  # Must be sub-10ms


def test_rag_engine_serialization():
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, "rag_index.json")
        rag1 = RAGEngine(save_path)
        rag1.add_terms(["WhisperFlow", "Gemma 4 E2B", "Qwen3-ASR"])
        rag1.save()

        rag2 = RAGEngine(save_path)
        rag2.load()
        assert "WhisperFlow" in rag2.terms
        assert "Gemma 4 E2B" in rag2.terms
