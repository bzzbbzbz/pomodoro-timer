"""Timer: MM:SS, Start/Pause/Reset, progress bar, run-state callback, theme."""
# [START SPEC:POMODORO-1:TIMER]
# [START SPEC:POMODORO-2:TIMER]
# req_refs: REQ-POMODORO-2-04

import tkinter as tk
from tkinter import ttk
from typing import Callable

from pomodoro.ui.rounded_button import RoundedButton

WORK = "work"
BREAK = "break"

CLOCK_FONT_SIZE = 44
BIG_BTN_WIDTH = 200
BIG_BTN_HEIGHT = 44
TAB_BTN_WIDTH = 100


def _format_mmss(seconds: int) -> str:
    m, s = divmod(max(0, seconds), 60)
    return f"{m:02d}:{s:02d}"


class TimerWidget:
    """
    Timer display, one big Start/Pause button, mode selector Pomodoro | Перерыв.
    Calls on_run_state_changed(running: bool) and on_phase_changed(phase) when phase changes.
    """

    def __init__(
        self,
        parent: tk.Misc,
        get_config: Callable[[], dict],
        on_finish: Callable[[str], None] | None = None,
        on_run_state_changed: Callable[[bool], None] | None = None,
        on_phase_changed: Callable[[str], None] | None = None,
    ) -> None:
        self._get_config = get_config
        self._on_finish = on_finish or (lambda _: None)
        self._on_run_state = on_run_state_changed or (lambda _: None)
        self._on_phase = on_phase_changed or (lambda _: None)
        self._remaining = 0
        self._total_seconds = 0
        self._phase: str = WORK
        self._selected_mode: str = WORK
        self._running = False
        self._after_id: str | None = None

        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, padx=(8, 14), pady=6)

        self._label = tk.Label(frame, text="25:00", font=("Consolas", CLOCK_FONT_SIZE))
        self._label.pack(pady=(0, 4))

        self._progress_var = tk.DoubleVar(value=0.0)
        self._time_progress = ttk.Progressbar(
            frame, variable=self._progress_var, maximum=100, mode="determinate"
        )
        self._time_progress.pack(fill=tk.X, pady=4)

        big_btn_frame = tk.Frame(frame)
        big_btn_frame.pack(pady=8)
        self._big_btn_frame = big_btn_frame
        self._btn_main = RoundedButton(
            big_btn_frame,
            text="Старт",
            width=BIG_BTN_WIDTH,
            height=BIG_BTN_HEIGHT,
            command=self._on_main_click,
        )
        self._btn_main.pack(padx=(0, 1), pady=(0, 1))

        tabs_frame = tk.Frame(frame)
        tabs_frame.pack(pady=6)
        self._btn_pomodoro = RoundedButton(
            tabs_frame,
            text="Помодоро",
            width=TAB_BTN_WIDTH,
            height=32,
            command=lambda: self._select_mode(WORK),
        )
        self._btn_pomodoro.pack(side=tk.LEFT, padx=(0, 2), pady=(0, 1))
        self._btn_break = RoundedButton(
            tabs_frame,
            text="Перерыв",
            width=TAB_BTN_WIDTH,
            height=32,
            command=lambda: self._select_mode(BREAK),
        )
        self._btn_break.pack(side=tk.LEFT, padx=(0, 1), pady=(0, 1))
        self._tabs_frame = tabs_frame
        self._update_tabs_highlight()

        self._btn_frame = frame
        self.reset_to_work()

    def _select_mode(self, mode: str) -> None:
        if self._running:
            return
        self._selected_mode = mode
        self._update_tabs_highlight()
        cfg = self._get_config()
        if mode == WORK:
            self._remaining = cfg["work_minutes"] * 60
            self._phase = WORK
        else:
            self._remaining = cfg["break_minutes"] * 60
            self._phase = BREAK
        self._total_seconds = self._remaining
        self._label.config(text=_format_mmss(self._remaining))
        self._progress_var.set(100.0)
        self._on_phase(self._phase)

    def _update_tabs_highlight(self) -> None:
        colors = getattr(self, "_last_theme", None) or {
            "btn_bg": "#e8e8e8",
            "btn_fg": "#1a1a1a",
            "bg": "#f0f0f0",
            "btn_active": "#d0d0d0",
        }
        self._btn_pomodoro.apply_theme(colors)
        self._btn_break.apply_theme(colors)
        active_bg = str(colors.get("btn_active", "#d0d0d0"))
        for btn, is_selected in [
            (self._btn_pomodoro, self._selected_mode == WORK),
            (self._btn_break, self._selected_mode == BREAK),
        ]:
            btn._bg = active_bg if is_selected else str(colors.get("btn_bg", "#e8e8e8"))
            btn._draw()

    def _on_main_click(self) -> None:
        if self._running:
            self._on_pause()
        else:
            self._on_start()

    def _set_pause_disabled(self, disabled: bool) -> None:
        pass

    def _layout_buttons(self, running: bool) -> None:
        self._btn_main._text = "Пауза" if running else "Старт"
        self._btn_main._draw()

    def set_compact(self, compact: bool) -> None:
        self._layout_buttons(running=compact)

    def _tick(self) -> None:
        if not self._running or self._remaining <= 0:
            return
        self._remaining -= 1
        self._label.config(text=_format_mmss(self._remaining))
        if self._total_seconds > 0:
            self._progress_var.set(100.0 * self._remaining / self._total_seconds)
        if self._remaining <= 0:
            self._running = False
            self._layout_buttons(running=False)
            self._on_run_state(False)
            self._on_finish(self._phase)
            # Switch to other mode with full duration so user can press Start
            cfg = self._get_config()
            if self._phase == WORK:
                self._selected_mode = BREAK
                self._phase = BREAK
                self._remaining = cfg["break_minutes"] * 60
            else:
                self._selected_mode = WORK
                self._phase = WORK
                self._remaining = cfg["work_minutes"] * 60
            self._total_seconds = self._remaining
            self._on_phase(self._phase)
            self._update_tabs_highlight()
            self._label.config(text=_format_mmss(self._remaining))
            self._progress_var.set(100.0)
            return
        self._after_id = self._label.after(1000, self._tick)

    def _on_start(self) -> None:
        if self._remaining <= 0:
            cfg = self._get_config()
            if self._selected_mode == WORK:
                self._remaining = cfg["work_minutes"] * 60
                self._phase = WORK
            else:
                self._remaining = cfg["break_minutes"] * 60
                self._phase = BREAK
            self._on_phase(self._phase)
        self._total_seconds = self._remaining
        self._progress_var.set(100.0)
        self._running = True
        self._layout_buttons(running=True)
        self._on_run_state(True)
        self._after_id = self._label.after(1000, self._tick)

    def _on_pause(self) -> None:
        self._running = False
        if self._after_id is not None:
            self._label.after_cancel(self._after_id)
            self._after_id = None
        self._layout_buttons(running=False)
        self._on_run_state(False)

    def _on_reset(self) -> None:
        self._on_pause()
        self.reset_to_work()

    def reset_to_work(self) -> None:
        self._selected_mode = WORK
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Update displayed time from config according to current selected mode."""
        cfg = self._get_config()
        if self._selected_mode == WORK:
            self._remaining = cfg["work_minutes"] * 60
            self._phase = WORK
        else:
            self._remaining = cfg["break_minutes"] * 60
            self._phase = BREAK
        self._total_seconds = self._remaining
        self._on_phase(self._phase)
        self._label.config(text=_format_mmss(self._remaining))
        self._progress_var.set(100.0)
        self._layout_buttons(running=False)

    def refresh_display(self) -> None:
        """Public: apply current work/break settings to display when not running."""
        if not self._running:
            self._refresh_display()

    def start_break(self) -> None:
        """Switch to break mode with full duration (e.g. after work finishes)."""
        cfg = self._get_config()
        self._selected_mode = BREAK
        self._remaining = cfg["break_minutes"] * 60
        self._total_seconds = self._remaining
        self._phase = BREAK
        self._on_phase(BREAK)
        self._update_tabs_highlight()
        self._label.config(text=_format_mmss(self._remaining))
        self._progress_var.set(100.0)
        self._layout_buttons(running=False)

    def apply_theme(self, colors: dict) -> None:
        self._last_theme = dict(colors)
        bg = str(colors.get("bg", "#f0f0f0"))
        fg = str(colors.get("fg", "#1a1a1a"))
        self._label.config(bg=bg, fg=fg)
        frame = self._label.master
        if isinstance(frame, tk.Frame):
            frame.config(bg=bg)
        if hasattr(self, "_btn_frame"):
            self._btn_frame["bg"] = bg
        if hasattr(self, "_tabs_frame"):
            self._tabs_frame["bg"] = bg
        if hasattr(self, "_big_btn_frame"):
            self._big_btn_frame["bg"] = bg
        self._btn_main.apply_theme(colors)
        self._update_tabs_highlight()
        style = ttk.Style()
        pb = str(colors.get("progress_bg", "#e0e0e0"))
        pf = str(colors.get("progress_fg", "#4caf50"))
        style.configure(
            "TProgressbar", background=pb, troughcolor=pb, darkcolor=pf, lightcolor=pf
        )

    @property
    def frame(self) -> tk.Misc:
        return self._label.master

    def is_running(self) -> bool:
        return self._running

    def get_phase(self) -> str:
        return self._phase

    def set_selected_mode(self, mode: str) -> None:
        """Set selected mode (work/break) from outside, e.g. when editing time fields."""
        self._select_mode(mode)

    def start(self) -> None:
        """Start or resume timer (for hotkeys)."""
        self._on_start()

    def pause(self) -> None:
        """Pause timer (for hotkeys)."""
        self._on_pause()

    def reset(self) -> None:
        """Reset timer (for hotkeys)."""
        self._on_reset()


# [END SPEC:POMODORO-1:TIMER]
# [END SPEC:POMODORO-2:TIMER]
