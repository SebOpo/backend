from typing import Any, List

from fastapi import APIRouter, Security, Depends

from sqlalchemy.orm import Session

from app import models, schemas
from app.api.dependencies import get_current_active_user, get_db
from app.crud.crud_oauth import scopes, roles


router = APIRouter()


@router.post('/roles/create', response_model=schemas.OauthRoleOut)
async def create_oauth_role(
        oauth_role: schemas.OauthRoleCreate,
        current_active_user: models.User = Security(
            get_current_active_user,
            scopes=['oauth:create']
        ),
        db: Session = Depends(get_db)
) -> Any:
    pass


@router.get('/roles/all', response_model=List[schemas.OauthRoleOut])
async def get_all_oauth_roles(
        current_active_user: models.User = Security(
            get_current_active_user,
            scopes=['oauth:read']
        ),
        db: Session = Depends(get_db)
) -> Any:

    role_list = roles.get_all(db)
    return role_list


@router.put('/roles/patch', response_model=schemas.OauthRoleOut)
async def patch_oauth_role(
        current_active_user: models.User = Security(
            get_current_active_user,
            scopes=['oauth:edit']
        ),
        db: Session = Depends(get_db)
) -> Any:

    pass


@router.get('/scopes/all', response_model=List[schemas.OauthScopeOut])
async def get_all_oauth_scopes(
        current_active_user: models.User = Security(
            get_current_active_user,
            scopes=['oauth:read']
        ),
        db: Session = Depends(get_db)
) -> Any:

    scope_list = scopes.get_all(db)
    return scope_list
