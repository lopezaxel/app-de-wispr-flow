import threading
import time

import sounddevice as sd
from openwakeword.model import Model

from .config import SAMPLE_RATE, WAKEWORD_MODEL, WAKEWORD_THRESHOLD

FRAME_SAMPLES = 1280  # 80ms a 16kHz: tamano de frame que espera openwakeword

# Al reanudar despues de un dictado, se ignoran detecciones por un rato: el
# eco de la propia voz o el buffer interno del modelo puede disparar un falso
# positivo inmediato si no se le da un respiro.
RESUME_COOLDOWN_SECONDS = 2.0


class WakeWordListener:
    """Escucha el microfono en segundo plano y dispara on_wake al detectar la frase."""

    def __init__(self, on_wake):
        self._on_wake = on_wake
        self._model = Model(wakeword_models=[WAKEWORD_MODEL], inference_framework="onnx")
        self._model_name = next(iter(self._model.models.keys()))
        self._stream = None
        self._paused = False
        self._triggered = False
        self._resumed_at = 0.0

    def pause(self):
        self._paused = True

    def resume(self):
        self._triggered = False
        self._resumed_at = time.monotonic()
        self._paused = False

    def _callback(self, indata, frames, time_info, status):
        if self._paused or self._triggered:
            return
        score = self._model.predict(indata[:, 0])[self._model_name]
        if time.monotonic() - self._resumed_at < RESUME_COOLDOWN_SECONDS:
            return
        if score >= WAKEWORD_THRESHOLD:
            self._triggered = True
            threading.Thread(target=self._on_wake, daemon=True).start()

    def start(self):
        self._resumed_at = time.monotonic()
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=FRAME_SAMPLES,
            callback=self._callback,
        )
        self._stream.start()
