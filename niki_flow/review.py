import queue
import threading
import tkinter as tk

from .config import REVIEW_ENABLED, REVIEW_TIMEOUT_SECONDS

WIDTH = 420
HEIGHT = 90
MARGIN_BOTTOM = 140
BG = "#1e1e1e"
FG = "white"


class ReviewPopup:
    """Muestra el texto transcripto antes de pegarlo, para corregirlo si hace
    falta. Se auto-acepta sola pasado un timeout si no se toca."""

    def __init__(self, root):
        self._root = root
        self._queue = queue.Queue()
        self._timeout_job = None
        self._result_event = None
        self._result = None
        self._poll()

    def _poll(self):
        try:
            while True:
                action = self._queue.get_nowait()
                action()
        except queue.Empty:
            pass
        self._root.after(30, self._poll)

    def request(self, text):
        """Llamado desde el hilo worker. Bloquea hasta que el usuario confirma,
        edita o descarta. Devuelve el texto final, o None si se descartó."""
        if not REVIEW_ENABLED:
            return text
        event = threading.Event()
        self._queue.put(lambda: self._show(text, event))
        event.wait()
        return self._result

    def _show(self, text, event):
        self._result_event = event
        self._result = text

        win = tk.Toplevel(self._root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=BG)

        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        x = (screen_w - WIDTH) // 2
        y = screen_h - MARGIN_BOTTOM
        win.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

        txt = tk.Text(
            win,
            bg=BG,
            fg=FG,
            insertbackground=FG,
            wrap="word",
            font=("Segoe UI", 10),
            bd=0,
            highlightthickness=0,
        )
        txt.insert("1.0", text)
        txt.pack(fill="both", expand=True, padx=10, pady=8)
        txt.focus_force()
        txt.mark_set("insert", "end")

        def accept(_event=None):
            self._finish(win, txt.get("1.0", "end-1c"))
            return "break"

        def discard(_event=None):
            self._finish(win, None)
            return "break"

        def newline(_event=None):
            txt.insert("insert", "\n")
            return "break"

        txt.bind("<Return>", accept)
        txt.bind("<Shift-Return>", newline)
        txt.bind("<Escape>", discard)
        win.protocol("WM_DELETE_WINDOW", discard)

        self._timeout_job = self._root.after(
            int(REVIEW_TIMEOUT_SECONDS * 1000), accept
        )

    def _finish(self, win, result):
        if self._timeout_job:
            self._root.after_cancel(self._timeout_job)
            self._timeout_job = None
        self._result = result
        win.destroy()
        self._result_event.set()
