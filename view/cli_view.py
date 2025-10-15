from __future__ import annotations

from datetime import datetime
from typing import Iterable

from ..models import DeadlineTask, Task


def _fmt_dt(dt: datetime) -> str:
    try:
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(dt)


def _truncate(text: str, width: int) -> str:
    return (text[: width - 1] + "…") if len(text) > width else text


def print_task(task: Task) -> None:
    due_str = _fmt_dt(task.due_date) if isinstance(task, DeadlineTask) else "-"
    print(
        f"#{task.id} | {task.status:<11} | {task.priority:<6} | due: {due_str} | {task.title}"
    )
    if task.description:
        print(f"    {task.description}")
    if task.tags:
        print(f"    tags: {', '.join(task.tags)}")


def print_task_list(tasks: Iterable[Task]) -> None:
    tasks = list(tasks)
    if not tasks:
        print("No tasks.")
        return
    header = f"{'ID':<4} {'STATUS':<11} {'PRIO':<6} {'DUE':<16} TITLE"
    print(header)
    print("-" * len(header))
    for t in tasks:
        due = _fmt_dt(t.due_date) if isinstance(t, DeadlineTask) else "-"
        title = _truncate(t.title, 60)
        print(f"{t.id:<4} {t.status:<11} {t.priority:<6} {due:<16} {title}")


def print_stats(stats: dict) -> None:
    print(f"Total tasks: {stats.get('total', 0)}")
    print("By status:")
    for k, v in stats.get("by_status", {}).items():
        print(f"  - {k:<12}: {v}")
    print("By priority:")
    for k, v in stats.get("by_priority", {}).items():
        print(f"  - {k:<12}: {v}")


def print_success(message: str) -> None:
    print(message)


def print_error(message: str) -> None:
    print(f"Error: {message}")

