"""Unit tests for Knowledge Base Vault Watcher, Model Manager, and Repo Crawler."""

import os
import tempfile
from whisper_flow.knowledge_watcher import KnowledgeVaultWatcher
from whisper_flow.model_manager import list_quant_models, validate_model_path
from whisper_flow.crawler import RepoCrawler
from whisper_flow.rag_engine import RAGEngine


def test_knowledge_base_vault_watcher():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy obsidian vault structure
        note1 = os.path.join(tmpdir, "Architecture Notes.md")
        with open(note1, "w", encoding="utf-8") as f:
            f.write("# Architecture Overview\nThis notes references [[VectorIndex]] and #deep_learning.\n")

        watcher = KnowledgeVaultWatcher(tmpdir)
        terms = watcher.scan_vault()

        assert "Architecture Notes" in terms
        assert "VectorIndex" in terms

        rag = RAGEngine()
        count = watcher.sync_to_rag(rag)
        assert count > 0
        assert "VectorIndex" in rag.terms


def test_model_manager_specs():
    models = list_quant_models()
    assert len(models) >= 3

    model_names = [m.name for m in models]
    assert any("Gemma 4 E2B" in n for n in model_names)

    # Validate non-existent path
    assert validate_model_path("C:/invalid_path/model.gguf") is False


def test_repo_crawler_extraction():
    crawler = RepoCrawler("zachlatta/freeflow")
    sample_code = """
    class AppState:
        func startRecording() {
            let config = WhisperConfig()
        }
    """
    terms = crawler.extract_symbols_and_terms(sample_code)
    assert "AppState" in terms
    assert "WhisperConfig" in terms
