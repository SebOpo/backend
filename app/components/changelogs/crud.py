import datetime
from typing import List

from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.components.changelogs import models, schemas
from app.components import users
from app.components import locations
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

    def search_changelogs(
            self,
            db: Session,
            organization_id: int = None,
            admin_id: int = None,
            query: str = None,
            date_min: datetime.datetime = None,
            date_max: datetime.datetime = datetime.datetime.utcnow()
    ) -> List[models.ChangeLog]:

        print(date_max)

        filters = []
        if organization_id:
            filters.append(self.model.user.has(models.User.organization == organization_id))
        if admin_id:
            filters.append(self.model.submitted_by == admin_id)
        if query:
            filters.append(
                self.model.location.has(
                    func.concat(
                        locations.models.Location.address, locations.models.Location.street_number
                    ).contains(query)
                )
            )
        if date_min:
            filters.append(self.model.created_at.between(date_min, date_max))
        else:
            filters.append(self.model.created_at <= date_max)
        return db.query(self.model).filter(*filters).all()

    def toggle_changelog_visibility(self, db: Session, changelog_id: int) -> models.ChangeLog:
        db_changelog = self.get(db, model_id=changelog_id)
        if not db_changelog:
            raise HTTPException(status_code=400, detail="No such record.")
        db_changelog.hidden = not db_changelog.hidden
        db.commit()
        db.refresh(db_changelog)
        return db_changelog


changelogs = CRUDChangelog(models.ChangeLog)
