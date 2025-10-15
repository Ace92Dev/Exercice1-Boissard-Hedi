from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .controller import TaskController
from .utils import TaskNotFoundError, ValidationError
from .view import print_error, print_stats, print_success, print_task, print_task_list


def _parse_tags(raw: Optional[str]) -> Optional[List[str]]:
    if raw is None:
        return None
    if raw.strip() == "":
        return []
    return [t.strip() for t in raw.split(",") if t.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Mini ToDo CLI (MVC). Use subcommands for actions.",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("--title", "-t", required=True, help="Task title")
    p_add.add_argument("--desc", "-d", default=None, help="Task description")
    p_add.add_argument("--priority", "-p", choices=["LOW", "MEDIUM", "HIGH"], default=None, help="Priority")
    p_add.add_argument("--due", default=None, help="Due date (YYYY-MM-DD[ HH:MM])")
    p_add.add_argument("--tags", default=None, help="Comma-separated tags")

    # list
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--status", choices=["PENDING", "IN_PROGRESS", "DONE"], default=None)
    p_list.add_argument("--priority", choices=["LOW", "MEDIUM", "HIGH"], default=None)
    p_list.add_argument("--tag", default=None)
    p_list.add_argument("--overdue", action="store_true")
    p_list.add_argument("--search", default=None)
    p_list.add_argument("--sort", choices=["id", "created", "priority", "due", "title"], default=None)

    # get
    p_get = sub.add_parser("get", help="Show a task by id")
    p_get.add_argument("id", type=int)

    # update
    p_up = sub.add_parser("update", help="Update a task by id")
    p_up.add_argument("id", type=int)
    p_up.add_argument("--title", default=None)
    p_up.add_argument("--desc", default=None)
    p_up.add_argument("--priority", choices=["LOW", "MEDIUM", "HIGH"], default=None)
    p_up.add_argument("--due", default=None, help="Set due date (or empty string to clear)")
    p_up.add_argument("--status", choices=["PENDING", "IN_PROGRESS", "DONE"], default=None)
    p_up.add_argument("--tags", default=None, help="Comma-separated tags (replaces existing)")

    # complete
    p_done = sub.add_parser("complete", help="Mark task as DONE")
    p_done.add_argument("id", type=int)

    # set-status
    p_set = sub.add_parser("set-status", help="Set status explicitly")
    p_set.add_argument("id", type=int)
    p_set.add_argument("status", choices=["PENDING", "IN_PROGRESS", "DONE"])

    # delete
    p_del = sub.add_parser("delete", help="Delete a task by id")
    p_del.add_argument("id", type=int)

    # clear
    p_clear = sub.add_parser("clear", help="Remove all tasks")
    p_clear.add_argument("--yes", action="store_true", help="Confirm deletion of all tasks")

    # stats
    sub.add_parser("stats", help="Show task statistics")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    controller = TaskController()

    try:
        if args.cmd == "add":
            task = controller.create(
                title=args.title,
                description=args.desc,
                priority=args.priority,
                due=args.due,
                tags=_parse_tags(args.tags),
            )
            print_success(f"Created task #{task.id}")
            print_task(task)
            return 0

        if args.cmd == "list":
            tasks = controller.list(
                status=args.status,
                priority=args.priority,
                tag=args.tag,
                overdue=args.overdue,
                search=args.search,
                sort=args.sort,
            )
            print_task_list(tasks)
            return 0

        if args.cmd == "get":
            task = controller.get(args.id)
            print_task(task)
            return 0

        if args.cmd == "update":
            task = controller.update(
                args.id,
                title=args.title,
                description=args.desc,
                priority=args.priority,
                due=args.due,
                status=args.status,
                tags=_parse_tags(args.tags),
            )
            print_success(f"Updated task #{task.id}")
            print_task(task)
            return 0

        if args.cmd == "complete":
            task = controller.complete(args.id)
            print_success(f"Completed task #{task.id}")
            print_task(task)
            return 0

        if args.cmd == "set-status":
            task = controller.set_status(args.id, args.status)
            print_success(f"Set status for task #{task.id}")
            print_task(task)
            return 0

        if args.cmd == "delete":
            ok = controller.delete(args.id)
            if ok:
                print_success(f"Deleted task #{args.id}")
                return 0
            else:
                print_error(f"Task #{args.id} not found")
                return 1

        if args.cmd == "clear":
            if not args.yes:
                print_error("Refusing to clear without --yes")
                return 2
            controller.clear()
            print_success("Cleared all tasks")
            return 0

        if args.cmd == "stats":
            s = controller.stats()
            print_stats(s)
            return 0

        parser.print_help()
        return 1

    except ValidationError as e:
        print_error(str(e))
        return 2
    except TaskNotFoundError as e:
        print_error(str(e))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

