from typing import Any, List

from fastapi import APIRouter, Security, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.components.oauth import crud, schemas

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.post("/roles/create", response_model=schemas.OauthRoleOut)
async def create_oauth_role(
    oauth_role: schemas.OauthRoleCreate,
    current_active_user=Security(get_current_active_user, scopes=["oauth:create"]),
    db: Session = Depends(get_db),
) -> Any:
    scope_list = crud.scopes.get_by_multi_id(db=db, ids=oauth_role.scope_ids)

    new_role = crud.roles.get_or_create_role(
        db=db,
        role=schemas.OauthRole(**oauth_role),
        scope_list=scope_list,
    )

    return new_role


@router.get("/roles/all", response_model=List[schemas.OauthRoleOut])
async def get_all_oauth_roles(
    current_active_user=Security(get_current_active_user, scopes=["oauth:read"]),
    db: Session = Depends(get_db),
) -> Any:
    role_list = crud.roles.get_all(db)
    return role_list


@router.put("/roles/patch", response_model=schemas.OauthRoleOut)
async def patch_oauth_role(
    role_id: int,
    oauth_role: schemas.OauthRoleCreate,
    current_active_user=Security(get_current_active_user, scopes=["oauth:edit"]),
    db: Session = Depends(get_db),
) -> Any:
    db_role = crud.roles.get(db=db, model_id=role_id)
    if not db_role:
        raise HTTPException(status_code=400, detail="Role not found.")

    scope_list = crud.scopes.get_by_multi_id(db=db, ids=oauth_role.scope_ids)
    patched_role = crud.roles.patch(
        db=db,
        role=db_role,
        scope_list=scope_list,
        obj_in=schemas.OauthRoleCreate(**oauth_role),
    )

    return patched_role


@router.get("/scopes/all", response_model=List[schemas.OauthScopeOut])
async def get_all_oauth_scopes(
    current_active_user=Security(get_current_active_user, scopes=["oauth:read"]),
    db: Session = Depends(get_db),
) -> Any:
    scope_list = crud.scopes.get_all(db)
    return scope_list
