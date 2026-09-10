import os
import sys
import threading

from niki_flow import storage
from niki_flow.config import GROQ_API_KEY, WAKEWORD_ENABLED
from niki_flow.hotkey import PushToTalk
from niki_flow.injector import inject
from niki_flow.overlay import Overlay
from niki_flow.recorder import Recorder
from niki_flow.review import ReviewPopup
from niki_flow.transcriber import transcribe
from niki_flow.tray import Tray
from niki_flow.wakeword import WakeWordListener

MIN_SAMPLES = 1600  # ~0.1s a 16kHz: descarta toques accidentales del hotkey


def main():
    if not GROQ_API_KEY:
        print("Falta GROQ_API_KEY. Copia .env.example a .env y completa tu clave.")
        sys.exit(1)

    storage.init_db()

    overlay = Overlay()
    recorder = Recorder(on_level=overlay.set_level)
    review = ReviewPopup(overlay.root)
    tray = Tray(on_exit=lambda: os._exit(0))

    state_lock = threading.Lock()
    state = {"recording": False, "cancelled": False}

    def finish_recording():
        tray.set_recording(False)
        audio = recorder.stop()

        if audio is None or len(audio) < MIN_SAMPLES:
            overlay.hide()
            wakeword.resume()
            with state_lock:
                state["recording"] = False
                state["cancelled"] = False
            return

        overlay.show_transcribing()

        def worker():
            try:
                raw_text = transcribe(audio)
                with state_lock:
                    cancelled = state["cancelled"]
                if not cancelled:
                    final_text = review.request(raw_text)
                    if final_text:
                        inject(final_text)
                        storage.log_dictation(raw_text, final_text)
            except Exception as e:
                print(f"Error transcribiendo: {e}")
            finally:
                overlay.hide()
                wakeword.resume()
                with state_lock:
                    state["recording"] = False
                    state["cancelled"] = False

        threading.Thread(target=worker, daemon=True).start()

    def begin_recording(auto_stop_on_silence):
        with state_lock:
            if state["recording"]:
                return
            state["recording"] = True
            state["cancelled"] = False
        tray.set_recording(True)
        overlay.show_recording()
        wakeword.pause()
        recorder.start(on_silence_timeout=finish_recording if auto_stop_on_silence else None)

    def on_hotkey_start():
        begin_recording(auto_stop_on_silence=False)

    def on_hotkey_stop():
        with state_lock:
            if not state["recording"]:
                return
        finish_recording()

    def on_wake():
        begin_recording(auto_stop_on_silence=True)

    def on_cancel():
        with state_lock:
            if not state["recording"]:
                return
            state["cancelled"] = True
        # Si todavia esta grabando (no llego a mandarse a transcribir), cortamos
        # y descartamos el audio directo, sin pasar por finish_recording.
        audio = recorder.stop()
        tray.set_recording(False)
        overlay.hide()
        if audio is not None:
            wakeword.resume()
            with state_lock:
                state["recording"] = False
                state["cancelled"] = False
        # Si ya estaba transcribiendo (audio is None: el stream ya se habia
        # cerrado antes), el flag "cancelled" hace que el worker de
        # finish_recording descarte el resultado en vez de pegarlo, y sea el
        # que finalmente reanude la palabra clave y cierre el estado.

    hotkey = PushToTalk(on_hotkey_start, on_hotkey_stop)
    hotkey.start()

    wakeword = WakeWordListener(on_wake)
    if WAKEWORD_ENABLED:
        wakeword.start()

    overlay.set_on_cancel(on_cancel)

    threading.Thread(target=tray.icon.run, daemon=True).start()

    overlay.run()


if __name__ == "__main__":
    main()
