from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.components.changelogs import models


def create_changelog(
    db: Session, location_id: int, old_object: dict, new_object: dict
) -> models.ChangeLog:

    changelog = models.ChangeLog(
        location_id=location_id,
        action_type=1,
        old_flags=old_object,
        new_flags=new_object,
    )

    db.add(changelog)
    db.commit()
    db.refresh(changelog)
    return changelog


def get_changelogs(db: Session, location_id: int) -> models.ChangeLog:
    return (
        db.query(models.ChangeLog)
        .filter(models.ChangeLog.location_id == location_id)
        .order_by(desc(models.ChangeLog.created_at))
        .all()
    )
