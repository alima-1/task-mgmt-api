from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

class TaskCreate(BaseModel):
    name: str
    description: str | None = None
    due_date: date | None = None
    completed: bool = False


class TaskResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    completed: bool
    created_at: datetime


    model_config = ConfigDict(from_attributes=True)

