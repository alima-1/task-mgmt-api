from src.task_mgmt_api.model.task import Task
from src.task_mgmt_api.schema.tasks import TaskCreate
from src.task_mgmt_api.database import get_session

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def create_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
    new_task = Task(**task.model_dump())
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return new_task