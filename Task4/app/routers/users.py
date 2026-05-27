from fastapi import APIRouter, Depends

from ..dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)) -> dict:
    return user

@router.get("/{user_id}")
async def get_user(user_id: int,
                   user: dict = Depends(get_current_user)) -> dict:
    return {
        "id": user_id
    }
