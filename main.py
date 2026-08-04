import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from opensuperwhisper_win.gui import OpenSuperWhisperApp

def main():
    print("Starting OpenSuperWhisper for Windows...")
    app = OpenSuperWhisperApp()
    app.mainloop()

if __name__ == "__main__":
    main()
