from typing import Any, List

import fastapi
from fastapi import APIRouter, Depends, HTTPException, Security, status, Response
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user
from app.components.organizations import crud, schemas
from app.components import users
from app.core.config import settings
from app.utils.email_sender import send_email

router = APIRouter()


@router.post("/create", response_model=schemas.OrganizationOut)
async def create_organization(
    organization: schemas.OrganizationBase,
    db: Session = Depends(get_db),
    current_active_user=Security(
        get_current_active_user, scopes=["organizations:create"]
    ),
) -> Any:
    existing_organization = crud.organizations.get_by_name(db, organization.name)

    if existing_organization:
        raise HTTPException(status_code=400, detail="Organization exists")

    new_organization = crud.organizations.create(db, obj_in=organization)

    if not new_organization:
        raise HTTPException(
            status_code=500,
            detail="Cannot connect to the database. Please try again later",
        )

    return new_organization


@router.post('/add', response_model=schemas.OrganizationOut)
async def add_new_organization(
        organization: schemas.OrganizationLeaderInvite,
        db: Session = Depends(get_db),
        current_active_user=Security(
            get_current_active_user, scopes=["organizations:create"]
        ),
) -> Any:
    existing_organization = crud.organizations.get_by_name(db, name=organization.name)
    if existing_organization:
        raise HTTPException(status_code=400, detail="Such organization already exists.")

    new_organization = crud.organizations.create(db, obj_in=organization.dict(exclude={'emails'}))

    for email in organization.emails:
        new_user = users.crud.create_invite(
            db,
            obj_in=users.schemas.UserInvite(
                email=email,
                organization=new_organization.id
            ),
            organization=new_organization,
            role_name="organizational_leader"
        )
        if settings.EMAILS_ENABLED:
            send_email(
                to_addresses=[new_user.email],
                template_type="invite",
                link="{}/registration/?access_token={}".format(
                    settings.DOMAIN_ADDRESS, new_user.registration_token
                ),
            )

    return new_organization


@router.put('/activate', response_model=schemas.OrganizationOut)
async def activate_organization(
        organization: schemas.OrganizationBase,
        db: Session = Depends(get_db),
        current_active_user=Security(
            get_current_active_user, scopes=["organizations:edit"]
        ),
) -> Any:
    pass


@router.get("/all", response_model=List[schemas.OrganizationOut])
async def get_organization_list(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_active_user=Security(
        get_current_active_user, scopes=["organizations:view"]
    ),
) -> Any:
    return crud.organizations.get_organizations_list(db, limit=limit, skip=page - 1)


@router.get("/search", response_model=List[schemas.OrganizationOut])
async def search_organizations_by_name(
    query: str,
    db: Session = Depends(get_db),
    current_active_user=Security(
        get_current_active_user, scopes=["organizations:view"]
    ),
) -> Any:
    organizations = crud.organizations.get_by_substr(db, query.lower())
    if not organizations:
        return []

    return organizations


@router.get("/{organization_id}", response_model=schemas.OrganizationOut)
async def get_organization_by_id(
    organization_id: int,
    db: Session = Depends(get_db),
    current_active_user=Security(
        get_current_active_user, scopes=["organizations:view"]
    ),
) -> Any:
    organization = crud.organizations.get(db, model_id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Not found")

    return organization


@router.put("/{organization_id}/edit", response_model=schemas.OrganizationOut)
async def edit_organization_data(
    organization_id: int,
    data: schemas.OrganizationBase,
    db: Session = Depends(get_db),
    current_active_user=Security(
        get_current_active_user, scopes=["organizations:edit"]
    ),
) -> Any:

    updated_organization = crud.organizations.edit_organization(
        db, organization_id=organization_id, obj_in=data
    )
    if not updated_organization:
        raise HTTPException(status_code=404, detail="Not found")

    return updated_organization


@router.put("/{organization_id}/invite", response_model=schemas.OrganizationOut)
async def invite_organization_members(
    organization_id: int,
    users: schemas.OrganizationUserInvite,
    db: Session = Depends(get_db),
    current_active_user=Security(
        get_current_active_user, scopes=["organizations:edit"]
    ),
) -> Any:
    organization = crud.organizations.get(db, model_id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Not found")

    updated_organization = crud.organizations.add_members(
        db, organization_id=organization_id, user_emails=users.emails
    )

    return updated_organization


@router.put("/{organization_id}/remove", response_model=schemas.OrganizationOut)
async def remove_organization_member(
    organization_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_active_user=Security(
        get_current_active_user, scopes=["organizations:edit"]
    ),
) -> Any:
    organization = crud.organizations.get(db, model_id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Not found")

    updated_organization = crud.organizations.remove_members(
        db, organization_id=organization_id, user_id=user_id
    )
    if not updated_organization:
        raise HTTPException(
            status_code=400, detail="This user does not belong to such organization"
        )

    return updated_organization


@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_active_user=Security(
        get_current_active_user, scopes=["organizations:delete"]
    ),
) -> Any:
    organization = crud.organizations.get(db, model_id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Not found")

    removed_organization = crud.organizations.delete_organization(db, organization_id=organization_id)
    if removed_organization:
        raise HTTPException(status_code=400, detail="Cannot perform such action")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
