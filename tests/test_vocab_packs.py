"""Unit tests for Niche Vocabulary Packs and Developer Workspace Code Scanner."""

import os
import tempfile
from whisper_flow.vocab_packs import get_vocab_pack, list_vocab_packs
from whisper_flow.code_scanner import scan_workspace_symbols


def test_vocab_packs_retrieval():
    packs = list_vocab_packs()
    assert "developer" in packs
    assert "medical" in packs
    assert "legal" in packs
    assert "corporate" in packs

    dev_pack = get_vocab_pack("developer")
    assert "TypeScript" in dev_pack
    assert "load_config" in dev_pack

    med_pack = get_vocab_pack("medical")
    assert "biopsy" in med_pack

    fallback = get_vocab_pack("non_existent_pack")
    assert len(fallback) > 0


def test_code_workspace_scanner():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy python file
        py_file = os.path.join(tmpdir, "sample.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("class CustomModelManager:\n    def execute_inference_pipeline():\n        pass\n")

        symbols = scan_workspace_symbols(tmpdir)
        assert "CustomModelManager" in symbols
        assert "execute_inference_pipeline" in symbols
        assert "sample.py" in symbols
