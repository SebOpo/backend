from typing import Any, List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Security
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user
from app.components import activity_logs

router = APIRouter(prefix="/activity-logs", tags=["activity-logs"])


@router.get('/organization/organization_id', response_model=List[activity_logs.schemas.ActivityLogOut])
async def get_organization_logs(
        organization_id: int,
        db: Session = Depends(get_db),
        current_user=Security(get_current_active_user, scopes=["organizations:edit"])
) -> Any:

    if current_user.role != "platform_administrator" and current_user.organization != organization_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    logs = activity_logs.crud.logs.get_multi(db, organization_id=organization_id)
    return logs
