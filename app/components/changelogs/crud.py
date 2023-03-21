import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.components import locations
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

    def search_changelogs(
        self,
        db: Session,
        organization_id: int = None,
        admin_id: int = None,
        query: str = None,
        date_min: datetime.datetime = None,
        date_max: datetime.datetime = datetime.datetime.utcnow(),
    ) -> List[models.ChangeLog]:
        filters = []
        if organization_id:
            filters.append(
                self.model.user.has(models.User.organization == organization_id)
            )
        if admin_id:
            filters.append(self.model.submitted_by == admin_id)
        if query:
            filters.append(
                self.model.location.has(
                    func.concat(
                        locations.models.Location.address,
                        locations.models.Location.street_number,
                        locations.models.Location.index,
                        locations.models.Location.city,
                    ).contains(query)
                )
            )
        if date_min:
            filters.append(self.model.created_at.between(date_min, date_max))
        else:
            filters.append(self.model.created_at <= date_max)
        return db.query(self.model).filter(*filters).all()

    def toggle_changelog_visibility(
        self, db: Session, changelog: models.ChangeLog
    ) -> models.ChangeLog:
        changelog.visible = not changelog.visible
        db.commit()
        db.refresh(changelog)
        return changelog

    def bulk_toggle_changelog_visibility(
        self,
        db: Session,
        visible: bool,
        user_id: int = None,
        organization_id: int = None,
    ) -> List[models.ChangeLog]:
        if not user_id and organization_id:
            raise HTTPException(status_code=402, detail="Bad params")

        if user_id:
            changelog_list = (
                db.query(self.model)
                .filter(self.model.submitted_by == user_id)
                .update({self.model.visible: visible}, synchronize_session=False)
            )
            return changelog_list

        elif organization_id:
            changelog_list = (
                db.query(self.model)
                .filter(self.model.user.organization == organization_id)
                .update({self.model.visible: visible})
            )
            return changelog_list


changelogs = CRUDChangelog(models.ChangeLog)
