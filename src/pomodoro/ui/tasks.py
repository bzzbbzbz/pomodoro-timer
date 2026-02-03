"""Tasks: plain multiline input, parse on save; clipboard; progress bar; theme."""
# [START SPEC:POMODORO-1:TASKS]
# [START SPEC:POMODORO-2:TASKS]
# req_refs: REQ-POMODORO-2-02

import tkinter as tk
from tkinter import ttk
from typing import Callable


def _tasks_to_text(tasks: list[dict]) -> str:
    """Serialize tasks to multiline: '+ ' prefix if done, else plain text."""
    lines: list[str] = []
    for t in tasks:
        text = t.get("text", "")
        if t.get("done", False):
            lines.append("+ " + text)
        else:
            lines.append(text)
    return "\n".join(lines)


def _text_to_tasks(text: str) -> list[dict]:
    """Parse multiline text: line starting with '+' = done."""
    tasks: list[dict] = []
    for line in text.splitlines():
        raw = line.rstrip("\n\r")
        if raw.lstrip().startswith("+"):
            rest = raw.lstrip("+ \t")
            tasks.append({"text": rest, "done": True})
        else:
            tasks.append({"text": raw, "done": False})
    return tasks


def _first_active_task_index(tasks: list[dict]) -> int | None:
    """First task that is not done and has non-empty text. Empty lines (empty text) ignored."""
    for i, t in enumerate(tasks):
        if t.get("done", False):
            continue
        if (t.get("text", "") or "").strip():
            return i
    return None


class TasksWidget:
    """
    Plain multi-line Text: free input; parsing to tasks only on save/load.
    Clipboard: Ctrl+C / Ctrl+V / Ctrl+X. Progress bar = completed/total.
    """

    def __init__(
        self,
        parent: tk.Misc,
        config: dict,
        save_callback: Callable[[], None],
        on_active_changed: Callable[[], None],
    ) -> None:
        self._config = config
        self._save = save_callback
        self._on_active = on_active_changed

        frame = tk.LabelFrame(
            parent,
            text="Задачи — каждая строка = задача, в начале '+' = выполнено",
            padx=4,
            pady=4,
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self._text = tk.Text(
            frame, height=8, font=("Segoe UI", 10), wrap=tk.WORD, undo=True
        )
        self._text.pack(fill=tk.BOTH, expand=True, pady=2)
        self._text.bind("<KeyRelease>", self._on_edit)
        self._text.bind("<FocusOut>", lambda e: self._sync_to_config())
        self._text.bind("<<Modified>>", self._on_modified)
        self._text.bind(
            "<ButtonRelease-1>", lambda e: self._update_active_and_progress()
        )
        self._text.bind("<Control-KeyPress>", self._on_control_key)

        prog_frame = tk.Frame(frame)
        prog_frame.pack(fill=tk.X, pady=4)
        self._progress_var = tk.DoubleVar(value=0.0)
        self._progress_bar = ttk.Progressbar(
            prog_frame, variable=self._progress_var, maximum=100
        )
        self._progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self._progress_label = tk.Label(prog_frame, text="0/0", font=("Segoe UI", 9))
        self._progress_label.pack(side=tk.RIGHT)

        self._frame = frame
        self._sync_from_config()

    def _on_modified(self, _event: tk.Event) -> None:
        if self._text.edit_modified():
            self._text.edit_modified(False)
            self._sync_to_config()

    def _on_edit(self, _event: tk.Event) -> None:
        self._update_active_and_progress()

    def _on_control_key(self, event: tk.Event) -> str | None:
        """Ctrl+C/V/X/Z/A by keycode so they work on Russian layout."""
        if not (getattr(event, "state", 0) & 0x4):
            return None
        keycode = getattr(event, "keycode", None)
        if keycode == 67:
            self._text.event_generate("<<Copy>>")
            return "break"
        if keycode == 86:
            self._text.event_generate("<<Paste>>")
            return "break"
        if keycode == 88:
            self._text.event_generate("<<Cut>>")
            return "break"
        if keycode == 90:
            self._text.event_generate("<<Undo>>")
            return "break"
        if keycode == 65:
            self._text.tag_add(tk.SEL, "1.0", "end-1c")
            self._text.mark_set(tk.INSERT, "1.0")
            return "break"
        return None

    def sync_to_config(self) -> None:
        """Parse text into config and save. Call on FocusOut or before close."""
        self._sync_to_config()

    def _sync_from_config(self) -> None:
        tasks = self._config.get("tasks", [])
        self._text.delete("1.0", tk.END)
        self._text.insert("1.0", _tasks_to_text(tasks))
        self._update_progress_display()

    def _sync_to_config(self) -> None:
        raw = self._text.get("1.0", tk.END)
        tasks = _text_to_tasks(raw)
        self._config["tasks"] = tasks
        idx = _first_active_task_index(tasks)
        self._config["active_task_index"] = idx
        self._save()
        self._update_progress_display()
        self._on_active()

    def _update_active_and_progress(self) -> None:
        raw = self._text.get("1.0", tk.END)
        tasks = _text_to_tasks(raw)
        self._config["tasks"] = tasks
        idx = _first_active_task_index(tasks)
        self._config["active_task_index"] = idx
        self._update_progress_display()
        self._on_active()

    def _update_progress_display(self) -> None:
        tasks = self._config.get("tasks", [])
        total = len(tasks)
        done = sum(1 for t in tasks if t.get("done", False))
        if total > 0:
            self._progress_var.set(100.0 * done / total)
            self._progress_label.config(text=f"{done}/{total}")
        else:
            self._progress_var.set(0.0)
            self._progress_label.config(text="0/0")

    def get_active_text(self) -> str:
        tasks = self._config.get("tasks", [])
        idx = _first_active_task_index(tasks)
        if idx is not None and 0 <= idx < len(tasks):
            return tasks[idx].get("text", "")
        return ""

    def apply_theme(self, colors: dict) -> None:
        fb = str(colors.get("frame_bg", "#f5f5f5"))
        fg = str(colors.get("fg", "#1a1a1a"))
        eb = str(colors.get("entry_bg", "#ffffff"))
        sb = str(colors.get("select_bg", "#b0d4f1"))
        sf = str(colors.get("select_fg", "#1a1a1a"))
        fdim = str(colors.get("fg_dim", "#666666"))
        self._frame.config(bg=fb, fg=fg)
        self._text.config(
            bg=eb, fg=fg, insertbackground=fg, selectbackground=sb, selectforeground=sf
        )
        self._progress_label.config(bg=fb, fg=fdim)

    def contains_focus(self, root: tk.Misc) -> bool:
        """True if keyboard focus is inside the tasks text widget (do not trigger hotkeys)."""
        try:
            return root.focus_get() == self._text
        except (tk.TclError, AttributeError):
            return False

    def contains_widget(self, widget: tk.Misc) -> bool:
        """True if widget is the tasks text or inside the tasks frame (do not steal focus)."""
        try:
            w = widget
            while w:
                if w == self._text or w == self._frame:
                    return True
                w = w.master
        except (tk.TclError, AttributeError):
            pass
        return False

    @property
    def frame(self) -> tk.Misc:
        return self._frame


# [END SPEC:POMODORO-1:TASKS]
# [END SPEC:POMODORO-2:TASKS]
