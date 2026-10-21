from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    # ensure that name is not empty
    name: str = Field(min_length=1)
    description: str | None = None
    due_date: date | None = None
    completed: bool = False


class TaskResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    due_date: date | None = None
    completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
