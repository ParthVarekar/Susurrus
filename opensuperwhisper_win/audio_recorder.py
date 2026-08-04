import os
import wave
import numpy as np
import sounddevice as sd

class AudioRecorder:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.audio_data = []
        self.current_volume = 0.0
        self.stream = None
        self.device_index = None

    @staticmethod
    def get_input_devices():
        devices = []
        try:
            device_list = sd.query_devices()
            for i, dev in enumerate(device_list):
                if dev['max_input_channels'] > 0:
                    devices.append({'id': i, 'name': dev['name']})
        except Exception as e:
            print("Error querying audio devices:", e)
        return devices

    def set_device(self, device_index):
        self.device_index = device_index

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print("Audio Callback Status:", status)
        if self.is_recording:
            self.audio_data.append(indata.copy())
            # Calculate RMS for visual audio level meter
            rms = float(np.sqrt(np.mean(indata**2)))
            self.current_volume = min(1.0, rms * 5.0)

    def start_recording(self):
        if self.is_recording:
            return
        self.audio_data = []
        self.is_recording = True
        self.current_volume = 0.0
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.device_index,
                callback=self._audio_callback,
                dtype='float32'
            )
            self.stream.start()
        except Exception as e:
            self.is_recording = False
            print("Failed to start audio recording stream:", e)
            raise e

    def stop_recording(self, output_filepath="temp_recording.wav"):
        if not self.is_recording:
            return None
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self.audio_data:
            return None

        # Concatenate audio frames
        audio_array = np.concatenate(self.audio_data, axis=0)
        # Convert float32 to 16-bit PCM
        audio_int16 = (audio_array * 32767).astype(np.int16)

        with wave.open(output_filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2) # 16-bit = 2 bytes
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_int16.tobytes())

        return output_filepath
