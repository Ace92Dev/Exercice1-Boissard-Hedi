from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    # package root is two levels up from this file
    return Path(__file__).resolve().parents[2]


def get_data_dir() -> Path:
    data_dir = get_project_root() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_data_file() -> Path:
    data_file = get_data_dir() / "tasks.json"
    if not data_file.exists():
        data_file.write_text("[]", encoding="utf-8")
    return data_file

