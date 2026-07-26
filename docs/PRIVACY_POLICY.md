# WhisperFlow Privacy Policy

**Effective Date:** July 26, 2026  
**Last Updated:** July 26, 2026

At WhisperFlow ("we", "our", or "us"), we believe that your voice, dictation audio, and text output belong exclusively to you. WhisperFlow is engineered from the ground up as a **100% local, on-device AI voice dictation tool**.

---

## 1. Zero Cloud Audio Transmission (100% On-Device Processing)

Unlike conventional cloud-based voice dictation services, WhisperFlow does **NOT** stream, upload, or transmit your audio or dictation text to any remote cloud servers.

- **Speech-to-Text (STT)**: Acoustic decoding is performed locally on your GPU/CPU using embedded `whisper.cpp` / `ggml` models.
- **LLM Cleanup & Formatting**: Text polishing is executed locally on your device via embedded GGUF models (`Gemma 4 E2B`).
- **Network Isolation**: WhisperFlow functions completely offline. No microphone data, system context, active window titles, or text snippets ever leave your computer.

---

## 2. Information We Collect

### 2.1 Analytics & Telemetry
- **Zero Telemetry**: WhisperFlow contains **no analytics tracking, telemetry scripts, or user fingerprinting**.
- **No Account Required**: WhisperFlow does not require registration, email collection, or user account creation.

### 2.2 Local Diagnostic Logs
- Diagnostic logs (`whisper_flow.log`) and local dictation history are saved exclusively on your local storage (`%APPDATA%` or repository directory). You have full control over these local files and may delete them at any time.

---

## 3. Data Security & GDPR / HIPAA Compliance

Because all voice processing occurs locally within your system's hardware environment:
- **HIPAA Compliance**: Suitable for medical, legal, and financial dictation without third-party BAA (Business Associate Agreement) risks, as no PHI (Protected Health Information) is transmitted over a network.
- **GDPR Compliance**: You retain full data ownership. Zero personal data is stored by us or third parties.

---

## 4. Third-Party Services

WhisperFlow integrates no third-party cloud SDKs, ad networks, or cloud AI APIs. All processing models run within your local system architecture.

---

## 5. Contact Us

If you have questions about WhisperFlow's privacy architecture or wish to review our open-source codebase, please visit our official repository or contact the maintainers on GitHub.
