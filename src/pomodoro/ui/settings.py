"""Settings: alpha, work/break durations, theme toggle; save on change; theme."""
# [START SPEC:POMODORO-1:SETTINGS]
# [START SPEC:POMODORO-2:SETTINGS]
# req_refs: REQ-POMODORO-2-04

import tkinter as tk
from typing import Callable


class SettingsWidget:
    """
    Controls for transparency, timer durations, and theme (light/dark).
    Persists on change. apply_theme(colors) for dark/light.
    """

    def __init__(
        self,
        parent: tk.Misc,
        config: dict,
        save_callback: Callable[[], None],
        set_alpha_callback: Callable[[float], None],
        on_theme_changed: Callable[[], None] | None = None,
        on_work_break_changed: Callable[[], None] | None = None,
        on_select_mode: Callable[[str], None] | None = None,
    ) -> None:
        self._config = config
        self._save = save_callback
        self._set_alpha = set_alpha_callback
        self._on_theme = on_theme_changed or (lambda: None)
        self._on_work_break = on_work_break_changed or (lambda: None)
        self._on_select_mode = on_select_mode or (lambda _: None)

        frame = tk.LabelFrame(parent, text="Настройки", padx=4, pady=4)
        frame.pack(fill=tk.X, padx=8, pady=4)
        self._frame = frame

        # Рабочий интервал и перерыв (сверху)
        row1 = tk.Frame(frame)
        row1.pack(fill=tk.X, pady=2)
        tk.Label(row1, text="Помодоро (мин):", width=14, anchor=tk.W).pack(side=tk.LEFT)
        self._work_var = tk.StringVar(value=str(config.get("work_minutes", 25)))
        work_entry = tk.Entry(row1, textvariable=self._work_var, width=6)
        work_entry.pack(side=tk.LEFT, padx=4)
        work_entry.bind("<FocusOut>", lambda e: self._apply_work_break())
        work_entry.bind("<Return>", lambda e: self._apply_work_break())
        work_entry.bind("<KeyRelease>", lambda e: self._apply_work_break())
        work_entry.bind("<FocusIn>", lambda e: self._on_select_mode("work"))

        tk.Label(row1, text="Перерыв (мин):", anchor=tk.W).pack(
            side=tk.LEFT, padx=(12, 0)
        )
        self._break_var = tk.StringVar(value=str(config.get("break_minutes", 5)))
        break_entry = tk.Entry(row1, textvariable=self._break_var, width=6)
        break_entry.pack(side=tk.LEFT, padx=4)
        break_entry.bind("<FocusOut>", lambda e: self._apply_work_break())
        break_entry.bind("<Return>", lambda e: self._apply_work_break())
        break_entry.bind("<KeyRelease>", lambda e: self._apply_work_break())
        break_entry.bind("<FocusIn>", lambda e: self._on_select_mode("break"))
        self._row1 = row1
        self._work_entry = work_entry
        self._break_entry = break_entry

        # Прозрачность
        row0 = tk.Frame(frame)
        row0.pack(fill=tk.X, pady=2)
        tk.Label(row0, text="Прозрачность:", width=14, anchor=tk.W).pack(side=tk.LEFT)
        alpha_val = config.get("alpha", 0.85)
        self._alpha_var = tk.DoubleVar(value=alpha_val)
        scale = tk.Scale(
            row0,
            from_=0.3,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self._alpha_var,
            command=self._on_alpha,
            length=180,
        )
        scale.pack(side=tk.LEFT, padx=4)
        self._row0 = row0
        self._scale = scale

        # Тема: светлая / тёмная
        row_theme = tk.Frame(frame)
        row_theme.pack(fill=tk.X, pady=2)
        tk.Label(row_theme, text="Тема:", width=14, anchor=tk.W).pack(side=tk.LEFT)
        self._theme_var = tk.StringVar(value=config.get("theme", "light"))
        dark_btn = tk.Radiobutton(
            row_theme,
            text="Тёмная",
            variable=self._theme_var,
            value="dark",
            command=self._on_theme_sel,
        )
        dark_btn.pack(side=tk.LEFT, padx=4)
        light_btn = tk.Radiobutton(
            row_theme,
            text="Светлая",
            variable=self._theme_var,
            value="light",
            command=self._on_theme_sel,
        )
        light_btn.pack(side=tk.LEFT, padx=4)
        self._theme_row = row_theme
        self._theme_btns = [dark_btn, light_btn]

    def _on_theme_sel(self) -> None:
        self._config["theme"] = self._theme_var.get()
        self._save()
        self._on_theme()

    def _on_alpha(self, value: str) -> None:
        a = float(value)
        self._config["alpha"] = a
        self._set_alpha(a)
        self._save()

    def _apply_work_break(self) -> None:
        try:
            w = int(self._work_var.get())
            b = int(self._break_var.get())
            if w >= 1 and b >= 1:
                self._config["work_minutes"] = w
                self._config["break_minutes"] = b
                self._save()
                self._on_work_break()
        except ValueError:
            pass

    def apply_theme(self, colors: dict) -> None:
        bg = str(colors.get("frame_bg", "#f5f5f5"))
        fg = str(colors.get("fg", "#1a1a1a"))
        eb = str(colors.get("entry_bg", "#ffffff"))
        pb = str(colors.get("progress_bg", "#e0e0e0"))
        self._frame["bg"] = bg
        # [START SPEC:POMODORO-3:SETTINGS_FG] req_refs: REQ-POMODORO-3-05
        self._frame["fg"] = fg
        # [END SPEC:POMODORO-3:SETTINGS_FG]
        for w in (self._theme_row, self._row0, self._row1):
            w["bg"] = bg
        for b in self._theme_btns:
            b["bg"] = bg
            b["fg"] = fg
            b["selectcolor"] = bg
        self._scale["bg"] = bg
        self._scale["fg"] = fg
        self._scale["troughcolor"] = pb
        self._work_entry.config(bg=eb, fg=fg, insertbackground=fg)
        self._break_entry.config(bg=eb, fg=fg, insertbackground=fg)
        for row in (self._theme_row, self._row0, self._row1):
            for c in row.winfo_children():
                if isinstance(c, tk.Label):
                    c["bg"] = bg
                    c["fg"] = fg


# [END SPEC:POMODORO-1:SETTINGS]
# [END SPEC:POMODORO-2:SETTINGS]
