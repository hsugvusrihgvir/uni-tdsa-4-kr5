from fastapi import APIRouter, Depends

from ..dependencies import require_admin, get_storage
from ..storage import get_stats, delete_any_task

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def stats(user: dict = Depends(require_admin),
                storage: list = Depends(get_storage)) -> dict:
    return get_stats()

@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int,
                      user: dict = Depends(require_admin),
                      storage: list = Depends(get_storage)):
    delete_any_task(task_id)
