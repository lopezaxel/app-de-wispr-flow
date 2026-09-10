import threading

import numpy as np
import sounddevice as sd

from .config import SAMPLE_RATE

SPEECH_THRESHOLD = 0.05
MIN_SPEECH_SECONDS = 0.15
SILENCE_SECONDS = 1.2
MAX_RECORD_SECONDS = 25.0  # red de seguridad: nunca queda grabando para siempre


class Recorder:
    """Captura audio del micrófono mientras el hotkey está mantenido, o hasta
    que detecta silencio sostenido si se activó por palabra clave."""

    def __init__(self, on_level=None):
        self._frames = []
        self._stream = None
        self._on_level = on_level
        self._on_silence_timeout = None
        self._speech_elapsed = 0.0
        self._silence_elapsed = 0.0
        self._total_elapsed = 0.0
        self._silence_fired = False

    def start(self, on_silence_timeout=None):
        self._frames = []
        self._on_silence_timeout = on_silence_timeout
        self._speech_elapsed = 0.0
        self._silence_elapsed = 0.0
        self._total_elapsed = 0.0
        self._silence_fired = False

        def callback(indata, frames, time_info, status):
            self._frames.append(indata.copy())

            rms = float(np.sqrt(np.mean(indata.astype(np.float32) ** 2)))
            normalized = rms / 32768.0
            # sqrt comprime el rango: hace visible el volumen de voz normal,
            # no solo picos fuertes.
            level = min((normalized ** 0.5) * 3.2, 1.0)

            if self._on_level:
                self._on_level(level)

            if self._on_silence_timeout and not self._silence_fired:
                chunk_seconds = frames / SAMPLE_RATE
                self._total_elapsed += chunk_seconds
                if level >= SPEECH_THRESHOLD:
                    self._speech_elapsed += chunk_seconds
                    self._silence_elapsed = 0.0
                else:
                    self._silence_elapsed += chunk_seconds

                should_stop = (
                    self._speech_elapsed >= MIN_SPEECH_SECONDS
                    and self._silence_elapsed >= SILENCE_SECONDS
                ) or self._total_elapsed >= MAX_RECORD_SECONDS

                if should_stop:
                    self._silence_fired = True
                    threading.Thread(target=self._on_silence_timeout, daemon=True).start()

        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=callback
        )
        self._stream.start()

    def stop(self):
        if self._stream is None:
            return None
        self._stream.stop()
        self._stream.close()
        self._stream = None
        if not self._frames:
            return None
        return np.concatenate(self._frames, axis=0)
