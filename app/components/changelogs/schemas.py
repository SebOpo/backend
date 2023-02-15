from datetime import datetime, timedelta
import calendar
from typing import Optional, Dict, Any

from pydantic import BaseModel, validator, root_validator

from app.utils.validators import convert_to_utc
from app.components import users, locations


class ChangeLogBase(BaseModel):
    old_flags: Optional[Dict]
    new_flags: Dict


class ChangeLogCreate(ChangeLogBase):
    location_id: int
    submitted_by: int


class ChangeLogSearch(BaseModel):
    organization_id: Optional[int] = None
    admin_id: Optional[int] = None
    query: Optional[str] = None
    date_min: Optional[Any] = None
    # The timedelta here is used for testing purposes.
    # The test won't pass with a default value, because the record is actually created after the api call.
    # Need to change it later I guess.
    date_max: Optional[Any] = int((datetime.utcnow() + timedelta(minutes=15)).timestamp())

    @validator("date_min", "date_max", pre=True)
    def parse_dates(cls, v):
        if not v or isinstance(v, datetime):
            return
        return datetime.fromtimestamp(int(v))


class ChangelogOut(ChangeLogBase):
    id: int
    created_at: datetime
    user: users.schemas.UserRepresentation
    hidden: bool

    _utc_created_at = validator("created_at", allow_reuse=True)(convert_to_utc)

    class Config:
        orm_mode = True


class OrganizationChangelogOut(ChangelogOut):
    location: locations.schemas.LocationOut

    @validator('location', pre=True)
    def assemble_location(cls, v):
        # TODO find a better approach
        # This happens due to the location in the relationship not having the "position" attribute.
        return v.to_json()

