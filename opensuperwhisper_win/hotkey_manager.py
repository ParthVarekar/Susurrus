import threading
import time
from pynput import keyboard, mouse

class HotkeyManager:
    def __init__(self, on_start_recording, on_stop_recording):
        self.on_start_recording = on_start_recording
        self.on_stop_recording = on_stop_recording
        self.mode = "hold"  # "hold" or "toggle"
        self.shortcut_name = "ctrl_shift_space"
        self.is_recording = False
        self.key_pressed = False

        self.keyboard_listener = None
        self.mouse_listener = None
        self.current_keys = set()

    def set_config(self, mode="hold", shortcut_name="ctrl_shift_space"):
        self.mode = mode
        self.shortcut_name = shortcut_name

    def start(self):
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click
        )
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

    def _is_target_shortcut(self, key):
        if self.shortcut_name == "caps_lock":
            return key == keyboard.Key.caps_lock
        elif self.shortcut_name == "f9":
            return key == keyboard.Key.f9
        elif self.shortcut_name == "f10":
            return key == keyboard.Key.f10
        elif self.shortcut_name == "alt_space":
            return (keyboard.Key.alt in self.current_keys or keyboard.Key.alt_l in self.current_keys or keyboard.Key.alt_r in self.current_keys) and key == keyboard.Key.space
        elif self.shortcut_name == "ctrl_shift_space":
            has_ctrl = any(k in self.current_keys for k in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r])
            has_shift = any(k in self.current_keys for k in [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r])
            return has_ctrl and has_shift and key == keyboard.Key.space
        return False

    def _on_key_press(self, key):
        self.current_keys.add(key)
        if self._is_target_shortcut(key):
            if self.mode == "hold":
                if not self.is_recording and not self.key_pressed:
                    self.key_pressed = True
                    self.is_recording = True
                    self.on_start_recording()
            elif self.mode == "toggle":
                if not self.key_pressed:
                    self.key_pressed = True
                    if not self.is_recording:
                        self.is_recording = True
                        self.on_start_recording()
                    else:
                        self.is_recording = False
                        self.on_stop_recording()

    def _on_key_release(self, key):
        if key in self.current_keys:
            self.current_keys.remove(key)

        if self.mode == "hold" and self.is_recording:
            # If target shortcut key released
            if self.shortcut_name in ["caps_lock", "f9", "f10"] and not self._is_key_down(self.shortcut_name):
                self.is_recording = False
                self.key_pressed = False
                self.on_stop_recording()
            elif self.shortcut_name in ["ctrl_shift_space", "alt_space"]:
                if key == keyboard.Key.space or not any(k in self.current_keys for k in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r]):
                    self.is_recording = False
                    self.key_pressed = False
                    self.on_stop_recording()

        if self.mode == "toggle":
            self.key_pressed = False

    def _is_key_down(self, name):
        if name == "caps_lock":
            return keyboard.Key.caps_lock in self.current_keys
        elif name == "f9":
            return keyboard.Key.f9 in self.current_keys
        elif name == "f10":
            return keyboard.Key.f10 in self.current_keys
        return False

    def _on_mouse_click(self, x, y, button, pressed):
        if self.shortcut_name == "middle_mouse" and button == mouse.Button.middle:
            if self.mode == "hold":
                if pressed and not self.is_recording:
                    self.is_recording = True
                    self.on_start_recording()
                elif not pressed and self.is_recording:
                    self.is_recording = False
                    self.on_stop_recording()
            elif self.mode == "toggle" and pressed:
                if not self.is_recording:
                    self.is_recording = True
                    self.on_start_recording()
                else:
                    self.is_recording = False
                    self.on_stop_recording()
