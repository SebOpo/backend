import datetime
from typing import Optional

from pydantic import BaseModel


class ActivityLogBase(BaseModel):
    user_id: Optional[int] = None
    organization_id: Optional[int] = None
    action_type: int
    description: str


class ActivityLogOut(ActivityLogBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True
