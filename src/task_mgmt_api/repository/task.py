import datetime
from select import select

from src.task_mgmt_api.model.task import Task
from src.task_mgmt_api.schema.tasks import TaskCreate
from src.task_mgmt_api.database import get_session

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def create_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
    new_task = Task(**task.model_dump())
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return new_task


async def get_task_by_name_and_due_date(name: str, due_date: datetime, session: AsyncSession = Depends(get_session)):
    existing_task = await session.scalar(
        select(Task).where(Task.name == name, Task.due_date == due_date)
    )
    return existing_task