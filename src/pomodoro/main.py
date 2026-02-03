"""Pomodoro timer application — entry point. [REQ-POMODORO-1-12]"""
# [START SPEC:POMODORO-1:MAIN]
# [START SPEC:POMODORO-2:MAIN]
# req_refs: REQ-POMODORO-2-01, REQ-POMODORO-2-03, REQ-POMODORO-2-04, REQ-POMODORO-2-05

import tkinter as tk

from pomodoro import config
from pomodoro.ui.theme import theme_colors
from pomodoro.ui.timer import TimerWidget, BREAK
from pomodoro.ui.window import set_alpha, setup_overlay
from pomodoro.ui.notify import notify_timer_end
from pomodoro.ui.tasks import TasksWidget
from pomodoro.ui.settings import SettingsWidget

COMPACT_GEOMETRY = "280x220"
FULL_GEOMETRY = "360x680"


def apply_theme(
    root: tk.Tk,
    content: tk.Frame,
    top_section: tk.Frame,
    active_label: tk.Label,
    full_section: tk.Frame,
    timer_widget: TimerWidget,
    tasks_widget: TasksWidget,
    settings_widget: SettingsWidget,
    theme: str,
) -> None:
    colors = theme_colors(theme)
    bg = str(colors.get("bg", "#f0f0f0"))
    fg = str(colors.get("fg", "#1a1a1a"))
    root.configure(bg=bg)
    content["bg"] = bg
    top_section["bg"] = bg
    active_label["bg"] = bg
    active_label["fg"] = fg
    if active_label.master:
        active_label.master["bg"] = bg
    for w in top_section.winfo_children():
        try:
            w["bg"] = bg
        except tk.TclError:
            pass
        for c in w.winfo_children():
            try:
                c["bg"] = bg
            except tk.TclError:
                pass
            if isinstance(c, tk.Label):
                try:
                    c["fg"] = fg
                except tk.TclError:
                    pass
    full_section["bg"] = bg
    timer_widget.apply_theme(colors)
    tasks_widget.apply_theme(colors)
    settings_widget.apply_theme(colors)


