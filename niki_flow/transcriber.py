import io

import soundfile as sf
from groq import Groq

from .config import GROQ_API_KEY, LANGUAGE, MODEL, SAMPLE_RATE
from .dictionary import build_prompt

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def transcribe(audio):
    # FLAC en vez de WAV: comprime sin perder calidad y sube mucho mas rapido
    # en conexiones con poco ancho de subida.
    buffer = io.BytesIO()
    sf.write(buffer, audio, SAMPLE_RATE, format="FLAC", subtype="PCM_16")
    buffer.seek(0)
    buffer.name = "audio.flac"

    result = _get_client().audio.transcriptions.create(
        file=buffer,
        model=MODEL,
        language=LANGUAGE,
        prompt=build_prompt(),
    )
    return result.text.strip()
