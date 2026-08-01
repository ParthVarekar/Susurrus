"""HuggingFace Model Downloader Helper for WhisperFlow."""

from __future__ import annotations

import os
import sys


def download_model(model_choice: str) -> str:
    models = {
        "1": ("bartowski/GRMR-2B-Instruct-GGUF", "GRMR-2B-Instruct-Q4_K_M.gguf"),
        "2": ("Qwen/Qwen2.5-1.5B-Instruct-GGUF", "qwen2.5-1.5b-instruct-q4_k_m.gguf"),
        "3": ("bartowski/gemma-2-2b-it-GGUF", "gemma-2-2b-it-Q4_K_M.gguf"),
    }

    if model_choice not in models:
        sys.stderr.write(f"[whisper-flow] Unknown model choice: {model_choice}\n")
        return ""

    repo_id, filename = models[model_choice]
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    target_path = os.path.join(models_dir, filename)

    if os.path.exists(target_path):
        print(f"[OK] Model file found: {target_path}")
        return target_path

    print(f"[DOWNLOAD] Auto-downloading {filename} from HuggingFace ({repo_id})...")
    try:
        from huggingface_hub import hf_hub_download
        path = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=models_dir)
        print(f"[OK] Successfully downloaded {filename} to {path}")
        return path
    except Exception as e:
        sys.stderr.write(f"[ERROR] Failed to download model: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    choice = sys.argv[1] if len(sys.argv) > 1 else "1"
    download_model(choice)
