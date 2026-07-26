# WhisperFlow User Guide & Feature Manual

Welcome to WhisperFlow — the ultra-fast, 100% local, privacy-first Wispr Flow alternative for Windows.

---

## 🚀 Quick Start

1. **Launch WhisperFlow**: Double-click `start.bat`.
   - Automatically initializes the voice dictation daemon and opens the **Control Center Dashboard GUI**.
2. **Push-to-Talk Dictation (`Ctrl + Shift + Space`)**:
   - Hold `Ctrl + Shift + Space` and speak naturally into your microphone.
   - Release the keys to instantly format and insert cleaned text directly into your active application cursor (VS Code, Browser, Slack, Notion, Word).
3. **Command Mode / Text Transformation (`Ctrl + Shift + T`)**:
   - Highlight any existing text in your document.
   - Hold `Ctrl + Shift + T` and speak an instruction (e.g. *"Rewrite this professionally"*, *"Summarize into 3 bullet points"*).
   - Release to replace the selection.

---

## 🎛️ Control Center Dashboard GUI

When you launch `start.bat`, the Control Center Dashboard window appears automatically.

### Key Settings:
- **LLM Temperature**: Adjust between `0.0` (100% deterministic / greedy) and `1.0`. Default is `0.0`.
- **Mode Selection**: `auto` (smart intent detection), `medium`, `correct`, `polish`, `summarize`, `smart_list`, `email`, `coding`, `meeting_notes`.
- **Custom Vocabulary Bias**: Add technical terms, AI models, proper nouns, or founder names separated by commas (*Claude 3.5 Opus, Gemini Flash, Zorin OS, Sam Altman, Dario Amodei*). These terms are passed directly to `whisper.cpp --prompt` for 100% accurate acoustic decoding.
- **Phase 1 Smart Formatting**: Toggle rule-based filler removal (`um`, `uh`) and punctuation normalization.

---

## 🎙️ Spoken Voice Commands & Formatting

| Spoken Voice Phrase | Action Executed | Example Output |
|---|---|---|
| *"bold [word]"* / *"make [word] bold"* | Wraps word in markdown bold | `**word**` |
| *"in bold [phrase]"* | Wraps phrase in markdown bold | `**phrase**` |
| *"and in the list say item 1, item 2"* | Formats list items as markdown bullets | `* Item 1`<br>`* Item 2` |
| *"new line"* | Inserts line break | `\n` |
| *"new paragraph"* | Inserts double line break | `\n\n` |
| *"scratch that"* / *"delete that"* | Removes last sentence | *(Drops abandoned sentence)* |

---

## ⚙️ System Tray Menu

Right-click the microphone icon in your Windows Taskbar tray:
- **`⚙️ Settings Dashboard`**: Opens the live Control Center Dashboard GUI.
- **`Cleanup Level`**: Switch between `Auto`, `Medium`, `Polish`, `Raw`.
- **`Quit`**: Exit WhisperFlow cleanly.
