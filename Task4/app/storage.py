from fastapi import HTTPException

from .schemas import TaskDB, Task

tasks = []
next_id = 1



def create_task(task: Task, owner_id: int) -> TaskDB:
    global next_id

    t = TaskDB(id=next_id,
               title=task.title,
               description=task.description,
               status=task.status,
               priority=task.priority,
               owner_id=owner_id)
    tasks.append(t)
    next_id += 1
    return t

def my_tasks(user_id: int,
             status: str | None = None,
             min_priority: int | None = None) -> list[TaskDB]:
    result = []

    for task in tasks:
        if task.owner_id != user_id:
            continue
        if status is not None and task.status != status:
            continue
        if min_priority is not None and task.priority < min_priority:
            continue
        result.append(task)

    return result
def get_my_task(task_id: int, user_id: int) -> TaskDB | None:
    for task in tasks:
        if task.id == task_id and task.owner_id == user_id:
            return task

def change_status(task_id: int, user_id: int, status: str) -> TaskDB | None:
    for task in tasks:
        if task.id == task_id and task.owner_id == user_id:
            task.status = status
            return task

def delete_task_from_db(task_id: int, user_id: int) -> None:
    for task in tasks:
        if task.id == task_id and task.owner_id == user_id:
            tasks.remove(task)
            return
    raise HTTPException(status_code=404, detail="Task not found")

def delete_any_task(task_id: int) -> None:
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return
    raise HTTPException(status_code=404, detail="Task not found")

def get_stats() -> dict:
    by_status = {
        "todo": 0,
        "in_progress": 0,
        "done": 0
    }

    for task in tasks:
        by_status[task.status] += 1

    return {
        "total_tasks": len(tasks),
        "by_status": by_status
    }

def clear_tasks() -> None:
    global next_id

    tasks.clear()
    next_id = 1
