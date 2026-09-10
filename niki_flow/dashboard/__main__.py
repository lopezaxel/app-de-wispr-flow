import signal  # noqa: F401  — must import before webview: works around a Python
# 3.14 / pywebview winforms backend crash ("dictionary changed size during
# iteration" in signal.py) when webview imports signal itself for the first time.
from pathlib import Path

import webview

from .. import storage
from .api import Api

WEB_DIR = Path(__file__).resolve().parent / "web"


def main():
    storage.init_db()
    api = Api()
    webview.create_window(
        "NIKI Flow — Panel",
        str(WEB_DIR / "index.html"),
        js_api=api,
        width=960,
        height=680,
        min_size=(720, 520),
        background_color="#0a0a0a",
    )
    webview.start()


if __name__ == "__main__":
    main()
