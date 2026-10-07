from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession


from src.task_mgmt_api.repository.task import get_task_by_name_and_due_date


async def check_task_uniqueness(name: str, due_date: date, session: AsyncSession) -> None:
    existing_task = await get_task_by_name_and_due_date(name, due_date, session)
    if existing_task is not None:
        raise ValueError("Task with the same name and due date already exists") 



def validate_due_date(due_date: date | None) -> None:
    if due_date is not None and due_date < date.today():
        raise ValueError("Due date cannot be in the past")

