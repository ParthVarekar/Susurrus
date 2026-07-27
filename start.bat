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
set "HF_REPO="
set "HF_FILE="
set "LLAMA_ARGS="

if "%MODEL_CHOICE%"=="1" (
    set "TARGET_MODEL_NAME=GRMR-2B-Instruct-Q4_K_M.gguf"
    set "HF_REPO=bartowski/GRMR-2B-Instruct-GGUF"
    set "HF_FILE=GRMR-2B-Instruct-Q4_K_M.gguf"
    set "LLAMA_ARGS=-ngl 99 --ctx-size 2048 -t 4 --temp 0.0 --repeat-penalty 1.0"
)
if "%MODEL_CHOICE%"=="2" (
    set "TARGET_MODEL_NAME=qwen2.5-1.5b-instruct-q4_k_m.gguf"
    set "HF_REPO=Qwen/Qwen2.5-1.5B-Instruct-GGUF"
    set "HF_FILE=qwen2.5-1.5b-instruct-q4_k_m.gguf"
    set "LLAMA_ARGS=-ngl 99 --ctx-size 4096 -t 4 --temp 0.1 --repeat-penalty 1.1"
)
if "%MODEL_CHOICE%"=="3" (
    set "TARGET_MODEL_NAME=gemma-2-2b-it-Q4_K_M.gguf"
    set "HF_REPO=bartowski/gemma-2-2b-it-GGUF"
    set "HF_FILE=gemma-2-2b-it-Q4_K_M.gguf"
    set "LLAMA_ARGS=-ngl 99 --ctx-size 2048 -t 4 --temp 0.1 --repeat-penalty 1.1"
)
if "%MODEL_CHOICE%"=="4" (
    set "TARGET_MODEL_NAME=gemma-4"
    set "LLAMA_ARGS=-hf unsloth/gemma-4-E4B-it-GGUF:UD-Q4_K_XL --ctx-size 32768 --parallel 2 --alias gemma-4-e2b-it --reasoning off"
)

:: Auto-download GGUF model if missing
if not "%MODEL_CHOICE%"=="5" if not "%MODEL_CHOICE%"=="4" (
    set "LOCAL_MODEL_PATH=%~dp0models\%TARGET_MODEL_NAME%"
    if not exist "%LOCAL_MODEL_PATH%" (
        echo [DOWNLOAD] Auto-downloading %TARGET_MODEL_NAME% from HuggingFace...
        python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='%HF_REPO%', filename='%HF_FILE%', local_dir='%~dp0models')"
        if %ERRORLEVEL% NEQ 0 (
            echo [ERROR] Model download failed. Please check internet connection.
            pause
            exit /b 1
        )
        echo [OK] Model downloaded successfully to models/%TARGET_MODEL_NAME%!
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
            start "llama-server" /min "%LLAMA_EXE%" -m "%~dp0models\%TARGET_MODEL_NAME%" %LLAMA_ARGS% --host 127.0.0.1 --port 8081
        )
        echo [OK] llama-server started in background. Waiting for model load (10-15s)...
        timeout /t 12 /nobreak >nul
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
