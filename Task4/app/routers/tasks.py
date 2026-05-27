from fastapi import APIRouter, Depends, HTTPException

from ..schemas import Task, TaskDB, TaskStatus
from ..dependencies import get_current_user, get_storage
from ..storage import create_task, my_tasks, get_my_task, change_status, delete_task_from_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskDB, status_code=201)
async def create_tasks(task: Task,
                       user: dict = Depends(get_current_user),
                       storage: list = Depends(get_storage)) -> TaskDB:
    return create_task(task, user["id"])

@router.get("", response_model=list[TaskDB], status_code=200)
async def get_tasks(status: str | None = None,
                    min_priority: int | None = None,
                    user: dict = Depends(get_current_user),
                    storage: list = Depends(get_storage)) -> list[TaskDB]:
    return my_tasks(user["id"], status, min_priority)

@router.get("/{task_id}", response_model=TaskDB, status_code=200)
async def get_task(task_id: int,
                   user: dict = Depends(get_current_user),
                   storage: list = Depends(get_storage)) -> TaskDB:
    t = get_my_task(task_id, user["id"])
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t

@router.patch("/{task_id}/status", response_model=TaskDB, status_code=200)
async def patch_task(task_id: int,
                     status: TaskStatus,
                     user: dict = Depends(get_current_user),
                     storage: list = Depends(get_storage)) -> TaskDB:
    task = change_status(task_id, user["id"], str(status.status))
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int,
                      user: dict = Depends(get_current_user),
                      storage: list = Depends(get_storage)):
    delete_task_from_db(task_id, user["id"])
