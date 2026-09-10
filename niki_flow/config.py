import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DICTIONARY_PATH = BASE_DIR / "dictionary.txt"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGUAGE = os.getenv("NIKI_FLOW_LANGUAGE", "es")
MODEL = os.getenv("NIKI_FLOW_MODEL", "whisper-large-v3-turbo")
SAMPLE_RATE = 16000

# Nombre corto de un modelo incluido (ej. "hey_jarvis") o ruta a un .onnx/.tflite
# propio (ej. wakeword/hey-niki_windows.onnx) generado en openwakeword.com/train.
WAKEWORD_MODEL = os.getenv("NIKI_FLOW_WAKEWORD_MODEL", "hey_jarvis")
WAKEWORD_THRESHOLD = float(os.getenv("NIKI_FLOW_WAKEWORD_THRESHOLD", "0.5"))
WAKEWORD_ENABLED = os.getenv("NIKI_FLOW_WAKEWORD_ENABLED", "true").lower() == "true"

# Ventana de revisión antes de pegar: permite corregir el texto transcripto
# (y que la app aprenda de esa corrección) antes de inyectarlo.
REVIEW_ENABLED = os.getenv("NIKI_FLOW_REVIEW_ENABLED", "true").lower() == "true"
REVIEW_TIMEOUT_SECONDS = float(os.getenv("NIKI_FLOW_REVIEW_TIMEOUT", "4"))

DATA_DIR = BASE_DIR / "niki_flow_data"
HISTORY_DB_PATH = DATA_DIR / "history.db"
