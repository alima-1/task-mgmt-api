from contextlib import asynccontextmanager
from src.task_mgmt_api.database import init_db, close_db
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .router.tasks import router as tasks_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    await close_db()    

app = FastAPI(title="Task Management API", version="1.0.0", lifespan=lifespan)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    return JSONResponse(status_code=409, content={"detail": "Task already exists or violates data constraints"})


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Database error"})


app.include_router(tasks_router)