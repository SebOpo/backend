from typing import Optional
from datetime import datetime

from pydantic import BaseModel, validator

from app.schemas.validators import convert_to_utc


class UserSession(BaseModel):
    id: int
    created_at: datetime
    expires_at: datetime
    user_agent: Optional[str]
    user_ip: Optional[str]

    _utc_datetime = validator('created_at', 'expires_at', allow_reuse=True)(convert_to_utc)

    class Config:
        orm_mode = True
