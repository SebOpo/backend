import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, validator

# TODO: Find a better name.
from app.components import user as userc
from app.schemas.validators import convert_to_utc


class OrganizationBase(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class OrganizationOut(OrganizationBase):
    id: int
    created_at: datetime.datetime
    participants: Optional[List[userc.schemas.UserRepresentation]]

    _utc_created_at = validator("created_at", allow_reuse=True)(convert_to_utc)

    class Config:
        orm_mode = True


class OrganizationUserInvite(BaseModel):
    emails: List[EmailStr]
