"""Unit tests for whisper_flow Control Center Dashboard."""

from __future__ import annotations

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from whisper_flow.config import Config, load_config, save_config
from whisper_flow.dashboard import ControlCenterDashboard


class TestControlCenterDashboard:
    """Test suite for Control Center Dashboard configuration management."""

    def test_load_and_save_config_roundtrip(self):
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False, mode="w") as tmp:
            tmp_path = tmp.name

        try:
            cfg = Config()
            cfg.mode = "polish"
            cfg.llm.temperature = 0.3
            cfg.dictionary = ["Zorin", "WSL", "Linux", "Gemma"]
            save_config(cfg, tmp_path)

            loaded = load_config(tmp_path)
            assert loaded.mode == "polish"
            assert loaded.llm.temperature == 0.3
            assert "Zorin" in loaded.dictionary
            assert "WSL" in loaded.dictionary
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_dashboard_instantiation(self):
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False, mode="w") as tmp:
            tmp_path = tmp.name

        try:
            cfg = Config()
            save_config(cfg, tmp_path)

            dash = ControlCenterDashboard(config_path=tmp_path)
            assert dash.cfg.mode == cfg.mode
            dash.root.destroy()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
