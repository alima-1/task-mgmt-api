import datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from task_mgmt_api.database import get_session
from task_mgmt_api.model.task import Task
from task_mgmt_api.schema.tasks import TaskCreate, TaskFullUpdate, TaskPartialUpdate


async def create_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
    try:
        new_task = Task(**task.model_dump())
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)
        return new_task
    except Exception:
        await session.rollback()
        raise


async def get_task_by_name_and_due_date(
    name: str,
    due_date: datetime,
    session: AsyncSession = Depends(get_session),
):
    existing_task = await session.scalar(
        select(Task).where(Task.name == name, Task.due_date == due_date)
    )
    return existing_task


async def get_all_tasks(session: AsyncSession = Depends(get_session)):
    tasks = await session.scalars(select(Task))
    return tasks.all()


async def get_task_by_id(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.scalar(select(Task).where(Task.id == task_id))
    return task


async def update_entire_task(
    task_id: int,
    task: TaskFullUpdate,
    session: AsyncSession = Depends(get_session),
):
    try:
        existing_task = await session.scalar(select(Task).where(Task.id == task_id))
        if existing_task is None:
            return None

        for field, value in task.model_dump().items():
            setattr(existing_task, field, value)

        await session.commit()
        await session.refresh(existing_task)
        return existing_task
    except Exception:
        await session.rollback()
        raise


async def update_task_partialy(
    task_id: int,
    task: TaskPartialUpdate,
    session: AsyncSession = Depends(get_session),
):
    existing_task = await session.get(Task, task_id)
    if existing_task is None:
        return None

    for field, value in task.model_dump(exclude_unset=True).items():
        setattr(existing_task, field, value)

    await session.commit()
    await session.refresh(existing_task)
    return existing_task


async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if task is None:
        return None

    await session.delete(task)
    await session.commit()
    return task
