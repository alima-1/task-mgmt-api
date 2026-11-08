from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.task_mgmt_api.database import get_session
from src.task_mgmt_api.repository.task import create_task as create_task_repo
from src.task_mgmt_api.repository.task import get_all_tasks, get_task_by_id
from src.task_mgmt_api.schema.tasks import TaskCreate, TaskResponse
from src.task_mgmt_api.services.task import check_task_uniqueness, validate_due_date

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
    try:
        if task.due_date is not None:
            validate_due_date(task.due_date)
        await check_task_uniqueness(task.name, task.due_date, session)
        return await create_task_repo(task, session)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"message": str(ve)},
        ) from ve


@router.get("", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
async def get_tasks(session: AsyncSession = Depends(get_session)):
    # there's no need to try-except here b'se the maojor
    # sqlalchemy errors are handled in main.py
    tasks = await get_all_tasks(session)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def get_task_by_id_(task_id: int, session: AsyncSession = Depends(get_session)):
    # there's no need to try-except here b'se the maojor
    # sqlalchemy errors are handled in main.py
    task = await get_task_by_id(task_id, session)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Task not found"},
        )
    return task
