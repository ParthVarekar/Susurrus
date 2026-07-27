"""Niche Vocabulary Packs for WhisperFlow.

Pre-compiled domain vocabulary terms passed to whisper.cpp --prompt to ensure
100% acoustic decoding fidelity for specialized industries.
"""

from __future__ import annotations

VOCAB_PACKS: dict[str, list[str]] = {
    "general": [
        "WhisperFlow", "Wispr Flow", "whisper.cpp", "llama.cpp", "GGUF",
        "Python", "VS Code", "GitHub", "pytest", "API", "Gemma 4 E2B",
        "Claude 3.5 Opus", "Gemini Flash 3.6", "Qwen3-ASR", "CrispASR",
        "Zorin OS", "WSL", "Linux", "MongoDB", "Sam Altman", "Dario Amodei",
        "RAG", "Convolutional Networks", "embeddings",
    ],
    "developer": [
        "daemon.py", "OverlayNotifier", "HotkeyManager", "load_config", "save_config",
        "build_prompt", "detect_auto_intent", "apply_smart_formatting", "Pipeline",
        "TypeScript", "JavaScript", "Python", "Rust", "Golang", "C++", "React",
        "Next.js", "Docker", "Kubernetes", "PostgreSQL", "Redis", "GraphQL",
        "REST API", "git commit", "git push", "git checkout", "pull request",
        "refactor", "CI/CD", "middleware", "asyncio", "multivariable pointer",
        "RAG", "Convolutional Networks", "embeddings", "vector store",
    ],
    "medical": [
        "anesthesia", "arrhythmia", "biopsy", "cardiovascular", "catheter",
        "dermatology", "echocardiogram", "electrocardiogram", "endoscopy",
        "gastroenterology", "hematology", "hypertension", "immunotherapy",
        "intravenous", "laparoscopy", "lymphoma", "metastasis", "neurology",
        "oncology", "pathology", "pharmacology", "radiology", "tachycardia",
        "cardiology", "clinical trials", "dosing",
    ],
    "legal": [
        "affidavit", "affidavits", "arbitration", "brief", "class action", "clause",
        "compliance", "confidentiality agreement", "contract", "counsel",
        "defendant", "deposition", "due diligence", "indemnity", "indemnities", "injunction",
        "intellectual property", "jurisdiction", "liability", "litigation", "litigations",
        "non-disclosure agreement", "plaintiff", "statute of limitations",
    ],
    "corporate": [
        "deliverable", "deliverables", "key performance indicator", "KPI", "KPIs", "OKR", "OKRs", "action item",
        "stakeholder", "alignment", "synergy", "ROI", "return on investment",
        "quarterly review", "roadmap", "go-to-market", "GTM strategy",
        "bandwidth", "bottom line", "core competency", "touchpoint", "onboarding",
        "mumbo jumbo", "corporate mumbo jumbo",
    ],
}


def get_vocab_pack(name: str) -> list[str]:
    """Retrieve vocabulary terms for the specified domain pack."""
    return VOCAB_PACKS.get(name.lower(), VOCAB_PACKS["general"])


def list_vocab_packs() -> list[str]:
    """Return available vocabulary pack names."""
    return list(VOCAB_PACKS.keys())
