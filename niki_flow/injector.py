import time

import keyboard
import pyperclip


def inject(text):
    """Pega el texto en donde esté el foco, preservando el portapapeles previo."""
    if not text:
        return
    previous = pyperclip.paste()
    pyperclip.copy(text)
    time.sleep(0.02)
    keyboard.send("ctrl+v")
    time.sleep(0.08)
    pyperclip.copy(previous)
