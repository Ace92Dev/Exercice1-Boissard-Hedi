from __future__ import annotations

from typing import Iterable, List, Optional

from ..models import Task
from ..service import TaskService


class TaskController:
    """Controller mediating between CLI and service layer."""

    def __init__(self, service: Optional[TaskService] = None) -> None:
        self.service = service or TaskService()

    # Actions
    def create(self, *, title: str, description: Optional[str], priority: Optional[str], due: Optional[str], tags: Optional[Iterable[str]]) -> Task:
        return self.service.create_task(title=title, description=description, priority=priority, due=due, tags=tags)

    def list(self, *, status: Optional[str], priority: Optional[str], tag: Optional[str], overdue: bool, search: Optional[str], sort: Optional[str]) -> List[Task]:
        return self.service.list_tasks(status=status, priority=priority, tag=tag, overdue=overdue, search=search, sort=sort)

    def get(self, task_id: int) -> Task:
        return self.service.get_task(task_id)

    def update(self, task_id: int, *, title: Optional[str], description: Optional[str], priority: Optional[str], due: Optional[str], status: Optional[str], tags: Optional[Iterable[str]]) -> Task:
        return self.service.update_task(task_id, title=title, description=description, priority=priority, due=due, status=status, tags=tags)

    def set_status(self, task_id: int, status: str) -> Task:
        return self.service.set_status(task_id, status)

    def complete(self, task_id: int) -> Task:
        return self.service.complete_task(task_id)

    def delete(self, task_id: int) -> bool:
        return self.service.delete_task(task_id)

    def clear(self) -> None:
        return self.service.clear_tasks()

    def stats(self) -> dict:
        return self.service.stats()

