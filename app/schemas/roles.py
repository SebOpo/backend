from typing import List

from pydantic import BaseModel


# TODO: Unused as of 31/01/2023
class UserRole(BaseModel):

    verbose_name: str
    permissions: List[str]

    class Config:
        orm_mode = True
