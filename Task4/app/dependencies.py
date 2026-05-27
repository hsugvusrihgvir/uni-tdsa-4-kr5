from fastapi import Header, HTTPException, Depends

from .storage import tasks


def get_current_user(x_user_id: str | None = Header(default=None),
                     x_user_role: str = Header(default="user")) -> dict:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "id": user_id,
        "role": x_user_role
    }

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user

def get_storage() -> list:
    return tasks
