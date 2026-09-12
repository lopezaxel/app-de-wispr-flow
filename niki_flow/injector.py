import threading
import time

import keyboard
import pyperclip

# No hay forma de saber cuándo la app destino terminó de leer el portapapeles
# tras el paste, así que restauramos el valor previo con un margen generoso
# en un hilo aparte para no bloquear al llamador ni cortar el paste en apps
# lentas (RDP, apps cargadas, etc.).
CLIPBOARD_RESTORE_DELAY = 0.3


def inject(text):
    """Pega el texto en donde esté el foco, preservando el portapapeles previo."""
    if not text:
        return
    previous = pyperclip.paste()
    pyperclip.copy(text)
    time.sleep(0.02)
    keyboard.send("ctrl+v")

    def restore():
        time.sleep(CLIPBOARD_RESTORE_DELAY)
        pyperclip.copy(previous)

    threading.Thread(target=restore, daemon=True).start()
