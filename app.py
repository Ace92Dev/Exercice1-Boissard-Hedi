from __future__ import annotations

from flask import Flask, jsonify, request

from .controller import TaskController, TaskNotFoundError, ValidationError
from .models import Task


def task_to_json(t: Task) -> dict:
    return t.to_dict()


app = Flask(__name__)
controller = TaskController()


@app.get("/health")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@app.get("/tasks")
def list_tasks():
    args = request.args
    tasks = controller.list(
        status=args.get("status"),
        priority=args.get("priority"),
        tag=args.get("tag"),
        overdue=(args.get("overdue", "false").lower() in ("1", "true", "yes", "on")),
        search=args.get("search"),
        sort=args.get("sort"),
    )
    return jsonify([task_to_json(t) for t in tasks])


@app.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    task = controller.create(
        title=data.get("title", ""),
        description=data.get("description"),
        priority=data.get("priority"),
        due=data.get("due"),
        tags=(data.get("tags") if isinstance(data.get("tags"), list) else None),
    )
    return task_to_json(task), 201


@app.get("/tasks/<int:task_id>")
def get_task(task_id: int):
    task = controller.get(task_id)
    return task_to_json(task)


@app.patch("/tasks/<int:task_id>")
def update_task(task_id: int):
    data = request.get_json(silent=True) or {}
    tags = data.get("tags")
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    elif not isinstance(tags, list):
        tags = None
    task = controller.update(
        task_id,
        title=data.get("title"),
        description=data.get("description"),
        priority=data.get("priority"),
        due=data.get("due"),
        status=data.get("status"),
        tags=tags,
    )
    return task_to_json(task)


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    ok = controller.delete(task_id)
    return ("", 204) if ok else (jsonify({"error": "not found"}), 404)


@app.post("/tasks/<int:task_id>/complete")
def complete_task(task_id: int):
    task = controller.complete(task_id)
    return task_to_json(task)


@app.post("/tasks/<int:task_id>/status")
def set_status(task_id: int):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    task = controller.set_status(task_id, status)
    return task_to_json(task)


@app.delete("/tasks")
def clear_tasks():
    if (request.args.get("confirm") or "").lower() != "yes":
        return {"error": "Set ?confirm=yes to clear all tasks"}, 400
    controller.clear()
    return "", 204


@app.get("/stats")
def stats():
    return controller.stats()


@app.errorhandler(ValidationError)
def handle_validation(err: ValidationError):  # type: ignore[override]
    return {"error": str(err)}, 400


@app.errorhandler(TaskNotFoundError)
def handle_not_found(err: TaskNotFoundError):  # type: ignore[override]
    return {"error": str(err)}, 404


if __name__ == "__main__":
    app.run(debug=True)

