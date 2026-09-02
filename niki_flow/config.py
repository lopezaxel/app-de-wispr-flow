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
