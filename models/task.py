from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type


ISO_FMT = "%Y-%m-%dT%H:%M:%S%z"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class Task:
    """Base Task model.

    Serves as the parent class for more specific task types.
    """

    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now().astimezone())

    TYPE: str = "Task"  # discriminator for (de)serialization

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.strftime(ISO_FMT)
        d["status"] = str(self.status)
        d["priority"] = str(self.priority)
        d["type"] = self.TYPE
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        task_type = data.get("type", "Task")
        klass: Type[Task] = Task if task_type == "Task" else DeadlineTask

        common = {
            "id": int(data["id"]),
            "title": str(data["title"]),
            "description": data.get("description"),
            "status": TaskStatus(data.get("status", TaskStatus.PENDING)),
            "priority": TaskPriority(data.get("priority", TaskPriority.MEDIUM)),
            "tags": list(data.get("tags", [])),
            "created_at": _parse_dt(data.get("created_at")),
        }

        if klass is Task:
            return Task(**common)
        else:
            due = _parse_dt(data.get("due_date"))
            return DeadlineTask(due_date=due, **common)

    def short_str(self) -> str:
        return f"#{self.id} [{self.priority}] {self.title} ({self.status})"


@dataclass
class DeadlineTask(Task):
    """Task with a due date."""

    due_date: datetime = field(default_factory=lambda: datetime.now().astimezone())

    TYPE: str = "DeadlineTask"

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["due_date"] = self.due_date.strftime(ISO_FMT)
        d["type"] = self.TYPE
        return d


def _parse_dt(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now().astimezone()
    try:
        # Accept both with and without timezone
        try:
            return datetime.strptime(value, ISO_FMT)
        except ValueError:
            # Try naive input and assume local timezone
            return datetime.fromisoformat(value)
    except Exception:
        return datetime.now().astimezone()

