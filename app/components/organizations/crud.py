from typing import Optional, List

from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.components import users
from app.components.organizations import models, schemas
from app.core.base_crud import CRUDBase


class CRUDOrganization(
    CRUDBase[models.Organization, schemas.OrganizationBase, schemas.OrganizationBase]
):

    def get_by_name(self, db: Session, name: str) -> Optional[models.Organization]:
        return (
            db.query(self.model).filter(self.model.name == name).first()
        )

    def get_by_substr(self, db: Session, name: str) -> List[models.Organization]:
        return (
            db.query(self.model)
                .filter(func.lower(self.model.name).startswith(name))
                .all()
        )

    def get_organizations_list(
            self, db: Session, limit: int = 20, skip: int = 0
    ) -> List[models.Organization]:
        return (
            db.query(self.model)
                .order_by(desc(self.model.created_at))
                .limit(limit)
                .offset(skip * limit)
                .all()
        )

    def edit_organization(
            self, db: Session, organization_id: int, obj_in: schemas.OrganizationBase
    ) -> Optional[models.Organization]:

        organization = self.get(db, model_id=organization_id)
        if not organization:
            return None

        # convert the request to dict to iterate over its fields
        data_to_update = obj_in.dict(exclude_unset=True)
        for field in data_to_update:
            # updated the organization with no explicit field declaration
            setattr(organization, field, data_to_update[field])

        db.commit()
        db.refresh(organization)
        return organization

    def add_members(
            self, db: Session, organization_id: int, user_emails: List[str]
    ) -> models.Organization:

        # TODO refactor this!

        for user in user_emails:
            db_user = (
                db.query(users.models.User)
                    .filter(
                    users.models.User.email == user,
                    users.models.User.email_confirmed == True,
                    users.models.User.is_active == True,
                )
                    .first()
            )
            if not db_user:
                continue

            db_user.organization = organization_id
            db.commit()
            db.refresh(db_user)

        return self.get(db, model_id=organization_id)

    def remove_members(
            self, db: Session, organization_id: int, user_id: int
    ) -> Optional[models.Organization]:

        db_user = db.query(users.models.User).get(user_id)
        if not db_user or not db_user.organization:
            return None

        db_user.organization = None
        db.commit()
        db.refresh(db_user)

        return self.get(db, model_id=organization_id)

    def delete_organization(
            self,
            db: Session,
            organization_id: int,
    ) -> Optional[models.Organization]:

        organization = self.get(db, model_id=organization_id)

        db.delete(organization)
        db.commit()

        return self.get(db, model_id=organization_id)


organizations = CRUDOrganization(models.Organization)
