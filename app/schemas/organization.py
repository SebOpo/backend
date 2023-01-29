import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, validator

from app.schemas.validators import convert_to_utc


class OrganizationBase(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class OrganizationOut(OrganizationBase):
    id: int
    created_at: datetime.datetime
    participants: Optional[List["userc.schemas.UserRepresentation"]]

    _utc_created_at = validator("created_at", allow_reuse=True)(convert_to_utc)

    class Config:
        orm_mode = True


class OrganizationUserInvite(BaseModel):
    emails: List[EmailStr]


# TODO: Find a better name
# TODO: Nasty import hack, will look for something better
# From here: https://stackoverflow.com/questions/63420889/fastapi-pydantic-circular-references-in-separate-files
from app.components import user as userc

# Pydantic hack to avoid circular imports
OrganizationOut.update_forward_refs()
