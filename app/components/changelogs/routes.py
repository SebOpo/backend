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


@router.get("/search/")
async def search_changelogs(
        search_params: changelogs.schemas.ChangeLogSearch = Depends(),
        db: Session = Depends(get_db)
) -> Any:
    print(search_params)
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

    changelog = changelogs.crud.changelogs.toggle_changelog_visibility(
        db, changelog_id=changelog_id
    )

    return changelog
