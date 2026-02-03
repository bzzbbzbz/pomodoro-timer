"""Config and tasks load/save. [REQ-POMODORO-1-03], [REQ-POMODORO-1-11]"""
# [START SPEC:POMODORO-1:CONFIG]
# req_refs: REQ-POMODORO-1-03, REQ-POMODORO-1-11

import sys
from pathlib import Path
from typing import Any

from pomodoro.ui.tasks import _tasks_to_text, _text_to_tasks

CONFIG_FILENAME = "config.json"
TASKS_FILENAME = "tasks.txt"


def get_base_dir() -> Path:
    """Base directory: same folder as exe when frozen, else project root (parent of src)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    # Running as script: src/pomodoro/config.py -> project root = parent of src
    return Path(__file__).resolve().parent.parent.parent


def get_config_path() -> Path:
    """Path to config.json in base dir. Creates base dir if missing."""
    base = get_base_dir()
    base.mkdir(parents=True, exist_ok=True)
    return base / CONFIG_FILENAME


def get_tasks_path() -> Path:
    """Path to tasks.txt in base dir."""
    return get_base_dir() / TASKS_FILENAME


def _default_settings() -> dict[str, Any]:
    """Settings only (no tasks)."""
    return {
        "alpha": 0.85,
        "work_minutes": 25,
        "break_minutes": 5,
        "theme": "light",
        "active_task_index": None,
    }


def _validate_settings(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize settings from config.json."""
    default = _default_settings()
    out: dict[str, Any] = {}
    out["alpha"] = float(data.get("alpha", default["alpha"]))
    out["alpha"] = max(0.3, min(1.0, out["alpha"]))
    out["work_minutes"] = max(1, int(data.get("work_minutes", default["work_minutes"])))
    out["break_minutes"] = max(1, int(data.get("break_minutes", default["break_minutes"])))
    out["theme"] = "dark" if data.get("theme") == "dark" else "light"
    out["active_task_index"] = data.get("active_task_index")
    return out


def load_config() -> dict[str, Any]:
    """
    Load settings from config.json and tasks from tasks.txt.
    If config.json is missing, create it with defaults. Tasks from tasks.txt or [].
    Post: returns dict with alpha, work_minutes, break_minutes, theme, active_task_index, tasks.
    """
    import json

    base = get_base_dir()
    base.mkdir(parents=True, exist_ok=True)
    config_path = base / CONFIG_FILENAME
    tasks_path = base / TASKS_FILENAME

    # Settings
    if not config_path.exists():
        config_path.write_text(
            json.dumps(_default_settings(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    try:
        settings = _validate_settings(
            json.loads(config_path.read_text(encoding="utf-8"))
        )
    except (OSError, ValueError):
        settings = _default_settings()

    # Tasks
    if tasks_path.exists():
        try:
            tasks = _text_to_tasks(tasks_path.read_text(encoding="utf-8"))
        except OSError:
            tasks = []
    else:
        tasks = []

    # Clamp active_task_index to tasks length
    ai = settings.get("active_task_index")
    if ai is None:
        active_idx: int | None = None
    else:
        idx = int(ai)
        active_idx = idx if 0 <= idx < len(tasks) else None
    settings["active_task_index"] = active_idx

    return {**settings, "tasks": tasks}


def save_config(data: dict[str, Any]) -> None:
    """
    Save settings to config.json (no tasks) and tasks to tasks.txt.
    Pre: data has keys alpha, work_minutes, break_minutes, theme, active_task_index, tasks.
    """
    import json

    base = get_base_dir()
    base.mkdir(parents=True, exist_ok=True)
    config_path = base / CONFIG_FILENAME
    tasks_path = base / TASKS_FILENAME

    settings = {
        "alpha": data.get("alpha", 0.85),
        "work_minutes": data.get("work_minutes", 25),
        "break_minutes": data.get("break_minutes", 5),
        "theme": data.get("theme", "light"),
        "active_task_index": data.get("active_task_index"),
    }
    config_path.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    tasks = data.get("tasks", [])
    tasks_path.write_text(_tasks_to_text(tasks), encoding="utf-8")


# [END SPEC:POMODORO-1:CONFIG]
