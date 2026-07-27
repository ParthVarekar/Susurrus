"""WhisperFlow Live Control Center & Hyperparameter Settings Dashboard.

Modern Dark-Mode Tkinter GUI for live tweaking and persistent configuration
of ASR engines, LLM sampling temperature, vocabulary prompt biasing,
and rule-based formatting toggles.
"""

from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable

from .config import Config, config_to_dict, load_config, save_config

# Modern Dark-Mode Color Tokens (matching HUD overlay)
BG_DARK = "#0f172a"        # Deep slate background
BG_PANEL = "#1e293b"       # Card / Tab panel background
FG_TEXT = "#f8fafc"        # Crisp white text
FG_MUTED = "#94a3b8"       # Muted slate label text
ACCENT_BLUE = "#38bdf8"    # Cyan / Sky blue accent
ACCENT_GREEN = "#22c55e"   # Green success badge
ACCENT_RED = "#ef4444"     # Red highlight


class ControlCenterDashboard:
    """Live Hyperparameter Control Center & Settings Dashboard GUI."""

    def __init__(self, config_path: str = "config.llama4.toml", on_apply: Callable[[Config], None] | None = None) -> None:
        self.config_path = config_path
        self.on_apply = on_apply
        self.cfg: Config = load_config(config_path)

        self.root = tk.Tk()
        self.root.title("WhisperFlow — Control Center Dashboard")
        self.root.geometry("640x680")
        self.root.minsize(580, 550)
        self.root.configure(bg=BG_DARK)

        self._init_styles()
        self._build_header()
        self._build_notebook()
        self._build_footer()
        self._populate_fields()

    def _init_styles(self) -> None:
        """Apply custom dark-mode TTK styles."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Notebook tab styling
        self.style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=BG_PANEL, foreground=FG_MUTED, padding=[12, 6], font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", ACCENT_BLUE)], foreground=[("selected", BG_DARK)])

        # Frame and Label styling
        self.style.configure("TFrame", background=BG_PANEL)
        self.style.configure("Dark.TFrame", background=BG_DARK)
        self.style.configure("TLabel", background=BG_PANEL, foreground=FG_TEXT, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=BG_DARK, foreground=ACCENT_BLUE, font=("Segoe UI", 14, "bold"))
        self.style.configure("SubHeader.TLabel", background=BG_DARK, foreground=FG_MUTED, font=("Segoe UI", 9))

        # Buttons
        self.style.configure("Accent.TButton", background=ACCENT_BLUE, foreground=BG_DARK, font=("Segoe UI", 10, "bold"), padding=6)
        self.style.map("Accent.TButton", background=[("active", "#0284c7")])

    def _build_header(self) -> None:
        header_frame = ttk.Frame(self.root, style="Dark.TFrame", padding=(16, 12, 16, 8))
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_lbl = ttk.Label(header_frame, text="⚙️ WhisperFlow Live Control Center", style="Header.TLabel")
        title_lbl.pack(anchor="w")

        sub_lbl = ttk.Label(header_frame, text="Tweak ASR vocabulary, LLM sampling, and formatting in real-time.", style="SubHeader.TLabel")
        sub_lbl.pack(anchor="w", pady=(2, 0))

    def _build_notebook(self) -> None:
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # Tab 1: LLM & Sampling
        self.tab_llm = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(self.tab_llm, text="🤖 LLM & Sampling")
        self._build_llm_tab()

        # Tab 2: ASR & Audio
        self.tab_asr = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(self.tab_asr, text="🎙️ ASR & Audio")
        self._build_asr_tab()

        # Tab 3: Vocabulary & Dictionary
        self.tab_vocab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(self.tab_vocab, text="📚 Vocabulary Bias")
        self._build_vocab_tab()

        # Tab 4: Formatting & Features
        self.tab_formatting = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(self.tab_formatting, text="⚡ Formatting")
        self._build_formatting_tab()

    def _build_llm_tab(self) -> None:
        # LLM Mode
        ttk.Label(self.tab_llm, text="LLM Post-Processing Mode:").grid(row=0, column=0, sticky="w", pady=6)
        self.var_mode = tk.StringVar()
        self.combo_mode = ttk.Combobox(self.tab_llm, textvariable=self.var_mode, values=["auto", "medium", "correct", "polish", "summarize", "smart_list", "email", "coding", "meeting_notes", "raw"], state="readonly", width=24)
        self.combo_mode.grid(row=0, column=1, sticky="w", pady=6, padx=8)

        # Temperature
        ttk.Label(self.tab_llm, text="LLM Temperature (0.0 = Deterministic):").grid(row=1, column=0, sticky="w", pady=6)
        temp_frame = ttk.Frame(self.tab_llm)
        temp_frame.grid(row=1, column=1, sticky="w", pady=6, padx=8)
        self.var_temp = tk.DoubleVar()
        self.scale_temp = ttk.Scale(temp_frame, from_=0.0, to=1.0, variable=self.var_temp, command=self._update_temp_lbl, length=140)
        self.scale_temp.pack(side=tk.LEFT)
        self.lbl_temp_val = ttk.Label(temp_frame, text="0.0")
        self.lbl_temp_val.pack(side=tk.LEFT, padx=6)

        # Writing Style
        ttk.Label(self.tab_llm, text="Writing Style / Tone:").grid(row=2, column=0, sticky="w", pady=6)
        self.var_style = tk.StringVar()
        self.combo_style = ttk.Combobox(self.tab_llm, textvariable=self.var_style, values=["default", "formal", "casual", "very_casual", "enthusiastic"], state="readonly", width=24)
        self.combo_style.grid(row=2, column=1, sticky="w", pady=6, padx=8)

        # LLM Context Window (n_ctx)
        ttk.Label(self.tab_llm, text="Max Context Length (n_ctx):").grid(row=3, column=0, sticky="w", pady=6)
        self.var_nctx = tk.IntVar()
        self.spin_nctx = ttk.Spinbox(self.tab_llm, from_=512, to=8192, increment=512, textvariable=self.var_nctx, width=12)
        self.spin_nctx.grid(row=3, column=1, sticky="w", pady=6, padx=8)

    def _build_asr_tab(self) -> None:
        # ASR Backend
        ttk.Label(self.tab_asr, text="STT ASR Engine Backend:").grid(row=0, column=0, sticky="w", pady=6)
        self.var_backend = tk.StringVar()
        self.combo_backend = ttk.Combobox(self.tab_asr, textvariable=self.var_backend, values=["whisper_cpp", "qwen3_asr", "moonshine"], state="readonly", width=24)
        self.combo_backend.grid(row=0, column=1, sticky="w", pady=6, padx=8)

        # Whisper Threads
        ttk.Label(self.tab_asr, text="CPU Threads Allocation:").grid(row=1, column=0, sticky="w", pady=6)
        self.var_threads = tk.IntVar()
        self.spin_threads = ttk.Spinbox(self.tab_asr, from_=1, to=16, increment=1, textvariable=self.var_threads, width=12)
        self.spin_threads.grid(row=1, column=1, sticky="w", pady=6, padx=8)

        # GPU Mode
        ttk.Label(self.tab_asr, text="GPU Hardware Acceleration:").grid(row=2, column=0, sticky="w", pady=6)
        self.var_gpu = tk.StringVar()
        self.combo_gpu = ttk.Combobox(self.tab_asr, textvariable=self.var_gpu, values=["auto", "cuda", "cpu", "metal", "vulkan"], state="readonly", width=24)
        self.combo_gpu.grid(row=2, column=1, sticky="w", pady=6, padx=8)

        # Flash Attention
        self.var_flash = tk.BooleanVar()
        self.chk_flash = tk.Checkbutton(self.tab_asr, text="Enable Flash Attention (GPU Speedup)", variable=self.var_flash, bg=BG_PANEL, fg=FG_TEXT, selectcolor=BG_DARK, activebackground=BG_PANEL, activeforeground=FG_TEXT)
        self.chk_flash.grid(row=3, column=0, columnspan=2, sticky="w", pady=8)

    def _build_vocab_tab(self) -> None:
        top_bar = ttk.Frame(self.tab_vocab)
        top_bar.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(top_bar, text="Load Industry Preset Pack:").pack(side=tk.LEFT, padx=(0, 6))

        def _append_pack(name: str):
            from .vocab_packs import get_vocab_pack
            terms = get_vocab_pack(name)
            current = self.txt_vocab.get("1.0", tk.END).strip()
            existing = [t.strip() for t in current.replace("\n", ",").split(",") if t.strip()]
            new_list = existing + [t for t in terms if t not in existing]
            self.txt_vocab.delete("1.0", tk.END)
            self.txt_vocab.insert("1.0", ", ".join(new_list))

        def _scan_workspace():
            from .code_scanner import scan_workspace_symbols
            symbols = scan_workspace_symbols(".")
            current = self.txt_vocab.get("1.0", tk.END).strip()
            existing = [t.strip() for t in current.replace("\n", ",").split(",") if t.strip()]
            new_list = existing + [s for s in symbols if s not in existing]
            self.txt_vocab.delete("1.0", tk.END)
            self.txt_vocab.insert("1.0", ", ".join(new_list))
            messagebox.showinfo("Workspace Scanner", f"Extracted {len(symbols)} code symbols from workspace directory!")

        btn_dev = ttk.Button(top_bar, text="💻 Developer", command=lambda: _append_pack("developer"))
        btn_dev.pack(side=tk.LEFT, padx=2)

        btn_med = ttk.Button(top_bar, text="🩺 Medical", command=lambda: _append_pack("medical"))
        btn_med.pack(side=tk.LEFT, padx=2)

        btn_leg = ttk.Button(top_bar, text="⚖️ Legal", command=lambda: _append_pack("legal"))
        btn_leg.pack(side=tk.LEFT, padx=2)

        btn_corp = ttk.Button(top_bar, text="🏢 Corporate", command=lambda: _append_pack("corporate"))
        btn_corp.pack(side=tk.LEFT, padx=2)

        btn_scan = ttk.Button(top_bar, text="🔍 Auto-Scan Workspace", command=_scan_workspace)
        btn_scan.pack(side=tk.RIGHT, padx=2)

        def _reindex_rag():
            from .rag_engine import RAGEngine
            raw_vocab = self.txt_vocab.get("1.0", tk.END).strip()
            terms = [t.strip() for t in raw_vocab.replace("\n", ",").split(",") if t.strip()]
            rag = RAGEngine()
            count = rag.add_terms(terms)
            messagebox.showinfo("RAG Vector Index", f"⚡ Reindexed {count} vocabulary terms into sub-5ms local RAG vector store!")

        btn_rag = ttk.Button(top_bar, text="⚡ Reindex RAG Store", command=_reindex_rag)
        btn_rag.pack(side=tk.RIGHT, padx=2)

        ttk.Label(self.tab_vocab, text="Custom Vocabulary & Proper Noun Bias List (Comma or newline separated):").pack(anchor="w", pady=(4, 4))

        self.txt_vocab = tk.Text(self.tab_vocab, bg=BG_DARK, fg=FG_TEXT, insertbackground=FG_TEXT, font=("Consolas", 10), height=12, wrap=tk.WORD, relief=tk.FLAT)
        self.txt_vocab.pack(fill=tk.BOTH, expand=True, pady=4)

        hint_lbl = ttk.Label(self.tab_vocab, text="💡 Terms are indexed into the sub-5ms local RAG vector store and passed directly to whisper.cpp & Gemma 4 E2B.", style="SubHeader.TLabel")
        hint_lbl.pack(anchor="w", pady=(4, 0))

    def _build_formatting_tab(self) -> None:
        self.var_smart = tk.BooleanVar()
        self.chk_smart = tk.Checkbutton(self.tab_formatting, text="Enable Phase 1 Smart Rule-Based Formatting", variable=self.var_smart, bg=BG_PANEL, fg=FG_TEXT, selectcolor=BG_DARK, font=("Segoe UI", 10, "bold"), activebackground=BG_PANEL, activeforeground=FG_TEXT)
        self.chk_smart.pack(anchor="w", pady=8)

        info_lbl = ttk.Label(self.tab_formatting, text="Phase 1 handles deterministic punctuation, spacing normalization, and vocal filler removal (um, uh) at zero network latency cost.", style="SubHeader.TLabel", wraplength=480)
        info_lbl.pack(anchor="w", pady=(0, 12))

    def _build_footer(self) -> None:
        footer_frame = ttk.Frame(self.root, style="Dark.TFrame", padding=(16, 8, 16, 12))
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        btn_save = ttk.Button(footer_frame, text="💾 Apply & Save Settings", style="Accent.TButton", command=self._on_save)
        btn_save.pack(side=tk.RIGHT, padx=(8, 0))

        btn_reload = ttk.Button(footer_frame, text="↺ Reload", command=self._populate_fields)
        btn_reload.pack(side=tk.RIGHT)

        self.lbl_status = ttk.Label(footer_frame, text="Ready.", style="SubHeader.TLabel")
        self.lbl_status.pack(side=tk.LEFT)

    def _update_temp_lbl(self, val: str) -> None:
        self.lbl_temp_val.config(text=f"{float(val):.2f}")

    def _populate_fields(self) -> None:
        """Load current config values into GUI widgets."""
        self.cfg = load_config(self.config_path)

        # LLM Tab
        self.var_mode.set(self.cfg.mode)
        self.var_temp.set(float(self.cfg.llm.temperature))
        self.lbl_temp_val.config(text=f"{self.cfg.llm.temperature:.2f}")
        self.var_style.set(self.cfg.writing_style)
        self.var_nctx.set(int(self.cfg.llm.n_ctx))

        # ASR Tab
        self.var_backend.set(self.cfg.transcription.backend)
        self.var_threads.set(int(self.cfg.transcription.threads))
        self.var_gpu.set(self.cfg.transcription.gpu)
        self.var_flash.set(bool(self.cfg.transcription.flash_attention))

        # Vocab Tab
        vocab_text = ", ".join(self.cfg.dictionary) if isinstance(self.cfg.dictionary, list) else ""
        self.txt_vocab.delete("1.0", tk.END)
        self.txt_vocab.insert("1.0", vocab_text)

        # Formatting Tab
        self.var_smart.set(bool(self.cfg.smart_formatting))
        self.lbl_status.config(text="Config loaded from disk.")

    def _on_save(self) -> None:
        """Apply GUI values to config, save to TOML, and update active daemon."""
        try:
            # Read values from GUI
            self.cfg.mode = self.var_mode.get()
            self.cfg.llm.temperature = round(float(self.var_temp.get()), 2)
            self.cfg.writing_style = self.var_style.get()
            self.cfg.llm.n_ctx = int(self.var_nctx.get())

            self.cfg.transcription.backend = self.var_backend.get()
            self.cfg.transcription.threads = int(self.var_threads.get())
            self.cfg.transcription.gpu = self.var_gpu.get()
            self.cfg.transcription.flash_attention = bool(self.var_flash.get())

            raw_vocab = self.txt_vocab.get("1.0", tk.END).strip()
            terms = [t.strip() for t in raw_vocab.replace("\n", ",").split(",") if t.strip()]
            self.cfg.dictionary = terms

            self.cfg.smart_formatting = bool(self.var_smart.get())

            # Save persistent config TOML
            save_config(self.cfg, self.config_path)

            # Trigger live in-memory update callback if daemon is running
            if self.on_apply:
                self.on_apply(self.cfg)

            self.lbl_status.config(text="✅ Settings saved & applied live!")
            messagebox.showinfo("WhisperFlow Settings", "Settings applied live and saved to config!")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Error Saving Settings", str(e))

    def run(self) -> None:
        self.root.mainloop()


def launch_dashboard(config_path: str = "config.llama4.toml", on_apply: Callable[[Config], None] | None = None) -> None:
    """Launch the Control Center Dashboard GUI window."""
    app = ControlCenterDashboard(config_path=config_path, on_apply=on_apply)
    app.run()


if __name__ == "__main__":
    launch_dashboard()
