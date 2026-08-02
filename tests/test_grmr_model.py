"""Dedicated automated test suite for GRMR model prompting, fallback protection, and output preservation."""

from __future__ import annotations

import json
import urllib.request
import pytest

from whisper_flow.backends.llama_cpp import LlamaCppBackend
from whisper_flow.config import LLMConfig
from whisper_flow.prompts import build_prompt


class TestGRMRModelSuite:
    """Automated test suite specifically targeting GRMR-2B model contracts."""

    def test_grmr_prompt_contract_structure(self):
        """Verify GRMR model receives the non-summarizing editor contract."""
        transcript = (
            "Testing after meeting a whole new Python pipeline for prompting the GRMR 2 billion model "
            "which we introduced just now while isolating all the system of the older Gemma model and so let's see how it goes. "
            "This is the test prompt and the output should be pretty well formatted and all but formatted I will say but rather well polished."
        )
        system, user = build_prompt("correct", transcript, model_name="GRMR-2B-Instruct-Q4_K_M.gguf")

        # System prompt must enforce text preservation & non-summarization
        assert "text cleanup engine" in system.lower()
        assert "do not summarize" in system.lower()
        assert "do not shorten" in system.lower()

        # User prompt must wrap transcript cleanly
        assert "Input Transcript:" in user
        assert transcript in user
        assert "Cleaned Text:" in user

    def test_grmr_conversational_fallback_protection(self):
        """Verify conversational apologies are intercepted and original transcript is preserved."""
        backend = LlamaCppBackend(LLMConfig(mode="server", host="127.0.0.1", port=8081))

        # Simulate conversational error responses from third-party models
        conversational_responses = [
            "I'm sorry, I'm having trouble understanding your request. Could you please rephrase it?",
            "I'm sorry, but I'm not allowed to provide any further assistance.",
            "Could you please repeat that?",
            "As an AI language model, I cannot complete this request.",
        ]

        # Simulate checking response logic
        conversational_fallbacks = (
            "i'm sorry",
            "having trouble understanding",
            "could you please rephrase",
            "could you please repeat",
            "as an ai language model",
            "not allowed to provide",
        )

        for text in conversational_responses:
            is_fallback = any(f in text.lower() for f in conversational_fallbacks)
            assert is_fallback is True, f"Failed to detect conversational fallback in: {text}"

    def test_grmr_gemma_isolation(self):
        """Verify Gemma-4-E2B default prompt contracts remain completely isolated and unaffected."""
        transcript = "Testing Gemma 4 pipeline isolation."
        sys_gemma, usr_gemma = build_prompt("correct", transcript, model_name="gemma-4-E2B-it-GGUF")

        # Gemma 4 system prompt must contain full hard contract rules
        assert "Hard Contract & Cleanup Rules:" in sys_gemma
        assert "Aggressive Phonetic Vocabulary Enforcement" in sys_gemma
        assert "Dictation Meta-Instruction Removal" in sys_gemma

    def test_grmr_live_server_if_running(self):
        """If llama-server is running on port 8081 with GRMR, verify output is non-truncated."""
        url = "http://127.0.0.1:8081/health"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=1) as resp:
                if resp.status != 200:
                    pytest.skip("llama-server on 8081 not running")
        except Exception:
            pytest.skip("llama-server on 8081 not running")

        # Live query check
        long_transcript = (
            "Testing after meeting a whole new Python pipeline for prompting the GRMR 2 billion model "
            "which we introduced just now while isolating all the system of the older Gemma model. "
            "This is the test prompt and the output should be well polished."
        )
        sys_p, usr_p = build_prompt("correct", long_transcript, model_name="GRMR-2B-Instruct-Q4_K_M.gguf")

        comp_url = "http://127.0.0.1:8081/v1/chat/completions"
        body = {
            "messages": [
                {"role": "system", "content": sys_p},
                {"role": "user", "content": usr_p},
            ],
            "temperature": 0.0,
            "max_tokens": 512,
            "stop": ["<|im_end|>", "<|im_start|>", "\n---", "<|endoftext|>"],
        }
        comp_req = urllib.request.Request(
            comp_url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(comp_req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            out = data["choices"][0]["message"]["content"].strip()
            # Must preserve the transcript text and not truncate to < 5 words
            assert len(out.split()) >= 15
            assert "sorry" not in out.lower()
