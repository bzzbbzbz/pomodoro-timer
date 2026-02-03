"""Light/dark theme colors (Shutdowner-style). Apply to root and widgets."""

from typing import Any

THEME_LIGHT: dict[str, Any] = {
    "bg": "#f0f0f0",
    "fg": "#1a1a1a",
    "fg_dim": "#666666",
    "frame_bg": "#f5f5f5",
    "entry_bg": "#ffffff",
    "entry_fg": "#1a1a1a",
    "btn_bg": "#e8e8e8",
    "btn_fg": "#1a1a1a",
    "btn_active": "#d0d0d0",
    "progress_bg": "#e0e0e0",
    "progress_fg": "#4caf50",
    "select_bg": "#b0d4f1",
    "select_fg": "#1a1a1a",
}

THEME_DARK: dict[str, Any] = {
    "bg": "#2b2b2b",
    "fg": "#e0e0e0",
    "fg_dim": "#a0a0a0",
    "frame_bg": "#333333",
    "entry_bg": "#3c3c3c",
    "entry_fg": "#e0e0e0",
    "btn_bg": "#404040",
    "btn_fg": "#e0e0e0",
    "btn_active": "#505050",
    "progress_bg": "#404040",
    "progress_fg": "#4caf50",
    "select_bg": "#505050",
    "select_fg": "#e0e0e0",
}


def theme_colors(theme: str) -> dict[str, Any]:
    if theme == "dark":
        return dict(THEME_DARK)
    return dict(THEME_LIGHT)
