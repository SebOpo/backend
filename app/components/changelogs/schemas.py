from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, validator

from app.utils.validators import convert_to_utc
from app.components.users import schemas


class ChangeLogBase(BaseModel):
    old_flags: Optional[Dict]
    new_flags: Dict


class ChangeLogCreate(ChangeLogBase):
    location_id: int
    submitted_by: int


class ChangelogOut(ChangeLogBase):
    id: int
    created_at: datetime
    user: schemas.UserRepresentation
    hidden: bool

    _utc_created_at = validator("created_at", allow_reuse=True)(convert_to_utc)

    class Config:
        orm_mode = True
