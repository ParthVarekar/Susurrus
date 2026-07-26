"""Automated Hyperparameter Grid Search & Evaluation Benchmark for WhisperFlow.

Evaluates configurations across LLM temperature, smart formatting toggles,
modes, writing styles, and context windows to discover the optimal
configuration matrix.
"""

from __future__ import annotations

import itertools
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from typing import Any

from .config import Config, load_config, save_config
from .formatting import apply_smart_formatting
from .prompts import build_prompt, resolve_mode


@dataclass
class BenchmarkItem:
    id: str
    category: str
    raw_transcript: str
    target_terms: list[str]       # Proper nouns / key terms that MUST be preserved
    disfluencies: list[str]        # Filler words that MUST be removed
    forbidden_terms: list[str]    # Abandoned phrases that MUST be removed


BENCHMARK_SUITE: list[BenchmarkItem] = [
    BenchmarkItem(
        id="tech_proper_nouns",
        category="technical",
        raw_transcript="I am running Zorin OS inside WSL on Linux and testing internal pointers, multivariable pointers, and Gemma 4 E2B IT GGUF.",
        target_terms=["Zorin OS", "WSL", "Linux", "internal pointers", "multivariable pointers", "Gemma 4 E2B"],
        disfluencies=[],
        forbidden_terms=[],
    ),
    BenchmarkItem(
        id="self_correction_backtrack",
        category="editing",
        raw_transcript="We should deploy the daemon.py service to AWS... scratch that, we should deploy to Vercel instead.",
        target_terms=["daemon.py", "Vercel"],
        disfluencies=[],
        forbidden_terms=["AWS"],
    ),
    BenchmarkItem(
        id="rambling_filler_cleanup",
        category="dictation",
        raw_transcript="um so yeah like I was thinking maybe we should update the README to look like an AI SaaS product with modern dark mode styling",
        target_terms=["README", "SaaS", "dark mode"],
        disfluencies=["um", "uh", "like"],
        forbidden_terms=[],
    ),
    BenchmarkItem(
        id="spoken_formatting_bold",
        category="formatting",
        raw_transcript="Make the word WhisperFlow bold and write Gemma in bold as well.",
        target_terms=["WhisperFlow", "Gemma"],
        disfluencies=[],
        forbidden_terms=["make the word", "in bold as well"],
    ),
    BenchmarkItem(
        id="inline_list_dictation",
        category="lists",
        raw_transcript="if I am going to write a list of items: tomatoes, cucumbers, strawberries, and zucchini",
        target_terms=["tomatoes", "cucumbers", "strawberries", "zucchini"],
        disfluencies=[],
        forbidden_terms=[],
    ),
    BenchmarkItem(
        id="code_file_extensions",
        category="code",
        raw_transcript="Check daemon.py and prompts.py to fix the exception in load_config.",
        target_terms=["daemon.py", "prompts.py", "load_config"],
        disfluencies=[],
        forbidden_terms=["daemon. py", "prompts. py"],
    ),
    BenchmarkItem(
        id="long_ui_feedback",
        category="feedback",
        raw_transcript="I saw that the UI is not where I wanted to be. The stripe UI is very nice, but the graphs and icons pose a problem as I cannot change them itself, but rather I can change the UI around them.",
        target_terms=["UI", "stripe UI", "graphs and icons", "change the UI around them"],
        disfluencies=[],
        forbidden_terms=[],
    ),
]


@dataclass
class ConfigurationScore:
    temperature: float
    smart_formatting: bool
    mode: str
    writing_style: str
    n_ctx: int
    proper_noun_score: float      # 0 - 100%
    intent_retention_score: float # 0 - 100%
    filler_cleanup_score: float  # 0 - 100%
    overall_score: float         # Weighted overall score (0 - 100)
    failed_items: list[str]


