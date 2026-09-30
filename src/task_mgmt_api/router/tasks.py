from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.task_mgmt_api.schema.tasks import TaskCreate, TaskResponse 
from src.task_mgmt_api.database import get_session
from src.task_mgmt_api.repository.task import create_task as create_task_repo

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse)
async def create_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
    return await create_task_repo(task, session)
