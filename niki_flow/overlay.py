import queue
import tkinter as tk

WIDTH = 150
HEIGHT = 34
MARGIN_BOTTOM = 90
BG = "#1e1e1e"
TRANSPARENT = "#123456"

COLOR_BARS = "#4da3ff"
COLOR_TRANSCRIBING = "#e0a828"

BAR_COUNT = 5
BAR_WIDTH = 4
BAR_GAP = 5
BAR_MIN_HEIGHT = 4
BAR_MAX_HEIGHT = 20
BARS_START_X = 18


class Overlay:
    """Barrita flotante, siempre encima, que muestra el estado del dictado."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT)
        self.root.attributes("-transparentcolor", TRANSPARENT)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - WIDTH) // 2
        y = screen_h - MARGIN_BOTTOM
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

        self.canvas = tk.Canvas(
            self.root, width=WIDTH, height=HEIGHT, bg=TRANSPARENT, highlightthickness=0
        )
        self.canvas.pack()

        r = HEIGHT // 2
        self.canvas.create_oval(0, 0, HEIGHT, HEIGHT, fill=BG, outline="")
        self.canvas.create_oval(WIDTH - HEIGHT, 0, WIDTH, HEIGHT, fill=BG, outline="")
        self.canvas.create_rectangle(r, 0, WIDTH - r, HEIGHT, fill=BG, outline="")

        cy = HEIGHT / 2
        self.bars = []
        for i in range(BAR_COUNT):
            bx = BARS_START_X + i * (BAR_WIDTH + BAR_GAP)
            bar = self.canvas.create_line(
                bx, cy, bx, cy, width=BAR_WIDTH, fill=COLOR_BARS, capstyle=tk.ROUND
            )
            self.bars.append(bar)

        self.dot = self.canvas.create_oval(
            12, cy - 6, 24, cy + 6, fill=COLOR_TRANSCRIBING, outline="", state="hidden"
        )
        self.label = self.canvas.create_text(
            WIDTH / 2 + 8, cy, text="", fill="white", font=("Segoe UI", 9), state="hidden"
        )

        self.root.withdraw()

        self._queue = queue.Queue()
        self._recording = False
        self._level = 0.0
        self._level_history = [0.0] * BAR_COUNT
        self._poll()

    def _poll(self):
        try:
            while True:
                action = self._queue.get_nowait()
                action()
        except queue.Empty:
            pass

        if self._recording:
            self._level_history.pop(0)
            self._level_history.append(self._level)
            self._redraw_bars()

        self.root.after(30, self._poll)

    def _redraw_bars(self):
        cy = HEIGHT / 2
        for bar, level in zip(self.bars, self._level_history):
            h = BAR_MIN_HEIGHT + level * (BAR_MAX_HEIGHT - BAR_MIN_HEIGHT)
            x = self.canvas.coords(bar)[0]
            self.canvas.coords(bar, x, cy - h / 2, x, cy + h / 2)

    def _set_recording_visuals(self, visible):
        state = "normal" if visible else "hidden"
        for bar in self.bars:
            self.canvas.itemconfig(bar, state=state)
        self.canvas.itemconfig(self.dot, state="hidden")
        self.canvas.itemconfig(self.label, state="hidden")

    def _set_transcribing_visuals(self):
        for bar in self.bars:
            self.canvas.itemconfig(bar, state="hidden")
        self.canvas.itemconfig(self.dot, state="normal")
        self.canvas.itemconfig(self.label, state="normal", text="Transcribiendo...")

    def show_recording(self):
        self._recording = True
        self._level_history = [0.0] * BAR_COUNT
        self._queue.put(lambda: (self._set_recording_visuals(True), self.root.deiconify()))

    def show_transcribing(self):
        self._recording = False
        self._queue.put(lambda: (self._set_transcribing_visuals(), self.root.deiconify()))

    def hide(self):
        self._recording = False
        self._queue.put(lambda: self.root.withdraw())

    def set_level(self, level):
        self._level = level

    def run(self):
        self.root.mainloop()
