from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from ..models import Task
from ..utils import TaskNotFoundError, get_data_file


class TaskRepository:
    """JSON-backed repository for tasks."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or get_data_file()

    # --- raw IO ---
    def _read_all_raw(self) -> List[Dict]:
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8") or "[]")
            if not isinstance(raw, list):
                return []
            return raw
        except json.JSONDecodeError:
            return []

    def _write_all_raw(self, items: List[Dict]) -> None:
        self.path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- public API ---
    def list_all(self) -> List[Task]:
        return [Task.from_dict(d) for d in self._read_all_raw()]

    def get(self, task_id: int) -> Task:
        for d in self._read_all_raw():
            if int(d.get("id")) == int(task_id):
                return Task.from_dict(d)
        raise TaskNotFoundError(f"Task #{task_id} not found")

    def add(self, task: Task) -> Task:
        items = self._read_all_raw()
        items.append(task.to_dict())
        self._write_all_raw(items)
        return task

    def update(self, task: Task) -> Task:
        items = self._read_all_raw()
        for i, d in enumerate(items):
            if int(d.get("id")) == int(task.id):
                items[i] = task.to_dict()
                self._write_all_raw(items)
                return task
        raise TaskNotFoundError(f"Task #{task.id} not found")

    def delete(self, task_id: int) -> bool:
        items = self._read_all_raw()
        new_items = [d for d in items if int(d.get("id")) != int(task_id)]
        if len(new_items) == len(items):
            return False
        self._write_all_raw(new_items)
        return True

    def clear(self) -> None:
        self._write_all_raw([])

    def next_id(self) -> int:
        items = self._read_all_raw()
        try:
            return max(int(d.get("id", 0)) for d in items) + 1
        except ValueError:
            return 1

