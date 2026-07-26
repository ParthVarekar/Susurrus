"""Unit tests for whisper_flow hyperparameter grid search suite."""

from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from whisper_flow.config import Config
from whisper_flow.grid_search import (
    BENCHMARK_SUITE,
    evaluate_single_config,
    run_hyperparameter_grid_search,
)


class TestHyperparameterGridSearch:
    """Test suite for automated hyperparameter grid search."""

    def test_benchmark_suite_integrity(self):
        assert len(BENCHMARK_SUITE) >= 7
        for item in BENCHMARK_SUITE:
            assert len(item.id) > 0
            assert len(item.raw_transcript) > 0
            assert len(item.target_terms) > 0

    def test_evaluate_single_config(self):
        cfg = Config()
        cfg.llm.temperature = 0.0
        cfg.smart_formatting = True
        cfg.mode = "auto"
        cfg.writing_style = "default"

        score = evaluate_single_config(cfg)
        assert score.overall_score > 0.0
        assert score.proper_noun_score >= 0.0
        assert score.intent_retention_score >= 0.0

    def test_grid_search_runs_and_selects_best(self):
        best_cfg, results = run_hyperparameter_grid_search(
            temperatures=[0.0, 0.2],
            smart_formattings=[True, False],
            modes=["auto", "medium"],
            writing_styles=["default"],
            n_ctx_list=[2048],
        )

        assert len(results) == 8  # 2 * 2 * 2 * 1 * 1 = 8 combinations
        assert best_cfg.overall_score >= results[-1].overall_score
        assert best_cfg.proper_noun_score >= 75.0
