import os
import sys
import threading

from niki_flow.config import GROQ_API_KEY
from niki_flow.hotkey import PushToTalk
from niki_flow.injector import inject
from niki_flow.overlay import Overlay
from niki_flow.recorder import Recorder
from niki_flow.transcriber import transcribe
from niki_flow.tray import Tray

MIN_SAMPLES = 1600  # ~0.1s a 16kHz: descarta toques accidentales del hotkey


def main():
    if not GROQ_API_KEY:
        print("Falta GROQ_API_KEY. Copia .env.example a .env y completa tu clave.")
        sys.exit(1)

    overlay = Overlay()
    recorder = Recorder(on_level=overlay.set_level)
    tray = Tray(on_exit=lambda: os._exit(0))

    def on_start():
        tray.set_recording(True)
        overlay.show_recording()
        recorder.start()

    def on_stop():
        tray.set_recording(False)
        audio = recorder.stop()
        if audio is None or len(audio) < MIN_SAMPLES:
            overlay.hide()
            return
        overlay.show_transcribing()

        def worker():
            try:
                text = transcribe(audio)
                inject(text)
            except Exception as e:
                print(f"Error transcribiendo: {e}")
            finally:
                overlay.hide()

        threading.Thread(target=worker, daemon=True).start()

    hotkey = PushToTalk(on_start, on_stop)
    hotkey.start()

    threading.Thread(target=tray.icon.run, daemon=True).start()

    overlay.run()


if __name__ == "__main__":
    main()
