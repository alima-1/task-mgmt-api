from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.task_mgmt_api.database import get_session
from src.task_mgmt_api.repository.task import create_task as create_task_repo
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
