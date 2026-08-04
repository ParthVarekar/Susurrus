import os
import urllib.request
from pywhispercpp.model import Model

AVAILABLE_MODELS = {
    "tiny.en": {
        "local_filename": "ggml-tiny.en.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin"
    },
    "base.en": {
        "local_filename": "ggml-base.en.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin"
    },
    "small.en": {
        "local_filename": "ggml-small.en.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin"
    },
    "large-v3-turbo": {
        "local_filename": "ggml-large-v3-turbo.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin"
    }
}

class WhisperEngine:
    def __init__(self, model_key="tiny.en", base_dir=None):
        self.base_dir = base_dir or os.getcwd()
        self.current_model_key = model_key
        self.model = None
        self.load_model(model_key)

    def get_model_path(self, model_key):
        info = AVAILABLE_MODELS.get(model_key, AVAILABLE_MODELS["tiny.en"])
        filename = info["local_filename"]
        # Check current dir or models dir
        path1 = os.path.join(self.base_dir, filename)
        path2 = os.path.join(self.base_dir, "models", filename)
        if os.path.exists(path1):
            return path1
        if os.path.exists(path2):
            return path2
        return path1

    def download_model_if_needed(self, model_key, progress_callback=None):
        info = AVAILABLE_MODELS.get(model_key)
        if not info:
            raise ValueError(f"Unknown model key: {model_key}")
        target_path = self.get_model_path(model_key)
        if os.path.exists(target_path):
            return target_path

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        url = info["url"]
        print(f"Downloading model {model_key} from {url} to {target_path}...")

        def _reporthook(blocknum, blocksize, totalsize):
            if totalsize > 0 and progress_callback:
                percent = min(100, int(blocknum * blocksize * 100 / totalsize))
                progress_callback(percent)

        urllib.request.urlretrieve(url, target_path, reporthook=_reporthook)
        print(f"Download completed: {target_path}")
        return target_path

    def load_model(self, model_key):
        try:
            model_path = self.get_model_path(model_key)
            if not os.path.exists(model_path):
                model_path = self.download_model_if_needed(model_key)
            print(f"Loading Whisper model: {model_path}")
            self.model = Model(model_path, print_realtime=False, print_progress=False)
            self.current_model_key = model_key
            return True
        except Exception as e:
            print(f"Failed to load model {model_key}:", e)
            return False

    def transcribe(self, audio_filepath, language="auto", enable_autocorrect=True):
        if not self.model:
            raise RuntimeError("Whisper model is not loaded.")
        if not os.path.exists(audio_filepath):
            raise FileNotFoundError(f"Audio file not found: {audio_filepath}")

        segments = self.model.transcribe(audio_filepath)
        text = " ".join([segment.text.strip() for segment in segments]).strip()

        if enable_autocorrect and text:
            text = self.post_process_text(text)

        return text

    def post_process_text(self, text):
        # Format spacing, clean double spaces, handle trailing spaces
        text = " ".join(text.split())
        return text
