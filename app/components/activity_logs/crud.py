from typing import List

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.components.activity_logs import models, schemas
from app.core.base_crud import CRUDBase


class CRUDActivityLogs(
    CRUDBase[models.ActivityLog, schemas.ActivityLogBase, schemas.ActivityLogBase]
):
    def get_multi(
        self, db: Session, organization_id: int, skip: int = 0, limit: int = 20
    ) -> List[models.ActivityLog]:
        return (
            db.query(self.model)
            .filter(self.model.organization_id == organization_id)
            .order_by(desc(self.model.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )


logs = CRUDActivityLogs(models.ActivityLog)
