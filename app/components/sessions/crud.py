from typing import Optional, List

from sqlalchemy.orm import Session

from app.components.sessions import models


def create(
    db: Session,
    *,
    user_id: int,
    access_token: str,
    user_agent: str = None,
    user_ip: str = None,
):
    db_obj = models.SessionHistory(
        user_id=user_id,
        access_token=access_token,
        user_agent=user_agent,
        user_ip=user_ip,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_by_access_token(
    db: Session, *, user_id: int, access_token: str
) -> Optional[models.SessionHistory]:
    return (
        db.query(models.SessionHistory)
        .filter(
            models.SessionHistory.access_token == access_token,
            models.SessionHistory.user_id == user_id,
        )
        .first()
    )


def get_user_active_sessions(
    db: Session,
    *,
    user_id: int,
) -> List[models.SessionHistory]:
    return (
        db.query(models.SessionHistory)
        .filter(
            models.SessionHistory.user_id == user_id,
            models.SessionHistory.is_active == True,
        )
        .all()
    )


def revoke_by_id(
    db: Session, *, user_id: int, session_id: int
) -> models.SessionHistory:
    db_obj = (
        db.query(models.SessionHistory)
        .filter(
            models.SessionHistory.user_id == user_id,
            models.SessionHistory.id == session_id,
        )
        .first()
    )
    if not db_obj:
        return None

    db_obj.is_active = False
    db.commit()
    db.refresh(db_obj)
    return db_obj


# def revoke_by_token(db: Session, *, user_id: int, access_token: str) -> SessionHistory:
#     db_obj = db.query(SessionHistory).filter(SessionHistory.user_id == user_id,
#                                              SessionHistory.access_token == access_token).first()
#     if not db_obj:
#         return None
#
#     db_obj.is_active = False
#     db.commit()
#     db.refresh(db_obj)
#     return db_obj
