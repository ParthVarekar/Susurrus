@echo off
title WhisperFlow - Voice Dictation Launcher
color 0A
cd /d "%~dp0"
cls
echo =======================================================================
echo               WHISPER FLOW - ONE-CLICK LAUNCHER
echo          Qwen3-ASR (1.7B) + Interactive Model Selector
echo =======================================================================
echo.

:: -----------------------------------------------------------------------
:: 1. Check Python is available
:: -----------------------------------------------------------------------
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Python was not found in PATH!
    echo Please install Python 3.10+ and add it to your System PATH.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: -----------------------------------------------------------------------
:: 2. Activate virtual environment if one exists (recommended)
:: -----------------------------------------------------------------------
set "VENV_DIR="
if exist ".qa-venv\Scripts\activate.bat" set "VENV_DIR=.qa-venv"
if exist ".venv\Scripts\activate.bat" set "VENV_DIR=.venv"

if defined VENV_DIR (
    echo [OK] Activating virtual environment: %VENV_DIR%
    call "%VENV_DIR%\Scripts\activate.bat"
) else (
    echo [INFO] No virtual environment found. Using system Python.
)

if /i "%1"=="gui" (
    echo [OK] Launching WhisperFlow Control Center Dashboard GUI...
    python -m whisper_flow gui --config config.llama4.toml
    pause
    exit /b 0
)

:: -----------------------------------------------------------------------
:: 3. Ensure required Python packages are installed
:: -----------------------------------------------------------------------
echo [CHECK] Verifying Python dependencies...

python -c "import sounddevice" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installing sounddevice ^(mic capture^)...
    python -m pip install sounddevice
)

python -c "import pynput" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installing pynput ^(global hotkeys^)...
    python -m pip install pynput
)

python -c "import pystray" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installing pystray + Pillow ^(system tray^)...
    python -m pip install pystray Pillow
)

python -c "import numpy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installing numpy...
    python -m pip install numpy
)

python -c "import pyperclip" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installing pyperclip ^(clipboard fallback^)...
    python -m pip install pyperclip
)

python -c "import huggingface_hub" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installing huggingface_hub ^(model downloader^)...
    python -m pip install huggingface_hub
)

:: -----------------------------------------------------------------------
:: 4. Verify Qwen3-ASR binary and model files exist
:: -----------------------------------------------------------------------
echo [CHECK] Verifying Qwen3-ASR installation...

set "QWEN_BIN=%~dp0third_party\crispasr\crispasr.exe"
set "QWEN_MODEL=%~dp0models\qwen3-asr-1.7b-q4_k.gguf"

if not exist "%~dp0models" mkdir "%~dp0models"

set "ALL_FOUND=1"

if not exist "%QWEN_BIN%" (
    echo [WARNING] crispasr.exe not found at: %QWEN_BIN%
    set "ALL_FOUND=0"
)

if not exist "%QWEN_MODEL%" (
    echo [WARNING] Qwen3-ASR model not found at: %QWEN_MODEL%
    set "ALL_FOUND=0"
)

if "%ALL_FOUND%"=="1" (
    echo [OK] Qwen3-ASR binary and model found.
)

:: -----------------------------------------------------------------------
:: 5. Interactive Model Selection Menu
:: -----------------------------------------------------------------------
echo.
echo =======================================================================
echo   SELECT LLM CLEANUP MODEL FOR VOICE DICTATION
echo =======================================================================
echo   [1] GRMR-2B-Instruct   ^(Recommended: Purpose-built Grammar Cleanup, 1.4GB VRAM^)
echo   [2] Qwen2.5-1.5B       ^(Ultra-Fast, Sub-1GB VRAM, 32K Context Window^)
echo   [3] Gemma-2-2B-it      ^(Google Knowledge-Distilled General Purpose^)
echo   [4] Gemma-4-E2B        ^(High-Precision Hybrid Attention Model^)
echo   [5] Raw STT Only       ^(Skip LLM Post-Processing^)
echo =======================================================================
echo.
set /p MODEL_CHOICE="Select model choice [1-5] (default 1): "
if "%MODEL_CHOICE%"=="" set "MODEL_CHOICE=1"

