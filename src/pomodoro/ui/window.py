"""Overlay window: topmost, alpha. [REQ-POMODORO-1-01], [REQ-POMODORO-1-02]"""
# [START SPEC:POMODORO-1:WINDOW]
# req_refs: REQ-POMODORO-1-01, REQ-POMODORO-1-02

import tkinter as tk
from typing import Callable


def setup_overlay(
    root: tk.Tk, alpha: float, on_close: Callable[[], None] | None = None
) -> None:
    """
    Configure root as always-on-top, semi-transparent overlay.
    Pre: root is Tk(); 0.3 <= alpha <= 1.0.
    Post: root has -topmost True, -alpha alpha; compact geometry; on_close called on WM_DELETE.
    """
    root.attributes("-topmost", True)
    root.attributes("-alpha", alpha)
    root.geometry("320x420+40+40")
    root.resizable(True, True)
    root.minsize(240, 180)
    root.title("Pomodoro")
    if on_close is not None:
        root.protocol("WM_DELETE_WINDOW", on_close)


def set_alpha(root: tk.Tk, alpha: float) -> None:
    """Set window transparency. Pre: 0.3 <= alpha <= 1.0."""
    root.attributes("-alpha", max(0.3, min(1.0, alpha)))


# [END SPEC:POMODORO-1:WINDOW]
