import os

import pystray
from PIL import Image, ImageDraw

from .config import DICTIONARY_PATH


def _make_icon(color):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((8, 4, 56, 44), fill=color)
    d.rectangle((28, 40, 36, 56), fill=color)
    d.rectangle((16, 56, 48, 60), fill=color)
    return img


IDLE_ICON = _make_icon((90, 90, 90, 255))
RECORDING_ICON = _make_icon((220, 40, 40, 255))


class Tray:
    def __init__(self, on_exit):
        self._on_exit = on_exit
        self.icon = pystray.Icon(
            "niki_flow",
            IDLE_ICON,
            "NIKI Flow",
            menu=pystray.Menu(
                pystray.MenuItem("Abrir diccionario", self._open_dictionary),
                pystray.MenuItem("Salir", self._exit),
            ),
        )

    def _open_dictionary(self, icon, item):
        if not DICTIONARY_PATH.exists():
            DICTIONARY_PATH.write_text(
                "# Una palabra o frase por linea\n", encoding="utf-8"
            )
        os.startfile(DICTIONARY_PATH)

    def _exit(self, icon, item):
        icon.stop()
        self._on_exit()

    def set_recording(self, is_recording):
        self.icon.icon = RECORDING_ICON if is_recording else IDLE_ICON