set "TARGET_MODEL_NAME="
set "LLAMA_ARGS="

if "%MODEL_CHOICE%"=="1" (
    set "TARGET_MODEL_NAME=GRMR-2B-Instruct-Q4_K_M.gguf"
    set "LLAMA_ARGS=-ngl 99 --ctx-size 2048 -t 4 --temp 0.0 --repeat-penalty 1.0"
)
if "%MODEL_CHOICE%"=="2" (
    set "TARGET_MODEL_NAME=qwen2.5-1.5b-instruct-q4_k_m.gguf"
    set "LLAMA_ARGS=-ngl 99 --ctx-size 4096 -t 4 --temp 0.1 --repeat-penalty 1.1"
)
if "%MODEL_CHOICE%"=="3" (
    set "TARGET_MODEL_NAME=gemma-2-2b-it-Q4_K_M.gguf"
    set "LLAMA_ARGS=-ngl 99 --ctx-size 2048 -t 4 --temp 0.1 --repeat-penalty 1.1"
)
if "%MODEL_CHOICE%"=="4" (
    set "TARGET_MODEL_NAME=gemma-4"
    set "LLAMA_ARGS=-hf unsloth/gemma-4-E4B-it-GGUF:UD-Q4_K_XL --ctx-size 32768 --parallel 2 --alias gemma-4-e2b-it --reasoning off"
)

:: Auto-download GGUF model if missing using Python downloader script
if not "%MODEL_CHOICE%"=="5" if not "%MODEL_CHOICE%"=="4" (
    python -m whisper_flow.downloader %MODEL_CHOICE%
    if errorlevel 1 (
        color 0C
        echo [ERROR] Model download failed.
        pause
        exit /b 1
    )
)

:: -----------------------------------------------------------------------
:: 6. Launch llama-server if not running
:: -----------------------------------------------------------------------
if not "%MODEL_CHOICE%"=="5" (
    echo [CHECK] Checking for llama-server on port 8081...
    powershell -Command "$s = New-Object System.Net.Sockets.TcpClient; try { $s.Connect('127.0.0.1', 8081); exit 0 } catch { exit 1 }" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] llama-server is already running on port 8081.
    ) else (
        echo [STARTING] Launching llama-server...
        set "LLAMA_EXE=D:\llama4\llama-server.exe"
        if not exist "%LLAMA_EXE%" set "LLAMA_EXE=llama-server.exe"

        if "%MODEL_CHOICE%"=="4" (
            start "llama-server" /min "%LLAMA_EXE%" %LLAMA_ARGS% --host 127.0.0.1 --port 8081
        ) else (
            start "llama-server" /min "%LLAMA_EXE%" -m "%~dp0models\%TARGET_MODEL_NAME%" %LLAMA_ARGS% --alias gemma-4-e2b-it --host 127.0.0.1 --port 8081
        )
        echo [OK] Waiting for llama-server to load model into VRAM...
        powershell -Command "for ($i=0; $i -lt 30; $i++) { $s = New-Object System.Net.Sockets.TcpClient; try { $s.Connect('127.0.0.1', 8081); $s.Close(); exit 0 } catch { Start-Sleep -Seconds 1 } }; exit 1" >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            color 0C
            echo [ERROR] llama-server failed to start on port 8081 within 30 seconds.
            pause
            exit /b 1
        )
        echo [OK] llama-server is ready on port 8081!
    )
)

:: -----------------------------------------------------------------------
:: 7. Start the WhisperFlow daemon
:: -----------------------------------------------------------------------
echo.
echo =======================================================================
echo   Starting WhisperFlow Daemon...
echo =======================================================================
echo   Dictation hotkey:  Ctrl+Shift+Space  (hold to record)
echo   Command hotkey:    Ctrl+Shift+T      (select text, hold + speak)
echo   Quit:              right-click tray icon -> Quit
echo =======================================================================
echo.

python -m whisper_flow daemon --config config.llama4.toml

echo.
echo =======================================================================
echo   WhisperFlow has stopped.
echo =======================================================================
pause
