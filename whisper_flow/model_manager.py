"""GGUF Model Manager & Quantization Selector for WhisperFlow.

Provides metadata management, download links, and validation for lightweight,
high-speed GGUF models (Gemma 4 E2B, Gemma 2 2B, Qwen 2.5 1.5B).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ModelSpec:
    name: str
    repo_id: str
    filename: str
    quant_type: str
    size_mb: int
    vram_mb: int
    est_tok_per_sec: int
    description: str


RECOMMENDED_MODELS: Dict[str, ModelSpec] = {
    "grmr-2b-instruct-q4": ModelSpec(
        name="GRMR-2B-Instruct (Q4_K_M)",
        repo_id="bartowski/GRMR-2B-Instruct-GGUF",
        filename="GRMR-2B-Instruct-Q4_K_M.gguf",
        quant_type="Q4_K_M",
        size_mb=1710,
        vram_mb=1400,
        est_tok_per_sec=85,
        description="Top-ranked purpose-built model fine-tuned specifically for voice dictation & grammar cleanup.",
    ),
    "qwen2.5-1.5b-q4": ModelSpec(
        name="Qwen 2.5 1.5B Instruct (Q4_K_M)",
        repo_id="Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        filename="qwen2.5-1.5b-instruct-q4_k_m.gguf",
        quant_type="Q4_K_M",
        size_mb=1120,
        vram_mb=850,
        est_tok_per_sec=95,
        description="Lightweight 1.5B model with 32K context window and sub-1GB VRAM footprint.",
    ),
    "gemma-2-2b-it-q4": ModelSpec(
        name="Gemma 2 2B Instruct (Q4_K_M)",
        repo_id="bartowski/gemma-2-2b-it-GGUF",
        filename="gemma-2-2b-it-Q4_K_M.gguf",
        quant_type="Q4_K_M",
        size_mb=1710,
        vram_mb=1450,
        est_tok_per_sec=80,
        description="Google's knowledge-distilled 2.5B parameter general-purpose instruction model.",
    ),
    "gemma-4-e2b-q3": ModelSpec(
        name="Gemma 4 E2B (Ultra-Fast Q3_K_M)",
        repo_id="unsloth/gemma-4-E4B-it-GGUF",
        filename="gemma-4-E4B-it-Q3_K_M.gguf",
        quant_type="Q3_K_M",
        size_mb=1420,
        vram_mb=1150,
        est_tok_per_sec=75,
        description="Hybrid local-global attention model for long-range dictation context.",
    ),
}


def list_quant_models() -> List[ModelSpec]:
    """Return available model specifications."""
    return list(RECOMMENDED_MODELS.values())


def validate_model_path(path: str) -> bool:
    """Validate that a model file exists and is a valid non-empty GGUF file."""
    if not path or not os.path.exists(path):
        return False
    try:
        size = os.path.getsize(path)
        if size < 100 * 1024 * 1024:  # Must be > 100 MB
            return False
        with open(path, "rb") as f:
            header = f.read(4)
            return header == b"GGUF"
    except Exception:  # noqa: BLE001
        return False
