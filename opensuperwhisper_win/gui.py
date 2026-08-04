import os
import sys
import threading
import time
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageDraw

from .audio_recorder import AudioRecorder
from .whisper_engine import WhisperEngine, AVAILABLE_MODELS
from .text_injector import inject_text
from .hotkey_manager import HotkeyManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class OpenSuperWhisperApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OpenSuperWhisper (Windows)")
        self.geometry("700 x 600")
        self.minsize(600, 500)

        # Base path
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Components
        self.recorder = AudioRecorder()
        self.engine = WhisperEngine(model_key="tiny.en", base_dir=self.base_dir)
        self.hotkey_mgr = HotkeyManager(
            on_start_recording=self.trigger_start_recording,
            on_stop_recording=self.trigger_stop_recording
        )

        # Settings state
        self.auto_paste_var = ctk.BooleanVar(value=True)
        self.asian_autocorrect_var = ctk.BooleanVar(value=True)
        self.mode_var = ctk.StringVar(value="hold")
        self.shortcut_var = ctk.StringVar(value="ctrl_shift_space")
        self.selected_device_var = ctk.StringVar(value="Default Microphone")

        # UI Setup
        self._create_widgets()

        # Audio meter timer
        self.update_audio_meter()

        # Start Hotkey Manager
        self.hotkey_mgr.set_config(mode=self.mode_var.get(), shortcut_name=self.shortcut_var.get())
        self.hotkey_mgr.start()

    def _create_widgets(self):
        # Header / Status Bar
        self.header_frame = ctk.CTkFrame(self, fg_color="#181820", corner_radius=12)
        self.header_frame.pack(fill="x", px=15, py=10, padx=15, pady=10)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🎙️ OpenSuperWhisper",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#F3F4F6"
        )
        self.title_label.pack(side="left", padx=15, pady=12)

        self.status_pill = ctk.CTkLabel(
            self.header_frame,
            text=" READY ",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#374151",
            text_color="#E5E7EB",
            corner_radius=8,
            padx=10, pady=4
        )
        self.status_pill.pack(side="right", padx=15, pady=12)

        # Visual Recording Indicator Card
        self.indicator_card = ctk.CTkFrame(self, fg_color="#1F2937", corner_radius=12)
        self.indicator_card.pack(fill="x", padx=15, pady=5)

        self.rec_button = ctk.CTkButton(
            self.indicator_card,
            text="🔴  Press / Hold Hotkey to Record",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=45,
            command=self.toggle_manual_recording
        )
        self.rec_button.pack(fill="x", padx=15, pady=12)

        # Audio Meter Bar
        self.meter_frame = ctk.CTkFrame(self.indicator_card, fg_color="transparent")
        self.meter_frame.pack(fill="x", padx=15, pady=(0, 12))

        self.meter_label = ctk.CTkLabel(self.meter_frame, text="Mic Input Level:", font=ctk.CTkFont(size=11), text_color="#9CA3AF")
        self.meter_label.pack(side="left", padx=5)

        self.audio_progress = ctk.CTkProgressBar(self.meter_frame, height=8, fg_color="#374151", progress_color="#10B981")
        self.audio_progress.pack(side="left", fill="x", expand=True, padx=10)
        self.audio_progress.set(0.0)

        # Tabview for Controls & Transcripts
        self.tabview = ctk.CTkTabview(self, corner_radius=12)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_transcripts = self.tabview.add("📜 Transcripts")
        self.tab_settings = self.tabview.add("⚙️ Settings & Engine")

        # Transcripts Tab Content
        self.transcript_box = ctk.CTkTextbox(self.tab_transcripts, font=ctk.CTkFont(size=14), corner_radius=8)
        self.transcript_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.transcript_box.insert("1.0", "Welcome to OpenSuperWhisper for Windows!\nPress your hotkey (Default: Ctrl+Shift+Space) or click the Record button to begin speaking.\n\n")

        self.trans_btn_frame = ctk.CTkFrame(self.tab_transcripts, fg_color="transparent")
        self.trans_btn_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.clear_btn = ctk.CTkButton(self.trans_btn_frame, text="Clear History", fg_color="#4B5563", hover_color="#374151", width=120, command=self.clear_transcripts)
        self.clear_btn.pack(side="left", padx=5)

        self.copy_btn = ctk.CTkButton(self.trans_btn_frame, text="Copy Last Transcript", fg_color="#2563EB", hover_color="#1D4ED8", width=160, command=self.copy_last_transcript)
        self.copy_btn.pack(side="right", padx=5)

        # Settings Tab Content
        # Model Selection
        self.model_lbl = ctk.CTkLabel(self.tab_settings, text="Whisper Model Engine:", font=ctk.CTkFont(weight="bold"))
        self.model_lbl.pack(anchor="w", padx=15, pady=(15, 2))

        self.model_combo = ctk.CTkOptionMenu(
            self.tab_settings,
            values=list(AVAILABLE_MODELS.keys()),
            command=self.on_model_change
        )
        self.model_combo.pack(fill="x", padx=15, pady=5)
        self.model_combo.set(self.engine.current_model_key)

        # Audio Input Device
        self.mic_lbl = ctk.CTkLabel(self.tab_settings, text="Microphone Input Device:", font=ctk.CTkFont(weight="bold"))
        self.mic_lbl.pack(anchor="w", padx=15, pady=(15, 2))

        devices = AudioRecorder.get_input_devices()
        dev_names = [d["name"] for d in devices] if devices else ["Default Microphone"]
        self.mic_combo = ctk.CTkOptionMenu(
            self.tab_settings,
            values=dev_names,
            command=self.on_mic_change
        )
        self.mic_combo.pack(fill="x", padx=15, pady=5)

        # Trigger Shortcut & Mode
        self.shortcut_lbl = ctk.CTkLabel(self.tab_settings, text="Global Shortcut Trigger:", font=ctk.CTkFont(weight="bold"))
        self.shortcut_lbl.pack(anchor="w", padx=15, pady=(15, 2))

        self.shortcut_combo = ctk.CTkOptionMenu(
            self.tab_settings,
            values=["ctrl_shift_space", "caps_lock", "f9", "f10", "alt_space", "middle_mouse"],
            command=self.on_shortcut_change
        )
        self.shortcut_combo.pack(fill="x", padx=15, pady=5)

        self.mode_chk_frame = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        self.mode_chk_frame.pack(fill="x", padx=15, pady=10)

        self.hold_radio = ctk.CTkRadioButton(
            self.mode_chk_frame, text="Hold-to-Record (Release to Transcribe)",
            variable=self.mode_var, value="hold", command=self.on_mode_change
        )
        self.hold_radio.pack(anchor="w", pady=3)

        self.toggle_radio = ctk.CTkRadioButton(
            self.mode_chk_frame, text="Toggle Mode (Press once to Start, press again to Stop)",
            variable=self.mode_var, value="toggle", command=self.on_mode_change
        )
        self.toggle_radio.pack(anchor="w", pady=3)

        # Toggles
        self.autopaste_chk = ctk.CTkCheckBox(self.tab_settings, text="Auto-paste transcript into active window (Ctrl+V)", variable=self.auto_paste_var)
        self.autopaste_chk.pack(anchor="w", padx=15, pady=8)

        self.last_text = ""

    def update_audio_meter(self):
        if self.recorder.is_recording:
            vol = self.recorder.current_volume
            self.audio_progress.set(vol)
        else:
            self.audio_progress.set(0.0)
        self.after(50, self.update_audio_meter)

    def trigger_start_recording(self):
        self.after(0, self._start_recording_ui)

    def trigger_stop_recording(self):
        self.after(0, self._stop_recording_ui)

    def _start_recording_ui(self):
        try:
            self.recorder.start_recording()
            self.status_pill.configure(text=" 🎙️ RECORDING ", fg_color="#EF4444", text_color="#FFFFFF")
            self.rec_button.configure(text="⏹️ Stop Recording...", fg_color="#DC2626")
        except Exception as e:
            self.status_pill.configure(text=" ERROR ", fg_color="#DC2626")
            print("Start recording error:", e)

    def _stop_recording_ui(self):
        self.status_pill.configure(text=" ⏳ TRANSCRIBING... ", fg_color="#F59E0B", text_color="#FFFFFF")
        self.rec_button.configure(text="⏳ Processing Audio...", fg_color="#D97706")

        threading.Thread(target=self._process_transcription, daemon=True).start()

    def _process_transcription(self):
        wav_file = self.recorder.stop_recording("temp_recording.wav")
        if not wav_file or not os.path.exists(wav_file):
            self.after(0, lambda: self.status_pill.configure(text=" READY ", fg_color="#374151"))
            self.after(0, lambda: self.rec_button.configure(text="🔴  Press / Hold Hotkey to Record", fg_color="#3B82F6"))
            return

        try:
            text = self.engine.transcribe(wav_file, enable_autocorrect=self.asian_autocorrect_var.get())
            if text:
                self.last_text = text
                self.after(0, lambda: self._append_transcript(text))
                if self.auto_paste_var.get():
                    inject_text(text, paste_to_active_window=True)
        except Exception as e:
            print("Transcription Error:", e)
            self.after(0, lambda: self._append_transcript(f"[Error: {e}]"))

        self.after(0, lambda: self.status_pill.configure(text=" READY ", fg_color="#374151"))
        self.after(0, lambda: self.rec_button.configure(text="🔴  Press / Hold Hotkey to Record", fg_color="#3B82F6"))

        if os.path.exists(wav_file):
            try:
                os.remove(wav_file)
            except Exception:
                pass

    def toggle_manual_recording(self):
        if not self.recorder.is_recording:
            self.trigger_start_recording()
        else:
            self.trigger_stop_recording()

    def _append_transcript(self, text):
        timestamp = time.strftime("[%H:%M:%S]")
        self.transcript_box.insert("end", f"{timestamp} {text}\n\n")
        self.transcript_box.see("end")

    def clear_transcripts(self):
        self.transcript_box.delete("1.0", "end")

    def copy_last_transcript(self):
        if self.last_text:
            inject_text(self.last_text, paste_to_active_window=False)

    def on_model_change(self, selected_model):
        def _load():
            self.status_pill.configure(text=" ⏳ LOADING MODEL... ", fg_color="#F59E0B")
            success = self.engine.load_model(selected_model)
            if success:
                self.status_pill.configure(text=" READY ", fg_color="#374151")
            else:
                self.status_pill.configure(text=" MODEL LOAD ERROR ", fg_color="#DC2626")

        threading.Thread(target=_load, daemon=True).start()

    def on_mic_change(self, selected_name):
        devices = AudioRecorder.get_input_devices()
        for d in devices:
            if d["name"] == selected_name:
                self.recorder.set_device(d["id"])
                print(f"Selected audio input device: {d['name']} (ID {d['id']})")
                break

    def on_shortcut_change(self, shortcut_name):
        self.hotkey_mgr.set_config(mode=self.mode_var.get(), shortcut_name=shortcut_name)

    def on_mode_change(self):
        self.hotkey_mgr.set_config(mode=self.mode_var.get(), shortcut_name=self.shortcut_var.get())

    def destroy(self):
        self.hotkey_mgr.stop()
        super().destroy()