def main() -> None:
    """Launch overlay window and run mainloop."""
    cfg = config.load_config()
    root = tk.Tk()

    def save() -> None:
        config.save_config(cfg)

    def on_close() -> None:
        tasks_widget.sync_to_config()
        save()
        root.destroy()

    setup_overlay(root, cfg.get("alpha", 0.85), on_close=on_close)
    root.geometry(FULL_GEOMETRY)
    root.configure(bg=str(theme_colors(cfg.get("theme", "light")).get("bg", "#f0f0f0")))

    content = tk.Frame(root, padx=0, pady=0)
    content.pack(fill=tk.BOTH, expand=True)

    top_section = tk.Frame(content)
    top_section.pack(fill=tk.X)

    header_row = tk.Frame(top_section)
    header_row.pack(fill=tk.X)

    active_frame = tk.Frame(header_row)
    active_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=2)
    _compact_width = 280
    _full_width = 360
    active_label = tk.Label(
        active_frame,
        text="",
        font=("Segoe UI", 10),
        anchor=tk.CENTER,
        justify=tk.CENTER,
        wraplength=_full_width - 16,
    )
    active_label.pack(fill=tk.X, expand=True)

    def get_cfg() -> dict:
        return cfg

    timer_widget: TimerWidget | None = None

    def on_timer_finish(phase: str) -> None:
        notify_timer_end(root)
        # Timer already switched to other mode with full duration in _tick()

    def _geometry_anchor_bottom(geom: str) -> None:
        """Set root geometry keeping bottom edge fixed (shrink from top)."""
        try:
            x, y = root.winfo_x(), root.winfo_y()
            _, h = root.winfo_width(), root.winfo_height()
        except tk.TclError:
            root.geometry(geom)
            return
        parts = geom.split("+")
        size_part = parts[0] if parts else geom
        if "x" in size_part:
            new_w, new_h = map(int, size_part.split("x"))
        else:
            root.geometry(geom)
            return
        new_y = y + h - new_h
        root.geometry(f"{new_w}x{new_h}+{x}+{new_y}")

    def on_run_state_changed(running: bool) -> None:
        if running:
            full_section.pack_forget()
            if timer_widget is not None:
                timer_widget.set_compact(True)
            active_label["wraplength"] = _compact_width - 16
            _geometry_anchor_bottom(COMPACT_GEOMETRY)
        else:
            if timer_widget is not None:
                timer_widget.set_compact(False)
            full_section.pack(fill=tk.BOTH, expand=True)
            active_label["wraplength"] = _full_width - 16
            _geometry_anchor_bottom(FULL_GEOMETRY)

    tasks_ref: list[TasksWidget | None] = [None]

    def on_phase_changed(_phase: str) -> None:
        if _phase == BREAK:
            active_label["text"] = "Перерыв"
        else:
            w = tasks_ref[0]
            active_label["text"] = (w.get_active_text() or "") if w else ""

    timer_widget = TimerWidget(
        top_section,
        get_cfg,
        on_finish=on_timer_finish,
        on_run_state_changed=on_run_state_changed,
        on_phase_changed=on_phase_changed,
    )

    full_section = tk.Frame(content)
    full_section.pack(fill=tk.BOTH, expand=True)

    def on_active_changed() -> None:
        if timer_widget is not None and timer_widget.get_phase() == BREAK:
            active_label["text"] = "Перерыв"
        else:
            t = tasks_widget.get_active_text()
            active_label["text"] = t if t else ""

    tasks_widget = TasksWidget(full_section, cfg, save, on_active_changed)
    tasks_ref[0] = tasks_widget
    on_active_changed()

    def set_alpha_cb(a: float) -> None:
        set_alpha(root, a)

    def on_theme_changed() -> None:
        theme = cfg.get("theme", "light")
        apply_theme(
            root,
            content,
            top_section,
            active_label,
            full_section,
            timer_widget,
            tasks_widget,
            settings_widget,
            theme,
        )
        colors = theme_colors(theme)
        active_label["bg"] = str(colors.get("bg", "#f0f0f0"))
        active_label["fg"] = str(colors.get("fg", "#1a1a1a"))
        if active_label.master:
            active_label.master["bg"] = str(colors.get("bg", "#f0f0f0"))

    def on_work_break_changed() -> None:
        """Apply new work/break minutes to timer display when not running."""
        if timer_widget is not None:
            timer_widget.refresh_display()

    def on_select_mode(mode: str) -> None:
        if timer_widget is not None:
            timer_widget.set_selected_mode(mode)

    settings_widget = SettingsWidget(
        full_section,
        cfg,
        save,
        set_alpha_cb,
        on_theme_changed=on_theme_changed,
        on_work_break_changed=on_work_break_changed,
        on_select_mode=on_select_mode,
    )

    def _on_root_click(event: tk.Event) -> None:
        """Move focus to root when clicking outside entries and tasks (saves values)."""
        w = event.widget
        try:
            if (
                w != settings_widget._work_entry
                and w != settings_widget._break_entry
                and not tasks_widget.contains_widget(w)
            ):
                root.focus_set()
        except (AttributeError, tk.TclError):
            root.focus_set()

    root.bind("<Button-1>", _on_root_click)

    # [START SPEC:POMODORO-3:HOTKEYS]
    # req_refs: REQ-POMODORO-3-01 — only Space for Start/Pause; no R reset
    def _on_hotkey(event: tk.Event) -> None:
        if tasks_widget.contains_focus(root):
            return
        try:
            w = root.focus_get()
            if w in (settings_widget._work_entry, settings_widget._break_entry):
                return
        except (AttributeError, tk.TclError):
            pass
        keycode = getattr(event, "keycode", None)
        keysym = (getattr(event, "keysym", None) or "").lower()
        is_space = keycode == 32 or keysym in ("space",)
        if is_space and timer_widget is not None:
            if timer_widget.is_running():
                timer_widget.pause()
            else:
                timer_widget.start()

    # [END SPEC:POMODORO-3:HOTKEYS]
    root.bind_all("<KeyPress>", _on_hotkey)

    on_theme_changed()

    root.mainloop()


# [END SPEC:POMODORO-1:MAIN]
