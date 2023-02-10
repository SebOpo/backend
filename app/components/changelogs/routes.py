from typing import Any

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
