from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from ..models import DeadlineTask, Task, TaskPriority, TaskStatus


class ValidationError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


class TaskController:
    """Minimal in-memory controller (no service/repository).

    Implements basic CRUD, filtering and stats using only models.
    """

    def __init__(self) -> None:
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    # --- parsing helpers ---
    @staticmethod
    def _parse_priority(value: Optional[str]) -> TaskPriority:
        if value is None:
            return TaskPriority.MEDIUM
        try:
            return TaskPriority(value.upper())
        except Exception as exc:
            raise ValidationError(f"Invalid priority: {value}") from exc

    @staticmethod
    def _parse_status(value: Optional[str]) -> TaskStatus:
        if value is None:
            return TaskStatus.PENDING
        try:
            return TaskStatus(value.upper())
        except Exception as exc:
            raise ValidationError(f"Invalid status: {value}") from exc

    @staticmethod
    def _parse_due(value: Optional[str]) -> Optional[datetime]:
        if value is None:
            return None
        v = value.strip()
        if v == "":
            return None
        fmts = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
        ]
        for fmt in fmts:
            try:
                return datetime.strptime(v, fmt).astimezone()
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(v).astimezone()
        except Exception as exc:
            raise ValidationError(f"Invalid due date: {value}") from exc

    # --- CRUD/actions ---
    def create(
        self,
        *,
        title: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> Task:
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty")
        prio = self._parse_priority(priority)
        due_dt = self._parse_due(due)
        tag_list = list(tags or [])
        new_id = self._next_id
        self._next_id += 1

        if due_dt is not None:
            task: Task = DeadlineTask(
                id=new_id,
                title=title.strip(),
                description=(description or None),
                priority=prio,
                tags=tag_list,
                due_date=due_dt,
            )
        else:
            task = Task(
                id=new_id,
                title=title.strip(),
                description=(description or None),
                priority=prio,
                tags=tag_list,
            )
        self._tasks[new_id] = task
        return task

    def list(
        self,
        *,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
        overdue: bool = False,
        search: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> List[Task]:
        tasks = list(self._tasks.values())

        if status:
            st = self._parse_status(status)
            tasks = [t for t in tasks if t.status == st]
        if priority:
            pr = self._parse_priority(priority)
            tasks = [t for t in tasks if t.priority == pr]
        if tag:
            tasks = [t for t in tasks if tag in (t.tags or [])]
        if search:
            s = search.lower()
            tasks = [
                t
                for t in tasks
                if s in t.title.lower() or (t.description or "").lower().find(s) >= 0
            ]
        if overdue:
            now = datetime.now().astimezone()
            tasks = [
                t
                for t in tasks
                if isinstance(t, DeadlineTask) and t.status != TaskStatus.DONE and t.due_date < now
            ]

        if sort:
            key = sort.lower()
            if key == "id":
                tasks.sort(key=lambda t: t.id)
            elif key == "created":
                tasks.sort(key=lambda t: t.created_at)
            elif key == "priority":
                order = {TaskPriority.HIGH: 0, TaskPriority.MEDIUM: 1, TaskPriority.LOW: 2}
                tasks.sort(key=lambda t: order.get(t.priority, 1))
            elif key == "due":
                def due_key(t: Task):
                    return t.due_date if isinstance(t, DeadlineTask) else datetime.max.replace(tzinfo=t.created_at.tzinfo)

                tasks.sort(key=due_key)
            elif key == "title":
                tasks.sort(key=lambda t: t.title.lower())
            else:
                raise ValidationError(f"Unknown sort key: {sort}")

        return tasks

    def _require(self, task_id: int) -> Task:
        try:
            return self._tasks[int(task_id)]
        except KeyError as exc:
            raise TaskNotFoundError(f"Task #{task_id} not found") from exc

    def get(self, task_id: int) -> Task:
        return self._require(task_id)

    def update(
        self,
        task_id: int,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> Task:
        task = self._require(task_id)
        new_title = title.strip() if title is not None else task.title
        if new_title == "":
            raise ValidationError("Title cannot be empty")
        new_desc = description if description is not None else task.description
        new_prio = self._parse_priority(priority) if priority is not None else task.priority
        new_status = self._parse_status(status) if status is not None else task.status
        new_tags = list(tags) if tags is not None else list(task.tags)

        # handle due date and type switch if needed
        if due is not None:
            due_dt = self._parse_due(due)
            if due_dt is not None and not isinstance(task, DeadlineTask):
                # upgrade to DeadlineTask
                task = DeadlineTask(
                    **{
                        k: getattr(task, k)
                        for k in (
                            "id",
                            "title",
                            "description",
                            "status",
                            "priority",
                            "tags",
                            "created_at",
                        )
                    },
                    due_date=due_dt,
                )
            elif due_dt is None and isinstance(task, DeadlineTask):
                # downgrade to Task (remove due)
                task = Task(
                    **{
                        k: getattr(task, k)
                        for k in (
                            "id",
                            "title",
                            "description",
                            "status",
                            "priority",
                            "tags",
                            "created_at",
                        )
                    }
                )

        # apply field updates
        updated = replace(
            task,
            title=new_title,
            description=new_desc,
            priority=new_prio,
            status=new_status,
            tags=new_tags,
        )
        # apply due change if applicable
        if isinstance(updated, DeadlineTask) and due is not None:
            due_dt = self._parse_due(due)
            if due_dt is not None:
                updated = replace(updated, due_date=due_dt)
        self._tasks[updated.id] = updated
        return updated

    def set_status(self, task_id: int, status: str) -> Task:
        task = self._require(task_id)
        new_status = self._parse_status(status)
        task = replace(task, status=new_status)
        self._tasks[task.id] = task
        return task

    def complete(self, task_id: int) -> Task:
        return self.set_status(task_id, TaskStatus.DONE.value)

    def delete(self, task_id: int) -> bool:
        return self._tasks.pop(int(task_id), None) is not None

    def clear(self) -> None:
        self._tasks.clear()

    def stats(self) -> dict:
        tasks = list(self._tasks.values())
        total = len(tasks)
        by_status = {s.value: 0 for s in TaskStatus}
        by_priority = {p.value: 0 for p in TaskPriority}
        for t in tasks:
            by_status[t.status.value] += 1
            by_priority[t.priority.value] += 1
        return {"total": total, "by_status": by_status, "by_priority": by_priority}