def evaluate_single_config(
    cfg: Config,
    items: list[BenchmarkItem] = BENCHMARK_SUITE,
    llm_runner: Any | None = None,
) -> ConfigurationScore:
    """Evaluate a single configuration against the benchmark suite."""
    proper_noun_hits = 0
    proper_noun_total = 0

    intent_retention_hits = 0
    intent_retention_total = len(items)

    filler_cleanup_hits = 0
    filler_cleanup_total = 0

    failed_items = []

    for item in items:
        # Phase 1: Smart Formatting
        processed = item.raw_transcript
        if cfg.smart_formatting:
            processed = apply_smart_formatting(processed, writing_style=cfg.writing_style)

        # Phase 2: Optional LLM execution (if llm_runner provided)
        if llm_runner is not None and cfg.mode != "raw":
            sys_p, usr_p = build_prompt(cfg.mode, processed, context_words=cfg.dictionary)
            try:
                processed = llm_runner.process(
                    usr_p,
                    system=sys_p,
                    max_tokens=cfg.llm.max_tokens,
                    temperature=cfg.llm.temperature,
                )
            except Exception:  # noqa: BLE001
                pass

        # Metric 1: Proper Noun Fidelity
        for term in item.target_terms:
            proper_noun_total += 1
            if term.lower() in processed.lower():
                proper_noun_hits += 1

        # Metric 2: Forbidden Terms (Backtracks / Abandoned Wording Removal)
        item_failed = False
        for forbidden in item.forbidden_terms:
            if forbidden.lower() in processed.lower():
                item_failed = True

        if not item_failed:
            intent_retention_hits += 1
        else:
            failed_items.append(f"{item.id} (found forbidden '{forbidden}')")

        # Metric 3: Filler Word Removal
        for filler in item.disfluencies:
            filler_cleanup_total += 1
            words_in_out = processed.lower().split()
            if filler.lower() not in words_in_out:
                filler_cleanup_hits += 1

    pn_score = (proper_noun_hits / proper_noun_total * 100.0) if proper_noun_total > 0 else 100.0
    intent_score = (intent_retention_hits / intent_retention_total * 100.0) if intent_retention_total > 0 else 100.0
    filler_score = (filler_cleanup_hits / filler_cleanup_total * 100.0) if filler_cleanup_total > 0 else 100.0

    # Weighted Overall Score: 40% Proper Nouns, 40% Intent/Backtracks, 20% Filler Cleanup
    overall = (pn_score * 0.40) + (intent_score * 0.40) + (filler_score * 0.20)

    return ConfigurationScore(
        temperature=cfg.llm.temperature,
        smart_formatting=cfg.smart_formatting,
        mode=cfg.mode,
        writing_style=cfg.writing_style,
        n_ctx=cfg.llm.n_ctx,
        proper_noun_score=round(pn_score, 2),
        intent_retention_score=round(intent_score, 2),
        filler_cleanup_score=round(filler_score, 2),
        overall_score=round(overall, 2),
        failed_items=failed_items,
    )


def run_hyperparameter_grid_search(
    temperatures: list[float] = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7],
    smart_formattings: list[bool] = [True, False],
    modes: list[str] = ["auto", "medium", "correct", "polish", "raw"],
    writing_styles: list[str] = ["default", "formal", "concise"],
    n_ctx_list: list[int] = [1024, 2048, 4096],
    llm_runner: Any | None = None,
) -> tuple[ConfigurationScore, list[ConfigurationScore]]:
    """Systematically sweep all hyperparameter combinations and return the top-performing configuration."""
    results: list[ConfigurationScore] = []
    base_cfg = Config()

    grid = list(itertools.product(temperatures, smart_formattings, modes, writing_styles, n_ctx_list))
    sys.stderr.write(f"[grid_search] Sweeping {len(grid)} total hyperparameter configurations...\n")

    for temp, smart_fmt, mode, style, n_ctx in grid:
        cfg = Config()
        cfg.llm.temperature = temp
        cfg.smart_formatting = smart_fmt
        cfg.mode = mode
        cfg.writing_style = style
        cfg.llm.n_ctx = n_ctx
        cfg.dictionary = ["Zorin", "Zorin OS", "WSL", "Linux", "internal pointers", "multivariable pointers", "Gemma 4 E2B", "daemon.py", "WhisperFlow"]

        score = evaluate_single_config(cfg, llm_runner=llm_runner)
        results.append(score)

    # Sort descending by overall score, then proper noun score, then intent retention score
    results.sort(key=lambda s: (s.overall_score, s.proper_noun_score, s.intent_retention_score), reverse=True)
    best_config = results[0]

    sys.stderr.write(
        f"[grid_search] Winning Configuration Found!\n"
        f"  Overall Score: {best_config.overall_score}%\n"
        f"  Temperature: {best_config.temperature}\n"
        f"  Smart Formatting: {best_config.smart_formatting}\n"
        f"  Mode: {best_config.mode}\n"
        f"  Writing Style: {best_config.writing_style}\n"
        f"  Context Window (n_ctx): {best_config.n_ctx}\n"
        f"  Proper Noun Score: {best_config.proper_noun_score}%\n"
        f"  Intent Retention: {best_config.intent_retention_score}%\n"
        f"  Filler Cleanup: {best_config.filler_cleanup_score}%\n"
    )

    return best_config, results
