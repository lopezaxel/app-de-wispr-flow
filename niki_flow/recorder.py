import numpy as np
import sounddevice as sd

from .config import SAMPLE_RATE


class Recorder:
    """Captura audio del micrófono mientras el hotkey está mantenido."""

    def __init__(self, on_level=None):
        self._frames = []
        self._stream = None
        self._on_level = on_level

    def start(self):
        self._frames = []

        def callback(indata, frames, time_info, status):
            self._frames.append(indata.copy())
            if self._on_level:
                rms = float(np.sqrt(np.mean(indata.astype(np.float32) ** 2)))
                normalized = rms / 32768.0
                # sqrt comprime el rango: hace visible el volumen de voz normal,
                # no solo picos fuertes.
                self._on_level(min((normalized ** 0.5) * 3.2, 1.0))

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
