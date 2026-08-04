import time
import win32clipboard
import win32con
from pynput.keyboard import Controller, Key

keyboard_controller = Controller()

def set_clipboard_text(text):
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return True
    except Exception as e:
        print("Clipboard error:", e)
        return False

def inject_text(text, paste_to_active_window=True):
    if not text:
        return
    set_clipboard_text(text)
    if paste_to_active_window:
        # Give a small pause for active window focus
        time.sleep(0.15)
        # Simulate Ctrl+V to paste
        keyboard_controller.press(Key.ctrl)
        keyboard_controller.press('v')
        keyboard_controller.release('v')
        keyboard_controller.release(Key.ctrl)
