import os

from fastapi import FastAPI, Header, Depends
from fastapi import HTTPException

from app.schemas import Task, TaskDB, TaskStatus
from app.db import create_task, my_tasks, get_my_task, change_status, delete_task_from_db

app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "env": os.getenv("APP_ENV", "local")
    }


def get_user(x_user_id: str | None = Header(default=None)) -> int:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Not authenticated")

@app.post("/tasks", response_model=TaskDB, status_code=201)
async def create_tasks(task: Task, x_user_id: int = Depends(get_user)) -> TaskDB:
    return create_task(task, x_user_id)

@app.get("/tasks", response_model=list[TaskDB], status_code=200)
async def get_tasks(status: str | None = None,
                    min_priority: int | None = None,
                    x_user_id: int = Depends(get_user)) -> list[TaskDB]:
    return my_tasks(x_user_id, status, min_priority)

@app.get("/tasks/{task_id}", response_model=TaskDB, status_code=200)
async def get_task(task_id: int, x_user_id: int = Depends(get_user)) -> TaskDB:
    t = get_my_task(task_id, x_user_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t

@app.patch("/tasks/{task_id}/status", response_model=TaskDB, status_code=200)
async def patch_task(task_id: int,
                     status: TaskStatus,
                     x_user_id: int = Depends(get_user)) -> TaskDB:
    task = change_status(task_id, x_user_id, str(status.status))
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int,
                      x_user_id: int = Depends(get_user)):
    delete_task_from_db(task_id, x_user_id)
