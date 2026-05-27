from pydantic import BaseModel, constr, conint
from typing import Literal

st = Literal["todo", "in_progress", "done"]

class Task(BaseModel):
    title: constr(min_length=3, max_length=80)
    description: str | None = None
    status: st
    priority: conint(ge=1, le=5)


class TaskDB(Task):
    id: int
    owner_id: int

class TaskStatus(BaseModel):
    status: st
