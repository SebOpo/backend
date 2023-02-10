import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, validator

from app.utils.validators import convert_to_utc


class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    organization: Optional[int]
    password: str


class UserInvite(BaseModel):
    email: EmailStr
    organization: int


class UserPasswordRenewal(BaseModel):
    access_token: str
    new_password: str


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class UserOrganizationDetails(BaseModel):
    id: int
    name: str
    # TODO Remove the nones when everything is tested
    disabled: Optional[bool] = None
    activated: Optional[bool] = None

    class Config:
        orm_mode = True


class UserRepresentation(UserBase):
    id: int
    last_activity: Optional[datetime.datetime] = None
    email_confirmed: bool
    is_active: bool
    organization: Optional[int]
    organization_model: Optional[UserOrganizationDetails] = None

    _utc_datetime = validator("last_activity", allow_reuse=True)(convert_to_utc)

    class Config:
        orm_mode = True


class UserOut(UserRepresentation):
    role: str
    # TODO REMOVE
    registration_token: Optional[str] = None


# TODO: Unused as of 31/01/2023
class UserRole(BaseModel):

    verbose_name: str
    permissions: List[str]

    class Config:
        orm_mode = True
