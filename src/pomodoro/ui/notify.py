"""Play sound and flash taskbar on timer end (Windows)."""

import sys
import tkinter as tk
from pathlib import Path
from typing import Any

_PKG_DIR = Path(__file__).resolve().parent.parent


def _sound_candidates() -> list[Path]:
    """sound.mp3: when frozen (exe) use sys._MEIPASS, else package or project root."""
    paths: list[Path] = []
    meipass: str | None = getattr(sys, "_MEIPASS", None)
    if getattr(sys, "frozen", False) and meipass is not None:
        paths.append(Path(meipass) / "sound.mp3")
    paths.extend([
        _PKG_DIR / "sound.mp3",
        _PKG_DIR.parent.parent / "sound.mp3",
    ])
    return paths


def _find_sound() -> Path | None:
    for p in _sound_candidates():
        if p.is_file():
            return p
    return None


def play_sound() -> None:
    """Play sound.mp3 if present (Windows MCI). Close alias before reopen so repeat plays."""
    path = _find_sound()
    if path is None:
        return
    try:
        import ctypes

        winmm = ctypes.windll.winmm
        alias = "pomodoro_snd"
        winmm.mciSendStringW(f"close {alias}", None, 0, None)
        path_str = str(path.resolve())
        cmd_open = f'open "{path_str}" type mpegvideo alias {alias}'
        buf = ctypes.create_unicode_buffer(256)
        err = winmm.mciSendStringW(cmd_open, buf, len(buf), None)
        if err != 0:
            return
        winmm.mciSendStringW(f"play {alias}", None, 0, None)
    except Exception:
        pass


def flash_taskbar(hwnd: int, count: int = 3) -> None:
    """Flash window in taskbar (Windows). FLASHW_ALL=3, flash count times."""
    try:
        import ctypes
        from ctypes import wintypes

        FLASHW_ALL = 0x00000003
        FLASHW_TIMERNOFG = 0x0000000C

        class FLASHWINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("hwnd", wintypes.HWND),
                ("dwFlags", wintypes.DWORD),
                ("uCount", wintypes.UINT),
                ("dwTimeout", wintypes.DWORD),
            ]

        info = FLASHWINFO(
            cbSize=ctypes.sizeof(FLASHWINFO),
            hwnd=hwnd,
            dwFlags=FLASHW_ALL | FLASHW_TIMERNOFG,
            uCount=count,
            dwTimeout=0,
        )
        ctypes.windll.user32.FlashWindowEx(ctypes.byref(info))
    except Exception:
        pass


def notify_timer_end(root: Any) -> None:
    """Play sound and flash taskbar 3 times. root is tk.Tk()."""
    play_sound()
    try:
        hwnd = root.winfo_id()
        if hwnd:
            flash_taskbar(hwnd, 3)
    except (tk.TclError, AttributeError):
        pass
