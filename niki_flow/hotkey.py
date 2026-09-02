import ctypes
import threading
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

VK_LCONTROL = 0xA2
VK_RCONTROL = 0xA3
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_SPACE = 0x20

CONTROL_VKS = {VK_LCONTROL, VK_RCONTROL}
WIN_VKS = {VK_LWIN, VK_RWIN}

LRESULT = ctypes.c_ssize_t
LowLevelKeyboardProc = ctypes.WINFUNCTYPE(
    LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.SetWindowsHookExW.argtypes = [
    ctypes.c_int,
    LowLevelKeyboardProc,
    wintypes.HINSTANCE,
    wintypes.DWORD,
]
user32.CallNextHookEx.restype = LRESULT
user32.CallNextHookEx.argtypes = [
    wintypes.HHOOK,
    ctypes.c_int,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.GetMessageW.argtypes = [
    ctypes.POINTER(wintypes.MSG),
    wintypes.HWND,
    ctypes.c_uint,
    ctypes.c_uint,
]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]


class PushToTalk:
    """Ctrl+Win+Espacio mantenidas = graba. Al soltar cualquiera, para.

    Se usa una tecla normal (Espacio) ademas de los dos modificadores porque
    Windows protege la tecla Windows a bajo nivel: con solo dos modificadoras
    (Ctrl+Win) a veces igual abre el buscador al soltar, sin importar como se
    suprima el evento. Con una tercera tecla normal en el combo, Windows nunca
    interpreta "Win sola" y el problema desaparece, sin necesitar suprimir nada.
    """

    def __init__(self, on_start, on_stop):
        self._on_start = on_start
        self._on_stop = on_stop
        self._pressed = set()
        self._active = False
        self._lock = threading.Lock()
        self._proc = LowLevelKeyboardProc(self._callback)
        self._hook_id = None

    def _combo_held(self):
        return (
            bool(self._pressed & CONTROL_VKS)
            and bool(self._pressed & WIN_VKS)
            and VK_SPACE in self._pressed
        )

    def _callback(self, code, wparam, lparam):
        if code == 0:
            kb = ctypes.cast(lparam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk = kb.vkCode
            with self._lock:
                if wparam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                    self._pressed.add(vk)
                elif wparam in (WM_KEYUP, WM_SYSKEYUP):
                    self._pressed.discard(vk)

                both = self._combo_held()
                if both and not self._active:
                    self._active = True
                    threading.Thread(target=self._on_start, daemon=True).start()
                elif not both and self._active:
                    self._active = False
                    threading.Thread(target=self._on_stop, daemon=True).start()
        return user32.CallNextHookEx(None, code, wparam, lparam)

    def start(self):
        def run():
            self._hook_id = user32.SetWindowsHookExW(
                WH_KEYBOARD_LL, self._proc, kernel32.GetModuleHandleW(None), 0
            )
            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

        threading.Thread(target=run, daemon=True).start()
