from sqlalchemy.orm import Session

from app.components.organizations import crud


def get_master_organization(db: Session) -> int:
    return crud.get_by_name(db, "DIM").id
