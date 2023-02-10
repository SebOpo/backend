from sqlalchemy import desc
from sqlalchemy.orm import Session
from fastapi import HTTPException

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

    def toggle_changelog_visibility(self, db: Session, changelog_id: int) -> models.ChangeLog:
        db_changelog = self.get(db, model_id=changelog_id)
        if not db_changelog:
            raise HTTPException(status_code=400, detail="No such record.")
        db_changelog.hidden = not db_changelog.hidden
        db.commit()
        db.refresh(db_changelog)
        return db_changelog


changelogs = CRUDChangelog(models.ChangeLog)
