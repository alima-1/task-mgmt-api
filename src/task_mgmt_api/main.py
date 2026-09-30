from contextlib import asynccontextmanager
from src.task_mgmt_api.database import init_db, close_db
from fastapi import FastAPI

from .router.tasks import router as tasks_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    await close_db()    

app = FastAPI(title="Task Management API", version="1.0.0", lifespan=lifespan)
app.include_router(tasks_router)