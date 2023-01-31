from typing import Optional, List

from pydantic import BaseModel


class OauthScope(BaseModel):
    module: str
    scope: str


class OauthScopeOut(OauthScope):
    id: int

    class Config:
        orm_mode = True


class OauthRole(BaseModel):
    verbose_name: str


class OauthRoleCreate(OauthRole):
    scope_ids: List[int]


class OauthRoleOut(OauthRole):
    id: int
    scopes: Optional[List[OauthScopeOut]]

    class Config:
        orm_mode = True
