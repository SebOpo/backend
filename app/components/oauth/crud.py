from typing import List, Optional

from sqlalchemy.orm import Session

from app.components.oauth import models, schemas
from app.core.base_crud import CRUDBase


class CRUDScopes(
    CRUDBase[
        models.OauthScope,
        schemas.OauthScope,
        schemas.OauthScope,
    ]
):
    def get_or_create_scope(
        self, db: Session, *, scope: schemas.OauthScope
    ) -> models.OauthScope:
        existing_scope = self.get_scope_by_scope_string(db, scope.scope)
        if existing_scope:
            return existing_scope

        db_object = models.OauthScope(module=scope.module, scope=scope.scope)

        db.add(db_object)
        db.commit()
        db.refresh(db_object)
        return db_object

    def get_scope_by_scope_string(
        self, db: Session, scope_string: str
    ) -> models.OauthScope:
        return db.query(self.model).filter(self.model.scope == scope_string).first()

    def get_by_multi_id(self, db: Session, ids: List[int]):
        return db.query(self.model).filter(self.model.id.in_(ids)).all()


class CRUDRoles(
    CRUDBase[
        models.OauthRole,
        schemas.OauthRoleCreate,
        schemas.OauthRoleCreate,
    ]
):
    def get_or_create_role(
        self,
        db: Session,
        *,
        role: schemas.OauthRole,
        scope_list: List[schemas.OauthScope],
    ) -> models.OauthRole:
        existing_role = self.get_role_by_name(db, role_name=role.verbose_name)
        if existing_role:
            return existing_role

        db_object = models.OauthRole(
            verbose_name=role.verbose_name, authority=role.authority
        )
        db_object.scopes.extend(scope_list)

        db.add(db_object)
        db.commit()
        db.refresh(db_object)
        return db_object

    def get_role_by_name(
        self,
        db: Session,
        role_name: str,
    ) -> models.OauthRole:
        return db.query(self.model).filter(self.model.verbose_name == role_name).first()

    def patch(
        self,
        db: Session,
        *,
        role: models.OauthRole,
        scope_list: List[schemas.OauthScope],
        obj_in: schemas.OauthRoleCreate,
    ) -> Optional[models.OauthRole]:
        data_to_update = obj_in.dict(exclude_unset=True)
        for field in data_to_update:
            setattr(role, field, data_to_update[field])

        role.scopes = scope_list
        db.commit()
        db.refresh(role)
        return role


scopes = CRUDScopes(models.OauthScope)
roles = CRUDRoles(models.OauthRole)
