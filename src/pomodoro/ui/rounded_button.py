"""Rounded button (Canvas-based) for light/dark theme."""

import tkinter as tk
from typing import Callable

RADIUS = 8


def _rounded_rect(
    canvas: tk.Canvas,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    r: int,
    fill: str = "",
    outline: str = "",
) -> list[int]:
    """Create rounded rectangle on canvas. Returns created item ids."""
    ids: list[int] = []
    r = min(r, (x2 - x1) // 2, (y2 - y1) // 2)
    ids.append(
        canvas.create_arc(
            x1,
            y1,
            x1 + 2 * r,
            y1 + 2 * r,
            start=90,
            extent=90,
            fill=fill,
            outline=outline,
        )
    )
    ids.append(
        canvas.create_arc(
            x2 - 2 * r,
            y1,
            x2,
            y1 + 2 * r,
            start=0,
            extent=90,
            fill=fill,
            outline=outline,
        )
    )
    ids.append(
        canvas.create_arc(
            x2 - 2 * r,
            y2 - 2 * r,
            x2,
            y2,
            start=270,
            extent=90,
            fill=fill,
            outline=outline,
        )
    )
    ids.append(
        canvas.create_arc(
            x1,
            y2 - 2 * r,
            x1 + 2 * r,
            y2,
            start=180,
            extent=90,
            fill=fill,
            outline=outline,
        )
    )
    ids.append(
        canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline=outline)
    )
    ids.append(
        canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline=outline)
    )
    return ids


class RoundedButton(tk.Canvas):
    """Clickable rounded button. Use config(background=..., ...) and apply_theme(colors)."""

    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        command: Callable[[], None] | None = None,
        width: int = 80,
        height: int = 28,
        radius: int = RADIUS,
    ) -> None:
        # Canvas +1px so right/bottom edge is not clipped by parent
        super().__init__(
            parent, width=width + 1, height=height + 1, highlightthickness=0
        )
        self._width = width
        self._height = height
        self._radius = radius
        self._command = command
        self._text = text
        self._rect_ids: list[int] = []
        self._text_id: int | None = None
        self._bg = "#e8e8e8"
        self._fg = "#1a1a1a"
        self._disabled = False
        self._draw()
        if command is not None:
            self.bind("<Button-1>", self._on_click)
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
        self._hover = False

    # [START SPEC:POMODORO-3:NO_CLIP]
    # req_refs: REQ-POMODORO-3-04
    def _draw(self) -> None:
        self.delete("all")
        # Draw to (width, height) so full rect is inside (width+1)x(height+1) canvas
        self._rect_ids = _rounded_rect(
            self,
            0,
            0,
            self._width,
            self._height,
            self._radius,
            fill=self._bg,
            outline="",
        )
        self._text_id = self.create_text(
            (self._width + 1) // 2,
            (self._height + 1) // 2,
            text=self._text,
            fill=str(self._fg),
            font=("Segoe UI", 10),
        )

    # [END SPEC:POMODORO-3:NO_CLIP]

    def _on_click(self, _event: tk.Event) -> None:
        if self._command is not None:
            self._command()

    def _on_enter(self, _event: tk.Event) -> None:
        self._hover = True
        self._update_fill()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hover = False
        self._update_fill()

    def _update_fill(self) -> None:
        fill = getattr(self, "_btn_active", self._bg) if self._hover else self._bg
        for iid in self._rect_ids:
            self.itemconfig(iid, fill=fill)

    def apply_theme(self, colors: dict) -> None:
        self._bg = str(colors.get("btn_bg", self._bg))
        self._fg = str(colors.get("btn_fg", self._fg))
        self._btn_active = str(colors.get("btn_active", self._bg))
        self.configure(bg=str(colors.get("bg", self._bg)))
        self._draw()
        if self._text_id is not None:
            self.itemconfig(self._text_id, fill=self._fg)

    def enable(self, disabled: bool) -> None:
        """Disable button if disabled=True, enable if disabled=False."""
        self._disabled = disabled
        if disabled:
            self.unbind("<Button-1>")
            self.unbind("<Enter>")
            self.unbind("<Leave>")
        elif self._command is not None:
            self.bind("<Button-1>", self._on_click)
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
