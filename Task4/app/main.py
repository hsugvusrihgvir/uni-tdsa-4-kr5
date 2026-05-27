from fastapi import FastAPI

from .routers import tasks, users, admin

app = FastAPI()

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)
