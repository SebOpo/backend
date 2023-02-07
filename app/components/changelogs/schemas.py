from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, validator

from app.utils.validators import convert_to_utc


class ChangeLogBase(BaseModel):
    old_flags: Optional[Dict]
    new_flags: Dict


class ChangeLogCreate(ChangeLogBase):
    location_id: int
    action_type: int = 1  # Subject to remove.


class ChangelogOut(ChangeLogBase):
    id: int
    created_at: datetime
    action_type: int

    _utc_created_at = validator("created_at", allow_reuse=True)(convert_to_utc)

    class Config:
        orm_mode = True