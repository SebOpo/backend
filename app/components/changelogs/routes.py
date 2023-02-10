from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Security
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user
from app.components import users


router = APIRouter(prefix="/changelogs", tags=['changelogs'])


@router.put("/visibility/{changelog_id}")
async def toggle_visibility(
        changelog_id: int,
        db: Session = Depends(get_db),
        current_user: users.models.User = Security(
            get_current_active_user, scopes=["changelogs:edit"]
        )
) -> Any:
    pass