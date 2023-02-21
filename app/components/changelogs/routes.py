from typing import Any, List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Security
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user
from app.components import users, changelogs


router = APIRouter(prefix="/changelogs", tags=['changelogs'])


@router.get("/{location_id}", response_model=List[changelogs.schemas.ChangelogOut])
async def get_location_changelogs(
    location_id: int, db: Session = Depends(get_db)
) -> Any:

    logs = changelogs.crud.changelogs.get_changelogs(db, location_id)

    return logs


@router.get("/search/", response_model=List[changelogs.schemas.OrganizationChangelogOut])
async def search_changelogs(
        search_params: changelogs.schemas.ChangeLogSearch = Depends(),
        db: Session = Depends(get_db)
) -> Any:
    changelog_list = changelogs.crud.changelogs.search_changelogs(
        db, **search_params.dict()
    )
    return changelog_list


@router.put("/visibility/{changelog_id}", response_model=changelogs.schemas.ChangelogOut)
async def toggle_visibility(
        changelog_id: int,
        db: Session = Depends(get_db),
        current_user: users.models.User = Security(
            get_current_active_user, scopes=["changelogs:edit"]
        )
) -> Any:

    changelog = changelogs.crud.changelogs.get(db, model_id=changelog_id)
    if not changelog:
        raise HTTPException(status_code=404, detail="Not found")

    if current_user.role != "platform_administrator" and changelog.user.organization != current_user.organization:
        raise HTTPException(status_code=403, detail="Not allowed")

    updated_changelog = changelogs.crud.changelogs.toggle_changelog_visibility(
        db, changelog=changelog
    )

    return updated_changelog
