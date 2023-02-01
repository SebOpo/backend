from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.components.changelogs import models, schemas
from app.core.base_crud import CRUDBase


class CRUDChangelog(
    CRUDBase[models.ChangeLog, schemas.ChangeLogCreate, schemas.ChangeLogCreate]
):
    def get_changelogs(self, db: Session, location_id: int) -> models.ChangeLog:
        return (
            db.query(self.model)
                .filter(self.model.location_id == location_id)
                .order_by(desc(self.model.created_at))
                .all()
        )


changelogs = CRUDChangelog(models.ChangeLog)
